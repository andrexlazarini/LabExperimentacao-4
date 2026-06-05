# Lab04S03 - Entrega Final

## Itens Entregues

| Item | Arquivo | Status |
| --- | --- | --- |
| Caracterizacao do dataset | `docs/lab04s01_caracterizacao_dataset.md` | Concluido |
| Visualizacoes para RQ1 e RQ2 | `docs/lab04s02_rq1_rq2.md` | Concluido |
| Dashboard final | `dashboard/dashboard_lab04_final.html` | Concluido |
| Artigo/relatorio final atualizado | `docs/artigo_final_lab04.md` | Concluido |
| Apresentacao final | `docs/apresentacao_final_lab04.md` | Concluido |
| Dados preparados para BI | `dados_powerbi/*.csv` | Concluido |

## Estrutura do Dashboard Final

O dashboard final esta organizado em tres blocos:

1. **Caracterizacao do Dataset**: apresenta tamanho da amostra, popularidade, idade,
   score de IA, grupos de evidencia e tipos de evidencia encontrados.
2. **RQ1 - Atividade de Manutencao**: compara metricas de atividade antes e depois
   dos sinais de IA.
3. **RQ2 - Qualidade e Manutenibilidade**: compara fixes, reverts, linhas alteradas e
   Maintainability Index.

## Respostas Sinteticas das RQs

**RQ1:** as medianas indicam reducao no volume de commits, issues e taxa de issues por
mes no periodo posterior. Tambem ha reducao no tempo mediano de resolucao.

**RQ2:** o percentual mediano de fixes aumenta, mas o percentual de reverts tambem tem
leve alta. O Maintainability Index medio apresenta pequena queda mediana, portanto nao
ha evidencia de melhora uniforme de manutenibilidade.

## Observacao Metodologica

As comparacoes sao observacionais e nao estabelecem causalidade direta entre uso de IA
e mudancas nas metricas. A interpretacao deve considerar maturidade dos projetos,
atividade da comunidade, politicas de manutencao e diferencas entre repositorios.
