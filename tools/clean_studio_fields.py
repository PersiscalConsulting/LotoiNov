"""Remove the Odoo Studio fields nobody uses from the migrated database.

Run it from the Odoo.sh shell, it reads the script from the standard input:

    odoo-bin shell -d <database> < ~/src/user/tools/clean_studio_fields.py

By default it only reports what it would delete. To delete, set CLEAN=1:

    CLEAN=1 odoo-bin shell -d <database> < ~/src/user/tools/clean_studio_fields.py

A field is deleted only if it is a manual field (not declared in code), has no
data, is not used by any active view (Studio views do not count), filter or
record rule, and no field that stays depends on it. The script is written
without blank lines inside blocks so the shell reads it from the standard input.
"""
import os
import re
CLEAN = os.environ.get('CLEAN') == '1'
MODELS = ['purchase.order', 'purchase.requisition', 'approval.request', 'approval.product.line', 'res.partner', 'hr.expense']
cr = env.cr
Fields = env['ir.model.fields']
views = env['ir.ui.view'].search([('active', '=', True)])
archs = ' '.join((v.arch_db or '') for v in views if not (v.name or '').startswith('Odoo Studio:'))
cr.execute("SELECT coalesce(string_agg(coalesce(domain, '') || ' ' || coalesce(context, '') || ' ' || coalesce(sort, ''), ' '), '') FROM ir_filters")
filters_text = cr.fetchone()[0]
cr.execute("SELECT coalesce(string_agg(coalesce(domain_force, ''), ' '), '') FROM ir_rule")
rules_text = cr.fetchone()[0]
def mentioned(name, text):
    return re.search(r'(?<![\w])' + re.escape(name) + r'(?![\w])', text) is not None
def count_data(f):
    if not f.store or f.ttype in ('one2many', 'many2many'):
        return 0
    cond = '"%s" IS TRUE' % f.name if f.ttype == 'boolean' else '"%s" IS NOT NULL' % f.name
    with cr.savepoint():
        cr.execute('SELECT count(*) FROM "%s" WHERE %s' % (f.model.replace('.', '_'), cond))
        return cr.fetchone()[0]
manual = Fields.search([('state', '=', 'manual'), ('model', 'in', MODELS)]).filtered(lambda f: f.name.startswith('x_'))
keep = {}
for f in manual:
    reasons = []
    rows = count_data(f)
    if rows:
        reasons.append('tiene %s registros con datos' % rows)
    if mentioned(f.name, archs):
        reasons.append('lo usa una vista activa')
    if mentioned(f.name, filters_text):
        reasons.append('lo usa un filtro guardado')
    if mentioned(f.name, rules_text):
        reasons.append('lo usa una regla de acceso')
    if reasons:
        keep[f.id] = '; '.join(reasons)
changed = True
while changed:
    changed = False
    delete = manual.filtered(lambda f: f.id not in keep)
    for f in delete:
        users = Fields.search(['|', '|', ('related', 'like', f.name), ('depends', 'like', f.name), '&', ('relation', '=', f.model), ('relation_field', '=', f.name)]) - delete
        if users:
            keep[f.id] = 'lo necesita: ' + ', '.join('%s.%s' % (u.model, u.name) for u in users[:3])
            changed = True
delete = manual.filtered(lambda f: f.id not in keep)
print('=== SE CONSERVAN (%s) ===' % len(manual.filtered(lambda f: f.id in keep)))
for f in manual.filtered(lambda f: f.id in keep).sorted(lambda f: (f.model, f.name)):
    print('  %s.%s -> %s' % (f.model, f.name, keep[f.id]))
print('=== SE BORRAN (%s) ===' % len(delete))
for f in delete.sorted(lambda f: (f.model, f.name)):
    print('  %s.%s (%s)' % (f.model, f.name, f.ttype))
if CLEAN and delete:
    delete.unlink()
    cr.commit()
    print('Borrados. Reiniciá con odoosh-restart.')
else:
    print('Solo informe: no se borró nada. Para borrar, correr con CLEAN=1.')
