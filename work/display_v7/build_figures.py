"""Display-only publication figures from released aggregate rows; no model fitting.

Figure contracts: F1 shows observed within-score risks, differences and support;
F2 shows conditional held-out Brier-loss trade-offs across test populations;
S1 shows the audit policy's distinct point/interval reporting states.
All inferential numbers and missing intervals are retained from source tables.
"""
from pathlib import Path
import argparse, hashlib, json, shutil
import numpy as np
import pandas as pd
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import FancyBboxPatch
from matplotlib.ticker import MaxNLocator, FuncFormatter

mpl.rcParams.update({'font.family':'sans-serif','font.sans-serif':['Liberation Sans','DejaVu Sans'],
 'font.size':8,'axes.labelsize':8,'axes.titlesize':9,'xtick.labelsize':7.5,'ytick.labelsize':7.5,
 'legend.fontsize':8,'pdf.fonttype':42,'svg.fonttype':'none','axes.spines.top':False,
 'axes.spines.right':False,'axes.linewidth':.65,'legend.frameon':False,'savefig.dpi':300})
BLUE='#267599';ORANGE='#BD7133';INK='#273542';GRAY='#E8EBEE'

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def export(fig,out,stem,w,h):
    fig.set_size_inches(w/25.4,h/25.4)
    fig.savefig(out/(stem+'.pdf'),facecolor='white')
    fig.savefig(out/(stem+'.svg'),facecolor='white')
    fig.savefig(out/(stem+'.png'),facecolor='white',dpi=300)
    fig.savefig(out/(stem+'.tiff'),facecolor='white',dpi=600,pil_kwargs={'compression':'tiff_lzw'})
    plt.close(fig)

def fig1(src,out):
    df=pd.read_csv(src);assert len(df)==20
    fig=plt.figure();outer=fig.add_gridspec(2,2,left=.105,right=.985,top=.89,bottom=.125,wspace=.29,hspace=.35)
    cells=[('eICU-CRD','sepsis'),('eICU-CRD','pneumonia'),('MIMIC-IV','sepsis'),('MIMIC-IV','pneumonia')]
    for k,(db,disease) in enumerate(cells):
        p=df[(df.database==db)&(df.disease==disease)].sort_values('level');x=p.level.to_numpy()
        grid=outer[k//2,k%2].subgridspec(3,1,height_ratios=[3.2,1.65,1],hspace=.16)
        ar=fig.add_subplot(grid[0]);ad=fig.add_subplot(grid[1],sharex=ar);an=fig.add_subplot(grid[2],sharex=ar)
        for ax in [ar,ad,an]:
            ax.set_xlim(x.min()-.45,x.max()+.45);ax.set_xticks(x);ax.tick_params(width=.6,length=2)
        for r in p.itertuples():
            if r.delta_ci_status=='computed' and r.delta_ci_pp_lo<=0<=r.delta_ci_pp_hi:
                for ax in [ar,ad]:ax.axvspan(r.level-.4,r.level+.4,color='#F3F4F5',zorder=0)
        for group,color,marker,offset in [('never',BLUE,'o',-.045),('primary',ORANGE,'s',.045)]:
            ar.plot(x+offset,p['risk_'+group],color=color,lw=1,zorder=2)
            for _,r in p.iterrows():
                y=r['risk_'+group];xx=r.level+offset;computed=r['risk_'+group+'_ci_status']=='computed'
                if computed:
                    lo=r['risk_'+group+'_ci_pp_lo'];hi=r['risk_'+group+'_ci_pp_hi']
                    ar.errorbar(xx,y,yerr=[[max(0,y-lo)],[max(0,hi-y)]],fmt='none',ecolor=color,elinewidth=.75,capsize=2,zorder=3)
                ar.scatter(xx,y,s=21,marker=marker if computed else 'D',facecolor=color if computed else 'white',edgecolor=color,lw=.85,zorder=4,clip_on=False)
        ar.set_ylim(-1.8,50);ar.set_yticks([0,20,40]);ar.set_ylabel('Mortality (%)');ar.tick_params(labelbottom=False)
        ar.set_title(db+'  |  '+disease.capitalize(),loc='left',pad=5)
        ar.text(-.19,1.05,'abcd'[k],transform=ar.transAxes,fontweight='bold',fontsize=10)
        ad.axhline(0,color='#89929B',lw=.7,ls=(0,(3,2)))
        ad.plot(x,p.diff_pp,color=INK,lw=.8)
        for r in p.itertuples():
            comp=r.delta_ci_status=='computed';zero=comp and r.delta_ci_pp_lo<=0<=r.delta_ci_pp_hi
            if comp:ad.errorbar(r.level,r.diff_pp,yerr=[[max(0,r.diff_pp-r.delta_ci_pp_lo)],[max(0,r.delta_ci_pp_hi-r.diff_pp)]],fmt='none',ecolor=INK,elinewidth=.8,capsize=2)
            ad.scatter(r.level,r.diff_pp,s=22,marker='o' if comp else 'D',facecolor='white' if zero or not comp else INK,edgecolor=INK,lw=.8,zorder=4)
        ad.set_ylim(-12,40);ad.set_yticks([0,20,40]);ad.set_ylabel(r'$\delta_s$ (pp)');ad.tick_params(labelbottom=False)
        an.bar(x,p.n_never,.6,color=BLUE);an.bar(x,p.n_primary,.6,bottom=p.n_never,color=ORANGE)
        an.yaxis.set_major_locator(MaxNLocator(2,integer=True));an.yaxis.set_major_formatter(FuncFormatter(lambda v,_:f'{v/1000:g}k' if v>=1000 else f'{v:g}'))
        an.set_ylim(0,p.n.max()*1.12);an.set_ylabel('Records');an.set_xlabel('qSOFA' if disease=='sepsis' else 'CURB-65')
    handles=[Line2D([],[],color=BLUE,marker='o',ms=4,label='Never-primary'),Line2D([],[],color=ORANGE,marker='s',ms=4,label='Primary'),
       Line2D([],[],color=INK,marker='o',mfc='white',ls='none',ms=4,label=r'$\delta_s$ CI contains zero'),
       Line2D([],[],color=INK,marker='D',mfc='white',ls='none',ms=4,label='Point only; no CI')]
    fig.legend(handles=handles,loc='upper center',bbox_to_anchor=(.52,.98),ncol=2,columnspacing=2.2,handlelength=1.6)
    fig.text(.105,.027,'Pointwise 95% intervals where issued. Shaded scores have a '+r'$\delta_s$'+' interval containing zero.\nPneumonia score 0: primary deaths / records = 0/17 (eICU), 0/13 (MIMIC-IV).',fontsize=7.5,linespacing=1.3)
    export(fig,out,'fig1_score_specific_risk',170,170)
    shutil.copy2(src,out/'fig1_score_specific_risk_source.csv')
    return {'figure':'Figure 1','source':src.name,'sha256':sha(src),'rows':20,'quantity':'observed risks and score-specific delta_s; not weighted summary','size_mm':[170,170]}

def fig2(src,out):
    df=pd.read_csv(src);df['_source_row']=np.arange(2,len(df)+2)
    contrasts=['primary_fixed_minus_broad_fixed','primary_recalibrated_minus_broad_recalibrated']
    p=df[(df.Interval=='pointwise_95pct')&df.Contrast.isin(contrasts)].copy();assert len(p)==24
    assert not p[['Brier loss difference','95% CI lower','95% CI upper']].isna().any().any()
    fig,axes=plt.subplots(1,3,sharey=True);fig.subplots_adjust(left=.22,right=.98,top=.84,bottom=.23,wspace=.12)
    cells=[('eICU','sepsis'),('eICU','pneumonia'),('MIMIC-IV','sepsis'),('MIMIC-IV','pneumonia')]
    for j,(ax,pop,title) in enumerate(zip(axes,['all','primary','never_primary'],['All test records','Primary test records','Never-primary test records'])):
        ax.axvline(0,color='#84919B',lw=.8,ls=(0,(3,2)))
        for i,(db,disease) in enumerate(cells):
            y=3-i
            if i%2==0:ax.axhspan(y-.45,y+.45,color='#F5F6F7',zorder=0)
            for contrast,color,mark,shift in zip(contrasts,[BLUE,ORANGE],['o','s'],[.12,-.12]):
                r=p[(p.Database==db)&(p.Condition==disease)&(p['Test population']==pop)&(p.Contrast==contrast)];assert len(r)==1;r=r.iloc[0]
                est=r['Brier loss difference']*1000;lo=r['95% CI lower']*1000;hi=r['95% CI upper']*1000
                ax.errorbar(est,y+shift,xerr=[[est-lo],[hi-est]],fmt=mark,color=color,ecolor=color,ms=4,lw=1,capsize=2,mew=.8)
        ax.set_title(title,fontsize=8.5,pad=10);ax.set_ylim(-.6,3.6);ax.set_xlim(-20,20);ax.set_xticks([-20,-10,0,10,20])
        ax.set_yticks([3,2,1,0]);ax.set_yticklabels([db+'\n'+d.capitalize() for db,d in cells]);ax.tick_params(length=2)
        ax.text(0,1.16,'abc'[j],transform=ax.transAxes,fontsize=10,fontweight='bold')
        ax.spines['left'].set_visible(False)
    fig.legend(handles=[Line2D([],[],color=BLUE,marker='o',ms=4,label='Before recalibration'),Line2D([],[],color=ORANGE,marker='s',ms=4,label='After independent intercept recalibration')],loc='lower center',bbox_to_anchor=(.5,.015),ncol=2,handlelength=1.5,columnspacing=1.5,fontsize=7.5)
    fig.text(.6,.135,'Brier loss difference × 1,000 (primary-trained − broad-trained)',ha='center',fontsize=8)
    fig.text(.22,.08,'← Lower loss for primary-trained mapping',ha='left',fontsize=7,color='#566471')
    fig.text(.98,.08,'Lower loss for broad-trained mapping →',ha='right',fontsize=7,color='#566471')
    export(fig,out,'fig2_heldout_brier',170,104)
    p.to_csv(out/'fig2_heldout_brier_source.csv',index=False,encoding='utf-8-sig')
    return {'figure':'Figure 2','source':src.name,'sha256':sha(src),'rows':24,'selection':'pointwise_95pct; primary-v-broad fixed and recalibrated contrasts, three test populations','quantity':'Brier loss difference, scaled x1000; conditional on realized maps','size_mm':[170,104]}

def suppfig(out):
    fig,ax=plt.subplots();fig.subplots_adjust(left=.02,right=.98,bottom=.02,top=.98);ax.set(xlim=(0,1),ylim=(0,1));ax.axis('off')
    def box(x,y,w,h,title,body,fc='#F3F5F6',ec='#A1ABB3'):
        ax.add_patch(FancyBboxPatch((x,y-h/2),w,h,boxstyle='round,pad=.006,rounding_size=.008',fc=fc,ec=ec,lw=.8))
        ax.text(x+w/2,y+h*.29,title,ha='center',va='center',fontsize=8.5,fontweight='bold',color=INK)
        ax.text(x+w/2,y-h*.12,body,ha='center',va='center',fontsize=7.5,color=INK,linespacing=1.3)
    def arrow(x,y,xx,yy,color='#71808B'):ax.annotate('',xy=(xx,yy),xytext=(x,y),arrowprops={'arrowstyle':'-|>','color':color,'lw':.85})
    steps=[(.91,'Input contract','Required fields and valid coding'),(.75,'Common score support','At least one shared score level'),(.59,'Observed-support point estimate','Pooled admission-record weights'),(.40,'Interval safeguards','Cell counts · distinct patients · outcome variation'),(.21,'Patient-cluster resampling','Support stability and usable draws')]
    for y,t,b in steps:box(.025,y,.56,.105,t,b)
    for (y,_,_),(ny,_,_) in zip(steps[:-1],steps[1:]):arrow(.305,y-.06,.305,ny+.06)
    box(.72,.83,.25,.18,'Not estimable','No point estimate or CI\nInvalid input or\nno shared score',fc='#F6E7E4',ec='#B78A80')
    box(.72,.46,.25,.21,'Point estimate only','No CI under this policy\nTarget support lost or\nany interval safeguard fails',fc='#FFF2D6',ec='#BA9C58')
    box(.72,.10,.25,.15,'Estimable under policy','Point estimate and interval\nAll applicable gates pass',fc='#E3F0EB',ec='#719B8C')
    arrow(.59,.91,.715,.87,'#B78A80');arrow(.59,.75,.715,.79,'#B78A80')
    for y in [.59,.40,.21]:
        ax.plot([.59,.655],[y,y],color='#BA9C58',lw=.8)
    ax.plot([.655,.655],[.21,.59],color='#BA9C58',lw=.8);arrow(.655,.46,.715,.46,'#BA9C58')
    arrow(.305,.15,.305,.10,'#719B8C');arrow(.305,.10,.715,.10,'#719B8C')
    ax.text(.65,.95,'Fail',fontsize=7,color='#986D64',ha='center');ax.text(.64,.65,'Withhold CI',fontsize=7,color='#97792F',ha='center');ax.text(.48,.12,'Pass',fontsize=7,color='#537F6F')
    export(fig,out,'figS1_audit_states',170,123)
    return {'figure':'Supplementary Figure S1','quantity':'software reporting policy; not a causal or universal-validity diagram','source':'cohort_definition_audit.py, protocol.md, benchmark_config.json; unchanged policy','size_mm':[170,123]}

def main():
    p=argparse.ArgumentParser();p.add_argument('--levels',type=Path,required=True);p.add_argument('--s46',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=True)
    contracts=[fig1(a.levels,a.out),fig2(a.s46,a.out),suppfig(a.out)]
    (a.out/'figure_display_contract.json').write_text(json.dumps({'backend':'python','figures':contracts,'intervals':'Source-issued; withheld intervals remain withheld','analysis':'No model fitting or numerical reanalysis'},indent=2),encoding='utf-8')
    print(json.dumps(contracts),flush=True)
if __name__=='__main__':main()
