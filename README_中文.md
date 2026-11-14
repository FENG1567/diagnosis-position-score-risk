# 诊断位置与评分隐含死亡风险：复现包

本仓库配套研究为 **“Diagnosis Position and Cohort-Dependent Interpretation of Score-Stratified Mortality: A Four-Database Audit Across Five Acute-Care Conditions, Including Acute Pancreatitis”**，当前稿件面向 *Journal of Intensive Care*。仓库：https://github.com/FENG1567/diagnosis-position-score-risk；公开版本 v1.0.0。尚未取得文章 DOI。

## 本仓库可以复现什么

公开复现包使用随附的作者自有、冻结汇总数据，可校验文件哈希，重建 6 张主表和 57 张补充表，重画 2 张正文图及补充图 S1，并运行软件测试和合成数据演示。仓库不含患者级记录、临床文本、原始数据库文件或私有缓存。因此，重建汇总表格不等于独立重做患者级分析，也不会根据原始记录重新计算置信区间。

主要比较是在 eICU 与 MIMIC-IV 中，考察脓毒症和肺炎在不同诊断位置下、按评分分层的死亡风险。δ_s 表示特定评分层中未经回归模型调整的观察风险差，不是回归模型估计值；Δ_w 表示按记录加权的汇总值。研究为观察性分析。Zigong 诊断分组字段的语义尚未充分确认，因此不应直接解释为与主分析相同的主要/次要诊断分组；BISAP-4 也不等同于 BISAP。

## 环境与运行命令

使用 Python 3.12，并在仓库根目录安装固定版本依赖：

    python -m venv .venv
    # 使用当前 shell 激活环境后运行：
    python -m pip install -r requirements.txt

在仓库根目录运行所需步骤：

    python reproduce.py verify
    python reproduce.py tables
    python reproduce.py figures
    python reproduce.py test
    python reproduce.py synthetic
    python reproduce.py all

- verify 校验 MANIFEST.sha256 并检查表格文件数量。
- tables 根据冻结汇总输入重建表格，并逐单元格与随附 CSV 比对。
- figures 重建 2 张主图及补充图 S1（PDF、TIFF、PNG、SVG），核对图 1 和图 2 的科学数据值。已发表版式使用 Arial 粗体；重建时若无 Arial，则使用 Liberation Sans 或 DejaVu Sans，因此外观和文件字节可能不同。字体文件不再分发。
- test 运行随附软件测试。
- synthetic 生成明确标注的人工合成数据并演示审计流程，不代表临床证据。
- all 依次运行校验、表格、图和测试；不包含合成数据演示。

新生成文件写入 _generated/。上述命令只使用复现包内文件，不会下载数据或连接外部数据库。

## 目录说明

- results/main_tables/：6 张主表 CSV（t1.csv–t6.csv）。
- results/supplementary_tables/：57 张补充表 CSV（S01.csv–S57.csv）。
- results/figures/：2 张正文图及补充图 S1，共 3 张图、每图 4 种格式。
- outputs/v2/、outputs/v3/validation/、outputs/v4/composition/：本审计使用的作者自有冻结汇总输入。
- provenance/：哈希、来源到表格单元格的链接，以及补充表新旧编号索引。
- docs/supplementary_methods.md：补充分析方法。
- work/v2/、work/v3/validation/、work/v4/、work/v5/：分析、验证、表图生成和呈现脚本。

## 受限源数据重跑

有权访问底层数据库的研究者，可参阅 [docs/PRIVATE_REANALYSIS.md](docs/PRIVATE_REANALYSIS.md)，了解相关模块入口、实际命令参数和路径配置。患者级临床分析没有一个命令可以全部从头重跑。请从数据提供方获取数据，并遵循其当前访问条件：

- [eICU Collaborative Research Database](https://physionet.org/content/eicu-crd/)
- [MIMIC-IV](https://physionet.org/content/mimiciv/)
- [MIMIC-III](https://physionet.org/content/mimiciii/)
- [Zigong ICU Infection Database，1.1 版](https://physionet.org/content/icu-infection-zigong-fourth/1.1/)
- [AmsterdamUMCdb](https://amsterdammedicaldatascience.nl/)

仓库不会分发原始数据库、患者级提取记录、缓存或临床文本；以下许可证不涵盖这些资料。

## 许可

作者自编代码按 MIT License 发布；作者自有的汇总数据和文档按 CC BY 4.0 发布。第三方 SQL 和字典 保留其自身许可证，不由本仓库重新授权。上述许可证不授予受限源数据库的访问权，也不覆盖患者级数据、缓存或临床文本。

## 引用与联系

引用元数据见 [CITATION.cff](CITATION.cff)。通信作者：Liwei Liu（刘立伟），邮箱：18940835066@163.com。



当前补充表编号与 2026-11-15 正文一致；57 张补充表经重编号后逐字节保留。新旧编号对应见 provenance/manuscript_supplement_mapping.json。旧来源表和历史脚本仍保留原编号，使用时应参照对应表。图 2 数据来自当前补充表 S25（旧 S46）。当前绘图入口为 work/publication_v12/build_figures.py。
