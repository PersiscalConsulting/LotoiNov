"""Fill the new "Referencia" selection (lotoi_obra_id) from the old text fields.

Run it from the Odoo.sh shell, it reads the script from the standard input:

    odoo-bin shell -d <database> < ~/src/user/tools/migrate_obras.py

By default it only reports what it would do. To write, set CLEAN=1:

    CLEAN=1 odoo-bin shell -d <database> < ~/src/user/tools/migrate_obras.py

The text is matched with the name or the reference of the analytic accounts of
the "Obras" plan, ignoring case, spaces, dashes and other symbols ("OB-12",
"ob 12" and "OB12" are the same work). Only the selection is filled: the
analytic distribution of the existing documents is not touched. The script is
written without blank lines inside blocks so the shell reads it from the
standard input.
"""
import os
import re
CLEAN = os.environ.get('CLEAN') == '1'
cr = env.cr
plan = env.ref('lotoi_obras.analytic_plan_obras')
accounts = env['account.analytic.account'].with_context(active_test=False).search([('plan_id', '=', plan.id)])
def key(text):
    return re.sub(r'[^A-Z0-9]', '', (text or '').upper())
by_key = {}
clash = set()
for acc in accounts:
    for text in (acc.name, acc.code):
        k = key(text)
        if not k:
            continue
        if k in by_key and by_key[k] != acc.id:
            clash.add(k)
        by_key[k] = acc.id
print('Obras en el plan: %s (claves repetidas entre obras distintas: %s)' % (len(accounts), sorted(clash)))
SOURCES = [('hr_expense', 'x_studio_reference', 'Gastos'), ('purchase_requisition', 'reference', 'Contratos de compra'), ('approval_product_line', 'x_studio_reference', 'Líneas de Aprobaciones')]
total = 0
for table, column, label in SOURCES:
    cr.execute('SELECT id, "%s" FROM "%s" WHERE lotoi_obra_id IS NULL AND "%s" IS NOT NULL AND "%s" <> \'\'' % (column, table, column, column))
    rows = cr.fetchall()
    ids_by_account = {}
    unmatched = {}
    for rec_id, text in rows:
        k = key(text)
        if k in clash or k not in by_key:
            unmatched[text] = unmatched.get(text, 0) + 1
        else:
            ids_by_account.setdefault(by_key[k], []).append(rec_id)
    matched = sum(len(v) for v in ids_by_account.values())
    total += matched
    print('=== %s: %s con texto, %s se pueden asignar, %s sin coincidencia (%s valores distintos)' % (label, len(rows), matched, sum(unmatched.values()), len(unmatched)))
    for text, n in sorted(unmatched.items(), key=lambda x: -x[1])[:40]:
        print('   sin coincidencia: %r (%s)' % (text, n))
    if CLEAN:
        for acc_id, ids in ids_by_account.items():
            cr.execute('UPDATE "%s" SET lotoi_obra_id = %%s WHERE id IN %%s' % table, (acc_id, tuple(ids)))
if CLEAN:
    cr.execute('UPDATE purchase_order po SET lotoi_obra_id = pr.lotoi_obra_id FROM purchase_requisition pr WHERE pr.id = po.requisition_id AND pr.lotoi_obra_id IS NOT NULL AND po.lotoi_obra_id IS NULL')
    print('Órdenes de compra que toman la obra de su contrato: %s' % cr.rowcount)
    env.invalidate_all()
    cr.commit()
    print('Listo: %s registros asignados.' % total)
else:
    print('Solo informe: no se escribió nada. Para escribir, correr con CLEAN=1.')
