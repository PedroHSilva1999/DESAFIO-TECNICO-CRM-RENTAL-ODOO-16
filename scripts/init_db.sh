#!/bin/bash
set -e
docker compose up -d db
echo "A aguardar o PostgreSQL..."
sleep 8
docker compose run --rm odoo odoo -c /etc/odoo/odoo.conf -d odoo -i base --stop-after-init
docker compose run --rm -T odoo odoo shell -c /etc/odoo/odoo.conf -d odoo --no-http < scripts/set_admin_password.py
docker compose up -d
echo "Pronto. Login: admin / admin em http://localhost:8069"
