from odoo import _, api, fields, models


class CrmLead(models.Model):
    _inherit = 'crm.lead'

    operation_type = fields.Selection([
        ('sale', 'Venda'),
        ('rental', 'Aluguer'),
    ], string='Tipo de Operacão', default='sale')
    pricelist_id = fields.Many2one('product.pricelist', string='Lista de Precos')
    rental_line_ids = fields.One2many('crm.rental.line', 'lead_id', string='Linhas da Cotação')

    currency_usd_id = fields.Many2one('res.currency', string='USD', default=lambda self: self.env.ref('base.USD'))
    currency_kz_id = fields.Many2one('res.currency', string='KZ',default=lambda self: self.env.ref('base.AOA'))
    exchange_rate = fields.Float(string='Cambio do dia', digits=(16, 4), compute='_compute_exchange_rate')

    amount_total_usd = fields.Monetary(string='Total USD', currency_field='currency_usd_id',compute='_compute_amounts', store=True)
    amount_total_kz = fields.Monetary(string='Total KZ', currency_field='currency_kz_id',compute='_compute_amounts', store=True)
    forecast_usd = fields.Monetary(string='Forecast USD', currency_field='currency_usd_id',compute='_compute_amounts', store=True)
    forecast_kz = fields.Monetary(string='Forecast KZ', currency_field='currency_kz_id',compute='_compute_amounts', store=True)

    def _compute_exchange_rate(self):
        rate = self.env['crm.rental.exchange.rate'].search([
            ('date', '<=', fields.Date.context_today(self)),
        ], limit=1)
        for lead in self:
            lead.exchange_rate = rate.rate

    @api.depends('probability', 'rental_line_ids.price_subtotal_usd', 'rental_line_ids.price_subtotal_kz')
    def _compute_amounts(self):
        for lead in self:
            total_usd = sum(lead.rental_line_ids.mapped('price_subtotal_usd'))
            total_kz = sum(lead.rental_line_ids.mapped('price_subtotal_kz'))
            lead.amount_total_usd = total_usd
            lead.amount_total_kz = total_kz
            lead.forecast_usd = total_usd * lead.probability / 100.0
            lead.forecast_kz = total_kz * lead.probability / 100.0
            if lead.rental_line_ids:
                if lead.company_currency == lead.currency_usd_id:
                    lead.expected_revenue = total_usd
                else:
                    lead.expected_revenue = total_kz

    @api.onchange('partner_id')
    def _onchange_partner_id_pricelist(self):
        if self.partner_id and self.partner_id.property_product_pricelist:
            self.pricelist_id = self.partner_id.property_product_pricelist

    def action_add_rental_line(self):
        self.ensure_one()
        return {
            'name': _('Periodo de Aluguer'),
            'type': 'ir.actions.act_window',
            'res_model': 'crm.rental.line.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_lead_id': self.id},
        }

    @api.model
    def _cron_notify_overdue_opportunities(self):
        today = fields.Date.context_today(self)
        leads = self.search([
            ('type', '=', 'opportunity'),
            ('date_deadline', '!=', False),
            ('date_deadline', '<', today),
            ('stage_id.is_won', '=', False),
            ('probability', '<', 100),
        ])
        activity_type = self.env.ref('mail.mail_activity_data_todo')
        for lead in leads:
            if not lead.user_id:
                continue
            pending = self.env['mail.activity'].search_count([
                ('res_model', '=', 'crm.lead'),
                ('res_id', '=', lead.id),
                ('activity_type_id', '=', activity_type.id),
                ('user_id', '=', lead.user_id.id),
            ])
            if pending:
                continue
            lead.activity_schedule(
                'mail.mail_activity_data_todo',
                user_id=lead.user_id.id,
                summary=_('Oportunidade em atraso'),
                note=_('A data prevista de fecho (%s) esta vencida. Actualize a oportunidade.') % lead.date_deadline,
            )
            
            lead.message_post(
                body=_('Oportunidade em atraso: data prevista de fecho %s.') % lead.date_deadline,
                subtype_xmlid='mail.mt_note',
            )
        return True
