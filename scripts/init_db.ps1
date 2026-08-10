docker compose up -d db
Write-Host "A aguardar o PostgreSQL..."
Start-Sleep -Seconds 8
docker compose run --rm odoo odoo -c /etc/odoo/odoo.conf -d odoo -i base --stop-after-init
Get-Content .\scripts\set_admin_password.py | docker compose run --rm -T odoo odoo shell -c /etc/odoo/odoo.conf -d odoo --no-http
docker compose up -d
Write-Host "Pronto. Login: admin / admin em http://localhost:8069"
