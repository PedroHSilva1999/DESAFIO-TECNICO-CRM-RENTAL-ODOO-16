from odoo import _, api, fields, models


class CrmRentalLine(models.Model):
    _name = 'crm.rental.line'
    _description = 'Linha de Cotação do CRM'
    _order = 'lead_id, sequence, id'

    sequence = fields.Integer(default=10)
    lead_id = fields.Many2one('crm.lead', string='Oportunidade', required=True, ondelete='cascade', index=True)
    partner_id = fields.Many2one(related='lead_id.partner_id', store=True)
    company_id = fields.Many2one(related='lead_id.company_id', store=True)
    pricelist_id = fields.Many2one(related='lead_id.pricelist_id', string='Lista de Precos')

    product_id = fields.Many2one('product.product', string='Produto', required=True)
    name = fields.Char(string='Descricao')
    operation_type = fields.Selection([
        ('sale', 'Venda'),
        ('rental', 'Aluguer'),
    ], string='Tipo', default='sale', required=True)

    quantity = fields.Float(string='Quantidade', digits='Product Unit of Measure', default=1.0)

    date_start = fields.Date(string='Data Inicio')
    date_end = fields.Date(string='Data Fim')
    rental_days = fields.Integer(string='Dias')

    currency_usd_id = fields.Many2one('res.currency', string='USD',default=lambda self: self.env.ref('base.USD'))
    currency_kz_id = fields.Many2one('res.currency', string='KZ',default=lambda self: self.env.ref('base.AOA'))
    exchange_rate = fields.Float(string='Câmbio', digits=(16, 4))

    price_unit_usd = fields.Monetary(string='Preco Unit. USD', currency_field='currency_usd_id')
    price_unit_kz = fields.Monetary(string='Preco Unit. KZ', currency_field='currency_kz_id')
    price_subtotal_usd = fields.Monetary(string='Subtotal USD', currency_field='currency_usd_id',compute='_compute_price_subtotal', store=True)
    price_subtotal_kz = fields.Monetary(string='Subtotal KZ', currency_field='currency_kz_id',compute='_compute_price_subtotal', store=True)

    @api.depends('quantity', 'price_unit_usd', 'price_unit_kz')
    def _compute_price_subtotal(self):
        for line in self:
            line.price_subtotal_usd = line.quantity * line.price_unit_usd
            line.price_subtotal_kz = line.quantity * line.price_unit_kz

    @api.onchange('product_id')
    def _onchange_product_id(self):
        if not self.product_id:
            return
        self.name = self.product_id.display_name
        if self.product_id.rental_ok:
            self.operation_type = 'rental'
            self.price_unit_usd = 0.0
            self.price_unit_kz = 0.0
            return {'warning': {
                'title': _('Produto de aluguer'),
                'message': _('Utilize o botao "Periodo" da linha (ou "Adicionar Aluguer") para definir as datas e calcular o valor do aluguer.'),
            }}
        self.operation_type = 'sale'
        self._apply_prices()

    @api.onchange('quantity')
    def _onchange_quantity(self):
        if self.product_id and self.operation_type == 'sale':
            self._apply_prices()

    def _apply_prices(self):
        price = self.product_id.lst_price
        if self.pricelist_id:
            price = self.product_id.with_context(
                pricelist=self.pricelist_id.id,
                quantity=self.quantity or 1.0,
                partner=self.partner_id.id,
                uom=self.product_id.uom_id.id,
            ).price

        rate = self.env['crm.rental.exchange.rate'].get_rate()
        self.exchange_rate = rate
        self.price_unit_usd = price
        self.price_unit_kz = price * rate

    def action_open_rental_wizard(self):
        self.ensure_one()
        return {
            'name': _('Periodo de Aluguer'),
            'type': 'ir.actions.act_window',
            'res_model': 'crm.rental.line.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_lead_id': self.lead_id.id,
                'default_line_id': self.id,
                'default_product_id': self.product_id.id,
                'default_quantity': self.quantity,
                'default_date_start': self.date_start,
                'default_date_end': self.date_end,
            },
        }
