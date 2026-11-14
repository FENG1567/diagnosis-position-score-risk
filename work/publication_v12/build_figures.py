"""Publication layout refresh for the three released figures; plotting values unchanged."""
from pathlib import Path
import argparse
import hashlib
import json
import shutil

import numpy as np
import pandas as pd
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.lines import Line2D
from matplotlib.patches import FancyBboxPatch
from matplotlib.text import Text
from matplotlib.ticker import MaxNLocator, FuncFormatter

EXPECTED_LEVELS_SHA = 'd6eede6aa22b12ca11abe5b5e4e792a99cbe53855008f73db2bb4dd0e1239fe6'
EXPECTED_S46_SHA = 'a0467c4df7cdfed1f032c94e0e03fba0d413861e452b42c88e8c5e7294c346a0'
BLUE = '#267599'
ORANGE = '#BD7133'
INK = '#273542'
GRAY = '#E8EBEE'


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def json_value(value):
    if pd.isna(value):
        return None
    if isinstance(value, (np.integer,)):
        return int(value)
    if isinstance(value, (np.floating,)):
        return float(value)
    if isinstance(value, (np.bool_,)):
        return bool(value)
    return value


def json_records(frame):
    return [{str(k): json_value(v) for k, v in row.items()} for row in frame.to_dict(orient='records')]


def configure_fonts(regular_path, bold_path):
    regular_path = Path(regular_path).resolve()
    bold_path = Path(bold_path).resolve()
    if not regular_path.is_file() or not bold_path.is_file():
        raise FileNotFoundError(f'Required Arial font files are missing: {regular_path}, {bold_path}')
    font_manager.fontManager.addfont(str(regular_path))
    font_manager.fontManager.addfont(str(bold_path))
    regular_family = font_manager.FontProperties(fname=str(regular_path)).get_name()
    bold_family = font_manager.FontProperties(fname=str(bold_path)).get_name()
    if regular_family != bold_family:
        raise RuntimeError(f'Expected paired Arial faces; detected {regular_family!r} and {bold_family!r}')
    mpl.rcParams.update({
        'font.family': regular_family,
        'font.sans-serif': [regular_family],
        'font.weight': 'bold',
        'font.size': 9.5,
        'axes.labelsize': 10,
        'axes.labelweight': 'bold',
        'axes.titlesize': 10.5,
        'axes.titleweight': 'bold',
        'xtick.labelsize': 9,
        'ytick.labelsize': 9,
        'legend.fontsize': 9.5,
        'pdf.fonttype': 42,
        'ps.fonttype': 42,
        'svg.fonttype': 'none',
        'axes.spines.top': False,
        'axes.spines.right': False,
        'axes.linewidth': .75,
        'legend.frameon': False,
        'savefig.dpi': 300,
        'mathtext.fontset': 'custom',
        'mathtext.rm': regular_family + ':bold',
        'mathtext.it': regular_family + ':bold',
        'mathtext.bf': regular_family + ':bold',
        'mathtext.sf': regular_family + ':bold',
        'mathtext.tt': regular_family + ':bold',
        'mathtext.cal': regular_family + ':bold',
        'mathtext.fallback': None,
        'mathtext.default': 'bf',
    })
    bold_match = font_manager.findfont(font_manager.FontProperties(family=regular_family, weight='bold'))
    return regular_family, bold_match


def apply_bold_arial(fig, family):
    for artist in fig.findobj(match=Text):
        if artist.get_visible() and artist.get_text().strip():
            artist.set_fontfamily(family)
            artist.set_fontweight('bold')


def layout_audit(fig, figure_name, family, font_match, extra_boxes=None):
    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()
    fw, fh = fig.canvas.get_width_height()
    texts = []
    font_issues = []
    clipped = []
    for artist in fig.findobj(match=Text):
        raw = artist.get_text()
        if not artist.get_visible() or not raw.strip():
            continue
        bbox = artist.get_window_extent(renderer)
        record = {
            'text': raw,
            'fontsize_pt': round(float(artist.get_fontsize()), 2),
            'weight': artist.get_fontweight(),
            'family': list(artist.get_fontfamily()),
            'bbox_px': [round(float(bbox.x0), 2), round(float(bbox.y0), 2), round(float(bbox.x1), 2), round(float(bbox.y1), 2)],
        }
        texts.append((artist, bbox, record))
        weight = artist.get_fontweight()
        if not (weight in ('bold', 'heavy', 'black', 'extra bold', 'ultrabold') or (isinstance(weight, (int, float)) and weight >= 600)):
            font_issues.append({'text': raw, 'issue': 'not-bold', 'weight': str(weight)})
        families = artist.get_fontfamily()
        if family not in families:
            font_issues.append({'text': raw, 'issue': 'non-Arial-family', 'family': families})
        if bbox.x0 < -1 or bbox.y0 < -1 or bbox.x1 > fw + 1 or bbox.y1 > fh + 1:
            clipped.append({'text': raw, 'bbox_px': record['bbox_px']})
    overlaps = []
    for i in range(len(texts)):
        ai, bi, ri = texts[i]
        for j in range(i + 1, len(texts)):
            aj, bj, rj = texts[j]
            width = min(bi.x1, bj.x1) - max(bi.x0, bj.x0)
            height = min(bi.y1, bj.y1) - max(bi.y0, bj.y0)
            if width > .75 and height > .75:
                overlaps.append({'first': ri['text'], 'second': rj['text'], 'overlap_px': [round(float(width), 2), round(float(height), 2)]})
    box_checks = []
    for box in (extra_boxes or []):
        patch_bbox = box['patch'].get_window_extent(renderer)
        for label, text_obj in [('title', box['title']), ('body', box['body'])]:
            tb = text_obj.get_window_extent(renderer)
            pad_x = max(2, patch_bbox.width * .035)
            pad_y = max(2, patch_bbox.height * .05)
            inside = bool(tb.x0 >= patch_bbox.x0 + pad_x and tb.x1 <= patch_bbox.x1 - pad_x and
                          tb.y0 >= patch_bbox.y0 + pad_y and tb.y1 <= patch_bbox.y1 - pad_y)
            box_checks.append({'box': box['name'], 'part': label, 'inside_box_with_padding': inside,
                               'bbox_px': [round(float(tb.x0), 2), round(float(tb.y0), 2), round(float(tb.x1), 2), round(float(tb.y1), 2)]})
    sizes = sorted({record['fontsize_pt'] for _, _, record in texts})
    return {
        'figure': figure_name,
        'canvas_px_at_audit_dpi': [fw, fh],
        'physical_size_mm': [round(fig.get_figwidth() * 25.4, 3), round(fig.get_figheight() * 25.4, 3)],
        'font_file_resolved_for_bold': font_match,
        'visible_text_count': len(texts),
        'fontsize_pt_values': sizes,
        'all_text_bold_arial': not font_issues,
        'font_issues': font_issues,
        'text_bbox_clipping': clipped,
        'text_bbox_overlaps': overlaps,
        'text_box_fit': box_checks,
        'pass': not font_issues and not clipped and not overlaps and all(x['inside_box_with_padding'] for x in box_checks),
    }


def export(fig, out_dir, stem, width_mm, height_mm, family, font_match, layout_reports, extra_boxes=None):
    fig.set_size_inches(width_mm / 25.4, height_mm / 25.4, forward=True)
    apply_bold_arial(fig, family)
    report = layout_audit(fig, stem, family, font_match, extra_boxes=extra_boxes)
    layout_reports.append(report)
    fig.savefig(out_dir / (stem + '.pdf'), facecolor='white')
    fig.savefig(out_dir / (stem + '.svg'), facecolor='white')
    fig.savefig(out_dir / (stem + '.png'), facecolor='white', dpi=300)
    fig.savefig(out_dir / (stem + '.tiff'), facecolor='white', dpi=600, pil_kwargs={'compression': 'tiff_lzw'})
    plt.close(fig)
    print(json.dumps({'preview': str(out_dir / (stem + '.png')), 'layout_pass': report['pass'],
                      'text_overlaps': len(report['text_bbox_overlaps']), 'clipped': len(report['text_bbox_clipping'])}), flush=True)
    return report


def fig1(src, out, family, font_match, layout_reports):
    df = pd.read_csv(src)
    assert len(df) == 20
    fig = plt.figure(figsize=(180 / 25.4, 180 / 25.4))
    outer = fig.add_gridspec(2, 2, left=.17, right=.99, top=.865, bottom=.12, wspace=.21, hspace=.32)
    cells = [('eICU-CRD', 'sepsis'), ('eICU-CRD', 'pneumonia'), ('MIMIC-IV', 'sepsis'), ('MIMIC-IV', 'pneumonia')]
    panel_heads = []
    for k, (db, disease) in enumerate(cells):
        p = df[(df.database == db) & (df.disease == disease)].sort_values('level')
        x = p.level.to_numpy()
        grid = outer[k // 2, k % 2].subgridspec(3, 1, height_ratios=[3.1, 1.65, 1.05], hspace=.18)
        ar = fig.add_subplot(grid[0])
        ad = fig.add_subplot(grid[1], sharex=ar)
        an = fig.add_subplot(grid[2], sharex=ar)
        for ax in [ar, ad, an]:
            ax.set_xlim(x.min() - .45, x.max() + .45)
            ax.set_xticks(x)
            ax.tick_params(width=.75, length=2.8, pad=3)
        for row in p.itertuples():
            if row.delta_ci_status == 'computed' and row.delta_ci_pp_lo <= 0 <= row.delta_ci_pp_hi:
                for ax in [ar, ad]:
                    ax.axvspan(row.level - .4, row.level + .4, color='#F3F4F5', zorder=0)
        for group, color, marker, offset in [('never', BLUE, 'o', -.045), ('primary', ORANGE, 's', .045)]:
            ar.plot(x + offset, p['risk_' + group], color=color, lw=1, zorder=2)
            for _, row in p.iterrows():
                y = row['risk_' + group]
                xx = row.level + offset
                computed = row['risk_' + group + '_ci_status'] == 'computed'
                if computed:
                    lo = row['risk_' + group + '_ci_pp_lo']
                    hi = row['risk_' + group + '_ci_pp_hi']
                    ar.errorbar(xx, y, yerr=[[max(0, y - lo)], [max(0, hi - y)]], fmt='none', ecolor=color, elinewidth=.85, capsize=2.5, zorder=3)
                ar.scatter(xx, y, s=24, marker=marker if computed else 'D', facecolor=color if computed else 'white', edgecolor=color, lw=.9, zorder=4, clip_on=False)
        ar.set_ylim(-1.8, 50)
        ar.set_yticks([0, 20, 40])
        ar.set_ylabel('Mortality (%)' if k % 2 == 0 else '')
        ar.tick_params(labelbottom=False, labelsize=9)
        ad.axhline(0, color='#89929B', lw=.8, ls=(0, (3, 2)))
        ad.plot(x, p.diff_pp, color=INK, lw=.9)
        for row in p.itertuples():
            comp = row.delta_ci_status == 'computed'
            zero = comp and row.delta_ci_pp_lo <= 0 <= row.delta_ci_pp_hi
            if comp:
                ad.errorbar(row.level, row.diff_pp, yerr=[[max(0, row.diff_pp - row.delta_ci_pp_lo)], [max(0, row.delta_ci_pp_hi - row.diff_pp)]], fmt='none', ecolor=INK, elinewidth=.9, capsize=2.5)
            ad.scatter(row.level, row.diff_pp, s=24, marker='o' if comp else 'D', facecolor='white' if zero or not comp else INK, edgecolor=INK, lw=.9, zorder=4)
        ad.set_ylim(-12, 40)
        ad.set_yticks([0, 20, 40])
        ad.set_ylabel(r'$\delta_s$ (pp)' if k % 2 == 0 else '')
        ad.tick_params(labelbottom=False, labelsize=9)
        an.bar(x, p.n_never, .6, color=BLUE)
        an.bar(x, p.n_primary, .6, bottom=p.n_never, color=ORANGE)
        an.yaxis.set_major_locator(MaxNLocator(2, integer=True))
        an.yaxis.set_major_formatter(FuncFormatter(lambda v, _: f'{v/1000:g}k' if v >= 1000 else f'{v:g}'))
        an.set_ylim(0, p.n.max() * 1.12)
        an.set_ylabel('Records', rotation=0, ha='right', va='center', labelpad=14) if k % 2 == 0 else an.set_ylabel('')
        an.set_xlabel('qSOFA' if disease == 'sepsis' else 'CURB-65')
        an.tick_params(labelsize=9)
        panel_heads.append((ar, 'ABCD'[k], db + '  |  ' + disease.capitalize()))
    fig.canvas.draw()
    for ax, letter, title in panel_heads:
        pos = ax.get_position()
        fig.text(pos.x0, pos.y1 + .008, letter, ha='left', va='bottom', fontsize=18, fontweight='bold', color=INK)
        fig.text(pos.x0 + .046, pos.y1 + .012, title, ha='left', va='bottom', fontsize=10.5, fontweight='bold', color=INK)
    handles = [
        Line2D([], [], color=BLUE, marker='o', ms=4.5, label='Never-primary'),
        Line2D([], [], color=ORANGE, marker='s', ms=4.5, label='Primary'),
        Line2D([], [], color=INK, marker='o', mfc='white', ls='none', ms=4.5, label=r'$\delta_s$ CI contains zero'),
        Line2D([], [], color=INK, marker='D', mfc='white', ls='none', ms=4.5, label='Point only; no CI'),
    ]
    fig.legend(handles=handles, loc='upper center', bbox_to_anchor=(.58, .995), ncol=2, columnspacing=2.1, handlelength=1.7, labelspacing=.6)
    fig.text(.145, .014, 'Pointwise 95% intervals where reported. Shaded scores have a $\\delta_s$ interval containing zero.\nPneumonia score 0: primary deaths / records = 0/17 (eICU), 0/13 (MIMIC-IV).', fontsize=9, linespacing=1.2, ha='left', va='bottom')
    report = export(fig, out, 'fig1_score_specific_risk', 180, 180, family, font_match, layout_reports)
    shutil.copy2(src, out / 'fig1_score_specific_risk_source.csv')
    audit_fields = list(df.columns)
    return {
        'figure': 'Figure 1', 'source': Path(src).name, 'source_sha256': sha(src), 'source_rows': len(df),
        'plotted_rows': len(df), 'plot_rows_equal_source_rows': True,
        'quantity': 'observed risks and score-specific delta_s; not weighted summary',
        'physical_size_mm': [180, 180], 'layout_bbox_pass': report['pass'],
        'plot_rows': json_records(df[audit_fields]),
    }


def fig2(src, out, family, font_match, layout_reports):
    df = pd.read_csv(src)
    df['_source_row'] = np.arange(2, len(df) + 2)
    contrasts = ['primary_fixed_minus_broad_fixed', 'primary_recalibrated_minus_broad_recalibrated']
    p = df[(df.Interval == 'pointwise_95pct') & df.Contrast.isin(contrasts)].copy()
    assert len(p) == 24
    assert not p[['Brier loss difference', '95% CI lower', '95% CI upper']].isna().any().any()
    fig, axes = plt.subplots(1, 3, figsize=(180 / 25.4, 110.12 / 25.4), sharey=True)
    fig.subplots_adjust(left=.20, right=.985, top=.83, bottom=.32, wspace=.24)
    cells = [('eICU', 'sepsis'), ('eICU', 'pneumonia'), ('MIMIC-IV', 'sepsis'), ('MIMIC-IV', 'pneumonia')]
    titles = ['All test\nrecords', 'Primary test\nrecords', 'Never-primary\ntest records']
    for j, (ax, pop, title) in enumerate(zip(axes, ['all', 'primary', 'never_primary'], titles)):
        ax.axvline(0, color='#84919B', lw=.85, ls=(0, (3, 2)))
        for i, (db, disease) in enumerate(cells):
            y = 3 - i
            if i % 2 == 0:
                ax.axhspan(y - .45, y + .45, color='#F5F6F7', zorder=0)
            for contrast, color, mark, shift in zip(contrasts, [BLUE, ORANGE], ['o', 's'], [.12, -.12]):
                row = p[(p.Database == db) & (p.Condition == disease) & (p['Test population'] == pop) & (p.Contrast == contrast)]
                assert len(row) == 1
                row = row.iloc[0]
                est = row['Brier loss difference'] * 1000
                lo = row['95% CI lower'] * 1000
                hi = row['95% CI upper'] * 1000
                ax.errorbar(est, y + shift, xerr=[[est - lo], [hi - est]], fmt=mark, color=color, ecolor=color, ms=4.5, lw=1.05, capsize=2.5, mew=.9)
        ax.set_ylim(-.6, 3.6)
        ax.set_xlim(-20, 20)
        ax.set_xticks([-20, 0, 20])
        ax.set_xticklabels(['−20', '0', '20'])
        endpoint_labels = ax.get_xticklabels()
        endpoint_labels[0].set_ha('left')
        endpoint_labels[-1].set_ha('right')
        ax.set_yticks([3, 2, 1, 0])
        if j == 0:
            ax.set_yticklabels([db + '\n' + disease.capitalize() for db, disease in cells])
            ax.tick_params(axis='y', length=0, pad=5, labelsize=9)
        else:
            ax.tick_params(axis='y', left=False, labelleft=False)
        ax.tick_params(axis='x', length=2.8, width=.75, pad=4, labelsize=9)
        ax.spines['left'].set_visible(False)
        ax.spines['right'].set_visible(False)
    fig.canvas.draw()
    for ax, letter, title in zip(axes, 'ABC', titles):
        pos = ax.get_position()
        header_top = pos.y1 + .09
        letter_h = 18 / (72 * fig.get_figheight())
        title_h = (2 * 10.5 * 1.04) / (72 * fig.get_figheight())
        fig.text(pos.x0, header_top - letter_h, letter, ha='left', va='bottom', fontsize=18, fontweight='bold', color=INK)
        fig.text(pos.x0 + .047, header_top - title_h, title, ha='left', va='bottom', fontsize=10.5, fontweight='bold', color=INK, linespacing=1.04)
    fig.text(.60, .22, 'Brier loss difference × 1,000 (primary-trained − broad-trained)', ha='center', va='bottom', fontsize=9.5)
    fig.text(.215, .13, '← Lower loss for primary-trained mapping', ha='left', va='bottom', fontsize=9)
    fig.text(.985, .13, 'Lower loss for broad-trained mapping →', ha='right', va='bottom', fontsize=9)
    fig.legend(handles=[
        Line2D([], [], color=BLUE, marker='o', ms=4.5, label='Before recalibration'),
        Line2D([], [], color=ORANGE, marker='s', ms=4.5, label='After independent intercept recalibration'),
    ], loc='lower center', bbox_to_anchor=(.60, .025), ncol=2, handlelength=1.6, columnspacing=1.8, labelspacing=.5)
    report = export(fig, out, 'fig2_heldout_brier', 180, 110.12, family, font_match, layout_reports)
    p.to_csv(out / 'fig2_heldout_brier_source.csv', index=False, encoding='utf-8-sig')
    plotted = []
    for _, row in p.sort_values('_source_row').iterrows():
        plotted.append({
            'source_row': int(row['_source_row']), 'Database': row['Database'], 'Condition': row['Condition'],
            'Test population': row['Test population'], 'Contrast': row['Contrast'], 'Interval': row['Interval'],
            'estimate_input': float(row['Brier loss difference']), 'ci_lower_input': float(row['95% CI lower']),
            'ci_upper_input': float(row['95% CI upper']), 'estimate_plotted_x1000': float(row['Brier loss difference'] * 1000),
            'ci_lower_plotted_x1000': float(row['95% CI lower'] * 1000), 'ci_upper_plotted_x1000': float(row['95% CI upper'] * 1000),
        })
    return {
        'figure': 'Figure 2', 'source': Path(src).name, 'source_sha256': sha(src), 'source_rows': len(df),
        'current_source_table': 'S25 (mapped from prior S46)',
        'plotted_rows': len(p), 'selection': 'pointwise_95pct; primary-v-broad fixed and recalibrated contrasts, three test populations',
        'quantity': 'Brier loss difference, scaled x1000; conditional on realized maps',
        'physical_size_mm': [180, 110.12], 'layout_bbox_pass': report['pass'], 'plot_rows': plotted,
    }


def wrap_measured(text, max_width_px, renderer, prop):
    lines = []
    for paragraph in str(text).split('\n'):
        words = paragraph.split()
        if not words:
            lines.append('')
            continue
        line = ''
        for word in words:
            candidate = word if not line else line + ' ' + word
            measured = renderer.get_text_width_height_descent(candidate, prop, ismath=False)[0]
            if line and measured > max_width_px:
                lines.append(line)
                line = word
            else:
                line = candidate
        if line:
            lines.append(line)
    return '\n'.join(lines)


def suppfig(out, family, bold_font_path, font_match, layout_reports):
    fig, ax = plt.subplots(figsize=(180 / 25.4, 130.24 / 25.4))
    fig.subplots_adjust(left=.012, right=.988, bottom=.018, top=.985)
    ax.set(xlim=(0, 1), ylim=(0, 1))
    ax.axis('off')
    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()
    px_per_x = abs(ax.transData.transform((1, 0))[0] - ax.transData.transform((0, 0))[0])
    px_per_y = abs(ax.transData.transform((0, 1))[1] - ax.transData.transform((0, 0))[1])
    title_prop = font_manager.FontProperties(fname=bold_font_path, size=10.5)
    body_prop = font_manager.FontProperties(fname=bold_font_path, size=9.25)
    box_items = []

    def box(x, y, w, h, title, body, fc='#F3F5F6', ec='#A1ABB3', name=''):
        patch = FancyBboxPatch((x, y - h / 2), w, h, boxstyle='round,pad=.004,rounding_size=.008', fc=fc, ec=ec, lw=.9)
        ax.add_patch(patch)
        max_width_px = w * px_per_x * .92
        title_text = wrap_measured(title, max_width_px, renderer, title_prop)
        body_text = wrap_measured(body, max_width_px, renderer, body_prop)
        title_artist = ax.text(x + w / 2, y, title_text, ha='center', va='center', fontproperties=title_prop, color=INK, linespacing=1.05)
        body_artist = ax.text(x + w / 2, y, body_text, ha='center', va='center', fontproperties=body_prop, color=INK, linespacing=1.12)
        box_items.append({'name': name or title, 'patch': patch, 'title': title_artist, 'body': body_artist, 'center': (x + w / 2, y), 'height_px': h * px_per_y})

    def arrow(x, y, xx, yy, color='#71808B'):
        ax.annotate('', xy=(xx, yy), xytext=(x, y), arrowprops={'arrowstyle': '-|>', 'color': color, 'lw': .95, 'mutation_scale': 10})

    steps = [
        (.90, 'Data requirements', 'Required fields and valid coding'),
        (.73, 'Common score support', 'At least one shared score level'),
        (.56, 'Weighted risk-difference summary', 'Pooled admission-record weights'),
        (.39, 'Interval reporting criteria', 'Record counts · distinct patients · outcome variation'),
        (.22, 'Patient-cluster resampling', 'Score support and usable resamples'),
    ]
    for idx, (y, title, body) in enumerate(steps, start=1):
        box(.02, y, .53, .13, title, body, name=f'step_{idx}')
    box(.67, .83, .31, .21, 'Not estimable', 'No point estimate or interval\nInvalid input or\nno shared score', fc='#F6E7E4', ec='#B78A80', name='not_estimable')
    box(.67, .46, .31, .22, 'Point estimate only', 'No confidence interval\nTarget score support lost or\nan interval criterion not met', fc='#FFF2D6', ec='#BA9C58', name='point_estimate_only')
    box(.67, .11, .31, .20, 'Estimate and interval', 'All reporting criteria met', fc='#E3F0EB', ec='#719B8C', name='estimable_under_policy')
    for (y, _, _), (next_y, _, _) in zip(steps[:-1], steps[1:]):
        arrow(.285, y - .065, .285, next_y + .065)
    arrow(.55, .90, .665, .87, '#B78A80')
    arrow(.55, .73, .665, .79, '#B78A80')
    branch_ys = [.56, .39, .22]
    for y in branch_ys:
        ax.plot([.55, .61], [y, y], color='#BA9C58', lw=.9)
    ax.plot([.61, .61], [min(branch_ys), max(branch_ys)], color='#BA9C58', lw=.9)
    arrow(.61, .46, .665, .46, '#BA9C58')
    arrow(.285, .155, .285, .11, '#719B8C')
    arrow(.285, .11, .665, .11, '#719B8C')
    fig.canvas.draw()
    gap_px = 5.5 * fig.dpi / 72
    for item in box_items:
        th = item['title'].get_window_extent(renderer).height
        bh = item['body'].get_window_extent(renderer).height
        if th + bh + gap_px > item['height_px'] * .90:
            raise RuntimeError(f"S1 text stack does not fit {item['name']}: {(th + bh + gap_px) / px_per_y:.3f} data units > {item['height_px'] * .90 / px_per_y:.3f}")
        cx, cy = item['center']
        item['title'].set_position((cx, cy + (bh + gap_px) / (2 * px_per_y)))
        item['body'].set_position((cx, cy - (th + gap_px) / (2 * px_per_y)))
    fig.canvas.draw()
    report = export(fig, out, 'figS1_audit_states', 180, 130.24, family, font_match, layout_reports, extra_boxes=box_items)
    return {
        'figure': 'Supplementary Figure S1', 'quantity': 'software reporting policy; not a causal or universal-validity diagram',
        'source': 'policy wording retained from current schematic', 'physical_size_mm': [180, 130.24],
        'layout_bbox_pass': report['pass'],
        'nodes': [{'title': title, 'body': body} for _, title, body in steps] + [
            {'title': 'Not estimable', 'body': 'No point estimate or interval; Invalid input or; no shared score'},
            {'title': 'Point estimate only', 'body': 'No confidence interval; Target score support lost or; an interval criterion not met'},
            {'title': 'Estimate and interval', 'body': 'All reporting criteria met'},
        ],
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--levels', type=Path, required=True)
    parser.add_argument('--s46', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--arial-regular', type=Path, default=None)
    parser.add_argument('--arial-bold', type=Path, default=None)
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    if bool(args.arial_regular) != bool(args.arial_bold):
        parser.error('Supply both font paths or neither')
    if args.arial_regular is None:
        for candidate in ['Arial', 'Liberation Sans', 'DejaVu Sans']:
            try:
                args.arial_regular = Path(font_manager.findfont(font_manager.FontProperties(family=candidate), fallback_to_default=False))
                args.arial_bold = Path(font_manager.findfont(font_manager.FontProperties(family=candidate, weight='bold'), fallback_to_default=False))
                break
            except ValueError:
                continue
        else:
            raise RuntimeError('No supported sans-serif font installed')
    levels_sha, s46_sha = sha(args.levels), sha(args.s46)
    assert levels_sha == EXPECTED_LEVELS_SHA, f'F1 source changed: {levels_sha}'
    assert s46_sha == EXPECTED_S46_SHA, f'F2 source changed: {s46_sha}'
    family, font_match = configure_fonts(args.arial_regular, args.arial_bold)
    layout_reports = []
    contracts = [
        fig1(args.levels, args.out, family, font_match, layout_reports),
        fig2(args.s46, args.out, family, font_match, layout_reports),
        suppfig(args.out, family, args.arial_bold.resolve(), font_match, layout_reports),
    ]
    artifact_hashes = {}
    for stem in ['fig1_score_specific_risk', 'fig2_heldout_brier', 'figS1_audit_states']:
        artifact_hashes[stem] = {ext: sha(args.out / f'{stem}.{ext}') for ext in ['pdf', 'svg', 'png', 'tiff']}
    value_audit = {
        'statement': 'Plotted values are direct source fields and declared ×1000 display scaling only; no analysis, CI recalculation, missing-value change, or mark filtering.',
        'figure_1': {'source_sha256': levels_sha, 'source_rows': 20, 'plotted_rows': 20, 'same_rows_as_source': True,
                     'fields_are_complete_source_rows': True, 'rows': contracts[0]['plot_rows']},
        'figure_2': {'source_sha256': s46_sha, 'source_rows': len(pd.read_csv(args.s46)), 'plotted_rows': 24,
                     'selection_rule': contracts[1]['selection'], 'pointwise_values_and_display_scaling': contracts[1]['plot_rows']},
    }
    (args.out / 'plot_value_equivalence.json').write_text(json.dumps(value_audit, indent=2, ensure_ascii=False, allow_nan=False), encoding='utf-8')
    for contract in contracts:
        contract.pop('plot_rows', None)
    display_contract = {
        'core_conclusion': 'Observed score-specific risk differences and conditional held-out loss trade-offs remain supported by the reported pointwise values and their stated uncertainty/status.',
        'figure_archetypes': {'fig1': 'quantitative grid', 'fig2': 'quantitative triptych', 'figS1': 'schematic-led composite'},
        'backend': 'Python / Matplotlib', 'font_family': family, 'bold_font_file_resolved': font_match,
        'data_integrity': 'Only layout and typography changed; plotted values, source-issued intervals, statuses, source rows and axes domains are preserved.',
        'source_hashes': {'fig1_levels': levels_sha, 'fig2_s46': s46_sha},
        'figures': contracts, 'artifact_sha256': artifact_hashes,
        'exports': {'vector': ['PDF with TrueType42', 'SVG with editable text'], 'raster': ['PNG 300 dpi', 'TIFF 600 dpi LZW']},
    }
    (args.out / 'figure_display_contract.json').write_text(json.dumps(display_contract, indent=2, ensure_ascii=False), encoding='utf-8')
    (args.out / 'layout_bbox_audit.json').write_text(json.dumps({'figures': layout_reports}, indent=2, ensure_ascii=False), encoding='utf-8')
    print(json.dumps({'status': 'rendered', 'figures': contracts, 'layout_reports': layout_reports}, ensure_ascii=False), flush=True)


if __name__ == '__main__':
    main()
