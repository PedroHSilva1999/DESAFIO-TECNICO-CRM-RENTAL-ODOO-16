# Desafio Técnico – CRM Rental (Odoo)

Odoo 16 + PostgreSQL + Nginx via Docker. Módulos em `addons/` (`crm_rental`, `account_balancete_filter`).

## Clonar o projeto

Crie uma pasta na sua máquina local e entre nela:

```bash
mkdir odoo-crm-rental
cd odoo-crm-rental
```

Depois clone o repositório na pasta criada:

```bash
git clone https://github.com/PedroHSilva1999/DESAFIO-TECNICO-CRM-RENTAL-ODOO-16.git
cd DESAFIO-TECNICO-CRM-RENTAL-ODOO-16
```

## Docker (OPCIONAL)

Se ainda não tiver Docker instalado, baixe (descarregue) o [Docker Desktop](https://www.docker.com/products/docker-desktop/) (Windows/macOS) ou no Linux:

```bash
sudo apt update && sudo apt install -y docker.io docker-compose-plugin
```

## Subir o projeto

```bash
docker compose up -d
```

Aceder em http://localhost:8069 (ou http://localhost via Nginx).

### Entrar

- Master Password: `odoo`
- Database Name: `odoo`
- Email: `admin`
- Password: `admin`

Na primeira vez, se a base ainda não existir, crie com esses dados no formulário (Email `admin`, Password `admin`)  
ou rode o script de inicialização:

```bash
# Linux / macOS
bash scripts/init_db.sh

# Windows (PowerShell)
.\scripts\init_db.ps1
```

Depois faça login em http://localhost:8069 com **admin** / **admin**.

### Instalar módulos pela tela

1. Abra http://localhost:8069/web?debug=1
2. Vá a **Definições** (ou **Apps**) → **Atualizar lista de Apps**
3. Remova o filtro "Apps" se necessário e procure `crm_rental` / `account_balancete_filter`
4. Instale os módulos

### Instalar pela linha de comando

```bash
docker compose stop odoo
docker compose run --rm odoo odoo -c /etc/odoo/odoo.conf -d odoo -i crm_rental,account_balancete_filter --stop-after-init
docker compose start odoo
```

## Comandos úteis

```bash
docker compose logs -f odoo
docker compose stop
docker compose start
```

Detalhes: `addons/crm_rental/README.md` e `addons/account_balancete_filter/README.md`.
