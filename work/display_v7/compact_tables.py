#!/usr/bin/env python3
"""Create compact display tables from the frozen RC02 table exports.

This is a formatting-only transformation. It does not fit models or derive
estimates. The full T1/T2/T3/T5 CSV inputs are archived as S54-S57 before the
stage display CSVs are replaced. RC02 and S01-S53 CSV bytes are audited.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import shutil
from collections import defaultdict
from pathlib import Path
from typing import Any


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def read_csv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        if reader.fieldnames is None:
            raise ValueError(f"Missing CSV header: {path}")
        rows = []
        for physical_row, row in enumerate(reader, start=2):
            rows.append({**row, "__source_row": str(physical_row)})
    return list(reader.fieldnames), rows


def write_csv(path: Path, headers: list[str], rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=headers, extrasaction="ignore", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def md_cell(value: Any) -> str:
    return str(value).replace("|", "\\|").replace("\n", "<br>")


def md_table(headers: list[str], rows: list[list[str]]) -> str:
    out = ["| " + " | ".join(md_cell(x) for x in headers) + " |", "| " + " | ".join("---" for _ in headers) + " |"]
    out.extend("| " + " | ".join(md_cell(x) for x in row) + " |" for row in rows)
    return "\n".join(out)


def translated(text: str) -> str:
    """Translate common labels/statuses for the Chinese companion table."""
    exact = {
        "eICU-CRD": "eICU-CRD",
        "eICU": "eICU",
        "MIMIC-IV": "MIMIC-IV",
        "MIMIC-III": "MIMIC-III",
        "Zigong": "自贡",
        "sepsis": "脓毒症",
        "pneumonia": "肺炎",
        "pancreatitis": "胰腺炎",
        "heart failure": "心力衰竭",
        "COPD": "慢性阻塞性肺疾病",
        "computed": "已计算",
        "not computed": "未计算",
        "Withheld by policy": "按报告策略不报告",
        "Descriptive": "描述性",
        "Point and interval in all replicates": "所有重复均输出点估计和区间",
        "Point only; failed gates:": "仅输出点估计；未通过门槛：",
        "Point only; failed gates": "仅输出点估计；未通过门槛",
        "Interval for a subset; failed gates:": "仅在部分重复中报告区间；未通过门槛：",
        "No point or interval; failed gates:": "未输出点估计或区间；未通过门槛：",
        "All intervals": "全部报告区间",
        "Some intervals": "部分重复报告区间",
        "Point only": "仅点估计",
        "No estimate": "无估计",
        "too few distinct patients": "独立患者数过少",
        "not computed; too few distinct patients": "未计算；独立患者数过少",
        "not separately summarized": "未单独汇总",
        "not reported": "未报告",
        "no emitted intervals": "未发出区间",
        "on-target intervals": "目标内区间",
        "no common support": "无共同支持",
        "patients/cell": "每单元患者数",
        "records/cell": "每单元记录数",
        "records/score": "每评分层记录数",
        "total patients": "患者总数",
        "outcome variation": "结局变异",
        "target support": "目标支持",
        "below 10 records/cell": "每单元记录数低于10",
        "Same records; common score support": "相同记录；共同评分支持集",
        "Paired code breadth": "代码范围配对比较",
        "Hospital × score": "医院×评分细分",
        "Component pattern": "组件模式细分",
        "Code breadth": "代码范围",
        "Hospital × score": "医院×评分",
        "Null, balanced IID": "零效应、平衡 IID",
        "Null, heterogeneous IID": "零效应、异质 IID",
        "Heterogeneous random weights": "异质随机权重",
        "Cross-group repeated admissions": "跨组重复住院",
        "Unequal cluster sizes": "不等聚类规模",
        "Near-boundary risks": "近边界风险",
        "Partial structural support": "部分结构支持",
        "Rare common-support holdout": "稀有共同支持留出",
        "Few large clusters": "少数大聚类",
        "No common support": "无共同支持",
        "High ICC, unbalanced holdout": "高 ICC、不平衡留出",
        "Fine cells (sparse)": "细分稀疏单元",
        "Tiny arm (sparse)": "极小组（稀疏）",
        "full sample": "全样本",
        "same classifiable subset": "同一可分类子集",
        "full-course diagnosis": "全程诊断分组",
        "never-primary-by-24-hours": "24小时内未列为首位",
    }
    # Prefer longer replacements first, preserving all numeric source text.
    out = text
    for old in sorted(exact, key=len, reverse=True):
        out = out.replace(old, exact[old])
    return out


def patient_count(r: dict[str, str], column: str) -> str:
    # Source field is records / patients; the risk field already supplies deaths / records.
    value = r[column]
    parts = [p.strip() for p in value.split("/")]
    return parts[-1] if parts else value


def compact_t1(rows: list[dict[str, str]]) -> tuple[list[str], list[dict[str, str]], list[list[str]]]:
    if len(rows) != 20:
        raise ValueError(f"T1 shape changed: expected 20 data rows, got {len(rows)}")
    headers = [
        "Database / condition",
        "Score level",
        "Never-primary deaths / n; risk (%)",
        "Primary deaths / n; risk (%)",
        "δ_s (pp; 95% CI)",
        "Pooled record weight",
    ]
    output: list[dict[str, str]] = []
    display: list[list[str]] = []
    for r in rows:
        def risk_point(value: str) -> str:
            parts = value.split(";", 1)
            event_n = parts[0].strip()
            risk = re.search(r"[-+]?\d+(?:\.\d+)?%", parts[1] if len(parts) > 1 else "")
            if not risk:
                raise ValueError(f"Could not find source risk percentage: {value}")
            return f"{event_n}; {risk.group(0)}"

        delta_source = r["δ_s (percentage points; 95% CI; status)"]
        if "[" in delta_source:
            delta = delta_source.split(";", 1)[0].strip()
        else:
            delta = delta_source.split("not computed", 1)[0].strip() + "†"
        row = {
            headers[0]: f"{r['Database']} — {r['Condition']}",
            headers[1]: f"{r['Instrument']} {r['Score level']}",
            headers[2]: risk_point(r["Never-primary deaths / risk (95% CI; status)"]),
            headers[3]: risk_point(r["Primary deaths / risk (95% CI; status)"]),
            headers[4]: delta,
            headers[5]: r["Pooled observed record weight"],
            "__source_row": r["__source_row"],
        }
        output.append(row)
        display.append([row[h] for h in headers])
    return headers, output, display


def compact_t2(rows: list[dict[str, str]]) -> tuple[list[str], list[dict[str, str]], list[list[str]]]:
    if len(rows) != 19:
        raise ValueError(f"T2 shape changed: expected 19 data rows, got {len(rows)}")
    headers = [
        "Database",
        "Condition / instrument",
        "Primary or sequence-one complete records (n)",
        "Never-primary or other-sequence complete records (n)",
        "Common-support levels; δ_s CIs excluding zero / issued",
        "Δ_w summary (pp); 95% CI status",
    ]
    output: list[dict[str, str]] = []
    display: list[list[str]] = []
    for r in rows:
        def complete_count(value: str) -> str:
            parts = value.split("→")
            if len(parts) < 2:
                raise ValueError(f"Unexpected eligibility flow: {value}")
            return parts[1].split("(", 1)[0].strip()

        status = r["Summary interval status"]
        ci = r["95% patient-cluster CI for Δ_w weighted summary"]
        weighted = r["Δ_w weighted summary (percentage points)"]
        if status == "computed" and ci not in {"not computed", "—", ""}:
            weighted = f"{weighted}; {ci}"
        else:
            weighted = f"{weighted}; CI withheld"
        counts = "; ".join([
            r["Common-support score levels"],
            r["Computed δ_s CIs excluding zero / computed δ_s CIs"],
        ])
        vals = [
            r["Database"],
            r["Condition / instrument"],
            complete_count(r["Primary or sequence-one (unqualified Zigong) eligible-complete-shared; outside support"]),
            complete_count(r["Never-primary or other-sequence (unqualified Zigong) eligible-complete-shared; outside support"]),
            counts,
            weighted,
        ]
        output.append({**dict(zip(headers, vals)), "__source_row": r["__source_row"]})
        display.append(vals)
    return headers, output, display


def compact_t3(rows: list[dict[str, str]]) -> tuple[list[str], list[dict[str, str]], list[list[str]]]:
    if len(rows) != 12:
        raise ValueError(f"T3 shape changed: expected 12 data rows, got {len(rows)}")
    headers = [
        "Analysis block / database / condition",
        "Records (patients)",
        "Narrow/score-only → broad/refined Δ_w weighted summary (pp)",
        "Paired difference (pp; numerical interval)",
        "Cell inventory / reconstruction",
        "Interval status",
    ]
    output: list[dict[str, str]] = []
    display: list[list[str]] = []
    block_names = {
        "Paired code breadth": "Code breadth",
        "Hospital × score": "Hospital × score",
        "Component pattern": "Component pattern",
    }
    db_names = {"eICU-CRD": "eICU", "MIMIC-IV": "MIMIC-IV", "MIMIC-III": "MIMIC-III", "Zigong": "Zigong"}
    for r in rows:
        breadth = " → ".join([
            r["Narrow / score-only Δ_w weighted summary"],
            r["Broad / refined Δ_w weighted summary"],
        ])
        inventory = r["Cell inventory / reconstruction"]
        inv = re.match(r"^(\d+) hospital-score cells; (\d+) with either arm ≤5; ([\d.]+%)$", inventory)
        if inv:
            inventory = f"{inv.group(1)} cells; {inv.group(2)} ≤5 ({inv.group(3)})"
        elif inventory == "Same records; common score support":
            inventory = "Same records; shared score support"
        vals = [
            f"{block_names.get(r['Analysis block'], r['Analysis block'])}: {db_names.get(r['Database'], r['Database'])} {r['Condition']}",
            r["Records (patients)"],
            breadth,
            r["Paired difference (percentage points; numerical interval)"],
            inventory,
            "Descriptive",
        ]
        output.append({**dict(zip(headers, vals)), "__source_row": r["__source_row"]})
        display.append(vals)
    return headers, output, display


def compact_t4(rows: list[dict[str, str]]) -> tuple[list[str], list[dict[str, str]], list[list[str]]]:
    if len(rows) != 6:
        raise ValueError(f"T4 shape changed: expected 6 data rows, got {len(rows)}")
    headers = [
        "Condition / grouping",
        "Records (patients)",
        "Landmark-classifiable / reclassified records",
        "Δ_w summary (pp)",
        "95% patient-cluster CI",
        "Interval status",
    ]
    output: list[dict[str, str]] = []
    display: list[list[str]] = []
    for r in rows:
        vals = [
            f"{r['Condition']} — {r['Grouping']}",
            f"{r['Records']} ({r['Patients']})",
            r["Landmark-classifiable / reclassified records"],
            r["Δ_w weighted summary (percentage points)"],
            r["95% patient-cluster CI"],
            "computed" if r["95% patient-cluster CI"] not in {"not computed", "—", ""} else "Withheld by policy",
        ]
        output.append({**dict(zip(headers, vals)), "__source_row": r["__source_row"]})
        display.append(vals)
    return headers, output, display


def coverage_without_mcse(value: str) -> str:
    # Retain the reported coverage and its denominator; detailed MCSE stays in S57.
    match = re.match(r"^(.*?)\s*\(n=([^;]+);.*\)$", value)
    if match:
        return f"{match.group(1)} (n={match.group(2)})"
    match = re.match(r"^(.*?)\s*\(([^()]*(?:on-target intervals|emitted intervals)[^()]*)\)$", value)
    if match:
        return f"{match.group(1)} ({match.group(2)})"
    return value


def design_label(value: str, chinese: bool = False) -> str:
    en = {
        "null_balanced_iid": "Null, balanced IID",
        "null_heterogeneous_iid": "Null, heterogeneous IID",
        "heterogeneous_random_weights": "Heterogeneous random weights",
        "repeated_admissions_cross_group": "Cross-group repeated admissions",
        "unequal_cluster_sizes": "Unequal cluster sizes",
        "near_boundary_risks": "Near-boundary risks",
        "partial_structural_support": "Partial structural support",
        "rare_common_support_holdout": "Rare common-support holdout",
        "few_large_clusters": "Few large clusters",
        "no common support": "No common support",
        "high_icc_unbalanced_holdout": "High ICC, unbalanced holdout",
        "fine_cells": "Fine cells (sparse)",
        "tiny_arm": "Tiny arm (sparse)",
    }
    zh = {
        "null_balanced_iid": "零效应、平衡 IID",
        "null_heterogeneous_iid": "零效应、异质 IID",
        "heterogeneous_random_weights": "异质随机权重",
        "repeated_admissions_cross_group": "跨组重复住院",
        "unequal_cluster_sizes": "不等聚类规模",
        "near_boundary_risks": "近边界风险",
        "partial_structural_support": "部分结构支持",
        "rare_common_support_holdout": "稀有共同支持留出",
        "few_large_clusters": "少数大聚类",
        "no common support": "无共同支持",
        "high_icc_unbalanced_holdout": "高 ICC、不平衡留出",
        "fine_cells": "细分稀疏单元",
        "tiny_arm": "极小组（稀疏）",
    }
    return (zh if chinese else en).get(value, value)


def compact_t5(rows: list[dict[str, str]]) -> tuple[list[str], list[dict[str, str]], list[list[str]]]:
    designs = sorted({r["Design"] for r in rows})
    if len(designs) != 7 or len(rows) != 21:
        raise ValueError(f"T5 shape changed: expected 7 designs × A/B/C, got {len(designs)} designs and {len(rows)} rows")
    by_key = {(r["Design"], r["Strategy"]): r for r in rows}
    headers = ["Design", "A: interval output; target coverage (n)", "B: interval output; target coverage (n)", "C: interval output; target coverage (n)", "A: off-target intervals", "Target support matched"]
    output: list[dict[str, str]] = []
    display: list[list[str]] = []
    strategy_rows: dict[str, list[str]] = {}
    for design in designs:
        group = {s: by_key[(design, s)] for s in ("A", "B", "C")}
        vals = [design_label(design)]
        for s in ("A", "B", "C"):
            row = group[s]
            vals.append(f"{row['Interval output (% of replicates)']}; {coverage_without_mcse(row['Population-truth coverage on target (n; MCSE, pp)'])}")
        vals.extend([
            group["A"]["Off-target interval output (% of replicates)"],
            group["A"]["Target support matched (% of replicates)"],
        ])
        display.append(vals)
        out = {**dict(zip(headers, vals)), "__source_rows": ",".join(group[s]["__source_row"] for s in ("A", "B", "C"))}
        output.append(out)
    return headers, output, display


def compact_t6(rows: list[dict[str, str]]) -> tuple[list[str], list[dict[str, str]], list[list[str]]]:
    if len(rows) != 13:
        raise ValueError(f"T6 shape changed: expected 13 data rows, got {len(rows)}")
    headers = ["Design (truth-defined n)", "C point / interval output (%)", "Mean Δ_w bias (pp)", "Conditional coverage (n)", "MCSE (pp)", "Tool state"]
    output: list[dict[str, str]] = []
    display: list[list[str]] = []
    for r in rows:
        coverage = r["Population-truth coverage on target (n; MCSE, pp)"]
        cov_match = re.match(r"^(.*?)\s*\(n=([^;]+);\s*([\d.]+)\s*pp\)$", coverage)
        if cov_match:
            coverage_display = f"{cov_match.group(1)} (n={cov_match.group(2)})"
            mcse = cov_match.group(3)
        else:
            coverage_display = coverage
            mcse = "—"
        emitted_parts = r["C point / interval output (% of replicates)"].split("/")
        if len(emitted_parts) != 2:
            raise ValueError(f"Unexpected T6 point/interval output: {r['C point / interval output (% of replicates)']}")
        point_pct, interval_pct = (x.strip() for x in emitted_parts)
        interval_value = float(interval_pct.rstrip("%"))
        point_value = float(point_pct.rstrip("%"))
        state = "All intervals" if interval_value >= 99.999 else "Some intervals" if interval_value > 0 else "Point only" if point_value > 0 else "No estimate"
        vals = [
            f"{design_label(r['Design'])} (n={r['Observed-weight truth defined (n)']})",
            r["C point / interval output (% of replicates)"],
            r["Mean bias of Δ_w weighted summary (pp)"],
            coverage_display,
            mcse,
            state,
        ]
        output.append({**dict(zip(headers, vals)), "__source_row": r["__source_row"]})
        display.append(vals)
    return headers, output, display


def render_main_tables(source_tables: dict[str, list[dict[str, str]]], compacted: dict[str, tuple[list[str], list[dict[str, str]], list[list[str]]]]) -> tuple[str, str]:
    en: list[str] = ["# Main tables", "", "Six main tables accompany the manuscript. δ_s denotes a score-specific observed risk difference; Δ_w denotes the record-weighted summary.", ""]
    zh: list[str] = ["# 正文表格", "", "正文共 6 张表。δ_s 表示评分层级的观察风险差；Δ_w 表示按记录数加权的汇总。", ""]

    titles = {
        "t1": ("Table 1. Score-level observed mortality risks and δ_s in the four primary analysis groups", "表 1. 四个主要分析组的评分层级观察死亡风险与 δ_s"),
        "t2": ("Table 2. Database-condition complete-group support and Δ_w weighted summaries", "表 2. 数据库-疾病组的完整记录支持与 Δ_w 加权汇总"),
        "t3": ("Table 3. Paired code-breadth and refinement comparisons of Δ_w summaries", "表 3. Δ_w 汇总的代码范围与分层细化配对比较"),
        "t4": ("Table 4. Full-course and documentation-by-24-hours weighted summaries in eICU", "表 4. eICU 全程诊断与 24 小时内记录分组的加权汇总"),
        "t5": ("Table 5. Selected audit-strategy interval emission and target coverage for Δ_w", "表 5. Δ_w 代表性审计策略的区间输出与目标覆盖"),
        "t6": ("Table 6. Δ_w bias, conditional coverage, Monte Carlo precision, and tool states under Strategy C", "表 6. 策略 C 下 Δ_w 的偏倚、条件覆盖、蒙特卡洛精度与工具状态"),
    }
    headers_zh = {
        "t1": ["数据源 / 疾病", "工具 / 评分层级", "非首位组死亡数 / n；风险（%）", "首位组死亡数 / n；风险（%）", "δ_s（百分点；95% CI）", "合并记录权重"],
        "t2": ["数据库", "疾病 / 工具", "首位或序号一组完整记录数", "非首位或其他序号组完整记录数", "共同支持层级；δ_s CI 排除零 / 已发出", "Δ_w 汇总（百分点）；95% CI 状态"],
        "t3": ["分析模块 / 数据库 / 疾病", "记录数（患者数）", "窄定义/仅评分 → 宽定义/细分 Δ_w 加权摘要（百分点）", "配对差值（百分点；数值区间）", "单元清单 / 重建", "区间状态"],
        "t4": ["疾病 / 分组方式", "记录数（患者数）", "时间节点可分类 / 重新分类记录", "Δ_w 汇总（百分点）", "患者聚类 95% CI", "区间状态"],
        "t5": ["设计", "A：区间输出；目标覆盖率（n）", "B：区间输出；目标覆盖率（n）", "C：区间输出；目标覆盖率（n）", "A：偏离目标的区间", "目标支持集匹配"],
        "t6": ["设计（已定义真值的重复数）", "C 点估计 / 区间输出（%）", "Δ_w 平均偏倚（百分点）", "条件覆盖率（n）", "MCSE（百分点）", "工具状态"],
    }
    notes_en = {
        "t1": [
            "At each score level, δ_s is observed mortality among never-primary records minus observed mortality among primary records. Repeated admission records remain separate in the record-weighted target; patient clustering handles dependence.",
            "Values show deaths / records and the point risk. The dagger marks a point estimate without a computed score-level interval; risk-interval endpoints and source statuses remain in Supplementary Table S54. Score-level δ_s intervals are source-issued patient-cluster sandwich Wald intervals and are separately gated.",
            "Pooled record weight is the observed admission-record share for that supported score level, not a patient share or external population weight. Full source columns, including patient counts and CI methods, are in Supplementary Table S54.",
        ],
        "t2": [
            "Complete records have complete score components and known outcome. Full eligibility, exclusion, shared-support, and outside-support flows are retained in Supplementary Table S55.",
            "Δ_w uses pooled observed admission-record shares over common score levels. Summary and per-level intervals have separate gates; a point estimate remains when its interval is withheld. Pancreatitis rows use adapted BISAP-4 without pleural effusion; this is not full BISAP. qSOFA for heart failure or COPD is outside intended use.",
            "Zigong groups are unqualified sequence-one and other-sequence records; Diagnosis_seq is not established as principal-diagnosis rank. The Zigong pancreatitis group has 63/47 eligible records but only 14/14 complete records. Full source table: S55.",
        ],
        "t3": [
            "Code-breadth contrasts compare narrow and broad definitions on identical records and common score support. Paired differences are descriptive numerical influence summaries, not causal or instrument-validity tests.",
            "Hospital-by-score and component-pattern refinements use the same records, but splitting pooled record weights changes the target. Hospital-by-score intervals are descriptive because calibration for that refined target is not established; cells with either arm ≤5 are inventoried. Component-pattern agreement does not resolve unmeasured severity.",
            "Full source rows and fields are supplied in Supplementary Table S56.",
        ],
        "t4": [
            "The 24-hour exposure label is never-primary-by-24-hours: it describes diagnosis documentation by the landmark, not disease onset. Main grouping uses full-course documentation.",
            "For each condition, rows compare the full sample with full-course grouping, the same classifiable subset with full-course grouping, and that subset grouped by never-primary-by-24-hours. Withheld intervals are not reconstructed.",
            "The 24-hour hospital-survivor sensitivity is supplied separately in the supplement. Patient-cluster summary intervals use the separately gated audit method.",
        ],
        "t5": [
            "Five selected designs and two sparse-boundary structures are shown. Strategy A off-target interval output is shown explicitly; target support matching distinguishes target-aligned emission from off-target emission.",
            "Coverage is conditional on intervals emitted for the declared support; the denominator n is retained. MCSEs, refusal details, and the full selected A/B/C results are in Supplementary Table S57. Broader simulation results are in S07–S09.",
        ],
        "t6": [
            "Coverage is conditional on intervals emitted for the declared support; the table retains the coverage denominator and Monte Carlo standard error (MCSE).",
            "The concise tool state distinguishes all intervals, a subset, point-only output, and no estimate. Support-match and noncoverage counts are available in S07–S09. These results do not establish universal strategy superiority.",
        ],
    }
    notes_zh = {
        "t1": [
            "各评分层级的 δ_s 为非首位记录观察死亡风险减去首位记录观察死亡风险。记录加权目标将重复住院记录分别计入；患者聚类用于处理依赖性。",
            "表中显示死亡数 / 记录数和风险点估计。† 表示点估计已报告，但评分层级区间未计算；风险区间端点和源状态保留在补充表 S54。δ_s 区间为源文件提供的患者聚类三明治 Wald 区间，并单独接受门槛判定。",
            "合并记录权重表示该评分层级的观察住院记录份额，不是患者份额或外部总体权重。患者数和区间方法等完整字段见补充表 S54。",
        ],
        "t2": [
            "完整记录具有完整评分组件且结局已知。资格、排除、共同支持和支持集外的完整计数流程保留在补充表 S55。",
            "Δ_w 在共同评分层级上使用合并观察住院记录份额加权。汇总区间与层级区间分别接受门槛判定；区间未报告时仍保留点估计。胰腺炎行使用未纳入胸腔积液的改编 BISAP-4，不应视为完整 BISAP；qSOFA 用于心力衰竭或慢性阻塞性肺疾病超出其预期用途。",
            "自贡组为未获资格确认的序号一与其他序号记录；尚未确定 Diagnosis_seq 代表首要诊断排序。自贡胰腺炎组有 63/47 条符合条件记录，但仅有 14/14 条完整记录。完整源表见 S55。",
        ],
        "t3": [
            "代码范围比较在相同记录和共同评分支持集上比较窄、宽定义。配对差值是描述性数值影响摘要，不是因果检验或评分工具效度检验。",
            "医院×评分和组件模式细分使用相同记录，但拆分合并记录权重会改变加权目标。医院×评分区间仅作描述，因为该细分目标的校准性质尚未确立；任一组记录数不超过 5 的单元已列入清单。组件模式一致性不能排除未测量的严重程度差异。",
            "完整源行和字段见补充表 S56。",
        ],
        "t4": [
            "24 小时暴露标签为 never-primary-by-24-hours，表示该时间节点前的诊断记录情况，而非疾病起病时间。主要分组依据全程记录。",
            "每种疾病分别比较全样本全程分组、同一可分类子集的全程分组，以及该子集按 24 小时内是否列为首位分组。未报告的区间不另行重建。",
            "24 小时后仍在院存活者敏感性分析另见补充材料。患者聚类汇总区间采用单独门槛控制的审计方法。",
        ],
        "t5": [
            "表中展示 5 种选定设计和 2 种稀疏边界结构，并明确列出策略 A 偏离目标的区间输出；同时列出目标支持匹配率，以区分目标内和目标外区间。",
            "覆盖率以针对声明支持集发出的区间为条件，本表保留分母 n；MCSE、拒绝报告细节和选定 A/B/C 结果见补充表 S57。更广泛模拟结果见 S07–S09。",
        ],
        "t6": [
            "覆盖率以针对声明支持集发出的区间为条件；表中保留覆盖率分母和蒙特卡洛标准误（MCSE）。",
            "简化工具状态区分全部报告区间、部分报告、仅点估计和无估计。支持匹配和未覆盖计数见 S07–S09。这些结果不能证明某一策略普遍占优。",
        ],
    }

    for key in ("t1", "t2", "t3", "t4", "t5", "t6"):
        headers, _, display_rows = compacted[key]
        en.append(f"## {titles[key][0]}")
        en.append("")
        en_rows = [list(row) for row in display_rows]
        if key == "t1":
            grouped_rows: list[list[str]] = []
            current_group = None
            for row in en_rows:
                if row[0] != current_group:
                    current_group = row[0]
                    grouped_rows.append([f"**{current_group}**"] + [""] * (len(headers) - 1))
                grouped_rows.append([""] + row[1:])
            en_rows = grouped_rows
        elif key == "t2":
            en_rows = [[f"**{cell}**" for cell in row] if "pancreatitis" in row[1].lower() else row for row in en_rows]
        en.append(md_table(headers, en_rows))
        en.append("")
        en.extend(f"- {note}" for note in notes_en[key])
        en.append("")

        zh.append(f"## {titles[key][1]}")
        zh.append("")
        zh_rows: list[list[str]] = []
        for row in display_rows:
            zh_rows.append([translated(value) for value in row])
        if key == "t1":
            grouped_rows_zh: list[list[str]] = []
            current_group_zh = None
            for row in zh_rows:
                if row[0] != current_group_zh:
                    current_group_zh = row[0]
                    grouped_rows_zh.append([f"**{current_group_zh}**"] + [""] * (len(headers_zh[key]) - 1))
                grouped_rows_zh.append([""] + row[1:])
            zh_rows = grouped_rows_zh
        elif key == "t2":
            zh_rows = [[f"**{cell}**" for cell in row] if "胰腺炎" in row[1] else row for row in zh_rows]
        # Use purpose-written, concise Chinese column labels; all values remain source-copied.
        zh.append(md_table(headers_zh[key], zh_rows))
        zh.append("")
        zh.extend(f"- {note}" for note in notes_zh[key])
        zh.append("")
    return "\n".join(en).rstrip() + "\n", "\n".join(zh).rstrip() + "\n"


def index_supplementary(source_supp: Path, stage_supp: Path, archive_dir: Path, original_tables: dict[str, tuple[list[str], list[dict[str, str]]]]) -> dict[str, Any]:
    csv_dir = stage_supp / "Supplementary_tables_CSV"
    source_csv_dir = source_supp / "Supplementary_tables_CSV"
    source_hashes: dict[str, str] = {}
    stage_before: dict[str, str] = {}
    for i in range(1, 54):
        name = f"S{i:02d}.csv"
        src = source_csv_dir / name
        staged = csv_dir / name
        if not src.exists() or not staged.exists():
            raise FileNotFoundError(f"Missing frozen supplement CSV: {src if not src.exists() else staged}")
        source_hashes[name] = sha256(src)
        stage_before[name] = sha256(staged)
        if source_hashes[name] != stage_before[name]:
            raise RuntimeError(f"Stage S{i:02d}.csv differs from RC02 source before transformation")

    titles = {
        "S54.csv": "Full score-level observed mortality risks and δ_s in the four primary analysis groups",
        "S55.csv": "Full database-condition cohort eligibility, complete-score support, and Δ_w summaries",
        "S56.csv": "Full paired code-breadth and refinement comparisons",
        "S57.csv": "Full selected audit-strategy and sparse-boundary interval validation results",
    }
    source_map = {"S54.csv": "t1", "S55.csv": "t2", "S56.csv": "t3", "S57.csv": "t5"}
    archive_dir.mkdir(parents=True, exist_ok=True)
    for dest_name, key in source_map.items():
        src = stage_supp.parent / "02_正文表格" / f"{key}.csv"
        # Use the immutable RC02 input, not the stage file that will be compacted.
        if key not in original_tables:
            raise KeyError(key)
        raw_src = (source_supp.parent / "02_正文表格" / f"{key}.csv").read_bytes()
        target = csv_dir / dest_name
        if target.exists() and target.read_bytes() != raw_src:
            raise RuntimeError(f"Refusing to replace nonmatching existing archive {target}")
        target.write_bytes(raw_src)
        archive_copy = archive_dir / dest_name
        if archive_copy.exists() and archive_copy.read_bytes() != raw_src:
            raise RuntimeError(f"Refusing to replace nonmatching audit archive {archive_copy}")
        archive_copy.write_bytes(raw_src)

    index_path = stage_supp / "supplementary_table_index.csv"
    index_headers, index_rows = read_csv(index_path)
    lookup = {h.lower(): h for h in index_headers}
    number_col = next((lookup[k] for k in ("table", "number", "no.") if k in lookup), index_headers[0])
    title_col = next((lookup[k] for k in ("title", "subject", "quantity or subject") if k in lookup), index_headers[1])
    rows_col = next((lookup[k] for k in ("rows", "records", "data rows") if k in lookup), index_headers[2])
    cols_col = next((lookup[k] for k in ("columns", "fields") if k in lookup), index_headers[3])
    file_col = next((lookup[k] for k in ("csv", "data file", "file") if k in lookup), index_headers[-1])
    existing_numbers = {str(row[number_col]).strip() for row in index_rows}
    for n, name in enumerate(("S54.csv", "S55.csv", "S56.csv", "S57.csv"), start=54):
        if str(n) in existing_numbers:
            continue
        key = source_map[name]
        source_headers, source_rows = original_tables[key]
        index_rows.append({
            number_col: str(n), title_col: titles[name], rows_col: str(len(source_rows)),
            cols_col: str(len(source_headers)), file_col: name,
        })
    write_csv(index_path, index_headers, index_rows)

    # Confirm all original supplementary CSVs remain byte-identical after edits.
    stage_after = {name: sha256(csv_dir / name) for name in source_hashes}
    if stage_after != stage_before or stage_after != source_hashes:
        raise RuntimeError("One or more original S01-S53 CSV files changed")
    return {
        "source_hashes": source_hashes,
        "stage_before_hashes": stage_before,
        "stage_after_hashes": stage_after,
        "new_archives": {
            name: {"sha256": sha256(csv_dir / name), "source_csv": f"02_正文表格/{source_map[name]}.csv"}
            for name in source_map
        },
        "index_rows": len(index_rows),
    }


def pivot_s46(rows: list[dict[str, str]]) -> tuple[str, list[dict[str, Any]]]:
    contrasts = [
        "primary_fixed_minus_broad_fixed",
        "primary_recalibrated_minus_broad_recalibrated",
        "primary_recalibrated_minus_fixed",
        "broad_recalibrated_minus_fixed",
    ]
    point = [r for r in rows if r["Interval"] == "pointwise_95pct"]
    hospital = [r for r in rows if r["Interval"] != "pointwise_95pct"]
    groups: dict[tuple[str, str, str], dict[str, dict[str, str]]] = defaultdict(dict)
    for r in point:
        key = (r["Database"], r["Condition"], r["Test population"])
        if r["Contrast"] in groups[key]:
            raise ValueError(f"Duplicate S46 pointwise contrast for {key}: {r['Contrast']}")
        groups[key][r["Contrast"]] = r
    if len(groups) != 12 or any(set(g) != set(contrasts) for g in groups.values()):
        raise ValueError(f"Unexpected S46 pointwise structure: {len(groups)} groups")
    headers = ["Database", "Condition", "Test population"] + [
        "Primary-only fixed − broad fixed", "Primary-only recalibrated − broad recalibrated",
        "Primary-only recalibrated − fixed", "Broad recalibrated − fixed",
    ]
    output_rows: list[list[str]] = []
    mapping: list[dict[str, Any]] = []
    for group_key in sorted(groups):
        row = list(group_key)
        src_rows = []
        for contrast in contrasts:
            r = groups[group_key][contrast]
            row.append(f"{r['Brier loss difference']} [{r['95% CI lower']}, {r['95% CI upper']}]")
            src_rows.append(int(r["__source_row"]))
        output_rows.append(row)
        mapping.append({"output_row": len(mapping) + 1, "section": "pointwise", "source_rows": src_rows})
    hospital_headers = ["Database", "Condition", "Test population", "Contrast", "Brier loss difference [95% CI]"]
    hospital_rows: list[list[str]] = []
    for r in hospital:
        hospital_rows.append([
            r["Database"], r["Condition"], r["Test population"], r["Contrast"],
            f"{r['Brier loss difference']} [{r['95% CI lower']}, {r['95% CI upper']}]"
        ])
        mapping.append({"output_row": len(mapping) + 1, "section": "hospital_cluster", "source_rows": [int(r["__source_row"])]})
    if len(hospital) != 8:
        raise ValueError(f"Expected 8 S46 hospital-cluster rows, found {len(hospital)}")
    md = [
        "## Supplementary Table 46. Held-out Brier-loss differences",
        "",
        "Prediction-loss differences are not score-level δ_s or the record-weighted summary Δ_w. Values are copied as source estimates with their pointwise 95% confidence intervals.",
        "",
        md_table(headers, output_rows),
        "",
        "### Hospital-cluster pointwise intervals (eight source contrasts)",
        "",
        md_table(hospital_headers, hospital_rows),
        "",
    ]
    return "\n".join(md), mapping


def pivot_s47(rows: list[dict[str, str]]) -> tuple[str, list[dict[str, Any]]]:
    mappings = ["primary_only_fixed", "broad_fixed", "primary_only_recalibrated", "broad_recalibrated"]
    groups: dict[tuple[str, str, str], dict[str, dict[str, str]]] = defaultdict(dict)
    for r in rows:
        key = (r["Database"], r["Condition"], r["Test population"])
        groups[key][r["Mapping"]] = r
    if len(groups) != 12 or any(set(g) != set(mappings) for g in groups.values()):
        raise ValueError(f"Unexpected S47 structure: {len(groups)} groups")
    headers = [
        "Database", "Condition", "Test population", "n", "Observed risk (%)",
        "Primary-only fixed (mean prediction; Brier; intercept/slope)",
        "Broad fixed (mean prediction; Brier; intercept/slope)",
        "Primary-only recalibrated (mean prediction; Brier; intercept/slope)",
        "Broad recalibrated (mean prediction; Brier; intercept/slope)",
    ]
    output: list[list[str]] = []
    mapping: list[dict[str, Any]] = []
    for key in sorted(groups):
        group = groups[key]
        anchor = group[mappings[0]]
        for name in mappings[1:]:
            other = group[name]
            if other["Records"] != anchor["Records"] or other["Observed risk (%)"] != anchor["Observed risk (%)"]:
                raise ValueError(f"S47 common observed-risk fields differ for {key}")
        row = list(key) + [anchor["Records"], anchor["Observed risk (%)"]]
        src_rows = []
        for name in mappings:
            r = group[name]
            row.append("; ".join([
                r["Mean predicted risk (%)"], r["Brier loss"],
                f"{r['Calibration intercept']}/{r['Calibration slope']}",
            ]))
            src_rows.append(int(r["__source_row"]))
        output.append(row)
        mapping.append({"output_row": len(mapping) + 1, "source_rows": src_rows})
    md = [
        "## Supplementary Table 47. Held-out risks and prediction summaries across four mappings",
        "",
        "Each mapping cell reports mean predicted risk (%), Brier loss, and calibration intercept/slope. Observed risk is shared across mappings within each test population. These prediction quantities are not δ_s or Δ_w.",
        "",
        md_table(headers, output),
        "",
    ]
    return "\n".join(md), mapping


def pivot_s48(rows: list[dict[str, str]]) -> tuple[str, list[dict[str, Any]]]:
    roles = ["train", "recalibration", "test"]
    groups: dict[tuple[str, str, str], dict[str, dict[str, str]]] = defaultdict(dict)
    for r in rows:
        key = (r["Database"], r["Condition"], r["Diagnosis group"])
        groups[key][r["Role"]] = r
    if len(groups) != 12 or any(set(g) != set(roles) for g in groups.values()):
        raise ValueError(f"Unexpected S48 structure: {len(groups)} diagnosis groups")
    headers = ["Database", "Condition", "Diagnosis group", "Train flow", "Recalibration flow", "Test flow"]
    output: list[list[str]] = []
    mapping: list[dict[str, Any]] = []
    for key in sorted(groups):
        group = groups[key]
        row = list(key)
        src_rows = []
        for role in roles:
            r = group[role]
            row.append(
                f"{r['Panel records']} → {r['Known group and outcome']} → {r['Complete scores']}; "
                f"{r['Patients']} patients, {r['Events']} events, {r['Hospitals']} hospitals"
            )
            src_rows.append(int(r["__source_row"]))
        output.append(row)
        mapping.append({"output_row": len(mapping) + 1, "source_rows": src_rows})
    md = [
        "## Supplementary Table 48. Cohort flow by diagnosis group and data role",
        "",
        "Within each role, the flow is panel records → known group and outcome → complete scores, followed by patients, events, and hospitals. Zero hospitals for MIMIC are retained from the source.",
        "",
        md_table(headers, output),
        "",
    ]
    return "\n".join(md), mapping


def render_supplementary(source_supp: Path, stage_supp: Path) -> tuple[str, str, dict[str, Any]]:
    index_headers, index_rows = read_csv(stage_supp / "supplementary_table_index.csv")
    lookup = {h.lower(): h for h in index_headers}
    number_col = next((lookup[k] for k in ("table", "number", "no.") if k in lookup), index_headers[0])
    title_col = next((lookup[k] for k in ("title", "subject", "quantity or subject") if k in lookup), index_headers[1])
    rows_col = next((lookup[k] for k in ("rows", "records", "data rows") if k in lookup), index_headers[2])
    cols_col = next((lookup[k] for k in ("columns", "fields") if k in lookup), index_headers[3])
    file_col = next((lookup[k] for k in ("csv", "data file", "file") if k in lookup), index_headers[-1])
    if len(index_rows) != 57:
        raise ValueError(f"Expected 57 indexed supplementary tables, found {len(index_rows)}")
    csv_dir = stage_supp / "Supplementary_tables_CSV"
    s46 = read_csv(csv_dir / "S46.csv")[1]
    s47 = read_csv(csv_dir / "S47.csv")[1]
    s48 = read_csv(csv_dir / "S48.csv")[1]
    section46, map46 = pivot_s46(s46)
    section47, map47 = pivot_s47(s47)
    section48, map48 = pivot_s48(s48)
    full_tables = (source_supp / "supplementary_tables.md").read_text(encoding="utf-8-sig").rstrip()
    archive_specs = [
        (54, "t1", "Full score-level observed mortality risks and δ_s in the four primary analysis groups"),
        (55, "t2", "Full database-condition cohort eligibility, complete-score support, and Δ_w summaries"),
        (56, "t3", "Full paired code-breadth and refinement comparisons"),
        (57, "t5", "Full selected audit-strategy and sparse-boundary interval results"),
    ]
    full_tables_parts = [full_tables]
    for table_number, key, title in archive_specs:
        headers, source_rows = read_csv(source_supp.parent / "02_正文表格" / f"{key}.csv")
        raw_rows = [[r[h] for h in headers] for r in source_rows]
        full_tables_parts.extend([
            f"## Supplementary Table {table_number}. {title}", "",
            md_table(headers, raw_rows), "",
            f"Complete row-level data are also supplied in S{table_number}.csv.", "",
        ])
    full_tables = "\n".join(full_tables_parts).rstrip() + "\n"
    results = [
        "# Supplementary results", "",
        "Full row-level admission pathways and diagnosis counts are available in S52.csv and S53.csv; their long listings are not repeated in this reader. Detailed score-level, cohort-flow, paired-refinement, and selected strategy results are supplied in S54–S57. The displays below compactly align selected source rows.", "",
        section46, section47, section48,
    ]
    map_info = {
        "S46": {"source_csv": "S46.csv", "source_data_rows": len(s46), "output_rows": map46},
        "S47": {"source_csv": "S47.csv", "source_data_rows": len(s47), "output_rows": map47},
        "S48": {"source_csv": "S48.csv", "source_data_rows": len(s48), "output_rows": map48},
    }
    return full_tables, "\n".join(results).rstrip() + "\n", map_info


def run(source: Path, dest: Path, audit_out: Path | None) -> dict[str, Any]:
    source = source.resolve()
    dest = dest.resolve()
    source_tables_dir = source / "02_正文表格"
    source_supp = source / "04_补充文件"
    dest_tables_dir = dest / "02_正文表格"
    dest_supp = dest / "04_补充文件"
    if not source_tables_dir.exists() or not dest_tables_dir.exists():
        raise FileNotFoundError("Expected RC02 and staged editor roots with 02_正文表格 folders")
    original_tables: dict[str, tuple[list[str], list[dict[str, str]]]] = {}
    compacted: dict[str, tuple[list[str], list[dict[str, str]], list[list[str]]]] = {}
    source_hashes: dict[str, str] = {}
    row_mappings: dict[str, list[dict[str, Any]]] = {}
    funcs = {"t1": compact_t1, "t2": compact_t2, "t3": compact_t3, "t4": compact_t4, "t5": compact_t5, "t6": compact_t6}

    # Read every source CSV before writing any stage CSV.
    for key in funcs:
        source_path = source_tables_dir / f"{key}.csv"
        stage_path = dest_tables_dir / f"{key}.csv"
        if not source_path.exists() or not stage_path.exists():
            raise FileNotFoundError(f"Missing source/stage table: {source_path} / {stage_path}")
        sh = sha256(source_path)
        source_hashes[f"main/{key}.csv"] = sh
        original_tables[key] = read_csv(source_path)
        compacted[key] = funcs[key](original_tables[key][1])
        staged_hash = sha256(stage_path)
        if staged_hash != sh:
            staged_headers, _ = read_csv(stage_path)
            if staged_headers != compacted[key][0]:
                raise RuntimeError(f"Staged {key}.csv is neither the RC02 source nor this script's compact display")
        row_mappings[key] = [
            {
                "output_row": idx,
                "source_csv": f"02_正文表格/{key}.csv",
                "source_data_rows": [int(x) for x in str(row.get("__source_rows", row.get("__source_row", ""))).split(",") if x],
                "source_data_row_index": idx,
            }
            for idx, row in enumerate(compacted[key][1], start=1)
        ]

    archive_dir = (audit_out.parent / "full_source_tables" if audit_out else dest.parent / "audit" / "full_source_tables")
    supp_integrity = index_supplementary(source_supp, dest_supp, archive_dir, original_tables)

    # Write compact display CSVs only after source S54-S57 archives exist.
    for key, (headers, rows, _) in compacted.items():
        write_csv(dest_tables_dir / f"{key}.csv", headers, rows)
    en, zh = render_main_tables({k: v[1] for k, v in original_tables.items()}, compacted)
    (dest_tables_dir / "tables_JIC.md").write_text(en, encoding="utf-8")
    (dest_tables_dir / "tables_JIC_中文.md").write_text(zh, encoding="utf-8")

    supp_index, supp_results, supp_maps = render_supplementary(source_supp, dest_supp)
    (dest_supp / "supplementary_tables.md").write_text(supp_index, encoding="utf-8")
    (dest_supp / "supplementary_results.md").write_text(supp_results, encoding="utf-8")
    row_mappings.update({"supplementary_pivots": supp_maps})

    outputs = [
        dest_tables_dir / f"{key}.csv" for key in funcs
    ] + [
        dest_tables_dir / "tables_JIC.md", dest_tables_dir / "tables_JIC_中文.md",
        dest_supp / "supplementary_tables.md", dest_supp / "supplementary_results.md",
        dest_supp / "supplementary_table_index.csv",
    ] + [dest_supp / "Supplementary_tables_CSV" / f"S{i:02d}.csv" for i in range(1, 58)]
    audit = {
        "purpose": "display-only compaction; no analysis or estimate recomputation",
        "source_root": str(source),
        "destination_root": str(dest),
        "source_main_csv_sha256": source_hashes,
        "supplementary_original_csv_integrity": {
            "count": 53,
            "source_rc02_sha256": supp_integrity["source_hashes"],
            "staged_before_sha256": supp_integrity["stage_before_hashes"],
            "staged_after_sha256": supp_integrity["stage_after_hashes"],
            "all_unchanged_and_equal_to_source": True,
        },
        "full_source_archives_S54_S57": supp_integrity["new_archives"],
        "supplementary_index_rows": supp_integrity["index_rows"],
        "main_display_row_counts": {k: len(v[1]) for k, v in compacted.items()},
        "row_mappings": row_mappings,
        "output_sha256": {str(p.relative_to(dest)): sha256(p) for p in outputs},
    }
    if audit_out is None:
        audit_out = dest.parent / "audit" / "display_transform_audit.json"
    audit_out.parent.mkdir(parents=True, exist_ok=True)
    audit_out.write_text(json.dumps(audit, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": "complete",
        "destination_root": str(dest),
        "audit_json": str(audit_out),
        "main_display_row_counts": audit["main_display_row_counts"],
        "supplementary_original_csvs_unchanged": True,
        "supplementary_index_rows": supp_integrity["index_rows"],
    }, ensure_ascii=False))
    return audit


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True, help="Immutable RC02 root")
    parser.add_argument("--dest", type=Path, required=True, help="Staged editor root to update")
    parser.add_argument("--audit-out", type=Path, help="Audit JSON output path")
    args = parser.parse_args()
    run(args.source, args.dest, args.audit_out)


if __name__ == "__main__":
    main()
