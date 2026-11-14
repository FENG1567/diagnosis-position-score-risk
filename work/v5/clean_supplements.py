from pathlib import Path
import re,csv,json,html
B=Path('/tmp/jic_v5_20261114');I=B/'input';O=B/'output';D=O/'supplementary_data';D.mkdir(exist_ok=True)
old=(I/'supplementary_tables_original.md').read_text(encoding='utf-8-sig')
new=(I/'supplementary_results_addendum.md').read_text(encoding='utf-8-sig')
blocks={int(re.search(r'Supplementary Table (\d+)',p)[1]):p.strip() for p in re.split(r'(?=^## Supplementary Table \d+)',old+'\n\n'+new,flags=re.M) if p.startswith('## Supplementary Table')}
keep=list(range(1,10))+list(range(18,24))+list(range(25,48))+[50,53,54,62,64,65,66]+list(range(67,75))
titles={18:'Amsterdam weighted summary Δ_w by GCS definition and interval method',19:'Amsterdam score-level δ_s for GCS ≤13',20:'Amsterdam score-level δ_s for GCS <15',21:'Amsterdam observed mortality by reconstructed qSOFA',22:'Patient-cluster bootstrap precision analyses',23:'Weighted-summary interval refusals by reporting policy',25:'Conditional-design θ_D intervals in clinical applications',26:'Conditional-design interval simulation results',27:'ED-linked cohort component completeness',28:'ED-linked cohort weighted summaries Δ_w',29:'Linked ED episode counts',30:'ED linkage eligibility',31:'ED-linked score-level risks and δ_s',32:'ED linkage coverage',33:'eICU diagnosis-group counts',34:'eICU reconstructed score availability',35:'Score-level simultaneous coverage diagnostics',36:'Score-level interval validation by design and method',37:'Score-level interval precision sensitivity',38:'Score-level interval refusal frequencies',39:'Score-level coverage sensitivity to rounding',40:'Score-level δ_s validation results',41:'Patient and hospital clustering sensitivity for weighted summary Δ_w',42:'Matched-record score-construction contrasts',43:'Measurement eligibility and selection counts',44:'Bonferroni score-level δ_s intervals',45:'Bonferroni interval-emission summary',46:'Counts by score and diagnosis group',47:'Score-construction weighted summaries Δ_w',50:'MIMIC-IV reconstructed score coverage',53:'MIMIC-III reconstructed score coverage',54:'Adapted PEER-cohort weighted summary Δ_w',62:'Zigong documented discharge-status combinations',64:'Zigong discharge status and follow-up death timing',65:'Zigong laboratory measurement units',66:'Zigong field-group score and outcome availability'}
mapping={k:i+1 for i,k in enumerate(keep)};records=[];cleanblocks=[];show=[]
def cells(l):return [x.strip().replace('\\|','|') for x in re.split(r'(?<!\\)\|',l.strip())[1:-1]]
def render(headers,rows):
    esc=lambda s:s.replace('|','\\|')
    return '| '+' | '.join(map(esc,headers))+' |\n| '+' | '.join(['---']*len(headers))+' |\n'+'\n'.join('| '+' | '.join(map(esc,row))+' |' for row in rows)
for k in keep:
    b=blocks[k];lines=b.splitlines();tab=[l for l in lines if l.startswith('|')];headers=cells(tab[0]);rows=[cells(l) for l in tab[2:]]
    assert all(len(r)==len(headers) for r in rows),(k,len(headers),[len(r) for r in rows])
    title=titles.get(k,re.sub(r'^## Supplementary Table \d+\.\s*','',lines[0]))
    title=title.replace('Full confirmatory','Full simulation').replace('Paired confirmatory','Paired simulation')
    if k==18:
        mid=headers.index('measurement_version');rows=[r for r in rows if r[mid]=='dictionary_unit_repair']
    # Keep scientific data; omit filesystem, version-label and build/check columns.
    omit=[j for j,h in enumerate(headers) if h in {'measurement_version','canonical_for_root_tables','source_path','source_file','source_csv','input_path','input_file','output_path','config_path','run_id'} or h.lower().endswith('_sha256') or h.lower().endswith('_md5')]
    headers=[h for j,h in enumerate(headers) if j not in omit]
    rows=[[v for j,v in enumerate(r) if j not in omit] for r in rows]
    if k==1:
        headers=[h.replace('primary / never-primary','sequence-one / other-sequence') for h in headers]
    if k in [1,66]:
        title+='; diagnosis-sequence semantics unverified'
    # Workflow paths and strategy-version tags are presentation metadata, not outcomes.
    def clean(v):
        v=re.sub(r'outputs/v\d+/[^\s;]+','',v)
        v=v.replace('dictionary_unit_repair','dictionary-specified units').replace('gcs_le_13','GCS ≤13').replace('gcs_lt_15_sensitivity','GCS <15')
        v=v.replace('v2 audit','audit').replace('v2_', '').replace('_v2','')
        return v
    rows=[[clean(v) for v in r] for r in rows]
    n=mapping[k];file=f'S{n:02d}.csv'
    with (D/file).open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.writer(f);w.writerow(headers);w.writerows(rows)
    note=''
    if '**Notes.**' in b:
        note=b.split('**Notes.**',1)[1]
        note=re.sub(r'^- Aggregate source table copied without recomputing estimates\.\s*','',note,flags=re.M)
        note=note.replace('This cell is supplemental and does not change the original 19-cell Table 2 contract.','This cell is supplementary to the 19 source-condition cells in Table 2.')
        note=re.sub(r'\n- Stagewise comparisons.*?(?=\n|$)','',note)
    for orig,newnum in sorted(mapping.items(),reverse=True):
        note=re.sub(r'(Supplementary Table )'+str(orig)+r'\b',lambda m:m[1]+str(newnum),note)
    cleanb=f'## Supplementary Table {n}. {title}\n\n'+render(headers,rows)
    if note.strip():cleanb+='\n\n**Notes.**\n\n'+note.strip()
    cleanblocks.append(cleanb)
    if k>=67:show.append(cleanb)
    records.append({'old_number':k,'number':n,'title':title,'csv':file,'rows':len(rows),'columns':len(headers)})
intro='# Supplementary results\n\nThe numbered supplementary tables are supplied as CSV files, with complete tables in supplementary_tables.md. Selected tables on held-out prediction and simulation design are reproduced below. Prediction-loss differences are neither score-level δ_s nor the record-weighted summary Δ_w. All Zigong groups are unqualified sequence-one and other-sequence field groups; they do not establish a principal-diagnosis association.\n\n'
index='## Supplementary table index\n\n'+render(['Table','Quantity or subject','Records in table','Data file'],[[str(r['number']),r['title'],str(r['rows']),r['csv']] for r in records])
(O/'supplementary_results.md').write_text(intro+index+'\n\n'+'\n\n'.join(show)+'\n',encoding='utf-8')
(O/'supplementary_tables.md').write_text('# Supplementary tables\n\nAll Zigong primary/never-primary labels denote unqualified sequence-one/other-sequence field groups. Δ_w denotes a weighted summary; patient clustering does not change the record-weighted target.\n\n'+'\n\n'.join(cleanblocks)+'\n',encoding='utf-8')
m=(I/'supplementary_methods.md').read_text(encoding='utf-8-sig')
m=m.replace('Supplementary Table 71',f'Supplementary Table {mapping[71]}').replace('Supplementary Tables 67–70',f'Supplementary Tables {mapping[67]}–{mapping[70]}')
repl={
'eleven locked weighted-summary designs':'eleven weighted-summary simulation designs',
'The original aggregate results had been inspected before the revision. Configurations for individual extensions were locked before their runs, which is not prospective preregistration of the overall study. No additional simulations were run merely to improve the reported coverage.':'Aggregate outcomes had been inspected before the exploratory extensions. Configurations were specified before their respective runs, but the overall study was not prospectively preregistered.',
'Multiple imputation under an unsupported missing-at-random assumption was not added to manufacture robustness. ':'',
'(dictionary physical CSV row 122)':'',
'A frozen extract of the diagnosis dictionary accompanies the aggregate supplement. We did not contact the data owners or assume a definition from the column name.':'The field was not interpreted as principal-diagnosis rank from its name alone.',
'The corrected discharge-status outcome':'The discharge-status outcome',
'Qualification is still unresolved; its effect on the manuscript was addressed by restricting the interpretation.':'Its principal-diagnosis semantics remain unresolved.',
' Credentialed source files were not downloaded through an unapproved access route.':'',
'The added composition tables retain exactly the four main complete-component, known-outcome analysis populations. Group sizes are checked against frozen main tables before producing output. No replacement cohort, new diagnosis definition or new admission index is introduced.':'The composition tables describe the same four complete-component, known-outcome populations as the main analysis.',
'original supplementary aggregates':'supplementary tables',
'The original-population sparse-inference extension stopped without a defensible ex ante contribution bound; no new finite-sample population guarantee is claimed.':'A finite-sample population guarantee would require an a priori bound on patient-cluster contributions, which was unavailable for this population target.',
}
for a,b in repl.items():
    if a not in m:raise ValueError(a)
    m=m.replace(a,b)
(O/'supplementary_methods.md').write_text(m,encoding='utf-8')
(O/'supplementary_data_index.json').write_text(json.dumps({'tables':records,'excluded_internal_or_redundant_tables':[k for k in blocks if k not in keep],'no_reanalysis':True},ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'completed':True,'data_tables':len(records),'display_tables':len(show)+1,'max_data_columns':max(r['columns'] for r in records),'old_to_new':mapping}),flush=True)
