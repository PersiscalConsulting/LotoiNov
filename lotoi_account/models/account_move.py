from datetime import date, timedelta

from odoo import api, fields, models

SATURDAY = 5


def _week_start(day):
    """Saturday on or before ``day``."""
    return day - timedelta(days=(day.weekday() - SATURDAY) % 7)


def lotoi_week(day):
    """Return (year, number) of the Saturday to Friday week of ``day``.

    Week 1 is the week that contains January 1st, so a week that crosses the
    new year belongs to the new year.
    """
    start = _week_start(day)
    year = (start + timedelta(days=6)).year
    first_week_start = _week_start(date(year, 1, 1))
    return year, (start - first_week_start).days // 7 + 1


class AccountMove(models.Model):
    _inherit = 'account.move'

    lotoi_week_number = fields.Integer(
        string='Week number',
        compute='_compute_lotoi_week',
        store=True,
        help='Saturday to Friday weeks, week 1 contains January 1st. Based on the invoice date.',
    )
    lotoi_week = fields.Char(
        string='Week',
        compute='_compute_lotoi_week',
        store=True,
        help='Year and week number, e.g. 2026-S42.',
    )

    @api.depends('invoice_date')
    def _compute_lotoi_week(self):
        for move in self:
            if move.invoice_date:
                year, number = lotoi_week(move.invoice_date)
                move.lotoi_week_number = number
                move.lotoi_week = f'{year}-S{number:02d}'
            else:
                move.lotoi_week_number = 0
                move.lotoi_week = False
