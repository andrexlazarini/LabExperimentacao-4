# Artigo Final - Impacto da IA em Repositorios GitHub

## 1. Introducao

Ferramentas de inteligencia artificial passaram a apoiar tarefas de desenvolvimento de
software, como escrita de codigo, revisao, correcao de defeitos e documentacao. Neste
trabalho, analisamos repositorios publicos do GitHub com evidencias de uso de IA para
investigar mudancas em metricas de manutencao e manutenibilidade.

## 2. Objetivo e Questoes de Pesquisa

O objetivo do estudo e avaliar como metricas de atividade, qualidade e
manutenibilidade se comportam antes e depois da identificacao de sinais de uso de IA.

RQ1: Como as metricas de atividade de manutencao mudam apos a identificacao de
sinais de uso de IA nos repositorios?

RQ2: Como as metricas de qualidade e manutenibilidade mudam apos a identificacao de
sinais de uso de IA nos repositorios?

## 3. Metodologia

A base analisada contem 105 repositorios publicos do GitHub. Cada
repositorio possui informacoes de popularidade, idade, evidencias de IA e metricas
coletadas nos periodos anterior e posterior ao marco de identificacao de IA.

Para a caracterizacao do dataset, foram usadas metricas como numero de estrelas, idade
do repositorio, score de evidencia de IA e tipo de evidencia encontrada. A Figura 1 do
dashboard apresenta a visao geral da amostra, enquanto a Figura 2 apresenta a
distribuicao dos repositorios por nivel de evidencia de IA.

Os repositorios foram agrupados em tres niveis: Baixo, Medio e Alto. A Tabela 1 resume
esses grupos.

| Grupo | Repositorios | Mediana estrelas | Mediana idade | Mediana score IA |
| --- | ---: | ---: | ---: | ---: |
| Baixo (2-3) | 55 | 14.662 | 9,50 | 3,00 |
| Medio (4-6) | 32 | 18.905,00 | 9,00 | 6,00 |
| Alto (7+) | 18 | 30.102,00 | 9,05 | 8,50 |

## 4. Resultados

### 4.1 RQ1 - Atividade de Manutencao

Para responder a RQ1, comparamos commits, issues, taxa mensal de issues e tempo medio
de resolucao antes e depois da identificacao dos sinais de IA. A Figura 3 do dashboard
apresenta a comparacao antes/depois por mediana.

| Metrica | Mediana antes | Mediana depois | Diferenca |
| --- | ---: | ---: | ---: |
| Commits | 255,00 | 166,00 | -89,00 |
| Issues | 399,00 | 113,00 | -286,00 |
| Taxa de issues por mes | 66,50 | 18,83 | -47,67 |
| Tempo medio de resolucao | 9.898,01 | 5.645,14 | -4.252,87 |

Os resultados indicam queda na mediana de commits, issues e taxa mensal de issues no
periodo posterior. Tambem houve reducao na mediana do tempo medio de resolucao, o que
pode indicar maior eficiencia na resolucao de issues ou mudancas no volume e no tipo
de demandas registradas.

### 4.2 RQ2 - Qualidade e Manutenibilidade

Para responder a RQ2, analisamos percentual de fixes, percentual de reverts, linhas
alteradas por commit e Maintainability Index. A Figura 4 do dashboard apresenta a
comparacao dessas metricas.

| Metrica | Mediana antes | Mediana depois | Diferenca |
| --- | ---: | ---: | ---: |
| Percentual de fixes | 32,12 | 36,07 | 3,95 |
| Percentual de reverts | 1,10 | 1,24 | 0,14 |
| Linhas alteradas por commit | 193,79 | 217,49 | 23,69 |
| Maintainability Index medio | 63,43 | 60,90 | -2,53 |
| Maintainability Index mediano | 60,29 | 58,50 | -1,80 |

A mediana do percentual de fixes aumenta apos os sinais de IA, enquanto o percentual
de reverts tambem apresenta leve crescimento. A mediana de linhas alteradas por commit
diminui, sugerindo alteracoes menores. Ja o Maintainability Index medio tem pequena
queda mediana, indicando que os resultados de manutenibilidade devem ser interpretados
com cautela.

## 5. Discussao

Os resultados nao devem ser interpretados como causalidade direta, pois o desenho do
dataset e observacional. As diferencas antes/depois podem refletir a introducao de IA,
mas tambem podem ser influenciadas por maturidade dos projetos, mudancas na equipe,
politicas de manutencao ou variacoes naturais da atividade open source.

Ainda assim, o dashboard facilita a leitura dos dados ao separar caracterizacao,
comparacoes antes/depois e analises por grupo de evidencia de IA. A escolha da mediana
como medida principal reduz a influencia de repositorios muito grandes ou muito ativos.

## 6. Conclusao

O estudo caracterizou 105 repositorios GitHub e comparou metricas de
manutencao antes e depois da identificacao de sinais de uso de IA. A amostra e composta
por projetos maduros e populares. As comparacoes mostram reducao em volume mediano de
atividade e melhoria em algumas metricas de fluxo, como tempo de resolucao e
percentual de fixes, mas nao evidenciam melhora uniforme na manutenibilidade.
