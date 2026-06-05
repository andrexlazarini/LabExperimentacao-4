# Lab04S01 - Caracterizacao do Dataset

## Objetivo

Esta etapa caracteriza o dataset usado no estudo sobre impacto da IA em repositorios
GitHub. Cada objeto de estudo e um repositorio publico, e o dashboard deve mostrar
quem compoe a amostra antes das comparacoes das questoes de pesquisa.

## Base Utilizada

- Arquivo original: `analise_impacto_ia.csv`.
- Total de repositorios: 105.
- Colunas no dataset preparado: 45.
- Valores faltantes identificados: 2.
- Unidade de analise: repositorio GitHub.

## Caracteristicas Gerais

| Indicador | Valor |
| --- | ---: |
| Mediana de estrelas | 17.169 |
| Media de estrelas | 29.044,61 |
| Mediana de idade | 9,3 anos |
| Media de idade | 10,22 anos |
| Mediana do score de IA | 3 |
| Media do score de IA | 4,73 |

## Subgrupos de Evidencia de IA

| Grupo | Repositorios | Mediana estrelas | Mediana idade | Mediana score IA |
| --- | ---: | ---: | ---: | ---: |
| Baixo (2-3) | 55 | 14.662 | 9,50 | 3,00 |
| Medio (4-6) | 32 | 18.905,00 | 9,00 | 6,00 |
| Alto (7+) | 18 | 30.102,00 | 9,05 | 8,50 |

Os grupos foram derivados do `ai_score`: Baixo para scores 2 e 3, Medio para scores
4 a 6, e Alto para scores maiores ou iguais a 7. O maior grupo e o Baixo, mas ha uma
parcela relevante de repositorios com evidencias mais fortes de IA.

## Evidencias de IA

| Evidencia | Repositorios |
| --- | ---: |
| Coautoria relacionada a IA | 94 |
| Mencao a Claude | 69 |
| Mencao a Copilot | 56 |
| Arquivo relacionado a IA | 42 |

As evidencias nao sao exclusivas, portanto um mesmo repositorio pode aparecer em mais
de uma categoria.

## Visualizacoes da Sprint 1

1. Cartoes com total de repositorios, mediana de estrelas, mediana de idade e mediana
   do score de IA.
2. Barras com quantidade de repositorios por grupo de IA.
3. Distribuicao do `ai_score`.
4. Barras com mediana de estrelas por grupo de IA.
5. Barras com idade mediana por grupo de IA.
6. Barras com tipos de evidencia de IA.
7. Tabela com os 10 repositorios mais populares.
