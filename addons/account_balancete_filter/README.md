# Balancete - Filtro por Débito/Crédito

Adiciona ao módulo de contabilidade um **Balancete** (`Contabilidade > Relatórios > Balancete`) com os
movimentos agrupados por conta e totais de débito, crédito e saldo, e um filtro personalizado que
permite pesquisar lançamentos pelo valor de **Débito** ou de **Crédito**.

## Utilização

Na barra de pesquisa do balancete (ou dos *Itens de Diário*), escreva o valor pretendido e escolha o
método de pesquisa proposto — *Pesquisar Débito por: ...* ou *Pesquisar Crédito por: ...*. O relatório
é filtrado no ecrã, mantendo os totais por conta.

O mesmo filtro é acrescentado à vista de pesquisa padrão dos itens de diário
(`account.view_account_move_line_filter`).

## Instalação

### Pela tela

1. Abra http://localhost:8069/web?debug=1
2. **Definições** / **Apps** → **Atualizar lista de Apps**
3. Instale Contabilidade (`account`) se ainda não estiver instalado
4. Procure `account_balancete_filter` (ou "Balancete") e instale

### Pela linha de comando

```bash
docker compose stop odoo
docker compose run --rm odoo odoo -c /etc/odoo/odoo.conf -d odoo -i account_balancete_filter --stop-after-init
docker compose start odoo
```

## Testes

1. Instalar o módulo `account` e lançar alguns movimentos (ou usar os dados de demonstração).
2. Abrir `Contabilidade > Relatórios > Balancete` e confirmar o agrupamento por conta com os
   somatórios de débito, crédito e saldo.
3. Escrever um valor na barra de pesquisa (ex.: `1500`) e escolher *Débito*; apenas os lançamentos com
   esse valor a débito devem ficar visíveis.
4. Repetir com *Crédito* e combinar com o filtro de conta ou de datas.
