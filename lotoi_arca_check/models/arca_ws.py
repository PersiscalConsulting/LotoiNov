"""Cliente minimo de los servicios de ARCA (ex AFIP) que usa el control de proveedores.

No depende de Odoo: solo arma y lee los mensajes, y firma el pedido de acceso (WSAA).
Los servicios son:
  * WSAA (login con certificado), servicio "ws_sr_constancia_inscripcion".
  * Padron A5 (getPersona_v2): constancia de inscripcion de un CUIT.
"""
import base64
import re
import time
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone
from xml.sax.saxutils import escape

SERVICE = 'ws_sr_constancia_inscripcion'

URLS = {
    'production': {
        'wsaa': 'https://wsaa.afip.gov.ar/ws/services/LoginCms',
        'padron': 'https://aws.afip.gov.ar/sr-padron/webservices/personaServiceA5',
    },
    'testing': {
        'wsaa': 'https://wsaahomo.afip.gov.ar/ws/services/LoginCms',
        'padron': 'https://awshomo.afip.gov.ar/sr-padron/webservices/personaServiceA5',
    },
}

AR_TZ = timezone(timedelta(hours=-3))


class ArcaError(Exception):
    """Error al hablar con ARCA (red, formato o rechazo del servicio)."""


def _local(tag):
    return tag.rsplit('}', 1)[-1]


def _find_all(root, name):
    return [e for e in root.iter() if _local(e.tag) == name]


def _find_text(root, name):
    for e in root.iter():
        if _local(e.tag) == name and e.text:
            return e.text.strip()
    return None


# --------------------------------------------------------------------------- WSAA
def build_tra(service=SERVICE, now=None):
    """Pedido de ticket de acceso (loginTicketRequest)."""
    now = now or datetime.now(AR_TZ)
    gen = (now - timedelta(minutes=10)).isoformat(timespec='seconds')
    exp = (now + timedelta(minutes=10)).isoformat(timespec='seconds')
    return (
        '<?xml version="1.0" encoding="UTF-8"?>'
        '<loginTicketRequest version="1.0"><header>'
        '<uniqueId>%d</uniqueId><generationTime>%s</generationTime><expirationTime>%s</expirationTime>'
        '</header><service>%s</service></loginTicketRequest>' % (int(time.time()), gen, exp, service)
    ).encode()


def sign_tra(tra, cert_pem, key_pem):
    """Firma el pedido (CMS / PKCS#7 en DER) con el certificado y la clave, y lo devuelve en base64."""
    from cryptography import x509
    from cryptography.hazmat.primitives import hashes, serialization
    from cryptography.hazmat.primitives.serialization import pkcs7

    cert = x509.load_pem_x509_certificate(cert_pem)
    key = serialization.load_pem_private_key(key_pem, password=None)
    cms = (pkcs7.PKCS7SignatureBuilder().set_data(tra).add_signer(cert, key, hashes.SHA256())
           .sign(serialization.Encoding.DER, [pkcs7.PKCS7Options.Binary]))
    return base64.b64encode(cms).decode()


def build_login_envelope(cms_b64):
    return (
        '<?xml version="1.0" encoding="UTF-8"?>'
        '<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" '
        'xmlns:wsaa="http://wsaa.view.sua.dvadac.desein.afip.gov">'
        '<soapenv:Header/><soapenv:Body><wsaa:loginCms><wsaa:in0>%s</wsaa:in0></wsaa:loginCms>'
        '</soapenv:Body></soapenv:Envelope>' % cms_b64
    ).encode()


def _fault(root):
    f = _find_text(root, 'faultstring')
    return f


def parse_login_response(content):
    """Devuelve (token, sign, vencimiento UTC naive)."""
    try:
        root = ET.fromstring(content)
    except ET.ParseError as e:
        raise ArcaError('Respuesta de WSAA ilegible: %s' % e)
    fault = _fault(root)
    if fault:
        raise ArcaError('WSAA: %s' % fault)
    ticket = _find_text(root, 'loginCmsReturn')
    if not ticket:
        raise ArcaError('WSAA no devolvio el ticket de acceso.')
    inner = ET.fromstring(ticket.encode())
    token, sign, exp = _find_text(inner, 'token'), _find_text(inner, 'sign'), _find_text(inner, 'expirationTime')
    if not (token and sign and exp):
        raise ArcaError('El ticket de WSAA esta incompleto.')
    exp_dt = datetime.fromisoformat(exp)
    if exp_dt.tzinfo:
        exp_dt = exp_dt.astimezone(timezone.utc).replace(tzinfo=None)
    return token, sign, exp_dt


# --------------------------------------------------------------------------- Padron A5
def build_persona_envelope(token, sign, cuit_representada, cuit):
    return (
        '<?xml version="1.0" encoding="UTF-8"?>'
        '<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" '
        'xmlns:a5="http://a5.soap.ws.server.puc.sr/"><soapenv:Header/><soapenv:Body>'
        '<a5:getPersona_v2><token>%s</token><sign>%s</sign>'
        '<cuitRepresentada>%s</cuitRepresentada><idPersona>%s</idPersona></a5:getPersona_v2>'
        '</soapenv:Body></soapenv:Envelope>' % (escape(token), escape(sign), cuit_representada, cuit)
    ).encode()


def parse_persona_response(content):
    """Interpreta la constancia de inscripcion.

    Devuelve un diccionario con:
      status: 'active' | 'inactive' | 'not_found' | 'constancia_error'
      message: texto para mostrar al usuario
      name: razon social / nombre (si vino)
    Si el servicio falla (no es un problema del CUIT) levanta ArcaError.
    """
    try:
        root = ET.fromstring(content)
    except ET.ParseError as e:
        raise ArcaError('Respuesta del padron ilegible: %s' % e)
    fault = _fault(root)
    if fault:
        low = fault.lower()
        if 'no existe persona' in low:
            return {'status': 'not_found', 'message': 'El CUIT no existe en ARCA.', 'name': ''}
        raise ArcaError('Padron: %s' % fault)
    errors = [e.text.strip() for ec in _find_all(root, 'errorConstancia') for e in ec.iter()
              if _local(e.tag) == 'error' and e.text]
    estado = _find_text(root, 'estadoClave')
    nombre = _find_text(root, 'razonSocial') or ' '.join(
        x for x in (_find_text(root, 'apellido'), _find_text(root, 'nombre')) if x)
    if estado and estado.upper() != 'ACTIVO':
        return {'status': 'inactive', 'message': 'La clave del CUIT figura como %s en ARCA.' % estado.upper(),
                'name': nombre or ''}
    if errors:
        return {'status': 'constancia_error', 'name': nombre or '',
                'message': 'La constancia de inscripcion tiene errores: %s' % '; '.join(errors)}
    if not estado:
        raise ArcaError('El padron no informo el estado del CUIT.')
    return {'status': 'active', 'message': 'CUIT activo.', 'name': nombre or ''}


def digits(value):
    return re.sub(r'\D', '', value or '')
