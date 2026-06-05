# Guia de Montagem no Power BI

## Arquivos para Importar

1. `dados_powerbi/repositorios_caracterizados.csv`
2. `dados_powerbi/evidencias_ia.csv`
3. `dados_powerbi/resumo_pre_pos.csv`
4. `dados_powerbi/resumo_por_nivel_ia.csv`

## Paginas do Dashboard

### Pagina 1 - Caracterizacao

- Cartoes: total de repositorios, mediana de estrelas, mediana de idade e mediana do
  score de IA.
- Barras: repositorios por grupo de IA.
- Barras: evidencias de IA.
- Tabela: top 10 repositorios por estrelas.

### Pagina 2 - RQ1

- Titulo com a pergunta de pesquisa.
- Grafico antes/depois para commits, issues, taxa de issues por mes e tempo de
  resolucao.
- Tabela com mediana antes, mediana depois e diferenca.
- Filtro por `ai_score_group`.

### Pagina 3 - RQ2

- Titulo com a pergunta de pesquisa.
- Grafico antes/depois para fixes, reverts, linhas alteradas e Maintainability Index.
- Tabela com mediana antes, mediana depois e diferenca.
- Grafico por grupo de evidencia de IA.

## Medidas DAX

```DAX
Total Repositorios = DISTINCTCOUNT(repositorios_caracterizados[repository])

Mediana Estrelas = MEDIAN(repositorios_caracterizados[stars])

Mediana Idade = MEDIAN(repositorios_caracterizados[age_years])

Mediana Score IA = MEDIAN(repositorios_caracterizados[ai_score])

Mediana MI Antes = MEDIAN(repositorios_caracterizados[pre_avg_mi])

Mediana MI Depois = MEDIAN(repositorios_caracterizados[pos_avg_mi])

Diferenca MI = [Mediana MI Depois] - [Mediana MI Antes]
```
