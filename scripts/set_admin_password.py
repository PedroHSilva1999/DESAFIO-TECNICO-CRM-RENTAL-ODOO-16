admin = env['res.users'].search([('login', '=', 'admin')], limit=1)
if admin:
    admin.write({'password': 'admin'})
    env.cr.commit()
    print('admin / admin ok')
else:
    print('utilizador admin nao encontrado')
