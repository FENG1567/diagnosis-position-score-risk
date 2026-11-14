"""Revision figure contract: unchanged observed curves; clarify policy semantics."""
from pathlib import Path
import importlib.util,json,shutil,hashlib
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'outputs/v4/delivery/figures';OUT.mkdir(parents=True,exist_ok=True)
original=ROOT/'work/v2/figures/build_jce_figures.py'
code=original.read_text(encoding='utf-8')
code=code.replace('"Admission records are clustered by patient."','"Policy states, not universal inferential limits. Records clustered by patient."')
code=code.replace('"Point estimate only", "No interval\\nLost target support','"Point estimate only", "Policy withholds CI\\nLost target support')
code=code.replace('"Estimable", "Point estimate and 95% interval','"Estimable under policy", "Point estimate and 95% interval')
adapted=ROOT/'work/v4/figures_adapted.py';adapted.write_text(code,encoding='utf-8')
spec=importlib.util.spec_from_file_location('v4_figures',adapted);mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
mod.ROOT=ROOT;mod.OUT=OUT;mod.WORK=ROOT/'work/v4'
fig2=mod.render_figure2()
for name in ['fig1_score_specific_risk.pdf','fig1_score_specific_risk.png','fig1_score_specific_risk.svg','fig1_score_specific_risk_source.csv']:
    shutil.copy2(ROOT/'outputs/v2/delivery/figures'/name,OUT/name)
caption=(ROOT/'outputs/v2/delivery/figures/figure_captions.md').read_text(encoding='utf-8')
caption=caption.replace('The record-weighted summary `Δ_w` appears in Table 2.','The record-weighted summary `Δ_w` appears in Table 2. Scores are operational reconstructions, not simultaneous baseline severity assessments.')
caption=caption.replace('**Figure 2 | Reportability flow','**Figure 2 | Operational reportability flow')
caption=caption.replace('Arrows describe the software decision sequence.','Arrows describe the software decision sequence. These policy states do not establish general statistical impossibility, universal interval validity or superiority over simpler rules. The reported primary intervals use a normal influence-function approximation; the bootstrap is an additional policy gate, not the calculation of those primary intervals.')
(OUT/'figure_captions.md').write_text(caption,encoding='utf-8')
record=dict(backend='python',archetype=['quantitative grid','process diagram'],figure1='exact reuse: unchanged primary data, estimates and interval states',figure2='exact policy retained, interpretive labels clarified',main_figures=2,figure2_metadata=fig2,outputs=[dict(file=p.name,sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for p in OUT.iterdir() if p.is_file()])
(OUT/'figure_manifest_v4.json').write_text(json.dumps(record,indent=2,ensure_ascii=False),encoding='utf-8')
print(json.dumps(dict(output=str(OUT),figures=2)))
