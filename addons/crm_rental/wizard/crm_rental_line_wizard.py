from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class CrmRentalLineWizard(models.TransientModel):
    _name = 'crm.rental.line.wizard'
    _description = 'Wizard de Periodo de Aluguer'

    lead_id = fields.Many2one('crm.lead', string='Oportunidade', required=True)
    line_id = fields.Many2one('crm.rental.line', string='Linha')
    partner_id = fields.Many2one(related='lead_id.partner_id')
    pricelist_id = fields.Many2one(related='lead_id.pricelist_id', string='Lista de Precos')

    product_id = fields.Many2one('product.product', string='Produto', required=True,domain=[('rental_ok', '=', True)])
    quantity = fields.Float(string='Quantidade', digits='Product Unit of Measure', default=1.0)
    date_start = fields.Date(string='Data de Inicio', required=True, default=fields.Date.context_today)
    date_end = fields.Date(string='Data de Fim', required=True)
    days = fields.Integer(string='Total de Dias', compute='_compute_days')

    currency_usd_id = fields.Many2one('res.currency', default=lambda self: self.env.ref('base.USD'))
    currency_kz_id = fields.Many2one('res.currency', default=lambda self: self.env.ref('base.AOA'))
    exchange_rate = fields.Float(string='Cambio (1 USD em KZ)', digits=(16, 4), compute='_compute_amounts')

    price_unit_usd = fields.Monetary(string='Preco/Dia USD', currency_field='currency_usd_id',compute='_compute_amounts')
    total_usd = fields.Monetary(string='Total USD', currency_field='currency_usd_id', compute='_compute_amounts')
    total_kz = fields.Monetary(string='Total KZ', currency_field='currency_kz_id', compute='_compute_amounts')

    @api.depends('date_start', 'date_end')
    def _compute_days(self):
        for wizard in self:
            if wizard.date_start and wizard.date_end and wizard.date_end >= wizard.date_start:
                wizard.days = (wizard.date_end - wizard.date_start).days + 1
            else:
                wizard.days = 0

    @api.depends('product_id', 'days', 'pricelist_id')
    def _compute_amounts(self):
        rate = self.env['crm.rental.exchange.rate'].get_rate()
        for wizard in self:
            price = 0.0
            if wizard.product_id:
                price = wizard.product_id.lst_price
                if wizard.pricelist_id:
                    price = wizard.product_id.with_context(
                        pricelist=wizard.pricelist_id.id,
                        quantity=1.0,
                        partner=wizard.partner_id.id,
                        uom=wizard.product_id.uom_id.id,
                    ).price
            wizard.exchange_rate = rate
            wizard.price_unit_usd = price
            wizard.total_usd = price * wizard.days
            wizard.total_kz = wizard.total_usd * rate

    @api.constrains('date_start', 'date_end')
    def _check_dates(self):
        for wizard in self:
            if wizard.date_start and wizard.date_end and wizard.date_end < wizard.date_start:
                raise ValidationError(_('A data de fim nao pode ser anterior a data de inicio.'))

    def action_confirm(self):
        self.ensure_one()
        vals = {
            'lead_id': self.lead_id.id,
            'product_id': self.product_id.id,
            'name': self.product_id.display_name,
            'operation_type': 'rental',
            'quantity': self.quantity,
            'date_start': self.date_start,
            'date_end': self.date_end,
            'rental_days': self.days,
            'exchange_rate': self.exchange_rate,
            'price_unit_usd': self.total_usd,
            'price_unit_kz': self.total_kz,
        }
        if self.line_id:
            self.line_id.write(vals)
        else:
            self.env['crm.rental.line'].create(vals)
        return {'type': 'ir.actions.act_window_close'}
