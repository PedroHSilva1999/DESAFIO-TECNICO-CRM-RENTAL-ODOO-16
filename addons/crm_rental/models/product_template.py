from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    rental_ok = fields.Boolean(string='Pode ser Alugado',help='Produtos marcados como aluguer sao cotados por periodo (dias) atraves do wizard.')
