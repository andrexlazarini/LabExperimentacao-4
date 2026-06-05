# Lab04S02 - Visualizacoes para RQ1 e RQ2

## RQ1

**RQ1: Como as metricas de atividade de manutencao mudam apos a identificacao de
sinais de uso de IA nos repositorios?**

Metricas usadas:

- commits;
- issues;
- taxa de issues por mes;
- tempo medio de resolucao de issues.

Visualizacoes recomendadas:

- grafico comparativo antes/depois usando medianas;
- tabela com mediana, media e diferenca;
- grafico por grupo de evidencia de IA.

Resultados principais:

| Metrica | Mediana antes | Mediana depois | Diferenca |
| --- | ---: | ---: | ---: |
| Commits | 255,00 | 166,00 | -89,00 |
| Issues | 399,00 | 113,00 | -286,00 |
| Taxa de issues por mes | 66,50 | 18,83 | -47,67 |
| Tempo medio de resolucao | 9.898,01 | 5.645,14 | -4.252,87 |

Interpretacao: usando a mediana para reduzir o efeito de outliers, observa-se reducao
em commits, issues e taxa mensal de issues no periodo posterior. O tempo mediano de
resolucao tambem diminui, sugerindo melhora operacional na resolucao das issues.

## RQ2

**RQ2: Como as metricas de qualidade e manutenibilidade mudam apos a identificacao
de sinais de uso de IA nos repositorios?**

Metricas usadas:

- percentual de fixes;
- percentual de reverts;
- linhas alteradas por commit;
- Maintainability Index medio;
- Maintainability Index mediano.

Visualizacoes recomendadas:

- grafico comparativo antes/depois usando medianas;
- barras divergentes com diferenca mediana;
- tabela por grupo de evidencia de IA.

Resultados principais:

| Metrica | Mediana antes | Mediana depois | Diferenca |
| --- | ---: | ---: | ---: |
| Percentual de fixes | 32,12 | 36,07 | 3,95 |
| Percentual de reverts | 1,10 | 1,24 | 0,14 |
| Linhas alteradas por commit | 193,79 | 217,49 | 23,69 |
| Maintainability Index medio | 63,43 | 60,90 | -2,53 |
| Maintainability Index mediano | 60,29 | 58,50 | -1,80 |

Interpretacao: a mediana do percentual de fixes aumenta no periodo posterior, enquanto
o percentual de reverts tem leve crescimento. A mediana de linhas alteradas por commit
fica menor, e o Maintainability Index medio apresenta pequena reducao mediana. Assim,
os resultados indicam ganhos em algumas metricas de fluxo, mas nao uma melhora clara
e uniforme de manutenibilidade.
