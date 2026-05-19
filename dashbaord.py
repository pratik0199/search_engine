import pandas as pd
import numpy as np
import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.lines import Line2D

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
div[data-testid="stVerticalBlock"] > div { gap: 0rem !important; }
div[data-testid="stHorizontalBlock"] { margin-top: 0 !important; margin-bottom: 0 !important; }
div[data-testid="column"] { padding: 0 3px !important; }
div.stButton > button {
    width: 200%;
    border-radius: 4px;
    height: 26px !important;
    min-height: 28px !important;
    font-weight: 700;
    font-size: 18px;
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
    color: white !important; font-weight: 500 !important; font-size: 13px !important;
}
div.stButton > button:hover { background-color: #0f172a; }
div.stButton > button:active { transform: scale(0.97); }
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
.kpi-row { display:flex; gap:20px; margin-bottom:0px; margin-top:0px; }
.kpi-card {
    flex:1; background:#f8fafc; border:1.5px solid #1e293b; border-left:3px solid #1e293b;
    border-radius:5px; padding:2px 6px 2px 6px; min-width:0;
    font-family:"Times New Roman",serif; text-align:center;
}
.kpi-label { font-size:8.5px; font-weight:900; color:#1e293b; text-transform:uppercase; letter-spacing:0.7px; margin-bottom:0px; }
.kpi-value { font-size:13px; font-weight:700; color:#1e293b; line-height:1.05; font-family:"Times New Roman",serif; }
.kpi-sub   { font-size:8.5px; font-weight:700; color:#334155; margin-top:0px; font-family:"Times New Roman",serif; }
.kpi-card.c1{border-left-color:#2563eb;} .kpi-card.c1 .kpi-value{color:#2563eb;}
.kpi-card.c2{border-left-color:#65a30d;} .kpi-card.c2 .kpi-value{color:#65a30d;}
.kpi-card.c3{border-left-color:#d97706;} .kpi-card.c3 .kpi-value{color:#d97706;}
.kpi-card.c4{border-left-color:#7c3aed;} .kpi-card.c4 .kpi-value{color:#7c3aed;}
.plot-box {
    border:1.5px solid black; border-radius:5px;
    padding:2px 4px 1px 4px; background:#f8fafc; margin-bottom:3px;
}
.plot-title {
    font-size:12px; font-weight:700; color:#1e293b; margin-bottom:0px;
    font-family:"Times New Roman",serif; text-align:center; line-height:1.2;
}
.no-data-msg {
    color:#64748b; font-size:12px; font-family:"Times New Roman",serif;
    text-align:center; padding:30px 8px;
}
.dash-title {
    text-align:center; color:#1e293b; font-family:"Times New Roman",serif;
    font-size:28px; font-weight:700; margin:1px 0 0px 0; padding:0;
}
div[data-testid="stDataFrame"] table { font-family: "Times New Roman", serif !important; font-size: 11px !important; }
div[data-testid="stDataFrame"] th {
    background-color: #1e293b !important; color: white !important;
    font-size: 10px !important; font-weight: 700 !important;
    text-transform: uppercase !important; letter-spacing: 0.5px !important; padding: 4px 6px !important;
}
div[data-testid="stDataFrame"] td { font-size: 11px !important; padding: 3px 6px !important; color: #1e293b !important; }
hr { margin:0px 0 0px 0 !important; border-color:#94a3b8; }
header { visibility:hidden; } footer { visibility:hidden; }
[data-testid="stAppViewContainer"] > section > div:first-child { padding-top: 0 !important; }
div[data-testid="stVerticalBlock"] > div:has(hr) + div { margin-top: 0 !important; padding-top: 0 !important; }
</style>

<script>
(function(){
  const BIF_LABELS = [
    "Shift Bifurcation","CW Bifurcation","CW Filter","Select Month",
    "Select Exchanger","Select Pump","Select Event"
  ];
  function applyAll(){
    const doc = window.parent.document;
    doc.querySelectorAll('[data-testid="stSelectbox"]').forEach(function(box){
      const label = box.querySelector(':scope > label');
      if(!label) return;
      const txt = label.innerText.trim();
      if(txt === "" || txt === "Pump" || txt === "Exchanger") return;
      if(!BIF_LABELS.some(l => txt.includes(l.split(" ")[0]))) return;
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
      if(!box.dataset.inlined){
        box.dataset.inlined = "1";
        box.style.setProperty('display','flex','important');
        box.style.setProperty('flex-direction','row','important');
        box.style.setProperty('align-items','center','important');
        box.style.setProperty('gap','7px','important');
        box.style.setProperty('flex-wrap','nowrap','important');
        box.style.setProperty('margin-bottom','0','important');
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
# COLOUR MAPS
# ─────────────────────────────────────────────────
PUMP_COLORS_MAP = {
    "seal_failure":"#2563eb","low_level":"#6366f1","pump_swap":"#d97706",
    "startup":"#059669","shutdown":"#64748b","trip_fault":"#be185d",
    "low_pressure":"#0891b2","oil_lubrication":"#be185d","steam_issue":"#ea580c",
    "strainer_clean":"#65a30d","maintenance_pm":"#78350f","vibration":"#7c3aed",
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
FIGSIZE  = (6.8, 2.8)
BAR_W    = 0.50

def make_colors(events, cmap):
    out = {}; fi = 0
    for e in events:
        out[e] = cmap[e] if e in cmap else FALLBACK_COLORS[fi % len(FALLBACK_COLORS)]; fi += 1
    return out

# title-case event label → snake_case key for color lookup
def _snake(label):
    return label.lower().replace(" ", "_")


# ─────────────────────────────────────────────────
# LOAD EPISODE DATA  (single source of truth)
# episode_log.xlsx already has the correct episode counts.
# We use it for:
#   • KPI cards  (total, avg/month, peak month, top event)
#   • Donut charts (episode counts per event)
#   • Bar charts  (episode counts per equipment, per month)
#   • Event Analysis tab (episode log table + top-5 bar)
# The raw CSVs are used ONLY for the Equipment History table.
# ─────────────────────────────────────────────────
EPISODE_LOG_PATH = "episode_log.xlsx"

@st.cache_data
def load_episodes():
    exch = pd.read_excel(EPISODE_LOG_PATH, sheet_name="Exchanger Episodes")
    pump = pd.read_excel(EPISODE_LOG_PATH, sheet_name="Pump Episodes")
    for df in [exch, pump]:
        df["start_dt"] = pd.to_datetime(df["Start Date"], dayfirst=True, errors="coerce")
        df["month_dt"] = df["start_dt"].dt.to_period("M").dt.to_timestamp()
        df["month"]    = df["start_dt"].dt.strftime("%B-%Y")
        df["snake_ev"] = df["Event"].apply(_snake)
    exch["is_cw"] = exch["Equipment"].apply(is_cw)
    return exch, pump

@st.cache_data
def load_raw_pump():
    df = pd.read_csv("classified_output.csv")
    df["date"]  = pd.to_datetime(df["date"], errors="coerce")
    df["shift"] = df["shift"].str.strip().replace({"Days":"Day","Nights":"Night"})
    return df[df["pump"].notna() & df["date"].notna()]

@st.cache_data
def load_raw_exchanger():
    df = pd.read_csv("exchanger_classified_final.csv")
    df = df[[c for c in df.columns if not c.startswith("[")]]
    df["shift"] = df["shift"].str.strip().replace({"Days":"Day","Nights":"Night"})
    df["date"]  = pd.to_datetime(df["date"], errors="coerce")
    return df[df["exchanger"].notna() & df["date"].notna()]

exch_ep, pump_ep = load_episodes()


# ─────────────────────────────────────────────────
# HELPER: build a "wide" episode-count dataframe
# rows = months, cols = events  → used for bar + donut
# ─────────────────────────────────────────────────
def ep_pivot(ep_df, months_labels, group_col="snake_ev", eq_filter=None):
    """
    Returns a monthly × event pivot of episode counts.
    Optionally filters to a specific equipment (eq_filter = equipment name).
    """
    df = ep_df.copy()
    if eq_filter is not None:
        df = df[df["Equipment"] == eq_filter]
    piv = (df.groupby(["month", group_col])
             .size()
             .unstack(fill_value=0)
             .reindex(months_labels, fill_value=0))
    return piv

def ep_counts_by_equip(ep_df, events_snake):
    """Episode count per equipment for the given event snake-keys."""
    df = ep_df[ep_df["snake_ev"].isin(events_snake)]
    return df.groupby("Equipment").size().sort_values(ascending=False)

def ep_series(ep_df, months_labels=None, cw_filter="All"):
    """Series: snake_event → total episode count (optionally CW-filtered)."""
    df = ep_df.copy()
    if cw_filter == "CW Only":      df = df[df["is_cw"]]
    elif cw_filter == "Non-CW Only":df = df[~df["is_cw"]]
    s = df.groupby("snake_ev").size()
    return s


# ─────────────────────────────────────────────────
# PLOT HELPERS  (unchanged from original)
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
# DONUT  (unchanged from original)
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
# KPI CARDS  — driven by episode data
# ─────────────────────────────────────────────────
def render_kpi(ep_df, months_labels, cw_filter="All"):
    df = ep_df.copy()
    if cw_filter == "CW Only"      and "is_cw" in df.columns: df = df[df["is_cw"]]
    elif cw_filter == "Non-CW Only" and "is_cw" in df.columns: df = df[~df["is_cw"]]

    total_ev  = len(df)
    total_mon = len(months_labels)
    avg_pm    = round(total_ev / max(total_mon, 1), 1)

    # peak month by episode count
    mon_counts = df.groupby("month").size().reindex(months_labels, fill_value=0)
    peak_mon   = mon_counts.idxmax() if not mon_counts.empty and mon_counts.max() > 0 else "—"
    peak_val   = int(mon_counts.max()) if not mon_counts.empty else 0

    # top event
    ev_counts = df.groupby("Event").size().sort_values(ascending=False)
    top_ev    = ev_counts.index[0] if len(ev_counts) > 0 else "—"
    top_ev_c  = int(ev_counts.iloc[0]) if len(ev_counts) > 0 else 0

    st.markdown(f"""
    <div class="kpi-row">
      <div class="kpi-card c1">
        <div class="kpi-label">Total Episodes</div>
        <div class="kpi-value">{total_ev:,}</div>
        <div class="kpi-sub">Unique job starts</div>
      </div>
      <div class="kpi-card c2">
        <div class="kpi-label">Avg / Month</div>
        <div class="kpi-value">{avg_pm}</div>
        <div class="kpi-sub">Across {total_mon} months</div>
      </div>
      <div class="kpi-card c3">
        <div class="kpi-label">Peak Month</div>
        <div class="kpi-value" style="font-size:9px;padding-top:1px;">{peak_mon}</div>
        <div class="kpi-sub">{peak_val} episodes</div>
      </div>
      <div class="kpi-card c4">
        <div class="kpi-label">Top Event</div>
        <div class="kpi-value" style="font-size:9px;padding-top:1px;">{top_ev}</div>
        <div class="kpi-sub">{top_ev_c} episodes</div>
      </div>
    </div>""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────
# TITLE & NAV  (unchanged)
# ─────────────────────────────────────────────────
st.markdown("<div class='dash-title'>Equipment Reliability Dashboard</div>",
            unsafe_allow_html=True)
st.markdown("""
<style>
div.stButton > button p,
div.stButton > button span,
div.stButton > button div,
div.stButton > button { font-size: 13px !important; white-space: nowrap !important; }
</style>
""", unsafe_allow_html=True)

c0, c1, c2, c3, c4 = st.columns([0.7, 1, 1, 1.15, 1])
with c0:
    equip = st.selectbox("", ["Pump","Exchanger"], key="equip_sel", label_visibility="collapsed")

nav_key = f"page_{equip}"
if nav_key not in st.session_state:
    st.session_state[nav_key] = "Overall"

with c1:
    if st.button("Overall Analysis", key=f"btn_ov_{equip}"): st.session_state[nav_key]="Overall"; st.rerun()
with c2:
    if st.button("Monthly Analysis", key=f"btn_mo_{equip}"): st.session_state[nav_key]="Monthly"; st.rerun()
with c3:
    btn_label = f"{equip} Analysis"
    if st.button(btn_label, key=f"btn_eq_{equip}"): st.session_state[nav_key]="Equipment"; st.rerun()
with c4:
    if st.button("Event Analysis", key=f"btn_ev_{equip}"): st.session_state[nav_key]="EventAnalysis"; st.rerun()

page = st.session_state[nav_key]
PAGE_KEYS = {"Overall":f"btn_ov_{equip}","Monthly":f"btn_mo_{equip}",
             "Equipment":f"btn_eq_{equip}","EventAnalysis":f"btn_ev_{equip}"}
active_key = PAGE_KEYS[page]
btn_label_for_js = f"{equip} Analysis"

st.markdown(f"""
<script>
(function(){{
  const ak = "{active_key}";
  const pm = {{"Overall Analysis":"{PAGE_KEYS['Overall']}","Monthly Analysis":"{PAGE_KEYS['Monthly']}",
               "{btn_label_for_js}":"{PAGE_KEYS['Equipment']}","Event Analysis":"{PAGE_KEYS['EventAnalysis']}"}};
  function styleBtn(btn, active){{
    if(active){{
      btn.style.cssText = btn.style.cssText +
        ';background-color:#ffffff !important;color:#1e293b !important' +
        ';border:2px solid #1e293b !important;outline:none !important;box-shadow:none !important';
      btn.querySelectorAll('*').forEach(el=>el.style.setProperty('color','#1e293b','important'));
    }} else {{
      btn.style.cssText = btn.style.cssText +
        ';background-color:#1e293b !important;color:#ffffff !important;border:1px solid #334155 !important';
      btn.querySelectorAll('*').forEach(el=>el.style.setProperty('color','#ffffff','important'));
    }}
  }}
  function apply(){{
    window.parent.document.querySelectorAll('.stButton button').forEach(btn=>{{
      const t=btn.innerText.trim();
      if(pm[t]===ak){{btn.dataset.navActive='1';styleBtn(btn,true);}}
      else if(pm[t]){{delete btn.dataset.navActive;styleBtn(btn,false);}}
    }});
  }}
  window.parent.document.addEventListener('mouseover',function(e){{const btn=e.target.closest('button');if(btn&&btn.dataset.navActive==='1')styleBtn(btn,true);}},true);
  window.parent.document.addEventListener('focusin',function(e){{const btn=e.target.closest('button');if(btn&&btn.dataset.navActive==='1')styleBtn(btn,true);}},true);
  apply();
  [100,300,600,1200,2500].forEach(t=>setTimeout(apply,t));
  new MutationObserver(apply).observe(window.parent.document.body,{{childList:true,subtree:true}});
}})();
</script>
""", unsafe_allow_html=True)

st.markdown("<hr>", unsafe_allow_html=True)


# ─────────────────────────────────────────────────
# ACTIVE CONFIG  — pick episode dataframe & settings
# ─────────────────────────────────────────────────
if equip == "Pump":
    ep_df    = pump_ep.copy()
    eq_col   = "Equipment"
    info_col = "pump_info"
    COLORS_MAP = PUMP_COLORS_MAP
else:
    ep_df    = exch_ep.copy()
    eq_col   = "Equipment"
    info_col = "exchanger_info"
    COLORS_MAP = EXCH_COLORS_MAP

# Ordered list of months from episode data
months_sorted = sorted(ep_df["month_dt"].dropna().unique())
months_labels = [pd.to_datetime(m).strftime("%B-%Y") for m in months_sorted]
x = np.arange(len(months_labels))

# Available events (snake_case keys, sorted by total episodes desc)
ev_order_snake = (ep_df.groupby("snake_ev").size()
                  .sort_values(ascending=False).index.tolist())
COLORS = make_colors(ev_order_snake, COLORS_MAP)

render_kpi(ep_df, months_labels)


# ══════════════════════════════════════════════════
# OVERALL ANALYSIS
# ══════════════════════════════════════════════════
if page == "Overall":

    if equip == "Exchanger":
        colA, colB, _ = st.columns([1, 1, 6])
        with colA:
            shift_on = st.selectbox("Shift Bifurcation", ["OFF","ON"], index=0, key=f"bif_{equip}") == "ON"
        with colB:
            cw_filter_ov = st.selectbox("CW Bifurcation", ["All","CW Only","Non-CW Only"],
                                        index=0, key=f"cw_bif_ov_{equip}")
    else:
        colA, _ = st.columns([1, 7])
        with colA:
            shift_on = st.selectbox("Shift Bifurcation", ["OFF","ON"], index=0, key=f"bif_{equip}") == "ON"
        cw_filter_ov = "All"

    # CW-filtered episode df for donut
    df_ov = ep_df.copy()
    if equip == "Exchanger":
        if cw_filter_ov == "CW Only":      df_ov = df_ov[df_ov["is_cw"]];  donut_suffix = " (CW Only)"
        elif cw_filter_ov == "Non-CW Only":df_ov = df_ov[~df_ov["is_cw"]]; donut_suffix = " (Non-CW Only)"
        else:                               donut_suffix = ""
    else:
        donut_suffix = ""

    col1, col2 = st.columns(2, gap="small")
    with col1:
        # monthly trend from episodes
        mon_shift = (ep_df.groupby(["month","Start Shift"])
                     .size().unstack(fill_value=0)
                     .reindex(months_labels, fill_value=0))
        day_vals   = mon_shift.get("Day",   pd.Series(0, index=months_labels)).values
        night_vals = mon_shift.get("Night", pd.Series(0, index=months_labels)).values

        if not shift_on:
            def draw_dn(ax):
                y_max = max((day_vals + night_vals).max(), 1)
                ax.set_ylim(0, y_max * 1.15)
                ax.bar(x, day_vals,   width=BAR_W, color=SHIFT_COLORS["Day"],   edgecolor="white", linewidth=0.6, label="Day")
                ax.bar(x, night_vals, width=BAR_W, bottom=day_vals, color=SHIFT_COLORS["Night"],
                       edgecolor="white", linewidth=0.6, hatch="//", label="Night")
                for i in range(len(x)):
                    inner_label(ax, x[i], 0,          day_vals[i],   "D")
                    inner_label(ax, x[i], day_vals[i], night_vals[i], "N")
                ax.set_xticks(x); ax.set_xticklabels(months_labels, rotation=30, ha='right', fontsize=6.5)
                ax.set_ylabel("Episode Count", fontsize=6.5, color="black")
                ax.legend(fontsize=6.5, loc='upper left', framealpha=0.9, edgecolor="black")
                style_bar(ax)
            wrap_plot("Monthly Episode Trend  (Day | Night)", draw_dn)
        else:
            # per-event breakdown by shift
            mon_ev_shift = (ep_df.groupby(["month","Start Shift","snake_ev"])
                            .size().unstack(fill_value=0)
                            .reindex(months_labels, fill_value=0))
            def draw_dual(ax):
                w = BAR_W / 2
                bd = np.zeros(len(months_labels)); bn = np.zeros(len(months_labels))
                for ev in ev_order_snake:
                    try:
                        d_vals = mon_ev_shift.xs("Day",   level="Start Shift")[ev].values if "Day"   in mon_ev_shift.index.get_level_values(1) else np.zeros(len(months_labels))
                        n_vals = mon_ev_shift.xs("Night", level="Start Shift")[ev].values if "Night" in mon_ev_shift.index.get_level_values(1) else np.zeros(len(months_labels))
                    except: d_vals = n_vals = np.zeros(len(months_labels))
                    ax.bar(x-w/2, d_vals, width=w, bottom=bd, color=COLORS.get(ev,"#94a3b8"), edgecolor="white", linewidth=0.4)
                    ax.bar(x+w/2, n_vals, width=w, bottom=bn, color=COLORS.get(ev,"#94a3b8"), edgecolor="white", linewidth=0.4)
                    bd += d_vals; bn += n_vals
                y_max = max(max(bd.max(), bn.max()), 1)
                ax.set_ylim(0, y_max * 1.15)
                for i in range(len(x)):
                    if bd[i]>0: safe_label(ax, x[i]-w/2, bd[i], "D", y_max*1.15, color="black")
                    if bn[i]>0: safe_label(ax, x[i]+w/2, bn[i], "N", y_max*1.15, color="black")
                ax.set_xticks(x); ax.set_xticklabels(months_labels, rotation=30, ha='right', fontsize=6.5)
                ax.set_ylabel("Episode Count", fontsize=6.5, color="black")
                style_bar(ax)
            wrap_plot("Monthly Episode Trend  (Shift × Event Type)", draw_dual)

    with col2:
        donut_series = df_ov.groupby("snake_ev").size()
        if equip == "Exchanger":
            plot_donut(f"Episode Distribution{donut_suffix}", donut_series, COLORS, top_n=10)
        else:
            plot_donut("Episode Distribution", donut_series, COLORS, filter_top5=True)


# ══════════════════════════════════════════════════
# MONTHLY ANALYSIS
# ══════════════════════════════════════════════════
elif page == "Monthly":

    if equip == "Exchanger":
        colA, colB, _ = st.columns([1, 1, 6])
        with colA:
            month_list     = months_labels
            selected_month = st.selectbox("Select Month", month_list, key=f"mon_{equip}")
        with colB:
            cw_filter = st.selectbox("CW Filter", ["All","CW Only","Non-CW Only"],
                                     index=0, key=f"cw_filter_{equip}")
    else:
        colA, _ = st.columns([1, 7])
        with colA:
            month_list     = months_labels
            selected_month = st.selectbox("Select Month", month_list, key=f"mon_{equip}")
        cw_filter = "All"

    fdf = ep_df[ep_df["month"] == selected_month].copy()
    if equip == "Exchanger":
        if cw_filter == "CW Only":      fdf = fdf[fdf["is_cw"]]
        elif cw_filter == "Non-CW Only":fdf = fdf[~fdf["is_cw"]]
    suffix = f"  [{cw_filter}]" if equip=="Exchanger" and cw_filter!="All" else ""

    col1, col2 = st.columns(2, gap="small")
    with col1:
        if equip == "Exchanger" and cw_filter == "All":
            # CW vs Non-CW per top-7 exchangers
            eq_counts = fdf.groupby("Equipment").size().sort_values(ascending=False).head(7)
            top7 = eq_counts.index.tolist()
            cw_v  = np.array([int(fdf[fdf["is_cw"]  & (fdf["Equipment"]==e)].shape[0]) for e in top7])
            ncw_v = np.array([int(fdf[~fdf["is_cw"] & (fdf["Equipment"]==e)].shape[0]) for e in top7])
            totals = cw_v + ncw_v
            def draw_mcw(ax):
                xi = np.arange(len(top7)); y_max = max(totals.max(), 1)
                ax.set_ylim(0, y_max * 1.18)
                ax.bar(xi, cw_v,  width=BAR_W, color=CW_COLOR,   edgecolor="white", linewidth=0.6, label="CW")
                ax.bar(xi, ncw_v, width=BAR_W, bottom=cw_v, color=NONCW_COLOR,
                       edgecolor="white", linewidth=0.6, hatch="//", label="Non-CW")
                grand = totals.sum()
                for i, tot in enumerate(totals):
                    inner_label(ax, xi[i], 0,       cw_v[i],  "CW", fontsize=5.5)
                    inner_label(ax, xi[i], cw_v[i], ncw_v[i], "NC", fontsize=5.5)
                    if tot>0 and grand>0:
                        safe_label(ax, xi[i], tot, f"{tot/grand*100:.0f}%", y_max*1.18, fontsize=6)
                ax.set_xticks(xi); ax.set_xticklabels(top7, rotation=25, ha='right', fontsize=6.5)
                ax.set_ylabel("Episode Count", fontsize=6.5, color="black")
                ax.legend(fontsize=6.5, loc='upper right', framealpha=0.9, edgecolor="black")
                style_bar(ax)
            wrap_plot(f"Top 7 Exchangers — CW/Non-CW  —  {selected_month}", draw_mcw)
        else:
            # top-7 equipment, stacked by top-5 events
            eq_counts = fdf.groupby("Equipment").size().sort_values(ascending=False).head(7)
            top7_names = eq_counts.index.tolist()
            ev_counts_m = fdf.groupby("Event").size().sort_values(ascending=False)
            top5_ev_labels = list(ev_counts_m.head(5).index)               # title-case
            top5_ev_snake  = [_snake(e) for e in top5_ev_labels]
            # build matrix: equipment × event
            mat = pd.DataFrame(0, index=top7_names, columns=top5_ev_labels)
            for eq_name in top7_names:
                sub = fdf[fdf["Equipment"]==eq_name]
                for ev_lbl in top5_ev_labels:
                    mat.loc[eq_name, ev_lbl] = int((sub["Event"]==ev_lbl).sum())
            def draw_ev(ax):
                bot = np.zeros(len(top7_names))
                for ev_lbl, ev_snake in zip(top5_ev_labels, top5_ev_snake):
                    vals = mat[ev_lbl].values
                    ax.bar(range(len(top7_names)), vals, bottom=bot, width=BAR_W,
                           color=COLORS.get(ev_snake,"#94a3b8"), edgecolor="white", linewidth=0.5)
                    bot += vals
                y_max = max(bot.max(), 1); ax.set_ylim(0, y_max * 1.18)
                grand = bot.sum()
                for i, tot in enumerate(bot):
                    if tot>0 and grand>0:
                        safe_label(ax, i, tot, f"{tot/grand*100:.0f}%", y_max*1.18, fontsize=6)
                ax.set_xticks(range(len(top7_names)))
                ax.set_xticklabels(top7_names, rotation=25, ha='right', fontsize=6.5)
                ax.set_ylabel("Episode Count", fontsize=6.5, color="black")
                style_bar(ax)
            lbl = "Pumps" if equip=="Pump" else "Exchangers"
            wrap_plot(f"Top 7 {lbl} — Top 5 Events  —  {selected_month}{suffix}", draw_ev)

    with col2:
        donut_m = fdf.groupby("snake_ev").size()
        if equip == "Exchanger":
            plot_donut(f"Top Events  —  {selected_month}{suffix}", donut_m, COLORS, top_n=10)
        else:
            plot_donut(f"Top Events  —  {selected_month}", donut_m, COLORS, filter_top5=True)


# ══════════════════════════════════════════════════
# EQUIPMENT ANALYSIS
# ══════════════════════════════════════════════════
elif page == "Equipment":

    if equip == "Exchanger":
        colA, colB, _ = st.columns([1, 1, 6])
        with colA:
            cw_eq_filter = st.selectbox("CW Filter", ["All","CW Only","Non-CW Only"],
                                        index=0, key=f"cw_eq_{equip}")
        eq_sub = ep_df.copy()
        if cw_eq_filter == "CW Only":       eq_sub = ep_df[ep_df["is_cw"]]
        elif cw_eq_filter == "Non-CW Only": eq_sub = ep_df[~ep_df["is_cw"]]
        eq_list = eq_sub.groupby("Equipment").size().sort_values(ascending=False).index.tolist()
        with colB:
            selected_eq = st.selectbox("Select Exchanger", eq_list, key=f"sel_{equip}")
    else:
        colA, _ = st.columns([1, 7])
        eq_list = ep_df.groupby("Equipment").size().sort_values(ascending=False).index.tolist()
        with colA:
            selected_eq = st.selectbox(f"Select {equip}", eq_list, key=f"sel_{equip}")

    eq_ep = ep_df[ep_df["Equipment"] == selected_eq]

    if equip == "Exchanger":
        cw_label    = "CW" if is_cw(selected_eq) else "Non-CW"
        donut_title = f"Top Events  —  {selected_eq}  [{cw_label}]"
    else:
        donut_title = f"Top Events  —  {selected_eq}"

    col1, col2 = st.columns(2, gap="small")
    with col1:
        # History table from RAW csv
        st.markdown('<div class="plot-box"><div class="plot-title">Equipment History</div>',
                    unsafe_allow_html=True)
        try:
            if equip == "Pump":
                raw = load_raw_pump()
                hist = raw[raw["pump"] == selected_eq][["date","shift","pump_info"]].sort_values("date").copy()
            else:
                raw = load_raw_exchanger()
                hist = raw[raw["exchanger"] == selected_eq][["date","shift","exchanger_info"]].sort_values("date").copy()
            hist.columns = ["Date","Shift","Event Info"]
            hist["Date"] = hist["Date"].dt.strftime("%d-%b-%Y")
            if hist.empty:
                st.markdown('<div class="no-data-msg">No data available</div>', unsafe_allow_html=True)
            else:
                st.dataframe(hist, use_container_width=True, height=260)
        except Exception:
            # fallback: show episode log for this equipment
            hist2 = eq_ep[["Start Date","Start Shift","End Date","End Shift","Event","Days Open"]].copy()
            st.dataframe(hist2, use_container_width=True, height=260)
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        ev_sum = eq_ep.groupby("snake_ev").size()
        plot_donut(donut_title, ev_sum, COLORS, top_n=10)


# ══════════════════════════════════════════════════
# EVENT ANALYSIS
# ══════════════════════════════════════════════════
elif page == "EventAnalysis":

    ev_options = ep_df.groupby("Event").size().sort_values(ascending=False).index.tolist()

    if equip == "Exchanger":
        colA, colB, _ = st.columns([1, 1, 6])
        with colA:
            sel_ev_label = st.selectbox("Select Event", ev_options, key=f"evsel_{equip}")
        with colB:
            cw_ev_filter = st.selectbox("CW Filter", ["All","CW Only","Non-CW Only"],
                                        index=0, key=f"cw_evf_{equip}")
    else:
        colA, _ = st.columns([1, 7])
        with colA:
            sel_ev_label = st.selectbox("Select Event", ev_options, key=f"evsel_{equip}")
        cw_ev_filter = "All"

    sel_ev_snake = _snake(sel_ev_label)
    ev_color     = COLORS_MAP.get(sel_ev_snake, FALLBACK_COLORS[0])

    ep_filt = ep_df[ep_df["Event"] == sel_ev_label].copy()
    if equip == "Exchanger" and cw_ev_filter != "All":
        cw_equips = {e for e in ep_filt["Equipment"].unique() if is_cw(e)}
        if cw_ev_filter == "CW Only":      ep_filt = ep_filt[ep_filt["Equipment"].isin(cw_equips)]
        else:                               ep_filt = ep_filt[~ep_filt["Equipment"].isin(cw_equips)]

    cw_suffix = f"  [{cw_ev_filter}]" if equip=="Exchanger" and cw_ev_filter!="All" else ""

    col1, col2 = st.columns(2, gap="small")

    # ── Episode Log table ──
    with col1:
        st.markdown(f'<div class="plot-box"><div class="plot-title">Episode Log — {sel_ev_label}{cw_suffix}</div>',
                    unsafe_allow_html=True)
        if ep_filt.empty:
            st.markdown('<div class="no-data-msg">No episodes found for this event.</div>',
                        unsafe_allow_html=True)
        else:
            display_df = ep_filt[["Equipment","Start Date","Start Shift","End Date","End Shift","Days Open"]].reset_index(drop=True)
            def color_days(val):
                if val <= 1:   return "background-color:#d1fae5; color:#064e3b;"
                elif val <= 3: return "background-color:#fef9c3; color:#713f12;"
                elif val <= 7: return "background-color:#fed7aa; color:#7c2d12;"
                else:          return "background-color:#fecaca; color:#7f1d1d;"
            styled = (display_df.style
                      .applymap(color_days, subset=["Days Open"])
                      .format({"Days Open": "{:.1f}"}))
            st.dataframe(styled, use_container_width=True, height=260)
        st.markdown('</div>', unsafe_allow_html=True)

    # ── Top-5 equipment bar chart ──
    with col2:
        eq_ev_counts = ep_filt.groupby("Equipment").size().sort_values(ascending=False).head(5)
        if eq_ev_counts.empty:
            st.markdown(f'<div class="plot-box"><div class="plot-title">Top 5 {equip}s — {sel_ev_label}{cw_suffix}</div>'
                        f'<div class="no-data-msg">No data available</div></div>', unsafe_allow_html=True)
        else:
            def draw_top5_bar(ax):
                eq_names = eq_ev_counts.index.tolist()
                ev_vals  = eq_ev_counts.values
                xi       = np.arange(len(eq_names))
                y_max    = max(ev_vals.max(), 1)
                ax.bar(xi, ev_vals, width=BAR_W, color=ev_color, edgecolor="white", linewidth=0.6, zorder=3)
                ax.set_ylim(0, y_max * 1.20)
                for i, v in enumerate(ev_vals):
                    safe_label(ax, xi[i], v, f"{int(v)}", y_max * 1.20, fontsize=6.2)
                ax.set_xticks(xi)
                ax.set_xticklabels(eq_names, rotation=25, ha="right", fontsize=6.5)
                ax.set_ylabel("Episode Count", fontsize=6.5, color="black")
                style_bar(ax)
            wrap_plot(f"Top 5 {equip}s — {sel_ev_label}{cw_suffix}", draw_top5_bar)
