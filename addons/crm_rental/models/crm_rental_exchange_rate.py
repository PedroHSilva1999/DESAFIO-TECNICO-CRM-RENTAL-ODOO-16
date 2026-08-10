from odoo import _, api, fields, models
from odoo.exceptions import UserError


class CrmRentalExchangeRate(models.Model):
    _name = 'crm.rental.exchange.rate'
    _description = 'Taxa de Câmbio USD / KZ'
    _order = 'date desc'
    _rec_name = 'date'

    date = fields.Date(string='Data', required=True, default=fields.Date.context_today, index=True)
    rate = fields.Float(string='1 USD em KZ', digits=(16, 4), required=True, default=990.0)
    company_id = fields.Many2one('res.company', string='Empresa', default=lambda self: self.env.company)

    _sql_constraints = [
        ('date_company_uniq', 'unique(date, company_id)', 'Ja existe uma taxa de cambio registada para esta data.'),
    ]

    @api.model
    def get_rate(self, date=None):
        rate = self.search([('date', '<=', date or fields.Date.context_today(self))], limit=1)
        if not rate:
            raise UserError(_('Nao existe nenhuma taxa de cambio USD/KZ configurada.'))
        return rate.rate
