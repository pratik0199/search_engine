import pandas as pd
import numpy as np
import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec

st.set_page_config(layout="wide")

st.markdown("""
<style>
.block-container {
    padding-top: 0.1rem !important;
    padding-bottom: 0rem !important;
    padding-left: 1.0rem !important;
    padding-right: 1.0rem !important;
    max-width: 100% !important;
}
html, body, [class*="css"] { font-family: "Times New Roman", serif; }

/* ── Collapse ALL vertical gaps ── */
div[data-testid="stVerticalBlock"] > div { gap: 0rem !important; }
div[data-testid="stHorizontalBlock"] { margin-top: 0 !important; margin-bottom: 0 !important; }
div[data-testid="column"] { padding: 0 3px !important; }

/* ── NAV BUTTONS — fixed width, centered ── */
div.stButton > button {
    width: 100%;
    border-radius: 4px;
    height: 34px !important;
    min-height: 34px !important;
    font-weight: 700;
    font-size: 13px;
    background-color: #1e293b;
    border: 1px solid #334155;
    color: white !important;
    padding: 0 6px !important;
    line-height: 1 !important;
    white-space: nowrap;
}
div.stButton > button p,
div.stButton > button span,
div.stButton > button div {
    color: white !important; font-weight: 700 !important; font-size: 13px !important;
}
div.stButton > button:hover { background-color: #0f172a; }
/* active state flash */
div.stButton > button:active { transform: scale(0.97); }

/* ── SELECTBOX — cap width so they don't stretch ── */
div[data-testid="stSelectbox"] {
    max-width: 160px !important;
    margin-bottom: 0 !important;
    padding-bottom: 0 !important;
}
div[data-baseweb="select"] > div {
    min-height: 30px !important;
    max-width: 160px !important;
    background-color: #ffffff !important;
    border: 1.5px solid #1e293b !important;
    border-radius: 3px !important;
}
div[data-baseweb="select"] > div:hover { border-color: #475569 !important; }
div[data-baseweb="select"] svg { fill: #1e293b !important; }
div[data-baseweb="select"] [class*="singleValue"],
div[data-baseweb="select"] [class*="placeholder"] {
    color: #1e293b !important; font-family: "Times New Roman", serif !important;
    font-size: 12px !important; font-weight: 700 !important;
    white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
}
div[data-baseweb="select"] input { color: #1e293b !important; font-size: 12px !important; }
div[data-testid="stSelectbox"] label {
    font-family: "Times New Roman", serif !important;
    font-size: 11px !important; font-weight: 700 !important;
    color: #1e293b !important; margin-bottom: 1px !important;
}

/* ── Bifurcation dropdowns — even more compact ── */
.bif-compact div[data-baseweb="select"] > div { min-height: 23px !important; }
.bif-compact div[data-baseweb="select"] [class*="singleValue"],
.bif-compact div[data-baseweb="select"] [class*="placeholder"] {
    font-size: 10px !important; font-weight: 600 !important;
}
.bif-compact div[data-baseweb="select"] input { font-size: 10px !important; }
.bif-compact div[data-testid="stSelectbox"] label {
    font-size: 9px !important; margin-bottom: 0 !important;
}
.bif-compact div[data-baseweb="select"] svg { width: 14px !important; height: 14px !important; }

/* ── KPI CARDS ── */
.kpi-row { display:flex; gap:6px; margin-bottom:0px; margin-top:0px; }
.kpi-card {
    flex:1; background:#f8fafc; border:1.5px solid #1e293b; border-left:3px solid #1e293b;
    border-radius:5px; padding:4px 8px 3px 8px; min-width:0;
    font-family:"Times New Roman",serif; text-align:center;
}
.kpi-label { font-size:8px; font-weight:900; color:#1e293b; text-transform:uppercase; letter-spacing:0.8px; margin-bottom:1px; }
.kpi-value { font-size:15px; font-weight:700; color:#1e293b; line-height:1.1; font-family:"Times New Roman",serif; }
.kpi-sub   { font-size:8px; font-weight:700; color:#334155; margin-top:1px; font-family:"Times New Roman",serif; }
.kpi-card.c1{border-left-color:#2563eb;} .kpi-card.c1 .kpi-value{color:#2563eb;}
.kpi-card.c2{border-left-color:#65a30d;} .kpi-card.c2 .kpi-value{color:#65a30d;}
.kpi-card.c3{border-left-color:#d97706;} .kpi-card.c3 .kpi-value{color:#d97706;}
.kpi-card.c4{border-left-color:#7c3aed;} .kpi-card.c4 .kpi-value{color:#7c3aed;}

/* ── PLOT BOX ── */
.plot-box {
    border:1.5px solid black; border-radius:5px;
    padding:2px 4px 1px 4px; background:#f8fafc; margin-bottom:3px;
}
.plot-title {
    font-size:11px; font-weight:700; color:#1e293b; margin-bottom:0px;
    font-family:"Times New Roman",serif; text-align:center; line-height:1.3;
}
.no-data-msg {
    color:#64748b; font-size:12px; font-family:"Times New Roman",serif;
    text-align:center; padding:30px 8px;
}

/* ── TITLE — bigger, tight spacing ── */
.dash-title {
    text-align:center; color:#1e293b; font-family:"Times New Roman",serif;
    font-size:28px; font-weight:700; margin:2px 0 3px 0; padding:0;
}

hr { margin:0px 0 1px 0 !important; border-color:#94a3b8; }
header { visibility:hidden; } footer { visibility:hidden; }
[data-testid="stAppViewContainer"] > section > div:first-child { padding-top: 0 !important; }
</style>

<script>
(function(){
  const BIF_LABELS = [
    "Shift Bifurcation","CW Bifurcation","CW Filter","Select Month","Select Exchanger","Select Pump"
  ];
  function applyAll(){
    const doc = window.parent.document;
    doc.querySelectorAll('[data-testid="stSelectbox"]').forEach(function(box){
      const label = box.querySelector(':scope > label');
      if(!label) return;
      const txt = label.innerText.trim();
      if(txt === "" || txt === "Pump" || txt === "Exchanger") return;
      if(!BIF_LABELS.some(l => txt.includes(l.split(" ")[0]))) return;

      // ── compact the select control ──
      box.querySelectorAll('[data-baseweb="select"] > div').forEach(el =>
        el.style.setProperty('min-height','26px','important'));
      box.querySelectorAll('[class*="singleValue"],[class*="placeholder"]').forEach(el => {
        el.style.setProperty('font-size','11px','important');
        el.style.setProperty('font-weight','700','important');
      });
      box.querySelectorAll('input').forEach(el =>
        el.style.setProperty('font-size','11px','important'));
      box.querySelectorAll('[data-baseweb="select"] svg').forEach(el => {
        el.style.setProperty('width','13px','important');
        el.style.setProperty('height','13px','important');
      });

      // ── inline: turn stSelectbox into a flex row so label + control sit side by side ──
      if(!box.dataset.inlined){
        box.dataset.inlined = "1";
        // Make the box itself flex
        box.style.setProperty('display','flex','important');
        box.style.setProperty('flex-direction','row','important');
        box.style.setProperty('align-items','center','important');
        box.style.setProperty('gap','7px','important');
        box.style.setProperty('flex-wrap','nowrap','important');
        box.style.setProperty('margin-bottom','0','important');
        // Style the native label as inline text
        label.style.setProperty('display','inline','important');
        label.style.setProperty('font-family','"Times New Roman",serif','important');
        label.style.setProperty('font-size','11px','important');
        label.style.setProperty('font-weight','700','important');
        label.style.setProperty('color','#1e293b','important');
        label.style.setProperty('white-space','nowrap','important');
        label.style.setProperty('flex-shrink','0','important');
        label.style.setProperty('margin-bottom','0','important');
        label.style.setProperty('padding-bottom','0','important');
        label.style.setProperty('line-height','1','important');
        label.style.setProperty('order','0','important');
        // Push the baseweb container to second position
        const bw = box.querySelector('[data-baseweb="select"]');
        if(bw){
          bw.style.setProperty('order','1','important');
          bw.style.setProperty('flex','1 1 auto','important');
          bw.style.setProperty('min-width','100px','important');
          bw.style.setProperty('max-width','160px','important');
        }
      }
    });
  }
  applyAll();
  [100,300,600,1200,2500].forEach(t => setTimeout(applyAll, t));
  new MutationObserver(applyAll).observe(
    window.parent.document.body, {childList:true, subtree:true}
  );
})();
</script>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────
# CW SET
# ─────────────────────────────────────────────────
CW_EXCHANGERS_RAW = [
    "E-43 A/B","E-43 C/D","E-246","E-47","E-248","E-97",
    "E-94 A","E-94 B","E-98","E-95 A","E-95 B","E-99",
    "E-96 A","E-96 B","E-206","E-6 A","E-6 B","E-5 A","E-5 B",
    "E-12","E-3 C","E-17","E-4","E-3 A","E-3 B",
    "E-304","E-656","E-07","E-16","E-38","E-60","E-53",
    "E-68","E-61","E-410","E-411","E-412","E-413","E-414",
    "E-415","E-416","E-417","E-418","E-419","E-420","E-421",
]
CW_SET = {s.upper().replace(" ","") for s in CW_EXCHANGERS_RAW}
def is_cw(n):
    if pd.isna(n): return False
    return str(n).upper().replace(" ","") in CW_SET


# ─────────────────────────────────────────────────
# EVENT DEFINITIONS
# ─────────────────────────────────────────────────
PUMP_ALL_EVENTS = [
    "seal_failure","low_level","pump_swap","startup","shutdown",
    "trip_fault","low_pressure","oil_lubrication","steam_issue","strainer_clean",
]
PUMP_EVENTS_FULL_SET = PUMP_ALL_EVENTS

EXCH_ALL_EVENTS = [
    "tube_leak","tube_plug","tube_repair","tube_bundle_replace",
    "tube_installed","tube_cleaning","hydroblast_cleaning",
    "installing_plates","gasket_installed","pressure_test",
    "temp_cooler_replace","transmitter_blowdown","drained_oil",
    "bypass_isolation","sv_repair_replacement","steam_issue",
    "n2_purging","dew_point_check","install_heater",
    "capital_project","cleaning","work_completed",
]
EXCH_EVENTS_FULL_SET = EXCH_ALL_EVENTS + ["maintenance"]

PUMP_COLORS_MAP = {
    "seal_failure":"#2563eb","low_level":"#6366f1","pump_swap":"#d97706",
    "startup":"#059669","shutdown":"#64748b","trip_fault":"#7c3aed",
    "low_pressure":"#0891b2","oil_lubrication":"#be185d","steam_issue":"#ea580c",
    "strainer_clean":"#65a30d","maintenance_pm":"#78350f",
}
EXCH_COLORS_MAP = {
    "tube_leak":"#dc2626","tube_plug":"#f59e0b","tube_repair":"#2563eb",
    "tube_bundle_replace":"#7c3aed","tube_installed":"#0284c7","tube_cleaning":"#06b6d4",
    "hydroblast_cleaning":"#059669","installing_plates":"#84cc16","gasket_installed":"#d97706",
    "pressure_test":"#f97316","temp_cooler_replace":"#be185d","transmitter_blowdown":"#0891b2",
    "drained_oil":"#94a3b8","bypass_isolation":"#475569","sv_repair_replacement":"#c026d3",
    "steam_issue":"#ea580c","n2_purging":"#65a30d","dew_point_check":"#0d9488",
    "install_heater":"#92400e","capital_project":"#78350f","cleaning":"#4d7c0f",
    "maintenance":"#334155","work_completed":"#1d4ed8",
}
FALLBACK_COLORS = ["#6366f1","#f43f5e","#10b981","#f97316","#8b5cf6",
                   "#06b6d4","#84cc16","#ec4899","#14b8a6","#ef4444"]

CW_COLOR    = "#0891b2"
NONCW_COLOR = "#d97706"
SHIFT_COLORS = {"Day":"#0d9488","Night":"#475569"}
PLOT_BG  = "#f8fafc"
GRID_CLR = "#cbd5e1"
FIGSIZE  = (6, 3)
BAR_W    = 0.50

def make_colors(events, cmap):
    out = {}; fi = 0
    for e in events:
        out[e] = cmap[e] if e in cmap else FALLBACK_COLORS[fi % len(FALLBACK_COLORS)]; fi += 1
    return out


# ─────────────────────────────────────────────────
# LOAD DATA
# ─────────────────────────────────────────────────
@st.cache_data
def load_pump():
    df = pd.read_csv("classified_output.csv")
    df["date"]     = pd.to_datetime(df["date"], errors="coerce")
    df             = df[df["pump"].notna()]
    df["month_dt"] = df["date"].dt.to_period("M").dt.to_timestamp()
    df["month"]    = df["month_dt"].dt.strftime("%B-%Y")
    for c in PUMP_EVENTS_FULL_SET + ["maintenance_pm"]:
        if c not in df.columns: df[c] = 0
        df[c] = pd.to_numeric(df[c], errors="coerce").fillna(0).astype(int)
    return df

@st.cache_data
def load_exchanger():
    df = pd.read_csv("exchanger_classified_final.csv")
    df = df[[c for c in df.columns if not c.startswith("[")]]
    df["shift"]    = df["shift"].str.strip().replace({"Days":"Day","Nights":"Night"})
    df["date"]     = pd.to_datetime(df["date"], errors="coerce")
    df             = df[df["exchanger"].notna()]
    df["month_dt"] = df["date"].dt.to_period("M").dt.to_timestamp()
    df["month"]    = df["month_dt"].dt.strftime("%B-%Y")
    df["is_cw"]    = df["exchanger"].apply(is_cw)
    for c in EXCH_EVENTS_FULL_SET:
        if c not in df.columns: df[c] = 0
        df[c] = pd.to_numeric(df[c], errors="coerce").fillna(0).astype(int)
    return df

pump_df = load_pump()
exch_df = load_exchanger()


# ─────────────────────────────────────────────────
# PLOT HELPERS
# ─────────────────────────────────────────────────
def border(ax):
    for sp in ax.spines.values():
        sp.set_visible(True); sp.set_linewidth(1.5); sp.set_color("black")

def style_bar(ax):
    ax.set_facecolor(PLOT_BG)
    ax.grid(axis='y', linestyle='--', linewidth=0.6, alpha=0.6, color=GRID_CLR)
    ax.grid(axis='x', visible=False)
    ax.tick_params(colors="black", labelsize=6.5)
    border(ax)

def wrap_plot(title, draw_fn, figsize=FIGSIZE):
    st.markdown(f'<div class="plot-box"><div class="plot-title">{title}</div>',
                unsafe_allow_html=True)
    fig, ax = plt.subplots(figsize=figsize, facecolor=PLOT_BG)
    fig.patch.set_facecolor(PLOT_BG)
    draw_fn(ax)
    plt.tight_layout(pad=0.5)
    st.pyplot(fig, use_container_width=True)
    plt.close(fig)
    st.markdown('</div>', unsafe_allow_html=True)

def get_shift(grouped, name, months_labels, events):
    try:    return grouped.xs(name, level=1).reindex(months_labels).fillna(0)
    except: return pd.DataFrame(0, index=months_labels, columns=events)

def safe_label(ax, xp, y_top, text, y_ceil, fontsize=6.2, color="#1e293b"):
    margin = y_ceil * 0.02
    y = min(y_top + margin, y_ceil * 0.96)
    ax.text(xp, y, text, ha="center", va="bottom",
            fontsize=fontsize, fontweight="bold", color=color, clip_on=True)

def inner_label(ax, xp, y_base, height, text, fontsize=5.8, color="white"):
    yrange = ax.get_ylim()[1] - ax.get_ylim()[0]
    if yrange == 0 or height / yrange < 0.07: return
    ax.text(xp, y_base + height/2, text, ha="center", va="center",
            fontsize=fontsize, fontweight="bold", color=color, zorder=6, clip_on=True)


# ─────────────────────────────────────────────────
# DONUT
# ─────────────────────────────────────────────────
def top_n_others(series, colors, top_n=10):
    series = series[series > 0].sort_values(ascending=False)
    if series.empty: return pd.Series(dtype=float), {}, []
    if len(series) <= top_n:
        return series, {k: colors.get(k,"#94a3b8") for k in series.index}, []
    top  = series.iloc[:top_n]; rest = series.iloc[top_n:]
    result = pd.concat([top, pd.Series({"Others": rest.sum()})])
    oc = {k: colors.get(k,"#94a3b8") for k in top.index}; oc["Others"] = "#94a3b8"
    return result, oc, list(rest.index)

def top5_gt5pct(series, colors):
    tot = series.sum()
    if tot == 0: return pd.Series(dtype=float), {}
    filt = series[series/tot*100 > 5].nlargest(5)
    return filt, {k: colors.get(k,"#94a3b8") for k in filt.index}

def plot_donut(title, raw_series, all_colors,
               filter_top5=False, top_n=None, figsize=FIGSIZE):
    others_list = []
    if top_n is not None:
        data, colors, others_list = top_n_others(raw_series, all_colors, top_n)
    elif filter_top5:
        data, colors = top5_gt5pct(raw_series, all_colors)
    else:
        data   = raw_series.reindex(list(all_colors.keys())).fillna(0)
        data   = data[data > 0]
        colors = {k: all_colors.get(k,"#94a3b8") for k in data.index}

    if data.empty:
        st.markdown(f'<div class="plot-box"><div class="plot-title">{title}</div>'
                    f'<div class="no-data-msg">No data available</div></div>',
                    unsafe_allow_html=True)
        return

    total = data.sum()
    fig   = plt.figure(figsize=figsize, facecolor=PLOT_BG)
    fig.patch.set_facecolor(PLOT_BG)
    gs    = gridspec.GridSpec(1, 2, figure=fig, width_ratios=[0.50, 0.50],
                              left=0.01, right=0.99, top=0.97, bottom=0.05, wspace=0.0)
    ax_pie = fig.add_subplot(gs[0]); ax_leg = fig.add_subplot(gs[1])
    ax_pie.set_facecolor(PLOT_BG)
    for sp in ax_pie.spines.values(): sp.set_visible(False)

    wedge_colors = [colors.get(k,"#94a3b8") for k in data.index]
    _, _, autotexts = ax_pie.pie(
        data, colors=wedge_colors, startangle=90,
        wedgeprops=dict(width=0.40, edgecolor="white", linewidth=0.7),
        autopct=lambda p: f"{p:.0f}%" if p >= 7 else "",
        pctdistance=0.76, radius=0.88, center=(0, 0.06),
    )
    for at in autotexts: at.set_fontsize(6); at.set_color("white"); at.set_fontweight("bold")
    ax_pie.text(0, 0.06, f"Total\n{int(total)}", ha="center", va="center",
                fontsize=7.5, fontweight="bold", color="#1e293b")

    ax_leg.set_facecolor(PLOT_BG); ax_leg.axis("off")
    ax_leg.set_xlim(0,1); ax_leg.set_ylim(0,1)
    n = len(data); row_h = min(0.11, 0.90/max(n,1))
    pad_t = 0.95; hw = 0.09; hh = min(0.045, row_h*0.48)

    for i, (ft, val) in enumerate(data.items()):
        yc = pad_t - i*row_h
        if yc < 0.02: break
        c = colors.get(ft,"#94a3b8")
        ax_leg.add_patch(plt.Rectangle((0.01, yc-hh/2), hw, hh,
                                        transform=ax_leg.transAxes,
                                        color=c, clip_on=False, zorder=10))
        pct_val = val/total*100
        ax_leg.text(0.01+hw+0.05, yc,
                    f"{ft.replace('_',' ').title()}  {pct_val:.0f}%",
                    transform=ax_leg.transAxes,
                    fontsize=5.5, va="center", color="#1e293b",
                    clip_on=False, fontweight="600")

    if others_list:
        fig.text(0.01, 0.005, "Others: "+", ".join(e.replace("_"," ").title() for e in others_list),
                 fontsize=4.5, color="#64748b", ha="left", va="bottom")

    st.markdown(f'<div class="plot-box"><div class="plot-title">{title}</div>',
                unsafe_allow_html=True)
    st.pyplot(fig, use_container_width=True)
    plt.close(fig)
    st.markdown('</div>', unsafe_allow_html=True)


# ─────────────────────────────────────────────────
# CW OVERALL DONUT
# ─────────────────────────────────────────────────
def plot_cw_overall_donut(df, events, title="CW vs Non-CW Distribution"):
    cw_tot  = int(df[df["is_cw"]][events].sum().sum())
    ncw_tot = int(df[~df["is_cw"]][events].sum().sum())
    total   = cw_tot + ncw_tot
    if total == 0:
        st.markdown(f'<div class="plot-box"><div class="plot-title">{title}</div>'
                    '<div class="no-data-msg">No data</div></div>', unsafe_allow_html=True)
        return
    fig = plt.figure(figsize=FIGSIZE, facecolor=PLOT_BG)
    fig.patch.set_facecolor(PLOT_BG)
    gs  = gridspec.GridSpec(1,2, figure=fig, left=0.05, right=0.95,
                            top=0.82, bottom=0.12, wspace=0.38)
    for idx,(label,val,color) in enumerate([("CW",cw_tot,CW_COLOR),("Non-CW",ncw_tot,NONCW_COLOR)]):
        ax = fig.add_subplot(gs[idx])
        ax.set_facecolor(PLOT_BG)
        for sp in ax.spines.values(): sp.set_visible(False)
        ax.pie([val, total-val], colors=[color,"#e2e8f0"], startangle=90,
               wedgeprops=dict(width=0.38, edgecolor="white", linewidth=0.7),
               radius=0.88, center=(0,0))
        pct = val/total*100 if total>0 else 0
        ax.text(0, 0.10, f"{val}",      ha="center", va="center", fontsize=11, fontweight="bold", color=color)
        ax.text(0,-0.20, f"{pct:.1f}%", ha="center", va="center", fontsize=8,  color="#475569")
        ax.set_title(label, fontsize=9, fontweight="bold", color=color, pad=3)
    st.markdown(f'<div class="plot-box"><div class="plot-title">{title}</div>',
                unsafe_allow_html=True)
    st.pyplot(fig, use_container_width=True)
    plt.close(fig)
    st.markdown('</div>', unsafe_allow_html=True)


# ─────────────────────────────────────────────────
# KPI CARDS
# ─────────────────────────────────────────────────
def render_kpi(df, events, months_labels):
    total_ev  = int(df[events].sum().sum())
    total_mon = len(months_labels)
    avg_pm    = round(total_ev / max(total_mon,1), 1)
    ev_by_mon = df.groupby("month")[events].sum().reindex(months_labels).fillna(0).sum(axis=1)
    peak_mon  = ev_by_mon.idxmax() if not ev_by_mon.empty else "—"
    peak_val  = int(ev_by_mon.max()) if not ev_by_mon.empty else 0
    ev_totals = df[events].sum().sort_values(ascending=False)
    top_ev    = ev_totals.index[0].replace("_"," ").title() if len(ev_totals)>0 else "—"
    top_ev_c  = int(ev_totals.iloc[0]) if len(ev_totals)>0 else 0
    st.markdown(f"""
    <div class="kpi-row">
      <div class="kpi-card c1">
        <div class="kpi-label">Total Events</div>
        <div class="kpi-value">{total_ev:,}</div>
        <div class="kpi-sub">All periods combined</div>
      </div>
      <div class="kpi-card c2">
        <div class="kpi-label">Avg / Month</div>
        <div class="kpi-value">{avg_pm}</div>
        <div class="kpi-sub">Across {total_mon} months</div>
      </div>
      <div class="kpi-card c3">
        <div class="kpi-label">Peak Month</div>
        <div class="kpi-value" style="font-size:10px;padding-top:2px;">{peak_mon}</div>
        <div class="kpi-sub">{peak_val} events recorded</div>
      </div>
      <div class="kpi-card c4">
        <div class="kpi-label">Top Event</div>
        <div class="kpi-value" style="font-size:10px;padding-top:2px;">{top_ev}</div>
        <div class="kpi-sub">{top_ev_c} occurrences</div>
      </div>
    </div>""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────
# TITLE & NAV
# ─────────────────────────────────────────────────
st.markdown("<div class='dash-title'>Equipment Reliability Dashboard</div>",
            unsafe_allow_html=True)

# ── Single row: [Equipment dropdown] [Overall] [Monthly] [Equipment] ──
# Use equal column widths so buttons are same size and everything is centred
c0, c1, c2, c3 = st.columns([1, 1, 1, 1])

with c0:
    equip = st.selectbox("", ["Pump","Exchanger"],
                         key="equip_sel", label_visibility="collapsed")

nav_key = f"page_{equip}"
if nav_key not in st.session_state:
    st.session_state[nav_key] = "Overall"

with c1:
    if st.button("Overall Analysis", key=f"btn_ov_{equip}"):
        st.session_state[nav_key] = "Overall"; st.rerun()
with c2:
    if st.button("Monthly Analysis", key=f"btn_mo_{equip}"):
        st.session_state[nav_key] = "Monthly"; st.rerun()
with c3:
    if st.button(f"{equip} Analysis", key=f"btn_eq_{equip}"):
        st.session_state[nav_key] = "Equipment"; st.rerun()

page = st.session_state[nav_key]
PAGE_KEYS = {"Overall":f"btn_ov_{equip}","Monthly":f"btn_mo_{equip}","Equipment":f"btn_eq_{equip}"}
active_key = PAGE_KEYS[page]

# Active nav button colour
st.markdown(f"""
<script>
(function(){{
  const ak = "{active_key}";
  const pm = {{"Overall Analysis":"{PAGE_KEYS['Overall']}",
               "Monthly Analysis":"{PAGE_KEYS['Monthly']}",
               "{equip} Analysis":"{PAGE_KEYS['Equipment']}"}};

  function styleBtn(btn, active){{
    if(active){{
      btn.style.cssText = btn.style.cssText +
        ';background-color:#ffffff !important' +
        ';color:#1e293b !important' +
        ';border:2px solid #1e293b !important' +
        ';outline:none !important' +
        ';box-shadow:none !important';
      btn.querySelectorAll('*').forEach(el=>{{
        el.style.setProperty('color','#1e293b','important');
      }});
    }} else {{
      btn.style.cssText = btn.style.cssText +
        ';background-color:#1e293b !important' +
        ';color:#ffffff !important' +
        ';border:1px solid #334155 !important';
      btn.querySelectorAll('*').forEach(el=>{{
        el.style.setProperty('color','#ffffff','important');
      }});
    }}
  }}

  function apply(){{
    window.parent.document.querySelectorAll('.stButton button').forEach(btn=>{{
      const t = btn.innerText.trim();
      if(pm[t]===ak){{
        btn.dataset.navActive = '1';
        styleBtn(btn, true);
      }} else if(pm[t]){{
        delete btn.dataset.navActive;
        styleBtn(btn, false);
      }}
    }});
  }}

  // Re-enforce active button on every mouseover/focus so hover CSS can't win
  window.parent.document.addEventListener('mouseover', function(e){{
    const btn = e.target.closest('button');
    if(btn && btn.dataset.navActive === '1') styleBtn(btn, true);
  }}, true);
  window.parent.document.addEventListener('focusin', function(e){{
    const btn = e.target.closest('button');
    if(btn && btn.dataset.navActive === '1') styleBtn(btn, true);
  }}, true);

  apply();
  [100,300,600,1200,2500].forEach(t=>setTimeout(apply,t));
  new MutationObserver(apply).observe(window.parent.document.body,{{childList:true,subtree:true}});
}})();
</script>
""", unsafe_allow_html=True)

st.markdown("<hr>", unsafe_allow_html=True)


# ─────────────────────────────────────────────────
# ACTIVE CONFIG
# ─────────────────────────────────────────────────
if equip == "Pump":
    df = pump_df.copy(); eq_col="pump"; info_col="pump_info"
    EVENTS      = [e for e in PUMP_ALL_EVENTS    if e in df.columns]
    EVENTS_FULL = [e for e in PUMP_EVENTS_FULL_SET+["maintenance_pm"] if e in df.columns]
    COLORS      = make_colors(EVENTS,      PUMP_COLORS_MAP)
    COLORS_FULL = make_colors(EVENTS_FULL, PUMP_COLORS_MAP)
else:
    df = exch_df.copy(); eq_col="exchanger"; info_col="exchanger_info"
    EVENTS      = [e for e in EXCH_ALL_EVENTS    if e in df.columns]
    EVENTS_FULL = [e for e in EXCH_EVENTS_FULL_SET if e in df.columns]
    COLORS      = make_colors(EVENTS,      EXCH_COLORS_MAP)
    COLORS_FULL = make_colors(EVENTS_FULL, EXCH_COLORS_MAP)

months_sorted = sorted(df["month_dt"].dropna().unique())
months_labels = [pd.to_datetime(m).strftime("%B-%Y") for m in months_sorted]
x = np.arange(len(months_labels))

render_kpi(df, EVENTS, months_labels)


# ══════════════════════════════════════════════════
# OVERALL ANALYSIS
# ══════════════════════════════════════════════════
if page == "Overall":

    if equip == "Exchanger":
        colA, colB, _ = st.columns([1, 1, 6])
        with colA:
            shift_on = st.selectbox("Shift Bifurcation", ["OFF","ON"],
                                    index=0, key=f"bif_{equip}") == "ON"
        with colB:
            cw_filter_ov = st.selectbox(
                "CW Bifurcation",
                ["All", "CW Only", "Non-CW Only"],
                index=0, key=f"cw_bif_ov_{equip}"
            )
    else:
        colA, _ = st.columns([1, 7])
        with colA:
            shift_on = st.selectbox("Shift Bifurcation", ["OFF","ON"],
                                    index=0, key=f"bif_{equip}") == "ON"
        cw_filter_ov = "All"

    if equip == "Exchanger":
        if cw_filter_ov == "CW Only":
            df_donut = df[df["is_cw"]]; donut_suffix = " (CW Only)"
        elif cw_filter_ov == "Non-CW Only":
            df_donut = df[~df["is_cw"]]; donut_suffix = " (Non-CW Only)"
        else:
            df_donut = df; donut_suffix = ""
    else:
        df_donut = df; donut_suffix = ""

    if not shift_on:
        col1, col2 = st.columns(2, gap="small")
        with col1:
            def draw_dn(ax):
                grp   = df.groupby(["month","shift"])[EVENTS].sum()
                day   = get_shift(grp,"Day",  months_labels, EVENTS)
                night = get_shift(grp,"Night",months_labels, EVENTS)
                dt = day.sum(axis=1).values; nt = night.sum(axis=1).values
                totals = dt + nt
                y_max = max(totals.max(), 1)
                ax.set_ylim(0, y_max * 1.15)
                ax.bar(x, dt, width=BAR_W, color=SHIFT_COLORS["Day"],
                       edgecolor="white", linewidth=0.6, label="Day")
                ax.bar(x, nt, width=BAR_W, bottom=dt,
                       color=SHIFT_COLORS["Night"], edgecolor="white",
                       linewidth=0.6, hatch="//", label="Night")
                for i in range(len(x)):
                    inner_label(ax, x[i], 0,     dt[i], "D")
                    inner_label(ax, x[i], dt[i], nt[i], "N")
                ax.set_xticks(x)
                ax.set_xticklabels(months_labels, rotation=30, ha='right', fontsize=6.5)
                ax.set_ylabel("Event Count", fontsize=6.5, color="black")
                ax.legend(fontsize=6.5, loc='upper left', framealpha=0.9, edgecolor="black")
                style_bar(ax)
            wrap_plot("Monthly Event Trend  (Day | Night)", draw_dn)
        with col2:
            if equip == "Exchanger":
                plot_donut(f"Event Distribution{donut_suffix}",
                           df_donut[EVENTS].sum(), COLORS, top_n=10)
            else:
                plot_donut("Overall Event Distribution",
                           df[EVENTS].sum(), COLORS, filter_top5=True)

    else:
        col1, col2 = st.columns(2, gap="small")
        with col1:
            def draw_dual(ax):
                grp   = df.groupby(["month","shift"])[EVENTS].sum()
                day   = get_shift(grp,"Day",  months_labels, EVENTS)
                night = get_shift(grp,"Night",months_labels, EVENTS)
                w = BAR_W/2
                bd = np.zeros(len(months_labels)); bn = np.zeros(len(months_labels))
                for ev in EVENTS:
                    ax.bar(x-w/2, day[ev].values,   width=w, bottom=bd,
                           color=COLORS[ev], edgecolor="white", linewidth=0.4)
                    ax.bar(x+w/2, night[ev].values, width=w, bottom=bn,
                           color=COLORS[ev], edgecolor="white", linewidth=0.4)
                    bd += day[ev].values; bn += night[ev].values
                y_max = max(max(bd.max(), bn.max()), 1)
                ax.set_ylim(0, y_max * 1.15)
                for i in range(len(x)):
                    if bd[i]>0: safe_label(ax, x[i]-w/2, bd[i], "D", y_max*1.15, color="black")
                    if bn[i]>0: safe_label(ax, x[i]+w/2, bn[i], "N", y_max*1.15, color="black")
                ax.set_xticks(x)
                ax.set_xticklabels(months_labels, rotation=30, ha='right', fontsize=6.5)
                ax.set_ylabel("Event Count", fontsize=6.5, color="black")
                style_bar(ax)
            wrap_plot("Monthly Event Trend  (Shift × Event Type)", draw_dual)
        with col2:
            if equip == "Exchanger":
                plot_donut(f"Event Distribution{donut_suffix}",
                           df_donut[EVENTS].sum(), COLORS, top_n=10)
            else:
                plot_donut("Overall Event Distribution",
                           df[EVENTS].sum(), COLORS, filter_top5=True)


# ══════════════════════════════════════════════════
# MONTHLY ANALYSIS
# ══════════════════════════════════════════════════
elif page == "Monthly":

    if equip == "Exchanger":
        colA, colB, _ = st.columns([1, 1, 6])
        with colA:
            month_list     = df.sort_values("month_dt")["month"].dropna().unique()
            selected_month = st.selectbox("Select Month", month_list, key=f"mon_{equip}")
        with colB:
            cw_filter = st.selectbox("CW Filter",
                                     ["All","CW Only","Non-CW Only"],
                                     index=0, key=f"cw_filter_{equip}")
    else:
        colA, _ = st.columns([1, 7])
        with colA:
            month_list     = df.sort_values("month_dt")["month"].dropna().unique()
            selected_month = st.selectbox("Select Month", month_list, key=f"mon_{equip}")
        cw_filter = "All"

    fdf = df[df["month"] == selected_month].copy()
    if equip == "Exchanger":
        if cw_filter == "CW Only":       fdf = fdf[fdf["is_cw"]]
        elif cw_filter == "Non-CW Only": fdf = fdf[~fdf["is_cw"]]

    suffix = f"  [{cw_filter}]" if equip=="Exchanger" and cw_filter!="All" else ""

    col1, col2 = st.columns(2, gap="small")

    with col1:
        if equip == "Exchanger" and cw_filter == "All":
            grp_all = fdf.groupby(eq_col)[EVENTS].sum()
            grp_all["_tot"] = grp_all.sum(axis=1)
            grp_all = grp_all[grp_all["_tot"] > 0]
            top7    = grp_all.sort_values("_tot", ascending=False).head(7).index
            cw_v  = np.array([int(fdf[fdf["is_cw"]  &(fdf[eq_col]==e)][EVENTS].sum().sum()) for e in top7])
            ncw_v = np.array([int(fdf[~fdf["is_cw"] &(fdf[eq_col]==e)][EVENTS].sum().sum()) for e in top7])
            totals = cw_v + ncw_v
            def draw_mcw(ax):
                xi = np.arange(len(top7))
                y_max = max(totals.max(), 1)
                ax.set_ylim(0, y_max * 1.18)
                ax.bar(xi, cw_v,  width=BAR_W, color=CW_COLOR,
                       edgecolor="white", linewidth=0.6, label="CW")
                ax.bar(xi, ncw_v, width=BAR_W, bottom=cw_v,
                       color=NONCW_COLOR, edgecolor="white", linewidth=0.6,
                       hatch="//", label="Non-CW")
                grand = totals.sum()
                for i, tot in enumerate(totals):
                    inner_label(ax, xi[i], 0,       cw_v[i],  "CW", fontsize=5.5)
                    inner_label(ax, xi[i], cw_v[i], ncw_v[i], "NC", fontsize=5.5)
                    if tot>0 and grand>0:
                        safe_label(ax, xi[i], tot, f"{tot/grand*100:.0f}%",
                                   y_max*1.18, fontsize=6)
                ax.set_xticks(xi)
                ax.set_xticklabels(top7, rotation=25, ha='right', fontsize=6.5)
                ax.set_ylabel("Event Count", fontsize=6.5, color="black")
                ax.legend(fontsize=6.5, loc='upper right', framealpha=0.9, edgecolor="black")
                style_bar(ax)
            wrap_plot(f"Top 7 Exchangers — CW/Non-CW  —  {selected_month}", draw_mcw)
        else:
            grp = fdf.groupby(eq_col)[EVENTS].sum()
            grp["_tot"] = grp.sum(axis=1)
            grp = grp[grp["_tot"] > 0]
            top7_names  = grp.sort_values("_tot", ascending=False).head(7).index
            ev_tot_m    = fdf[EVENTS].sum().sort_values(ascending=False)
            top5_ev     = list(ev_tot_m[ev_tot_m > 0].index[:5])
            top7_df     = grp.loc[top7_names, [e for e in top5_ev if e in grp.columns]]

            def draw_ev(ax):
                ev_cols = [e for e in top5_ev if e in top7_df.columns]
                bot = np.zeros(len(top7_df))
                for ev in ev_cols:
                    ax.bar(top7_df.index, top7_df[ev], bottom=bot,
                           width=BAR_W, color=COLORS.get(ev,"#94a3b8"),
                           edgecolor="white", linewidth=0.5)
                    bot += top7_df[ev].values
                y_max = max(bot.max(), 1)
                ax.set_ylim(0, y_max * 1.18)
                grand = bot.sum()
                for i, tot in enumerate(bot):
                    if tot>0 and grand>0:
                        safe_label(ax, i, tot, f"{tot/grand*100:.0f}%",
                                   y_max*1.18, fontsize=6)
                ax.set_xticks(range(len(top7_df)))
                ax.set_xticklabels(top7_df.index, rotation=25, ha='right', fontsize=6.5)
                ax.set_ylabel("Event Count", fontsize=6.5, color="black")
                style_bar(ax)

            lbl = "Pumps" if equip=="Pump" else "Exchangers"
            wrap_plot(f"Top 7 {lbl} — Top 5 Events  —  {selected_month}{suffix}", draw_ev)

    with col2:
        if equip == "Exchanger":
            plot_donut(f"Top Events  —  {selected_month}{suffix}",
                       fdf[EVENTS].sum(), COLORS, top_n=10)
        else:
            plot_donut(f"Top Events  —  {selected_month}",
                       fdf[EVENTS].sum(), COLORS, filter_top5=True)


# ══════════════════════════════════════════════════
# EQUIPMENT ANALYSIS
# ══════════════════════════════════════════════════
elif page == "Equipment":

    if equip == "Exchanger":
        colA, colB, _ = st.columns([1, 1, 6])
        with colA:
            cw_eq_filter = st.selectbox("CW Filter",["All","CW Only","Non-CW Only"],
                                        index=0, key=f"cw_eq_{equip}")
        eq_sub = df.copy()
        if cw_eq_filter=="CW Only":       eq_sub = df[df["is_cw"]]
        elif cw_eq_filter=="Non-CW Only": eq_sub = df[~df["is_cw"]]
        eq_list = (eq_sub.groupby(eq_col)[EVENTS_FULL].sum()
                   .sum(axis=1).sort_values(ascending=False).index.tolist())
        with colB:
            selected_eq = st.selectbox("Select Exchanger", eq_list, key=f"sel_{equip}")
    else:
        colA, _ = st.columns([1, 7])
        eq_list = (df.groupby(eq_col)[EVENTS_FULL].sum()
                   .sum(axis=1).sort_values(ascending=False).index.tolist())
        with colA:
            selected_eq = st.selectbox(f"Select {equip}", eq_list, key=f"sel_{equip}")

    eq_df = df[df[eq_col] == selected_eq]

    if equip == "Exchanger":
        cw_label    = "CW" if is_cw(selected_eq) else "Non-CW"
        donut_title = f"Top Events  —  {selected_eq}  [{cw_label}]"
    else:
        donut_title = f"Top Events  —  {selected_eq}"

    col1, col2 = st.columns(2, gap="small")
    with col1:
        st.markdown('<div class="plot-box"><div class="plot-title">Equipment History</div>',
                    unsafe_allow_html=True)
        hist = eq_df[["date","shift",info_col]].sort_values("date").copy()
        hist.columns = ["Date","Shift","Event Info"]
        if hist.empty:
            st.markdown('<div class="no-data-msg">No data available</div>', unsafe_allow_html=True)
        else:
            st.dataframe(hist, use_container_width=True, height=260)
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        ev_sum = eq_df[EVENTS_FULL].sum()
        ev_sum = ev_sum[ev_sum > 0]
        plot_donut(donut_title, ev_sum,
                   make_colors(EVENTS_FULL, PUMP_COLORS_MAP if equip=="Pump" else EXCH_COLORS_MAP),
                   top_n=10)
