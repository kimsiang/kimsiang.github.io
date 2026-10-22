"""Headline results page (results.html). Called from build.py: build_results(build_module)."""
import math, html

def build_results(B):
    bi = B.bi

    ACC, ACC2, MUT, FAINT, LINE, TXT, WARM = '#2fc8ff', '#2251ff', '#8d9bb0', '#56637a', 'rgba(150,180,220,.18)', '#e9eff8', '#ffb547'

    def svg_dot(rows, xmin, xmax, ticks, xlabel, logx=False, W=760, rowh=46, left=230, right=40, top=18):
        """rows: (label_en, label_zh, value, err_or_None, style) style in exp|ours|theory|goal|limit"""
        H = top + rowh * len(rows) + 52
        f = (lambda v: math.log10(v)) if logx else (lambda v: v)
        X = lambda v: left + (f(v) - f(xmin)) / (f(xmax) - f(xmin)) * (W - left - right)
        o = [f'<svg viewBox="0 0 {W} {H}" class="rplot" role="img" xmlns="http://www.w3.org/2000/svg">']
        for t, lab in ticks:
            x = X(t)
            o.append(f'<line x1="{x:.1f}" y1="{top-6}" x2="{x:.1f}" y2="{H-44}" stroke="{LINE}" stroke-width="1"/>')
            o.append(f'<text x="{x:.1f}" y="{H-26}" fill="{FAINT}" font-size="12" text-anchor="middle" font-family="JetBrains Mono, monospace">{lab}</text>')
        o.append(f'<text x="{(left + W - right) / 2:.0f}" y="{H-6}" fill="{MUT}" font-size="12.5" text-anchor="middle">{xlabel}</text>')
        for i, (en, zh, v, e, st) in enumerate(rows):
            y = top + rowh * i + rowh / 2
            col = {'ours': ACC, 'exp': '#7fa8d6', 'theory': WARM, 'goal': ACC, 'limit': '#7fa8d6'}[st]
            o.append(f'<line x1="{left}" y1="{y:.1f}" x2="{W-right}" y2="{y:.1f}" stroke="{LINE}" stroke-dasharray="1 5"/>')
            o.append(f'<text x="{left-14}" y="{y+4:.1f}" fill="{TXT if st == "ours" else MUT}" font-size="13.5" text-anchor="end" font-weight="{600 if st == "ours" else 400}">'
                     f'<tspan class="en">{html.escape(en)}</tspan><tspan class="zh">{html.escape(zh)}</tspan></text>')
            x = X(v)
            if st in ('limit', 'goal', 'ours') and e is None:      # lollipop from axis start
                o.append(f'<line x1="{left}" y1="{y:.1f}" x2="{x:.1f}" y2="{y:.1f}" stroke="{col}" stroke-width="1.5" opacity=".55"{" stroke-dasharray=\"4 4\"" if st == "goal" else ""}/>')
            if e is not None:
                o.append(f'<line x1="{X(v-e):.1f}" y1="{y:.1f}" x2="{X(v+e):.1f}" y2="{y:.1f}" stroke="{col}" stroke-width="2"/>')
                for xx in (X(v - e), X(v + e)):
                    o.append(f'<line x1="{xx:.1f}" y1="{y-5:.1f}" x2="{xx:.1f}" y2="{y+5:.1f}" stroke="{col}" stroke-width="1.5"/>')
            r = 7 if st == 'ours' else 5
            fill = 'none' if st == 'goal' else col
            o.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="{fill}" stroke="{col}" stroke-width="2"/>')
            if st == 'ours':
                o.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="13" fill="none" stroke="{ACC}" stroke-opacity=".35"/>')
        o.append('</svg>')
        return ''.join(o)

    # ---- 1. Muon g-2 (values ×10^-11, offset 116 592 000)
    g2 = svg_dot([
        ('BNL E821 (2006)', 'BNL E821（2006）', 89, 63, 'exp'),
        ('Fermilab Run-1 (2021)', '费米实验室 Run-1（2021）', 40, 54, 'exp'),
        ('Fermilab Run-1–3 (2023)', '费米实验室 Run-1–3（2023）', 55, 24, 'exp'),
        ('Fermilab final (2025)', '费米实验室最终结果（2025）', 70.5, 14.8, 'ours'),
        ('SM, White Paper 2020', '标准模型 白皮书2020', -190, 43, 'theory'),
        ('SM, White Paper 2025', '标准模型 白皮书2025', 33, 62, 'theory'),
    ], -260, 180, [(-200, '−200'), (-100, '−100'), (0, '0'), (100, '+100')],
        'a<tspan dy="4" font-size="10">μ</tspan><tspan dy="-4"> − 116 592 000  [×10⁻¹¹]</tspan>')

    # ---- 2. Muon EDM (e·cm, log)
    edm = svg_dot([
        ('BNL E821 (2009)', 'BNL E821（2009）', 1.8e-19, None, 'limit'),
        ('Fermilab g-2 (2026)', '费米实验室 g-2（2026）', 1.10e-19, None, 'ours'),
        ('PSI muEDM Phase I — goal', 'PSI muEDM 第一阶段 · 目标', 4e-21, None, 'goal'),
        ('PSI muEDM Phase II — goal', 'PSI muEDM 第二阶段 · 目标', 6e-23, None, 'goal'),
    ], 1e-23, 1e-18, [(1e-23, '10⁻²³'), (1e-22, '10⁻²²'), (1e-21, '10⁻²¹'), (1e-20, '10⁻²⁰'), (1e-19, '10⁻¹⁹'), (1e-18, '10⁻¹⁸')],
        '|d<tspan dy="4" font-size="10">μ</tspan><tspan dy="-4">|  [e·cm]  ·  95% CL limit or projected sensitivity — smaller is better</tspan>', logx=True)

    # ---- 3. SHINE repetition rate (Hz, log)
    shine = svg_dot([
        ('Proton-driven pulsed sources', '质子驱动脉冲缪子源', 50, None, 'limit'),
        ('SHINE electron-driven (design)', 'SHINE 电子驱动（设计）', 5e4, None, 'ours'),
    ], 1, 1e6, [(1, '1'), (10, '10'), (100, '100'), (1e3, '1k'), (1e4, '10k'), (1e5, '100k'), (1e6, '1M')],
        'Pulse repetition rate  [Hz]', logx=True, rowh=52)

    def block(i, code, en_pillar, zh_pillar, head_en, head_zh, big, unit, body_en, body_zh, role_en, role_zh, fig, src, links):
        return f'''<article class="res rv" id="r{i}">
      <div class="res-l">
        <p class="mono eyebrow">{code} · {bi(en_pillar, zh_pillar)}</p>
        <p class="res-big">{big}<span class="res-unit">{unit}</span></p>
        <h2>{bi(head_en, head_zh)}</h2>
        <p class="res-p">{bi(body_en, body_zh)}</p>
        <p class="res-role"><b class="mono">{bi("OUR ROLE", "我们的贡献")}</b> {bi(role_en, role_zh)}</p>
        <p class="res-links mono">{links}</p>
      </div>
      <figure class="res-fig">{fig}<figcaption class="mono">{src}</figcaption></figure>
    </article>'''

    ins = lambda i: f'https://inspirehep.net/literature/{i}'
    A = lambda href, t: f'<a href="{href}" target="_blank" rel="noopener">{t}</a>'

    strip = f'''<div class="hstrip">
      <a href="#r1"><b>127<small> ppb</small></b><span>{bi("Final precision on the muon anomalous magnetic moment", "缪子反常磁矩最终测量精度")}</span><i class="mono">MUON g-2 →</i></a>
      <a href="#r2"><b>1.1×10⁻¹⁹<small> e·cm</small></b><span>{bi("New direct limit on the muon EDM", "缪子电偶极矩新直接上限")}</span><i class="mono">muEDM →</i></a>
      <a href="#r3"><b>50<small> kHz</small></b><span>{bi("Pulsed muon beam design at SHINE — 1000× today’s pulse rate", "SHINE脉冲缪子束设计——脉冲频率为现有装置的1000倍")}</span><i class="mono">SHINE →</i></a>
      <a href="#r4"><b>Tides<small> seen by muons</small></b><span>{bi("Muography beneath the Huangpu River, Shanghai Outer Ring Tunnel", "黄浦江下外环隧道缪子成像")}</span><i class="mono">MUOGRAPHY →</i></a>
    </div>'''

    blocks = [
      block(1, '01', 'Muon g-2 · Fermilab', '缪子g-2 · 费米实验室',
            'The muon’s magnetic anomaly, measured to 127 parts per billion',
            '缪子反常磁矩测量精度达到十亿分之127',
            '127', ' ppb',
            'The Fermilab Muon g-2 Experiment’s final result, a<sub>μ</sub> = 116 592 070.5(14.8) × 10⁻¹¹, is four times more precise than the previous world average. It now agrees with the 2025 Standard Model prediction, which moved after a new evaluation of the hadronic contribution.',
            '费米实验室缪子g-2实验最终结果 a<sub>μ</sub> = 116 592 070.5(14.8) × 10⁻¹¹，将世界平均值精度提高了四倍以上；与采用新强子贡献评估的2025年标准模型预言相符。',
            'As members of the Muon g-2 Collaboration, we work mainly on the measurement of the anomalous precession frequency ω<sub>a</sub> and its beam-dynamics corrections.',
            '作为缪子g-2国际合作组成员，我们主要参与反常进动频率ω<sub>a</sub>的测量及其束流动力学修正。',
            g2, 'Sources: Muon g-2 Collaboration, PRL 135, 101802 (2025); PRL 131, 161802 (2023); PRL 126, 141801 (2021); BNL E821; Muon g-2 Theory Initiative WP20, WP25.',
            ' · '.join([A(ins(2928642), 'PRL 2025'), A(ins(3169190), 'Final report'), A('{ROOT}research.html#muon-g-2', bi('Research →', '研究方向 →'))])),
      block(2, '02', 'Muon EDM · Fermilab & PSI', '缪子电偶极矩 · 费米实验室与PSI',
            'A tighter direct limit on the muon EDM — and a path to 10⁻²³',
            '缪子电偶极矩直接上限进一步收紧——并迈向10⁻²³',
            '1.1×10⁻¹⁹', ' e·cm',
            'Using tracker data from the Fermilab g-2 ring (2019–2020), the collaboration set |d<sub>μ</sub>| &lt; 1.10 × 10⁻¹⁹ e·cm at 95% CL, improving on Brookhaven’s 2009 limit. The frozen-spin muEDM experiment at PSI aims for 4 × 10⁻²¹ e·cm in Phase I and 6 × 10⁻²³ e·cm in Phase II.',
            '利用费米实验室g-2储存环2019–2020年径迹数据，得到 |d<sub>μ</sub>| &lt; 1.10 × 10⁻¹⁹ e·cm（95%置信度），优于布鲁克海文2009年上限。PSI冻结自旋muEDM实验第一阶段目标灵敏度 4 × 10⁻²¹ e·cm，第二阶段 6 × 10⁻²³ e·cm。',
            'We design, build and test the muon entrance trigger detector and its fast front-end electronics for muEDM.',
            '我们负责muEDM实验缪子入射触发探测器及其快速前端电子学的设计、建造与测试。',
            edm, 'Sources: Muon g-2 Collaboration, arXiv preprint (2026); BNL E821, PRD 80, 052008 (2009); muEDM, EPJC 85, 622 (2025).',
            ' · '.join([A(ins(3190062), bi('EDM limit', 'EDM上限')), A(ins(2874447), 'EPJC 2025'), A(ins(3137131), bi('Trigger detector', '触发探测器'))])),
      block(3, '03', 'SHINE muon source · Shanghai', 'SHINE缪子源 · 上海',
            'A 50 kHz pulsed muon beam from an X-ray laser’s electron linac',
            '利用X射线自由电子激光电子直线加速器产生50 kHz脉冲缪子束',
            '3×10⁶', ' μ⁺/s',
            'Simulations show that SHINE’s 8 GeV, 100 pC electron bunches on a copper target can deliver about 60 surface muons per bunch to the end of a beamline — 3 × 10⁶ μ⁺/s at 50 kHz. That rate is comparable to existing muon facilities, with a pulse rate a thousand times higher than proton-driven pulsed sources.',
            '模拟表明，SHINE 8 GeV、100 pC电子束团轰击铜靶，每束团约60个表面缪子可传输至束线末端，在50 kHz下对应 3 × 10⁶ μ⁺/s——与现有缪子装置相当，而脉冲频率比质子驱动脉冲源高约千倍。',
            'We lead the target, beamline and source design studies.',
            '我们主导靶、束线与缪子源的设计研究。',
            shine, 'Sources: PRAB 28, 083401 (2025); IPAC 2025 TUPM092. Proton-driven pulsed sources operate at 25–50 Hz.',
            ' · '.join([A(ins(2896777), 'PRAB 2025'), A(ins(3101005), 'IPAC 2025'), A('{ROOT}research.html#shine-muon-source', bi('Research →', '研究方向 →'))])),
      block(4, '04', 'Muography · Shanghai', '缪子成像 · 上海',
            'Watching the Huangpu River’s tide from inside a tunnel',
            '在隧道中用缪子“看见”黄浦江潮汐',
            'Tides', '',
            'A portable scintillator detector inside the Shanghai Outer Ring Tunnel, an immersed tube beneath the Huangpu River, recorded a muon rate that rises and falls opposite to the water level at a nearby tide gauge. The scan along the tunnel matched sediment data and Geant4 simulations.',
            '在黄浦江下的上海外环沉管隧道内，便携式闪烁体探测器测得的缪子计数率与附近潮位站水位呈明显反相关；沿隧道的扫描结果与泥沙数据及Geant4模拟一致。',
            'We designed the detector, ran the field campaign and led the analysis.',
            '我们设计了探测器、完成现场测量并主导数据分析。',
            '<img src="{ROOT}assets/media/2399.webp" alt="Muon rate versus river level" loading="lazy">',
            'Source: J. Appl. Phys. 138, 114902 (2025). Blue: muon rate per 10 min; red: river level.',
            ' · '.join([A(ins(2906901), 'J. Appl. Phys. 2025'), A('{ROOT}news/our-paper-on-the-shanghai-outer-ring-tunnel-muography-is-out.html', bi('News', '新闻'))])),
    ]


    legend = f'''<p class="legend"><span><i style="background:{ACC}"></i>{bi("Our group’s result / experiment", "本组参与的结果/实验")}</span><span><i style="background:#7fa8d6"></i>{bi("Other measurements", "其他测量")}</span><span><i style="background:{WARM}"></i>{bi("Standard Model prediction", "标准模型预言")}</span><span><i style="border:2px solid {ACC};width:7px;height:7px"></i>{bi("Projected sensitivity", "预期灵敏度")}</span></p>'''

    body = B.phero('RESULTS', 'Research', '研究', bi('Headline results', '代表性成果'), scene='ring', lead_html=bi(
        'Four numbers that summarise where the group stands: from precision tests of the Standard Model to a new muon source and muography beneath Shanghai.',
        '用四个数字概括课题组的进展：从标准模型精密检验，到新型缪子源，再到上海地下的缪子成像。'))
    body += '<section class="pbody"><div class="wrap">' + strip + legend + ''.join(blocks) + \
        '<p class="src mono">' + bi('Values quoted from the group’s publications; see linked papers for full uncertainties.', '数值引自课题组论文，完整误差见所链接文献。') + '</p></div></section>'
    B.layout('results.html', 'Headline results', 'Headline results of the TDLI Muon Physics Group.', body, 'research')

