# CRM Rental

Módulo que estende o CRM padrão do Odoo 16 para cotação de **serviços** e **alugueres**, com lista de preços
em USD e conversão automática para Kwanza (KZ / AOA).

## Instalação

O ambiente está no `docker-compose.yml` da raiz (`./addons` → `/mnt/extra-addons`).

### Pela tela

1. Abra http://localhost:8069/web?debug=1
2. **Definições** / **Apps** → **Atualizar lista de Apps**
3. Procure `CRM Rental` e instale

### Pela linha de comando

```bash
docker compose stop odoo
docker compose run --rm odoo odoo -c /etc/odoo/odoo.conf -d odoo -i crm_rental --stop-after-init
docker compose start odoo
```

Para dados de demonstração, use `without_demo = False` no `config/odoo/odoo.conf` ao criar a base.

Módulo de contabilidade: `account_balancete_filter`.

## Estrutura

```
crm_rental/
├── data/               taxa de câmbio inicial + cron semanal
├── demo/               produtos, lista de preços, clientes e oportunidades de exemplo
├── models/
│   ├── crm_lead.py                 extensão da oportunidade + cron
│   ├── crm_rental_line.py          linhas da cotação
│   ├── crm_rental_exchange_rate.py taxa de câmbio USD/KZ
│   └── product_template.py         flag "Pode ser Alugado"
├── security/           ACL + record rules
├── views/
└── wizard/             wizard de período de aluguer
```

## Modelos

### `crm.rental.exchange.rate`
Taxa de câmbio configurável por data (`CRM > Configuração > Taxas de Câmbio (USD/KZ)`).
O método `get_rate(date)` devolve sempre a última taxa registada com data **igual ou anterior** à data
indicada (por omissão a data actual). O módulo instala uma taxa inicial de `1 USD = 990 KZ`.

### `crm.lead` (extensão)
| Campo | Descrição |
|---|---|
| `operation_type` | Venda / Aluguer |
| `pricelist_id` | Lista de preços (preenchida automaticamente a partir do cliente) |
| `rental_line_ids` | Linhas da cotação |
| `amount_total_usd` / `amount_total_kz` | Totais calculados a partir das linhas |
| `forecast_usd` / `forecast_kz` | Totais ponderados pela probabilidade |
| `exchange_rate` | Câmbio do dia (informativo) |

O `expected_revenue` da oportunidade é actualizado com o total na moeda da empresa, o que alimenta
o forecast padrão do CRM.

### `crm.rental.line`
Produto, quantidade, preço unitário em USD e KZ, subtotais em USD e KZ (calculados automaticamente),
datas e nº de dias no caso do aluguer.

## Regras de negócio

**Serviço / Venda**
1. Ao escolher o cliente, a lista de preços do cliente é copiada para a oportunidade.
2. O vendedor escolhe o tipo de operação e adiciona linhas directamente na grelha.
3. Ao seleccionar o produto, o preço é lido da lista de preços (USD), convertido para KZ pela taxa do dia
   e os subtotais são calculados com base na quantidade.

**Aluguer**
1. Produtos com a opção *Pode ser Alugado* activa são cotados pelo wizard
   (botão **Adicionar Aluguer** na oportunidade ou o botão de calendário da linha).
2. No wizard escolhem-se produto, quantidade e datas de início/fim; o total de dias é calculado
   de forma inclusiva (`fim - início + 1`).
3. `Total USD = nº de dias × preço unitário USD da lista`, convertido para KZ pela taxa do dia.
4. Esse valor passa a ser o preço unitário da linha, pelo que
   `Subtotal KZ = Quantidade × Preço unitário KZ` (idem para USD).

Se um produto de aluguer for escolhido directamente na grelha, o sistema avisa o utilizador de que o
valor tem de ser calculado no wizard.

## Dashboard e forecast

`CRM > Relatórios > Forecast Aluguer / Venda` (pivot, gráfico e lista) sobre as próprias oportunidades,
sem views SQL — os valores vêm dos campos calculados do `crm.lead`:

- total de oportunidades (medida `Contagem` do pivot);
- receita total em USD e em KZ;
- forecast ponderado pela probabilidade em ambas as moedas;
- clientes com maior número de oportunidades (o pivot já agrupa por cliente nas linhas).

A lista de oportunidades do pipeline mostra também colunas com o total em USD e KZ.

## Cron

`CRM Rental: notificar oportunidades em atraso` corre **semanalmente**, procura oportunidades abertas
(não ganhas, probabilidade < 100) com data prevista de fecho vencida e, para cada uma, agenda uma
actividade "A Fazer" ao responsável e regista uma nota no chatter. Não são criadas actividades
duplicadas enquanto a anterior não for concluída.

## Segurança

- ACL para vendedores (leitura/escrita) e gestores de vendas nas linhas e no wizard; taxas de câmbio em
  leitura para qualquer utilizador interno e escrita apenas para gestores.
- Record rules: regra global multi-empresa, vendedores só vêem linhas das oportunidades que lhes estão
  atribuídas (ou da sua equipa) e gestores vêem todas.

## Instruções para testes

1. **Câmbio** – `CRM > Configuração > Taxas de Câmbio (USD/KZ)`, criar uma taxa com a data de hoje
   (ex.: 990). Criar outra com data anterior e confirmar que continua a ser usada a mais recente.
2. **Produtos** – criar/abrir um produto e marcar *Pode ser Alugado*. Criar uma lista de preços em USD
   com um preço fixo para o produto e associá-la ao cliente.
3. **Venda** – nova oportunidade, escolher o cliente (a lista de preços é preenchida), separador
   *Cotação*, tipo *Venda*, adicionar uma linha com um produto de serviço.
   Verificar preço USD, preço KZ (`USD × câmbio`) e os subtotais ao alterar a quantidade.
4. **Aluguer** – na mesma oportunidade, botão *Adicionar Aluguer*, escolher o produto de aluguer e as
   datas. Confirmar o nº de dias, o total USD (`dias × preço da lista`) e o total KZ.
   Após confirmar, validar os subtotais da linha e os totais da oportunidade.
5. **Dashboard** – `CRM > Relatórios > Forecast Aluguer / Venda`; agrupar por cliente e comparar as
   medidas com os valores das oportunidades.
6. **Cron** – colocar a data prevista de fecho de uma oportunidade no passado e executar manualmente
   a acção agendada em *Definições > Técnico > Acções Automatizadas > Acções Planeadas*.
   Deve ser criada uma actividade para o responsável e uma nota no chatter.
