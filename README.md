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

## IMPORTANTE: O projeto pode levar alguns minutos para iniciar. Aguarde de 5 a 10 minutos, mesmo que todas as dependências já estejam instaladas no Docker.

Aceder em http://localhost:8069 (ou http://localhost via Nginx).

### Entrar

- Master Password: `odoo`
- Database Name: `odoo`
- Email: `admin`
- Password: `admin`

Na primeira vez, se a base ainda não existir, crie com esses dados no formulário (Email `admin`, Password `admin`)  
ou rode o script de inicialização (opcional) já vem com "admin" por padrão no Email e Password:

```bash
# Linux / macOS
bash scripts/init_db.sh

# Windows (PowerShell)
.\scripts\init_db.ps1
```

Depois faça login em http://localhost:8069 com **admin** / **admin**.

### Instalar módulos pela tela

1. Abra http://localhost:8069/web?debug=1
2. Vá a **Apps** → **Atualizar lista de Apps (Update App List)**
3. Remova o filtro "Apps" e procure `crm_rental` / `account_balancete_filter`
4. Instale os módulos

### Instalar pela linha de comando (OPCIONAL)

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

---

## Como Usar

### CRM Rental (`crm_rental`)

#### Câmbio, dashboard e cron

- **Câmbio:** CRM > Configuração > Taxas de Câmbio (USD/KZ). Taxa inicial `1 USD = 990 KZ`. Usa-se a última taxa com data ≤ à data da cotação.
- **Dashboard:** CRM > Relatórios > Forecast Aluguer / Venda (pivot, gráfico e lista) — totais USD/KZ, forecast por probabilidade, clientes com mais oportunidades.
- **Cron:** semanalmente notifica oportunidades em atraso (actividade "A Fazer" + nota no chatter), sem duplicados.

#### Cotar uma venda (serviço)

1. Crie uma nova **oportunidade** no CRM e escolha o cliente — a **lista de preços** é preenchida automaticamente.
2. No separador **Cotação**, escolha o tipo de operação **Venda**.
3. Adicione linhas na grelha e seleccione o produto de serviço.
4. O sistema preenche:
   - preço unitário em **USD** (da lista de preços);
   - preço unitário em **KZ** (USD × câmbio do dia);
   - subtotais em USD e KZ com base na quantidade.
5. Confirme os totais da oportunidade (`amount_total_usd` / `amount_total_kz`) e o forecast ponderado pela probabilidade.

#### Cotar um aluguer (rental)

1. Na oportunidade, use um destes atalhos para abrir o wizard:
   - **Ícone de calendário / Período** — na própria linha da cotação: ícone de calendário na linha(grelha) , ou o botão **Definir Periodo** se abrir o formulário da linha. Serve para (re)definir as datas e recalcular o valor.
   - **Adicionar Aluguer** — no separador **Cotação** da oportunidade (botão com ícone de calendário no topo).
2. No wizard, escolha produto (com **Pode ser Alugado**), quantidade e datas de início/fim.
3. O sistema calcula o nº de dias de forma inclusiva (`fim - início + 1`), `Total USD = dias × preço da lista`, e converte para KZ.
4. Após confirmar, esses valores passam a ser o preço unitário da linha; subtotais = `Qty × preço unitário` em USD e KZ.
5. Se escolher um produto de aluguer directamente na grelha (sem wizard), o sistema avisa para usar o ícone de calendário / botão **Periodo** da linha (ou **Adicionar Aluguer**).

#### Preparar produtos e lista de preços (Opcional)

Só é necessário se não estiver a usar os **dados de demonstração** do módulo:

1. Crie/abra um produto de **serviço** (venda) e outro com a opção **Pode ser Alugado** activa (aluguer).
2. Crie uma **lista de preços em USD** com preços fixos para esses produtos.
3. Associe essa lista de preços ao **cliente**.

Para carregar a demo ao criar a base, use `without_demo = False` no `config/odoo/odoo.conf` (Opcional).


#### Instruções para testes

1. **Câmbio** – CRM > Configuração > Taxas de Câmbio (USD/KZ), criar uma taxa com a data de hoje (ex.: 990). Criar outra com data anterior e confirmar que continua a ser usada a mais recente.
2. **Produtos** (Opcional) – se não usar demo: criar/abrir um produto e marcar **Pode ser Alugado**. Criar uma lista de preços em USD e associá-la ao cliente.
3. **Venda** – nova oportunidade, escolher o cliente (a lista de preços é preenchida), separador Cotação, tipo Venda, adicionar uma linha com um produto de serviço. Verificar preço USD, preço KZ (USD × câmbio) e os subtotais ao alterar a quantidade.
4. **Aluguer** – ícone de calendário / **Definir Periodo** na linha (ou **Adicionar Aluguer**), escolher o produto de aluguer e as datas. Confirmar o nº de dias, o total USD e o total KZ. Validar subtotais da linha e totais da oportunidade.
5. **Dashboard** – CRM > Relatórios > Forecast Aluguer / Venda; agrupar por cliente e comparar as medidas com os valores das oportunidades.
6. **Cron** – colocar a data prevista de fecho no passado e executar a acção planeada em Definições > Técnico > Acções Automatizadas > Acções Planeadas. Deve criar actividade e nota no chatter.

---

### Balancete – Filtro por Débito/Crédito (`account_balancete_filter`)

Adiciona ao módulo de contabilidade um **Balancete** (Contabilidade > Relatórios > Balancete) com os movimentos agrupados por conta e totais de débito, crédito e saldo, e um filtro personalizado que permite pesquisar lançamentos pelo valor de Débito ou de Crédito.

#### Utilização

Na barra de pesquisa do balancete (ou dos Itens de Diário), escreva o valor pretendido e escolha o método de pesquisa proposto — **Pesquisar Débito por: ...** ou **Pesquisar Crédito por: ...**. O relatório é filtrado no ecrã, mantendo os totais por conta.

O mesmo filtro é acrescentado à vista de pesquisa padrão dos itens de diário (`account.view_account_move_line_filter`).

#### Instalação

**Pela tela**

1. Abra http://localhost:8069/web?debug=1
2. Definições / Apps → Atualizar lista de Apps
3. Instale Contabilidade (`account`) se ainda não estiver instalado
4. Procure `account_balancete_filter` (ou "Balancete") e instale

**Pela linha de comando**

```bash
docker compose stop odoo
docker compose run --rm odoo odoo -c /etc/odoo/odoo.conf -d odoo -i account_balancete_filter --stop-after-init
docker compose start odoo
```

#### Testes

1. Instalar o módulo `account` e lançar alguns movimentos (ou usar os dados de demonstração).
2. Abrir Contabilidade > Relatórios > Balancete e confirmar o agrupamento por conta com os somatórios de débito, crédito e saldo.
3. Escrever um valor na barra de pesquisa (ex.: 1500) e escolher Débito; apenas os lançamentos com esse valor a débito devem ficar visíveis.
4. Repetir com Crédito e combinar com o filtro de conta ou de datas.

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
| Cron não cria actividade | A oportunidade precisa de responsável (`user_id`), data prevista de fecho no passado, não estar ganha e probabilidade &lt; 100. Execute a acção planeada manualmente em Definições > Técnico > Acções Planeadas. Se já existir actividade "A Fazer" pendente, não cria outra. |
| Menu Balancete não aparece | Instale primeiro Contabilidade (`account`) e depois `account_balancete_filter`. Actualize a lista de Apps se necessário. |
| Filtro Débito/Crédito não encontra valor | A pesquisa é por igualdade exacta. Use o mesmo número do lançamento (ex.: `1500.0` vs `1500`) e escolha *Pesquisar Débito* ou *Pesquisar Crédito*. |
| Alterações no código não reflectem | `docker compose restart odoo` ou actualize o módulo em Apps. Em erro de XML/Python, veja `docker compose logs -f odoo`. |

---

Detalhes adicionais: `addons/crm_rental/README.md` e `addons/account_balancete_filter/README.md`.
