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

## Docker (Caso não tenha na máquina)

Se ainda não tiver Docker instalado, baixe (descarregue) o [Docker Desktop](https://www.docker.com/products/docker-desktop/) (Windows/macOS) ou no Linux:

```bash
sudo apt update && sudo apt install -y docker.io docker-compose-plugin
```

## Subir o projeto (Aviso: O projeto pode levar alguns minutos para iniciar. Aguarde de 5 a 10 minutos, mesmo que todas as dependências já estejam instaladas no Docker.)

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
2. Vá a **Apps** → **Atualizar lista de Apps (Update Apps List)**
3. Remova o filtro "Apps" e procure `crm_rental` / `account_balancete_filter`
4. Instale os módulos

### Instalar pela linha de comando

```bash
docker compose stop odoo
docker compose run --rm odoo odoo -c /etc/odoo/odoo.conf -d odoo -i crm_rental,account_balancete_filter --stop-after-init
docker compose start odoo
```

Para dados de demonstração do `crm_rental` (Opcional), use `without_demo = False` no `config/odoo/odoo.conf` ao criar a base.

## Comandos úteis

```bash
docker compose logs -f odoo
docker compose stop
docker compose start
```

---

## Como Usar — CRM Rental (`crm_rental`)

Estende o CRM para cotação de **serviços** e **alugueres**, com lista de preços em USD e conversão automática para Kwanza (KZ / AOA).

### Preparar produtos e lista de preços (Opcional)

Só é necessário se não estiver a usar os **dados de demonstração** do módulo:

1. Crie/abra um produto de **serviço** (venda) e outro com a opção **Pode ser Alugado** activa (aluguer).
2. Crie uma **lista de preços em USD** com preços fixos para esses produtos.
3. Associe essa lista de preços ao **cliente**.

### Configurar o câmbio (USD → KZ)

1. Vá a **CRM > Configuração > Taxas de Câmbio (USD/KZ)**.
2. Crie ou edite uma taxa (ex.: `1 USD = 990 KZ`). Taxa inicial do módulo: `990`.
3. Usa-se sempre a **última taxa com data igual ou anterior** à data da cotação (por omissão, hoje).

### Cotar uma venda (serviço)

1. Crie uma nova **oportunidade** no CRM e escolha o cliente — a **lista de preços** é preenchida automaticamente.
2. No separador **Cotação**, escolha o tipo de operação **Venda**.
3. Adicione linhas na grelha e seleccione o produto de serviço.
4. O sistema preenche:
   - preço unitário em **USD** (da lista de preços);
   - preço unitário em **KZ** (USD × câmbio do dia);
   - subtotais em USD e KZ com base na quantidade.
5. Confirme os totais da oportunidade (`amount_total_usd` / `amount_total_kz`) e o forecast ponderado pela probabilidade.

### Cotar um aluguer (rental)

1. Na oportunidade, use um destes atalhos para abrir o wizard:
   - **Ícone de calendário / Período** — na própria linha da cotação: ícone de calendário na linha (grelha), ou o botão **Definir Periodo** se abrir o formulário da linha. Serve para (re)definir as datas e recalcular o valor.
   - <img width="1531" height="674" alt="image" src="https://github.com/user-attachments/assets/02fd3af1-5838-4fc1-bd80-d9d2c7b4fe9c" />
   - **Adicionar Aluguer** — no separador **Cotação** da oportunidade (botão com ícone de calendário no topo). Cria uma linha nova com datas e valor.
2. No wizard, escolha produto (com **Pode ser Alugado**), quantidade e datas de início/fim.
3. O sistema calcula o nº de dias de forma inclusiva (`fim - início + 1`), `Total USD = dias × preço da lista`, e converte para KZ.
4. Após confirmar, esses valores passam a ser o preço unitário da linha; subtotais = `Qty × preço unitário` em USD e KZ.
5. Se escolher um produto de aluguer directamente na linha( grelha) (sem wizard), o sistema avisa para usar o ícone de calendário / botão **Periodo** da linha (ou **Adicionar Aluguer**).

### Dashboard e forecast

1. Vá a **CRM > Relatórios > Forecast Aluguer / Venda**.
2. Use as vistas **pivot**, **gráfico** e **lista** para analisar:
   - total de oportunidades;
   - receita total em USD e em KZ;
   - forecast ponderado pela probabilidade (USD e KZ);
   - clientes com maior número de oportunidades (agrupar por cliente no pivot).
3. Na lista do pipeline, confira também as colunas de total em USD e KZ.

### Cron — oportunidades em atraso

O job **CRM Rental: notificar oportunidades em atraso** corre **semanalmente** e:

- identifica oportunidades abertas (não ganhas, probabilidade &lt; 100) com data prevista de fecho vencida;
- cria uma actividade **"A Fazer"** para o responsável;
- regista uma nota no chatter;
- **não** cria actividades duplicadas enquanto a anterior não for concluída.

### Testes CRM Rental

| # | Cenário | Passos | Resultado esperado |
|---|---|---|---|
| 1 | **Câmbio** | CRM > Configuração > Taxas de Câmbio (USD/KZ). Criar taxa com data de hoje (ex.: 990) e outra com data anterior. | Continua a ser usada a taxa mais recente com data ≤ hoje. |
| 2 | **Produtos e pricelist** (Opcional) | Se não usar demo: marcar produto com *Pode ser Alugado*. Criar lista de preços em USD e associá-la ao cliente. | Cliente fica com lista USD; produto de aluguer identificado. |
| 3 | **Venda / serviço** | Nova oportunidade → cliente → Cotação → tipo Venda → linha com produto de serviço. Alterar quantidade. | Lista de preços preenchida; preço USD da lista; KZ = USD × câmbio; subtotais recalculados. |
| 4 | **Aluguer / wizard** | Ícone de calendário / *Definir Periodo* na linha (ou *Adicionar Aluguer*) → produto, datas início/fim → confirmar. | Dias inclusivos; Total USD = dias × preço da lista; conversão KZ; subtotais e totais correctos. |
| 5 | **Aviso na grelha** | Escolher produto de aluguer directamente na grelha (sem wizard). | Sistema avisa que o valor deve ser calculado no wizard. |
| 6 | **Dashboard / forecast** | CRM > Relatórios > Forecast Aluguer / Venda; agrupar por cliente. | Contagem, receita USD/KZ e forecast ponderado batem certo com as oportunidades. |
| 7 | **Cron em atraso** | Colocar `date_deadline` no passado. Executar a acção planeada em *Definições (Settings) > Técnico (Technical) > Acções Planejadas (Schedules Actions) *. | Actividade "A Fazer" + nota no chatter; sem duplicados se voltar a correr. |

### Modelos (referência técnica)

**`crm.rental.exchange.rate`** — taxa por data; `get_rate(date)` devolve a última taxa com data ≤ à indicada.

**`crm.lead` (extensão)**

| Campo | Descrição |
|---|---|
| `operation_type` | Venda / Aluguer |
| `pricelist_id` | Lista de preços (do cliente) |
| `rental_line_ids` | Linhas da cotação |
| `amount_total_usd` / `amount_total_kz` | Totais das linhas |
| `forecast_usd` / `forecast_kz` | Totais × probabilidade |
| `exchange_rate` | Câmbio do dia (informativo) |

O `expected_revenue` é actualizado com o total na moeda da empresa (forecast padrão do CRM).

**`crm.rental.line`** — produto, quantidade, preços unitários e subtotais em USD/KZ, datas e nº de dias (aluguer).

### Segurança

- ACL: vendedores (leitura/escrita) e gestores nas linhas/wizard; câmbio — leitura para internos, escrita só gestores.
- Record rules: multi-empresa; vendedores só vêem linhas das suas oportunidades/equipa; gestores vêem todas.

### Estrutura do módulo

```
addons/crm_rental/
├── data/               taxa de câmbio inicial + cron semanal
├── demo/               produtos, lista de preços, clientes e oportunidades
├── models/
│   ├── crm_lead.py
│   ├── crm_rental_line.py
│   ├── crm_rental_exchange_rate.py
│   └── product_template.py
├── security/
├── views/
└── wizard/
```

---

## Como Usar — Balancete (`account_balancete_filter`)

Adiciona ao módulo de contabilidade um **Balancete** (Contabilidade > Relatórios > Balancete) com movimentos agrupados por conta e totais de débito, crédito e saldo, e um filtro para pesquisar lançamentos pelo valor de **Débito** ou **Crédito**.

Dependência: Contabilidade (`account`).

### Abrir o balancete

1. Vá a **Contabilidade > Relatórios > Balancete**.
2. O ecrã mostra os movimentos (`account.move.line`) agrupados por conta, com totais de Débito, Crédito e Saldo.
3. Por omissão, vem agrupado por conta e filtrado para lançamentos publicados.

### Filtrar por Débito ou Crédito

1. Na barra de pesquisa, escreva o valor (ex.: `1500`).
2. Escolha **Pesquisar Débito por: …** ou **Pesquisar Crédito por: …**.
3. O relatório filtra no ecrã e mantém os totais por conta sobre o resultado.

Pode combinar com filtros de conta, datas, Lançado/Rascunho e agrupamentos (Conta, Diário, Parceiro, Mês).

O mesmo filtro está nos **Itens de Diário** (herança de `account.view_account_move_line_filter`).

### Instalação (só este módulo)

**Pela tela:** Apps → actualizar lista → instalar `account` se necessário → instalar `account_balancete_filter`.

**Pela linha de comando:**

```bash
docker compose stop odoo
docker compose run --rm odoo odoo -c /etc/odoo/odoo.conf -d odoo -i account_balancete_filter --stop-after-init
docker compose start odoo
```

### Testes Balancete

| # | Cenário | Passos | Resultado esperado |
|---|---|---|---|
| 1 | **Pré-requisitos** | Instalar `account` e lançar movimentos (ou demo). | Existem linhas com débito/crédito conhecidos. |
| 2 | **Balancete base** | Abrir Contabilidade > Relatórios > Balancete. | Agrupamento por conta com somatórios de débito, crédito e saldo. |
| 3 | **Filtro Débito** | Escrever valor (ex.: `1500`) → *Pesquisar Débito por: …*. | Só lançamentos com esse valor a débito; totais recalculados. |
| 4 | **Filtro Crédito** | Idem com *Pesquisar Crédito por: …*. | Só lançamentos com esse valor a crédito. |
| 5 | **Combinação** | Débito/Crédito + conta e/ou datas. | Resultado reflecte a combinação. |
| 6 | **Itens de diário** | Repetir a pesquisa na lista de itens de diário. | Mesmo método de pesquisa funciona fora do balancete. |

### Estrutura do módulo

```
addons/account_balancete_filter/
├── __manifest__.py
├── __init__.py
└── views/
    └── account_move_line_views.xml   # tree, search, action, menu + herança da search
```

Não há modelos Python novos: reutiliza `account.move.line` e acrescenta views/menu + campos pesquisáveis `debit` / `credit`.

---

## Possíveis problemas e como resolver

| Problema | Como resolver |
|---|---|
| Containers não sobem / porta 8069 ocupada | Confirme que o Docker Desktop está a correr. Pare outros serviços na porta ou altere o mapeamento no `docker-compose.yml`. Depois: `docker compose up -d`. |
| Base de dados ainda não existe | Crie-a no formulário de setup (admin/admin) ou rode `.\scripts\init_db.ps1` (Windows) / `bash scripts/init_db.sh` (Linux/macOS). |
| Módulo não aparece em Apps | Abra com `?debug=1`, **Atualizar lista de Apps**, remova o filtro "Apps" e procure pelo nome técnico (`crm_rental` / `account_balancete_filter`). |
| Lista de preços vazia na oportunidade | Associe uma lista de preços em USD ao cliente, ou use os dados de demo. Guarde o cliente e volte a seleccioná-lo na oportunidade. |
| Preço USD/KZ a 0 na linha de venda | Confirme que o produto tem preço na lista USD da oportunidade e que existe taxa de câmbio com data ≤ hoje (CRM > Configuração > Taxas de Câmbio). |
| Aviso ao escolher produto de aluguer na grelha | Comportamento esperado. Use o ícone de calendário / **Definir Periodo** da linha (ou **Adicionar Aluguer**) para calcular pelo wizard. |
| Não encontro o botão Período | Na grelha da Cotação: ícone de calendário na linha; ou abra a linha → **Definir Periodo**; ou use **Adicionar Aluguer** no topo do separador. |
| Dias / total do aluguer incorrectos | Confirme datas início/fim no wizard (dias = `fim - início + 1`) e o preço unitário USD na lista de preços. |
| Cron não cria actividade | A oportunidade precisa de responsável (`user_id`), data prevista de fecho no passado, não estar ganha e probabilidade &lt; 100. Execute a acção planeada em Definições > Técnico > Acções Planeadas. Se já existir actividade "A Fazer" pendente, não cria outra. |
| Menu Balancete não aparece | Instale primeiro Contabilidade (`account`) e depois `account_balancete_filter`. Actualize a lista de Apps se necessário. |
| Filtro Débito/Crédito não encontra valor | A pesquisa é por igualdade exacta. Use o mesmo número do lançamento (ex.: `1500.0` vs `1500`) e escolha *Pesquisar Débito* ou *Pesquisar Crédito*. |
| Alterações no código não reflectem | `docker compose restart odoo` ou actualize o módulo em Apps. Em erro de XML/Python, veja `docker compose logs -f odoo`. |
