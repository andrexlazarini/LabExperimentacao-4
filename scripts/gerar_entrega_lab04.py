import csv
import html
import json
import math
from pathlib import Path
from statistics import mean, median


ROOT = Path(__file__).resolve().parents[1]
DATASET = ROOT / "analise_impacto_ia.csv"
DATA_DIR = ROOT / "dados_powerbi"
DOCS_DIR = ROOT / "docs"
DASH_DIR = ROOT / "dashboard"


def br(value, digits=2):
    if isinstance(value, int):
        return f"{value:,}".replace(",", ".")
    if value is None or (isinstance(value, float) and math.isnan(value)):
        return "-"
    text = f"{value:,.{digits}f}"
    return text.replace(",", "X").replace(".", ",").replace("X", ".")


def num(row, key):
    return float(row[key])


def score_group(score):
    if score <= 3:
        return "Baixo (2-3)"
    if score <= 6:
        return "Medio (4-6)"
    return "Alto (7+)"


def stars_group(stars):
    if stars < 15000:
        return "Menos de 15 mil"
    if stars < 30000:
        return "15 mil a 29,9 mil"
    if stars < 60000:
        return "30 mil a 59,9 mil"
    return "60 mil ou mais"


def age_group(age):
    if age < 8:
        return "Menos de 8 anos"
    if age < 12:
        return "8 a 11,9 anos"
    return "12 anos ou mais"


def pct_change(pre, pos):
    if pre == 0:
        return None
    return ((pos - pre) / pre) * 100


def read_rows():
    with DATASET.open("r", encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))

    enriched = []
    for r in rows:
        reason = r["ai_validation_reason"].lower()
        stars = int(float(r["stars"]))
        age = num(r, "age_years")
        score = num(r, "ai_score")
        out = dict(r)
        out.update(
            {
                "owner": r["repository"].split("/")[0],
                "stars": stars,
                "age_years": age,
                "age_group": age_group(age),
                "ai_score": score,
                "ai_score_group": score_group(score),
                "stars_group": stars_group(stars),
                "has_detected_file": "arquivo detectado" in reason,
                "has_coauthorship": "co-autoria detectada" in reason,
                "mentions_copilot": "copilot" in reason,
                "mentions_claude": "claude" in reason,
            }
        )
        numeric = [
            "pre_commits",
            "pre_issues",
            "pre_avg_resolution_hours",
            "pre_issue_rate_per_month",
            "pre_fix_percent",
            "pre_revert_percent",
            "pre_avg_lines_changed",
            "pre_avg_mi",
            "pre_median_mi",
            "pre_std_mi",
            "pos_commits",
            "pos_issues",
            "pos_avg_resolution_hours",
            "pos_issue_rate_per_month",
            "pos_fix_percent",
            "pos_revert_percent",
            "pos_avg_lines_changed",
            "pos_avg_mi",
            "pos_median_mi",
            "pos_std_mi",
            "comparison_mi_change_percent",
        ]
        for key in numeric:
            out[key] = num(r, key)

        out["delta_commits"] = out["pos_commits"] - out["pre_commits"]
        out["delta_issues"] = out["pos_issues"] - out["pre_issues"]
        out["delta_resolution_hours"] = (
            out["pos_avg_resolution_hours"] - out["pre_avg_resolution_hours"]
        )
        out["delta_issue_rate"] = (
            out["pos_issue_rate_per_month"] - out["pre_issue_rate_per_month"]
        )
        out["delta_fix_percent"] = out["pos_fix_percent"] - out["pre_fix_percent"]
        out["delta_revert_percent"] = (
            out["pos_revert_percent"] - out["pre_revert_percent"]
        )
        out["delta_lines_changed"] = (
            out["pos_avg_lines_changed"] - out["pre_avg_lines_changed"]
        )
        out["delta_avg_mi"] = out["pos_avg_mi"] - out["pre_avg_mi"]
        out["pct_commits"] = pct_change(out["pre_commits"], out["pos_commits"])
        out["pct_issues"] = pct_change(out["pre_issues"], out["pos_issues"])
        out["pct_issue_rate"] = pct_change(
            out["pre_issue_rate_per_month"], out["pos_issue_rate_per_month"]
        )
        enriched.append(out)
    return enriched


def write_csv(path, rows, fields=None):
    path.parent.mkdir(parents=True, exist_ok=True)
    if fields is None and rows:
        fields = list(rows[0].keys())
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def group_rows(rows, key):
    groups = {}
    for r in rows:
        groups.setdefault(r[key], []).append(r)
    return groups


def med(rows, key):
    return median([r[key] for r in rows])


def avg(rows, key):
    return mean([r[key] for r in rows])


def count_true(rows, key):
    return sum(1 for r in rows if r[key])


def build_summaries(rows):
    by_score = [
        {"ai_score": k, "repositories": len(v)}
        for k, v in sorted(group_rows(rows, "ai_score").items())
    ]
    by_group = []
    order = ["Baixo (2-3)", "Medio (4-6)", "Alto (7+)"]
    groups = group_rows(rows, "ai_score_group")
    for name in order:
        v = groups.get(name, [])
        by_group.append(
            {
                "ai_score_group": name,
                "repositories": len(v),
                "median_stars": med(v, "stars"),
                "average_stars": round(avg(v, "stars"), 2),
                "median_age_years": med(v, "age_years"),
                "average_age_years": round(avg(v, "age_years"), 2),
                "median_ai_score": med(v, "ai_score"),
                "detected_file_count": count_true(v, "has_detected_file"),
                "coauthorship_count": count_true(v, "has_coauthorship"),
                "copilot_count": count_true(v, "mentions_copilot"),
                "claude_count": count_true(v, "mentions_claude"),
                "median_delta_commits": round(med(v, "delta_commits"), 2),
                "median_delta_issues": round(med(v, "delta_issues"), 2),
                "median_delta_issue_rate": round(med(v, "delta_issue_rate"), 2),
                "median_delta_resolution_hours": round(
                    med(v, "delta_resolution_hours"), 2
                ),
                "median_delta_fix_percent": round(med(v, "delta_fix_percent"), 2),
                "median_delta_revert_percent": round(
                    med(v, "delta_revert_percent"), 2
                ),
                "median_delta_lines_changed": round(med(v, "delta_lines_changed"), 2),
                "median_delta_avg_mi": round(med(v, "delta_avg_mi"), 2),
            }
        )

    metric_pairs = [
        ("Commits", "pre_commits", "pos_commits", "commits"),
        ("Issues", "pre_issues", "pos_issues", "issues"),
        (
            "Taxa de issues por mes",
            "pre_issue_rate_per_month",
            "pos_issue_rate_per_month",
            "issues/mes",
        ),
        (
            "Tempo medio de resolucao",
            "pre_avg_resolution_hours",
            "pos_avg_resolution_hours",
            "horas",
        ),
        ("Percentual de fixes", "pre_fix_percent", "pos_fix_percent", "%"),
        ("Percentual de reverts", "pre_revert_percent", "pos_revert_percent", "%"),
        (
            "Linhas alteradas por commit",
            "pre_avg_lines_changed",
            "pos_avg_lines_changed",
            "linhas",
        ),
        ("Maintainability Index medio", "pre_avg_mi", "pos_avg_mi", "MI"),
        ("Maintainability Index mediano", "pre_median_mi", "pos_median_mi", "MI"),
    ]
    pre_pos = []
    for label, pre, pos, unit in metric_pairs:
        pre_median = med(rows, pre)
        pos_median = med(rows, pos)
        pre_pos.append(
            {
                "metric": label,
                "unit": unit,
                "pre_median": round(pre_median, 2),
                "pos_median": round(pos_median, 2),
                "delta_median": round(pos_median - pre_median, 2),
                "pre_average": round(avg(rows, pre), 2),
                "pos_average": round(avg(rows, pos), 2),
                "delta_average": round(avg(rows, pos) - avg(rows, pre), 2),
            }
        )

    evidence = []
    evidence_map = [
        ("Arquivo relacionado a IA", "has_detected_file"),
        ("Coautoria relacionada a IA", "has_coauthorship"),
        ("Mencao a Copilot", "mentions_copilot"),
        ("Mencao a Claude", "mentions_claude"),
    ]
    for r in rows:
        for label, key in evidence_map:
            if r[key]:
                evidence.append(
                    {"repository": r["repository"], "evidence_type": label}
                )

    star_dist = [
        {"stars_group": k, "repositories": len(v)}
        for k, v in sorted(group_rows(rows, "stars_group").items())
    ]
    top10 = sorted(rows, key=lambda r: r["stars"], reverse=True)[:10]
    return by_score, by_group, pre_pos, evidence, star_dist, top10


def md_table(rows, columns):
    header = "| " + " | ".join(c[0] for c in columns) + " |"
    sep = "| " + " | ".join("---:" if c[2] else "---" for c in columns) + " |"
    body = []
    for row in rows:
        vals = []
        for _, key, numeric in columns:
            value = row[key]
            vals.append(br(value) if numeric else str(value))
        body.append("| " + " | ".join(vals) + " |")
    return "\n".join([header, sep, *body])


def write_docs(rows, by_group, pre_pos, evidence, top10):
    total = len(rows)
    columns = len(rows[0])
    evidence_counts = {
        "Coautoria relacionada a IA": count_true(rows, "has_coauthorship"),
        "Mencao a Claude": count_true(rows, "mentions_claude"),
        "Mencao a Copilot": count_true(rows, "mentions_copilot"),
        "Arquivo relacionado a IA": count_true(rows, "has_detected_file"),
    }
    missing = 0
    for r in rows:
        missing += sum(1 for v in r.values() if v == "" or v is None)

    s01 = f"""# Lab04S01 - Caracterizacao do Dataset

## Objetivo

Esta etapa caracteriza o dataset usado no estudo sobre impacto da IA em repositorios
GitHub. Cada objeto de estudo e um repositorio publico, e o dashboard deve mostrar
quem compoe a amostra antes das comparacoes das questoes de pesquisa.

## Base Utilizada

- Arquivo original: `analise_impacto_ia.csv`.
- Total de repositorios: {br(total, 0)}.
- Colunas no dataset preparado: {br(columns, 0)}.
- Valores faltantes identificados: {br(missing, 0)}.
- Unidade de analise: repositorio GitHub.

## Caracteristicas Gerais

| Indicador | Valor |
| --- | ---: |
| Mediana de estrelas | {br(med(rows, "stars"), 0)} |
| Media de estrelas | {br(avg(rows, "stars"), 2)} |
| Mediana de idade | {br(med(rows, "age_years"), 1)} anos |
| Media de idade | {br(avg(rows, "age_years"), 2)} anos |
| Mediana do score de IA | {br(med(rows, "ai_score"), 0)} |
| Media do score de IA | {br(avg(rows, "ai_score"), 2)} |

## Subgrupos de Evidencia de IA

{md_table(by_group, [
    ("Grupo", "ai_score_group", False),
    ("Repositorios", "repositories", True),
    ("Mediana estrelas", "median_stars", True),
    ("Mediana idade", "median_age_years", True),
    ("Mediana score IA", "median_ai_score", True),
])}

Os grupos foram derivados do `ai_score`: Baixo para scores 2 e 3, Medio para scores
4 a 6, e Alto para scores maiores ou iguais a 7. O maior grupo e o Baixo, mas ha uma
parcela relevante de repositorios com evidencias mais fortes de IA.

## Evidencias de IA

| Evidencia | Repositorios |
| --- | ---: |
| Coautoria relacionada a IA | {br(evidence_counts["Coautoria relacionada a IA"], 0)} |
| Mencao a Claude | {br(evidence_counts["Mencao a Claude"], 0)} |
| Mencao a Copilot | {br(evidence_counts["Mencao a Copilot"], 0)} |
| Arquivo relacionado a IA | {br(evidence_counts["Arquivo relacionado a IA"], 0)} |

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
"""

    s02 = f"""# Lab04S02 - Visualizacoes para RQ1 e RQ2

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

{md_table([r for r in pre_pos if r["metric"] in ["Commits", "Issues", "Taxa de issues por mes", "Tempo medio de resolucao"]], [
    ("Metrica", "metric", False),
    ("Mediana antes", "pre_median", True),
    ("Mediana depois", "pos_median", True),
    ("Diferenca", "delta_median", True),
])}

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

{md_table([r for r in pre_pos if r["metric"] in ["Percentual de fixes", "Percentual de reverts", "Linhas alteradas por commit", "Maintainability Index medio", "Maintainability Index mediano"]], [
    ("Metrica", "metric", False),
    ("Mediana antes", "pre_median", True),
    ("Mediana depois", "pos_median", True),
    ("Diferenca", "delta_median", True),
])}

Interpretacao: a mediana do percentual de fixes aumenta no periodo posterior, enquanto
o percentual de reverts tem leve crescimento. A mediana de linhas alteradas por commit
fica menor, e o Maintainability Index medio apresenta pequena reducao mediana. Assim,
os resultados indicam ganhos em algumas metricas de fluxo, mas nao uma melhora clara
e uniforme de manutenibilidade.
"""

    article = f"""# Artigo Final - Impacto da IA em Repositorios GitHub

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

A base analisada contem {br(total, 0)} repositorios publicos do GitHub. Cada
repositorio possui informacoes de popularidade, idade, evidencias de IA e metricas
coletadas nos periodos anterior e posterior ao marco de identificacao de IA.

Para a caracterizacao do dataset, foram usadas metricas como numero de estrelas, idade
do repositorio, score de evidencia de IA e tipo de evidencia encontrada. A Figura 1 do
dashboard apresenta a visao geral da amostra, enquanto a Figura 2 apresenta a
distribuicao dos repositorios por nivel de evidencia de IA.

Os repositorios foram agrupados em tres niveis: Baixo, Medio e Alto. A Tabela 1 resume
esses grupos.

{md_table(by_group, [
    ("Grupo", "ai_score_group", False),
    ("Repositorios", "repositories", True),
    ("Mediana estrelas", "median_stars", True),
    ("Mediana idade", "median_age_years", True),
    ("Mediana score IA", "median_ai_score", True),
])}

## 4. Resultados

### 4.1 RQ1 - Atividade de Manutencao

Para responder a RQ1, comparamos commits, issues, taxa mensal de issues e tempo medio
de resolucao antes e depois da identificacao dos sinais de IA. A Figura 3 do dashboard
apresenta a comparacao antes/depois por mediana.

{md_table([r for r in pre_pos if r["metric"] in ["Commits", "Issues", "Taxa de issues por mes", "Tempo medio de resolucao"]], [
    ("Metrica", "metric", False),
    ("Mediana antes", "pre_median", True),
    ("Mediana depois", "pos_median", True),
    ("Diferenca", "delta_median", True),
])}

Os resultados indicam queda na mediana de commits, issues e taxa mensal de issues no
periodo posterior. Tambem houve reducao na mediana do tempo medio de resolucao, o que
pode indicar maior eficiencia na resolucao de issues ou mudancas no volume e no tipo
de demandas registradas.

### 4.2 RQ2 - Qualidade e Manutenibilidade

Para responder a RQ2, analisamos percentual de fixes, percentual de reverts, linhas
alteradas por commit e Maintainability Index. A Figura 4 do dashboard apresenta a
comparacao dessas metricas.

{md_table([r for r in pre_pos if r["metric"] in ["Percentual de fixes", "Percentual de reverts", "Linhas alteradas por commit", "Maintainability Index medio", "Maintainability Index mediano"]], [
    ("Metrica", "metric", False),
    ("Mediana antes", "pre_median", True),
    ("Mediana depois", "pos_median", True),
    ("Diferenca", "delta_median", True),
])}

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

O estudo caracterizou {br(total, 0)} repositorios GitHub e comparou metricas de
manutencao antes e depois da identificacao de sinais de uso de IA. A amostra e composta
por projetos maduros e populares. As comparacoes mostram reducao em volume mediano de
atividade e melhoria em algumas metricas de fluxo, como tempo de resolucao e
percentual de fixes, mas nao evidenciam melhora uniforme na manutenibilidade.
"""

    presentation = f"""# Apresentacao Final - Lab04

## Slide 1 - Titulo

Impacto da IA em Repositorios GitHub

Dashboard de BI para caracterizacao e analise de resultados

---

## Slide 2 - Objetivo

O objetivo foi construir um dashboard para apresentar os dados do estudo e responder
as questoes de pesquisa sobre mudancas antes e depois de sinais de uso de IA.

---

## Slide 3 - Dataset

- {br(total, 0)} repositorios GitHub.
- Repositorios com metricas antes e depois.
- Mediana de {br(med(rows, "stars"), 0)} estrelas.
- Mediana de {br(med(rows, "age_years"), 1)} anos de idade.
- Sem valores faltantes.

---

## Slide 4 - Grupos de IA

{md_table(by_group, [
    ("Grupo", "ai_score_group", False),
    ("Repositorios", "repositories", True),
    ("Mediana score", "median_ai_score", True),
])}

---

## Slide 5 - RQ1

RQ1: Como as metricas de atividade de manutencao mudam apos a identificacao de sinais
de uso de IA?

Principais metricas: commits, issues, taxa de issues por mes e tempo de resolucao.

---

## Slide 6 - Resultado da RQ1

As medianas indicam reducao no volume de commits, issues e taxa mensal de issues. O
tempo medio de resolucao tambem diminui na mediana, sugerindo melhora no fluxo de
tratamento de issues.

---

## Slide 7 - RQ2

RQ2: Como as metricas de qualidade e manutenibilidade mudam apos a identificacao de
sinais de uso de IA?

Principais metricas: fixes, reverts, linhas alteradas e Maintainability Index.

---

## Slide 8 - Resultado da RQ2

O percentual mediano de fixes aumenta, mas o percentual de reverts tambem cresce um
pouco. O Maintainability Index medio apresenta pequena queda mediana, indicando um
resultado misto.

---

## Slide 9 - Conclusao

O dashboard mostra que os dados sugerem mudancas importantes apos os sinais de IA, mas
sem conclusao causal direta. A caracterizacao e as comparacoes ajudam a interpretar o
comportamento dos repositorios.
"""

    guide = """# Guia de Montagem no Power BI

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
"""

    s03 = f"""# Lab04S03 - Entrega Final

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
"""

    DOCS_DIR.mkdir(exist_ok=True)
    (DOCS_DIR / "lab04s01_caracterizacao_dataset.md").write_text(s01, encoding="utf-8")
    (DOCS_DIR / "lab04s02_rq1_rq2.md").write_text(s02, encoding="utf-8")
    (DOCS_DIR / "lab04s03_entrega_final.md").write_text(s03, encoding="utf-8")
    (DOCS_DIR / "artigo_final_lab04.md").write_text(article, encoding="utf-8")
    (DOCS_DIR / "apresentacao_final_lab04.md").write_text(
        presentation, encoding="utf-8"
    )
    (DOCS_DIR / "guia_powerbi.md").write_text(guide, encoding="utf-8")


def svg_bar(title, data, label_key, value_key, width=640, height=260):
    max_v = max(d[value_key] for d in data) or 1
    left = 170
    top = 42
    bar_h = 28
    gap = 14
    lines = [
        f'<svg viewBox="0 0 {width} {height}" class="chart" role="img" aria-label="{html.escape(title)}">',
        f'<text x="0" y="22" class="chart-title">{html.escape(title)}</text>',
        f'<line x1="{left}" y1="{top - 10}" x2="{left}" y2="{height - 28}" class="axis-line" />',
    ]
    for i, d in enumerate(data):
        y = top + i * (bar_h + gap)
        w = (width - left - 60) * d[value_key] / max_v
        lines.append(
            f'<text x="0" y="{y + 19}" class="axis-label">{html.escape(str(d[label_key]))}</text>'
        )
        lines.append(f'<rect x="{left}" y="{y}" width="{w:.2f}" height="{bar_h}" rx="5" />')
        lines.append(
            f'<text x="{left + w + 8}" y="{y + 19}" class="value">{br(d[value_key], 0)}</text>'
        )
    lines.append("</svg>")
    return "\n".join(lines)


def svg_prepos(title, rows, metrics, width=900, height=None):
    data = [r for r in rows if r["metric"] in metrics]
    if height is None:
        height = 76 + len(data) * 72
    label_x = 0
    bar_x = 255
    value_x = 730
    top = 64
    group_h = 72
    bar_h = 16
    scale_w = 410
    lines = [
        f'<svg viewBox="0 0 {width} {height}" class="chart" role="img" aria-label="{html.escape(title)}">',
        f'<text x="0" y="24" class="chart-title">{html.escape(title)}</text>',
        f'<text x="0" y="44" class="chart-subtitle">Cada linha compara a mediana da metrica antes e depois dos sinais de IA.</text>',
        f'<text x="{bar_x}" y="54" class="legend before">Antes</text>',
        f'<text x="{bar_x + 112}" y="54" class="legend after">Depois</text>',
        f'<text x="{value_x}" y="54" class="legend delta-label">Diferenca</text>',
    ]
    for i, r in enumerate(data):
        y = top + i * group_h
        max_v = max(r["pre_median"], r["pos_median"]) or 1
        pre_w = scale_w * r["pre_median"] / max_v
        pos_w = scale_w * r["pos_median"] / max_v
        delta = r["delta_median"]
        delta_class = "positive" if delta > 0 else "negative" if delta < 0 else "neutral"
        lines.append(
            f'<text x="{label_x}" y="{y + 24}" class="axis-label metric-name">{html.escape(r["metric"])}</text>'
        )
        lines.append(
            f'<text x="{bar_x}" y="{y + 13}" class="value before-value">{br(r["pre_median"])}</text>'
        )
        lines.append(
            f'<text x="{bar_x + 112}" y="{y + 13}" class="value after-value">{br(r["pos_median"])}</text>'
        )
        lines.append(f'<rect class="track" x="{bar_x}" y="{y + 22}" width="{scale_w}" height="{bar_h}" rx="5" />')
        lines.append(f'<rect class="before-bar" x="{bar_x}" y="{y + 22}" width="{pre_w:.2f}" height="{bar_h}" rx="5" />')
        lines.append(f'<rect class="track" x="{bar_x}" y="{y + 45}" width="{scale_w}" height="{bar_h}" rx="5" />')
        lines.append(f'<rect class="after-bar" x="{bar_x}" y="{y + 45}" width="{pos_w:.2f}" height="{bar_h}" rx="5" />')
        lines.append(
            f'<text x="{value_x}" y="{y + 34}" class="delta {delta_class}">{br(delta)}</text>'
        )
    lines.append("</svg>")
    return "\n".join(lines)


def write_dashboard(rows, by_group, by_score, pre_pos, evidence, top10):
    evidence_counts = [
        {"evidence": k, "repositories": v}
        for k, v in {
            "Coautoria IA": count_true(rows, "has_coauthorship"),
            "Claude": count_true(rows, "mentions_claude"),
            "Copilot": count_true(rows, "mentions_copilot"),
            "Arquivo IA": count_true(rows, "has_detected_file"),
        }.items()
    ]
    top_rows = "\n".join(
        f"<tr><td>{html.escape(r['repository'])}</td><td>{br(r['stars'], 0)}</td><td>{br(r['age_years'], 1)}</td><td>{br(r['ai_score'], 0)}</td><td>{html.escape(r['ai_score_group'])}</td></tr>"
        for r in top10
    )
    prepos_table = "\n".join(
        f"<tr><td>{html.escape(r['metric'])}</td><td>{br(r['pre_median'])}</td><td>{br(r['pos_median'])}</td><td>{br(r['delta_median'])}</td></tr>"
        for r in pre_pos
    )
    html_doc = f"""<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>Dashboard Lab04 - Impacto da IA</title>
<style>
:root {{
  --bg: #eef3f8;
  --ink: #13202f;
  --muted: #ffffff;
  --panel: #ffffff;
  --line: #d7e0ea;
  --blue: #2f6fed;
  --blue-dark: #1e4fb8;
  --green: #13a36f;
  --green-dark: #087a55;
  --amber: #c98113;
  --red: #cf3f4a;
  --soft-blue: #eaf1ff;
  --soft-green: #e8f8f1;
  --shadow: 0 18px 45px rgba(20, 34, 52, 0.10);
}}
* {{ box-sizing: border-box; }}
body {{
  margin: 0;
  font-family: "Segoe UI", Arial, Helvetica, sans-serif;
  color: var(--ink);
  background:
    linear-gradient(180deg, #dfe9f5 0, var(--bg) 330px),
    var(--bg);
}}
header {{
  padding: 34px 42px 78px;
  color: white;
  background:
    linear-gradient(135deg, rgba(19, 32, 47, 0.96), rgba(20, 69, 135, 0.94)),
    radial-gradient(circle at 78% 18%, rgba(94, 234, 212, 0.28), transparent 30%);
}}
.header-inner {{
  max-width: 1180px;
  margin: 0 auto;
}}
.eyebrow {{
  display: inline-flex;
  align-items: center;
  gap: 8px;
  margin: 0 0 14px;
  padding: 6px 10px;
  border: 1px solid rgba(255, 255, 255, 0.22);
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.10);
  color: #dbeafe;
  font-size: 12px;
  font-weight: 700;
  text-transform: uppercase;
}}
header h1 {{
  margin: 0 0 10px;
  max-width: 760px;
  font-size: 36px;
  line-height: 1.08;
  letter-spacing: 0;
}}
header p {{
  margin: 0;
  max-width: 900px;
  color: #d8e4f2;
  font-size: 16px;
  line-height: 1.55;
}}
main {{
  max-width: 1180px;
  margin: -54px auto 0;
  padding: 0 28px 48px;
}}
section {{
  margin: 0 0 22px;
  padding: 24px;
  background: rgba(255, 255, 255, 0.96);
  border: 1px solid rgba(215, 224, 234, 0.94);
  border-radius: 8px;
  box-shadow: var(--shadow);
}}
.section-head {{
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 20px;
  margin-bottom: 18px;
}}
.section-kicker {{
  margin: 0 0 6px;
  color: var(--blue-dark);
  font-size: 12px;
  font-weight: 800;
  text-transform: uppercase;
}}
h2 {{
  margin: 0;
  font-size: 22px;
  line-height: 1.2;
}}
h3 {{
  margin: 20px 0 10px;
  font-size: 16px;
}}
.section-summary {{
  max-width: 460px;
  margin: 0;
  color: var(--muted);
  line-height: 1.45;
}}
.cards {{
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 14px;
  margin-bottom: 18px;
}}
.card {{
  position: relative;
  min-height: 104px;
  overflow: hidden;
  border: 1px solid var(--line);
  border-radius: 8px;
  padding: 16px;
  background: linear-gradient(180deg, #ffffff, #f8fbff);
}}
.card::before {{
  content: "";
  position: absolute;
  inset: 0 auto 0 0;
  width: 4px;
  background: var(--blue);
}}
.card span {{
  display: block;
  color: var(--muted);
  font-size: 13px;
  font-weight: 700;
}}
.card strong {{
  display: block;
  margin-top: 12px;
  font-size: 28px;
  line-height: 1;
}}
.grid {{
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 18px;
}}
.chart-panel {{
  border: 1px solid var(--line);
  border-radius: 8px;
  padding: 16px;
  background: #fbfdff;
}}
.chart {{
  width: 100%;
  height: auto;
  display: block;
}}
.chart rect {{
  fill: var(--blue);
}}
.chart-title {{
  font-size: 17px;
  font-weight: 800;
  fill: var(--ink);
}}
.axis-label {{
  font-size: 13px;
  fill: var(--ink);
}}
.axis-line {{
  stroke: #c8d4e2;
  stroke-width: 1;
}}
.value {{
  font-size: 12px;
  fill: var(--muted);
}}
.chart-subtitle {{
  font-size: 12px;
  fill: var(--muted);
}}
.legend {{
  font-size: 12px;
  font-weight: 800;
}}
.before {{
  fill: var(--blue);
}}
.after {{
  fill: var(--green);
}}
.track {{
  fill: #e8eef6;
}}
.chart .before-bar {{
  fill: var(--blue);
}}
.chart .after-bar {{
  fill: var(--green);
}}
.metric-name {{
  font-weight: 700;
}}
.before-value {{
  fill: var(--blue-dark);
  font-weight: 800;
}}
.after-value {{
  fill: var(--green-dark);
  font-weight: 800;
}}
.delta {{
  font-size: 15px;
  font-weight: 900;
}}
.delta.negative {{
  fill: var(--red);
}}
.delta.positive {{
  fill: var(--green-dark);
}}
.delta.neutral {{
  fill: var(--muted);
}}
.delta-label {{
  fill: var(--muted);
}}
.table-wrap {{
  overflow-x: auto;
  border: 1px solid var(--line);
  border-radius: 8px;
  background: white;
}}
table {{
  width: 100%;
  border-collapse: collapse;
  margin: 0;
  font-size: 14px;
}}
th, td {{
  border-bottom: 1px solid var(--line);
  padding: 10px 12px;
  text-align: left;
}}
tr:last-child td {{
  border-bottom: 0;
}}
th {{
  color: var(--muted);
  font-size: 12px;
  font-weight: 800;
  text-transform: uppercase;
  background: #f8fafc;
}}
tbody tr:nth-child(even) {{
  background: #fbfdff;
}}
.note {{
  color: var(--muted);
  line-height: 1.5;
}}
.insight {{
  margin: 14px 0 0;
  padding: 12px 14px;
  border-left: 4px solid var(--green);
  border-radius: 0 8px 8px 0;
  background: var(--soft-green);
  color: #244034;
  line-height: 1.45;
}}
@media print {{
  body {{
    background: white;
  }}
  header {{
    padding-bottom: 28px;
  }}
  main {{
    margin: 0;
    max-width: none;
    padding: 16px;
  }}
  section {{
    break-inside: avoid;
    box-shadow: none;
  }}
}}
@media (max-width: 900px) {{
  .cards, .grid {{
    grid-template-columns: 1fr;
  }}
  main {{
    margin-top: -42px;
    padding: 0 14px 32px;
  }}
  header {{
    padding: 26px 16px 64px;
  }}
  header h1 {{
    font-size: 28px;
  }}
  .section-head {{
    display: block;
  }}
  .section-summary {{
    margin-top: 8px;
  }}
}}
</style>
</head>
<body>
<header>
  <div class="header-inner">
    <div class="eyebrow">Lab04 S03 - Dashboard final</div>
    <h1>Impacto da IA em Repositorios GitHub</h1>
    <p>Caracterizacao do dataset e visualizacoes para responder RQ1 e RQ2. Os valores principais usam mediana para reduzir o efeito de repositorios muito grandes.</p>
  </div>
</header>
<main>
  <section>
    <div class="section-head">
      <div>
        <p class="section-kicker">Caracterizacao</p>
        <h2>Perfil dos repositorios analisados</h2>
      </div>
      <p class="section-summary">A amostra reune projetos maduros e populares do GitHub, agrupados por nivel de evidencia de uso de IA.</p>
    </div>
    <div class="cards">
      <div class="card"><span>Repositorios</span><strong>{br(len(rows), 0)}</strong></div>
      <div class="card"><span>Mediana de estrelas</span><strong>{br(med(rows, "stars"), 0)}</strong></div>
      <div class="card"><span>Mediana de idade</span><strong>{br(med(rows, "age_years"), 1)} anos</strong></div>
      <div class="card"><span>Mediana score IA</span><strong>{br(med(rows, "ai_score"), 0)}</strong></div>
    </div>
    <div class="grid">
      <div class="chart-panel">{svg_bar("Repositorios por grupo de IA", by_group, "ai_score_group", "repositories")}</div>
      <div class="chart-panel">{svg_bar("Tipos de evidencia de IA", evidence_counts, "evidence", "repositories")}</div>
    </div>
    <h3>Top 10 repositorios por estrelas</h3>
    <div class="table-wrap">
    <table>
      <thead><tr><th>Repositorio</th><th>Estrelas</th><th>Idade</th><th>Score IA</th><th>Grupo IA</th></tr></thead>
      <tbody>{top_rows}</tbody>
    </table>
    </div>
  </section>
  <section>
    <div class="section-head">
      <div>
        <p class="section-kicker">Questao de pesquisa 1</p>
        <h2>Atividade de manutencao</h2>
      </div>
      <p class="section-summary">Como as metricas de atividade mudam apos a identificacao de sinais de uso de IA?</p>
    </div>
    <div class="chart-panel">
      {svg_prepos("Medianas antes/depois - RQ1", pre_pos, ["Commits", "Issues", "Taxa de issues por mes", "Tempo medio de resolucao"])}
    </div>
    <p class="insight">As medianas indicam reducao em commits, issues, taxa mensal de issues e tempo medio de resolucao no periodo posterior.</p>
  </section>
  <section>
    <div class="section-head">
      <div>
        <p class="section-kicker">Questao de pesquisa 2</p>
        <h2>Qualidade e manutenibilidade</h2>
      </div>
      <p class="section-summary">Como fixes, reverts, linhas alteradas e Maintainability Index se comportam no periodo posterior?</p>
    </div>
    <div class="chart-panel">
      {svg_prepos("Medianas antes/depois - RQ2", pre_pos, ["Percentual de fixes", "Percentual de reverts", "Linhas alteradas por commit", "Maintainability Index medio", "Maintainability Index mediano"])}
    </div>
    <p class="insight">O percentual mediano de fixes aumenta, mas o Maintainability Index tem pequena queda; o resultado e misto e deve ser interpretado com cautela.</p>
    <h3>Resumo das metricas</h3>
    <div class="table-wrap">
    <table>
      <thead><tr><th>Metrica</th><th>Mediana antes</th><th>Mediana depois</th><th>Diferenca</th></tr></thead>
      <tbody>{prepos_table}</tbody>
    </table>
    </div>
  </section>
</main>
</body>
</html>
"""
    DASH_DIR.mkdir(exist_ok=True)
    (DASH_DIR / "dashboard_lab04_final.html").write_text(html_doc, encoding="utf-8")


def update_readme():
    readme = """# LabExperimentacao-4

Projeto completo do Lab04: visualizacao de dados com ferramenta de BI para analise do
impacto de IA em repositorios GitHub.

## Entregaveis

- `dashboard/dashboard_lab04_final.html`: dashboard final autocontido, abrindo direto
  no navegador e exportavel como PDF.
- `dashboard/dashboard_lab04_final.pdf`: versao em PDF do dashboard final.
- `docs/lab04s01_caracterizacao_dataset.md`: caracterizacao do dataset.
- `docs/lab04s02_rq1_rq2.md`: visualizacoes e interpretacoes para RQ1 e RQ2.
- `docs/lab04s03_entrega_final.md`: checklist da entrega final.
- `docs/artigo_final_lab04.md`: texto de artigo/relatorio final atualizado.
- `docs/apresentacao_final_lab04.md`: roteiro de apresentacao final.
- `docs/guia_powerbi.md`: orientacao para reproduzir o dashboard no Power BI.
- `dados_powerbi/*.csv`: dados preparados e tabelas-resumo para importacao no Power BI.

## Como usar

1. Abra `dashboard/dashboard_lab04_final.html` no navegador para visualizar o dashboard.
2. Para entregar em PDF, use a opcao de imprimir/salvar como PDF do navegador.
3. Para montar no Power BI, importe os CSVs da pasta `dados_powerbi` e siga
   `docs/guia_powerbi.md`.
"""
    (ROOT / "README.md").write_text(readme, encoding="utf-8")


def main():
    DATA_DIR.mkdir(exist_ok=True)
    rows = read_rows()
    by_score, by_group, pre_pos, evidence, star_dist, top10 = build_summaries(rows)

    full_fields = list(rows[0].keys())
    write_csv(DATA_DIR / "repositorios_caracterizados.csv", rows, full_fields)
    write_csv(DATA_DIR / "distribuicao_ai_score.csv", by_score)
    write_csv(DATA_DIR / "resumo_por_nivel_ia.csv", by_group)
    write_csv(DATA_DIR / "resumo_pre_pos.csv", pre_pos)
    write_csv(DATA_DIR / "evidencias_ia.csv", evidence)
    write_csv(DATA_DIR / "distribuicao_faixa_estrelas.csv", star_dist)
    write_csv(
        DATA_DIR / "top10_repositorios_estrelas.csv",
        [
            {
                "repository": r["repository"],
                "stars": r["stars"],
                "age_years": r["age_years"],
                "ai_score": r["ai_score"],
                "ai_score_group": r["ai_score_group"],
            }
            for r in top10
        ],
    )

    write_docs(rows, by_group, pre_pos, evidence, top10)
    write_dashboard(rows, by_group, by_score, pre_pos, evidence, top10)
    update_readme()


if __name__ == "__main__":
    main()
