{
    'name': 'CRM Rental',
    'version': '1',
    'summary': 'Cotação	 de servicos e alugueres no CRM com precos em USD e conversao para KZ',
    'category': 'Sales/CRM',
    'author': 'Pedro Henrique',
    'depends': ['crm', 'product'],
    'data': [
        'security/crm_rental_security.xml',
        'security/ir.model.access.csv',
        'data/crm_rental_data.xml',
        'wizard/crm_rental_line_wizard_views.xml',
        'views/crm_rental_exchange_rate_views.xml',
        'views/crm_rental_line_views.xml',
        'views/product_views.xml',
        'views/crm_lead_views.xml',
    ],
    'demo': [
        'demo/crm_rental_demo.xml',
    ],
    'installable': True,
    'application': False,
}
