import pandas as pd
import numpy as np
import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec

st.set_page_config(layout="wide")

# ── Uniform figure size used for EVERY plot panel (bar + donut) ──────────────
FIGSIZE = (6.5, 2.75)
BAR_W   = 0.50

st.markdown("""
<style>
/* ── page frame ─────────────────────────────────────────────────────── */
.block-container {
    padding-top: 0.18rem !important; padding-bottom: 0 !important;
    padding-left: 0.9rem !important; padding-right: 0.9rem !important;
    max-width: 100% !important;
}
html, body, [class*="css"] { font-family: "Times New Roman", serif; }

/* ── collapse ALL streamlit gaps ────────────────────────────────────── */
div[data-testid="stVerticalBlock"] > div      { gap: 0 !important; }
div[data-testid="stHorizontalBlock"]          { margin-top:0 !important; margin-bottom:0 !important; }
div[data-testid="column"]                     { padding: 0 3px !important; }
.element-container                            { margin-bottom:0 !important; padding-bottom:0 !important; }

/* ── NAV BUTTONS — all exactly the same size ────────────────────────── */
div.stButton > button {
    width: 100% !important;
    height: 30px !important;
    min-height: 30px !important;
    max-height: 30px !important;
    border-radius: 4px;
    background-color: #1e293b;
    border: 1px solid #334155;
    color: white !important;
    padding: 0 !important;
    line-height: 1 !important;
    white-space: nowrap;
    overflow: hidden;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    box-sizing: border-box !important;
}
div.stButton > button p,
div.stButton > button span,
div.stButton > button div {
    color: white !important;
    font-size: 12px !important;
    font-weight: 700 !important;
    line-height: 1 !important;
    margin: 0 !important; padding: 0 !important;
}
div.stButton > button:hover  { background-color: #0f172a; }
div.stButton > button:active { transform: scale(0.97); }

/* ── SELECTBOX ─────────────────────────────────────────────────────── */
div[data-testid="stSelectbox"] { margin-bottom:0 !important; padding-bottom:0 !important; }
div[data-baseweb="select"] > div {
    min-height: 27px !important;
    background-color: #ffffff !important;
    border: 1.5px solid #1e293b !important;
    border-radius: 3px !important;
}
div[data-baseweb="select"] > div:hover { border-color: #475569 !important; }
div[data-baseweb="select"] svg { fill: #1e293b !important; }
div[data-baseweb="select"] [class*="singleValue"],
div[data-baseweb="select"] [class*="placeholder"] {
    color: #1e293b !important; font-family: "Times New Roman", serif !important;
    font-size: 11px !important; font-weight: 700 !important; white-space: nowrap;
}
div[data-baseweb="select"] input { color: #1e293b !important; font-size: 11px !important; }
div[data-testid="stSelectbox"] label {
    font-family: "Times New Roman", serif !important; font-size: 11px !important;
    font-weight: 700 !important; color: #1e293b !important;
    margin-bottom: 0 !important; white-space: nowrap;
}

/* ── KPI ROW ────────────────────────────────────────────────────────── */
.kpi-row  { display:flex; gap:8px; margin:2px 0; }
.kpi-card {
    flex:1; background:#f8fafc;
    border:1.5px solid #1e293b; border-left:4px solid #1e293b;
    border-radius:4px; padding:2px 6px; min-width:0;
    font-family:"Times New Roman",serif; text-align:center;
}
.kpi-label{ font-size:9px;  font-weight:900; color:#1e293b; text-transform:uppercase; letter-spacing:.7px; margin-bottom:0; }
.kpi-value{ font-size:14px; font-weight:700; color:#1e293b; line-height:1.15; }
.kpi-sub  { font-size:9px;  font-weight:600; color:#334155; margin-top:0; }
.kpi-card.c1{border-left-color:#2563eb;}.kpi-card.c1 .kpi-value{color:#2563eb;}
.kpi-card.c2{border-left-color:#65a30d;}.kpi-card.c2 .kpi-value{color:#65a30d;}
.kpi-card.c3{border-left-color:#d97706;}.kpi-card.c3 .kpi-value{color:#d97706;}
.kpi-card.c4{border-left-color:#7c3aed;}.kpi-card.c4 .kpi-value{color:#7c3aed;}

/* ── PLOT BOX — equal height enforced by figsize ────────────────────── */
.plot-box {
    border:1.5px solid #1e293b; border-radius:5px;
    padding:1px 3px 0 3px; background:#f8fafc; margin-bottom:2px;
}
.plot-title {
    font-size:11.5px; font-weight:700; color:#1e293b;
    font-family:"Times New Roman",serif; text-align:center;
    line-height:1.2; margin:0; padding:1px 0 0 0;
}
.no-data-msg{ color:#64748b; font-size:12px; font-family:"Times New Roman",serif;
              text-align:center; padding:24px 8px; }

/* strip matplotlib bottom margin */
div[data-testid="stImage"], .stpyplot { margin-bottom:0 !important; padding-bottom:0 !important; }

/* ── TITLE ──────────────────────────────────────────────────────────── */
.dash-title{ text-align:center; color:#1e293b; font-family:"Times New Roman",serif;
             font-size:22px; font-weight:700; margin:0 0 2px 0; padding:0; line-height:1.2; }

hr{ margin:2px 0 !important; border-color:#94a3b8; }
header{ visibility:hidden; } footer{ visibility:hidden; }
[data-testid="stAppViewContainer"] > section > div:first-child{ padding-top:0 !important; }
</style>

<script>
/* inline every named selectbox label so label+dropdown sit on one row */
(function(){
  const TARGETS = ["Shift Bifurcation","CW Bifurcation","CW Filter",
                   "Select Month","Select Exchanger","Select Pump","Select Event"];
  function applyAll(){
    window.parent.document.querySelectorAll('[data-testid="stSelectbox"]').forEach(function(box){
      const label = box.querySelector(':scope > label');
      if(!label) return;
      const txt = label.innerText.trim();
      if(txt===""||txt==="Pump"||txt==="Exchanger") return;
      if(!TARGETS.some(t=>txt.startsWith(t.split(" ")[0]))) return;

      box.querySelectorAll('[data-baseweb="select"]>div').forEach(el=>
        el.style.setProperty('min-height','26px','important'));
      box.querySelectorAll('[class*="singleValue"],[class*="placeholder"]').forEach(el=>{
        el.style.setProperty('font-size','11px','important');
        el.style.setProperty('font-weight','700','important');
      });
      box.querySelectorAll('input').forEach(el=>el.style.setProperty('font-size','11px','important'));
      box.querySelectorAll('[data-baseweb="select"] svg').forEach(el=>{
        el.style.setProperty('width','12px','important');
        el.style.setProperty('height','12px','important');
      });

      if(!box.dataset.inlined){
        box.dataset.inlined="1";
        box.style.setProperty('display','flex','important');
        box.style.setProperty('flex-direction','row','important');
        box.style.setProperty('align-items','center','important');
        box.style.setProperty('gap','5px','important');
        box.style.setProperty('flex-wrap','nowrap','important');
        box.style.setProperty('margin-bottom','0','important');
        label.style.setProperty('display','inline','important');
        label.style.setProperty('font-size','11px','important');
        label.style.setProperty('font-weight','700','important');
        label.style.setProperty('color','#1e293b','important');
        label.style.setProperty('white-space','nowrap','important');
        label.style.setProperty('flex-shrink','0','important');
        label.style.setProperty('margin-bottom','0','important');
        label.style.setProperty('line-height','1','important');
        label.style.setProperty('order','0','important');
        const bw = box.querySelector('[data-baseweb="select"]');
        if(bw){
          bw.style.setProperty('order','1','important');
          bw.style.setProperty('flex','1 1 auto','important');
          /* wide enough to read the full value text */
          bw.style.setProperty('min-width','110px','important');
          bw.style.setProperty('max-width','170px','important');
        }
      }
    });
  }
  applyAll();
  [80,250,500,1000,2000].forEach(t=>setTimeout(applyAll,t));
  new MutationObserver(applyAll).observe(window.parent.document.body,{childList:true,subtree:true});
})();
</script>
""", unsafe_allow_html=True)


# ═════════════════════════════════════════════════════════════════════════════
# CW SET
# ═════════════════════════════════════════════════════════════════════════════
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


# ═════════════════════════════════════════════════════════════════════════════
# EPISODE LOGIC
# ─────────────────────────────────────────────────────────────────────────────
# Core idea: for each (equipment, event) pair, consecutive shift-entries that
# are ≤ GAP shifts apart form a single EPISODE.  Only the FIRST row of each
# episode keeps flag=1; all continuations become 0.
#
# Result: a single dataframe (`*_ep`) where .sum() everywhere == episode count.
# KPI cards, donut, bar charts, monthly trend — ALL use *_ep, so every number
# on the dashboard is automatically in "episodes", not "raw flag occurrences".
#
# The episode-log table in the Event Analysis tab uses extract_episodes() which
# also captures start/end dates and duration for each episode.
# ═════════════════════════════════════════════════════════════════════════════
DEDUP_GAP = 3   # shifts of silence → episode closed

def _shift_ord(df):
    """Monotonic integer: each calendar day has 2 slots (Day=0, Night=1)."""
    min_date = df["date"].min()
    day_n = (df["date"] - min_date).dt.days
    sh_n  = df["shift"].map({"Day":0,"Night":1}).fillna(0).astype(int)
    return day_n * 2 + sh_n

def episode_flag_df(df, eq_col, events, gap=DEDUP_GAP):
    """
    Return a copy of df where every event column contains episode-start flags:
      1  = first shift of a new episode
      0  = continuation of an existing episode (or no event)
    Summing any slice of the result gives episode counts, not raw flag counts.
    """
    df_out = df.copy()
    df_out["_sord"] = _shift_ord(df_out)
    for ev in events:
        if ev not in df_out.columns:
            continue
        for _, grp in df_out.groupby(eq_col):
            active = grp[grp[ev] == 1].sort_values("_sord")
            if active.empty:
                continue
            prev_ord = None
            for idx, row in active.iterrows():
                s = row["_sord"]
                if prev_ord is not None and (s - prev_ord) <= gap:
                    df_out.loc[idx, ev] = 0   # continuation → zero out
                prev_ord = s
    df_out.drop(columns=["_sord"], inplace=True)
    return df_out

def extract_episodes(df, eq_col, events, gap=DEDUP_GAP):
    """
    Build a table of episodes: one row per (equipment, event, episode).
    Columns: Equipment, Event, Start Date, Start Shift, End Date, End Shift,
             Shifts Open, Days Open.
    Used only in the Event Analysis tab's episode-log table.
    """
    df_w = df.copy()
    df_w["_sord"] = _shift_ord(df_w)
    records = []
    for ev in events:
        if ev not in df_w.columns:
            continue
        for eq, grp in df_w.groupby(eq_col):
            active = grp[grp[ev] == 1].sort_values("_sord")
            if active.empty:
                continue
            prev_ord = ep_start_idx = prev_idx = None
            for idx, row in active.iterrows():
                s = row["_sord"]
                if prev_ord is None or (s - prev_ord) > gap:
                    if ep_start_idx is not None:
                        _append_ep(records, df_w, eq, ev, ep_start_idx, prev_idx)
                    ep_start_idx = idx
                prev_ord = s; prev_idx = idx
            if ep_start_idx is not None:
                _append_ep(records, df_w, eq, ev, ep_start_idx, prev_idx)
    return pd.DataFrame(records)

def _append_ep(records, df_w, eq, ev, start_idx, end_idx):
    st_r = df_w.loc[start_idx]; en_r = df_w.loc[end_idx]
    dur  = int(en_r["_sord"] - st_r["_sord"]) + 1
    records.append({
        "Equipment":   eq,
        "Event":       ev.replace("_"," ").title(),
        "Start Date":  st_r["date"].strftime("%d-%b-%Y"),
        "Start Shift": st_r["shift"],
        "End Date":    en_r["date"].strftime("%d-%b-%Y"),
        "End Shift":   en_r["shift"],
        "Shifts Open": dur,
        "Days Open":   round(dur / 2, 1),
    })


# ═════════════════════════════════════════════════════════════════════════════
# EVENT LISTS  (work_completed intentionally excluded)
# ═════════════════════════════════════════════════════════════════════════════
PUMP_EVENTS = [
    "seal_failure","low_level",
    "trip_fault","low_pressure","steam_issue","strainer_clean",
]

EXCH_EVENTS = [
    "tube_leak","tube_plug","tube_repair","tube_bundle_replace",
    "tube_installed","tube_cleaning","hydroblast_cleaning",
    "installing_plates","gasket_installed","pressure_test",
    "temp_cooler_replace","transmitter_blowdown","drained_oil",
    "sv_repair_replacement","steam_issue",
    "n2_purging","dew_point_check","install_heater",
    "capital_project","cleaning",
    # "work_completed" intentionally excluded
]

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
    "maintenance":"#334155",
}
FALLBACK_COLORS = ["#6366f1","#f43f5e","#10b981","#f97316","#8b5cf6",
                   "#06b6d4","#84cc16","#ec4899","#14b8a6","#ef4444"]

CW_COLOR     = "#0891b2"
NONCW_COLOR  = "#d97706"
SHIFT_COLORS = {"Day":"#0d9488","Night":"#475569"}
PLOT_BG      = "#f8fafc"
GRID_CLR     = "#cbd5e1"

def make_colors(events, cmap):
    out = {}; fi = 0
    for e in events:
        out[e] = cmap.get(e, FALLBACK_COLORS[fi % len(FALLBACK_COLORS)]); fi += 1
    return out


# ═════════════════════════════════════════════════════════════════════════════
# LOAD DATA
# ─────────────────────────────────────────────────────────────────────────────
# Both load functions return TWO dataframes:
#   df_raw  : original binary flags (used only for Equipment History table)
#   df_ep   : episode-start flags   (used for ALL charts, KPIs, donuts)
# ═════════════════════════════════════════════════════════════════════════════
def _prep_cols(df, events):
    """Ensure all event columns exist and are binary 0/1."""
    for c in events:
        if c not in df.columns: df[c] = 0
        df[c] = pd.to_numeric(df[c], errors="coerce").fillna(0).clip(upper=1).astype(int)
    return df

@st.cache_data
def load_pump():
    df = pd.read_csv("classified_output.csv")
    df["date"]     = pd.to_datetime(df["date"], errors="coerce")
    df             = df[df["pump"].notna() & df["date"].notna()]
    df["shift"]    = df["shift"].str.strip().replace({"Days":"Day","Nights":"Night"})
    df["month_dt"] = df["date"].dt.to_period("M").dt.to_timestamp()
    df["month"]    = df["month_dt"].dt.strftime("%B-%Y")
    df = _prep_cols(df, PUMP_EVENTS)
    keep = ["pump","pump_info","date","shift","month_dt","month"] + PUMP_EVENTS
    df = df[[c for c in keep if c in df.columns]]
    df_ep = episode_flag_df(df, "pump", PUMP_EVENTS)
    return df, df_ep   # (raw, episode-flagged)

@st.cache_data
def load_exchanger():
    df = pd.read_csv("exchanger_classified_final.csv")
    df = df[[c for c in df.columns if not c.startswith("[")]]
    df["shift"]    = df["shift"].str.strip().replace({"Days":"Day","Nights":"Night"})
    df["date"]     = pd.to_datetime(df["date"], errors="coerce")
    df             = df[df["exchanger"].notna() & df["date"].notna()]
    df["month_dt"] = df["date"].dt.to_period("M").dt.to_timestamp()
    df["month"]    = df["month_dt"].dt.strftime("%B-%Y")
    df["is_cw"]    = df["exchanger"].apply(is_cw)
    df = _prep_cols(df, EXCH_EVENTS)
    keep = ["exchanger","exchanger_info","date","shift","month_dt","month","is_cw"] + EXCH_EVENTS
    df = df[[c for c in keep if c in df.columns]]
    df_ep = episode_flag_df(df, "exchanger", EXCH_EVENTS)
    return df, df_ep   # (raw, episode-flagged)

@st.cache_data
def load_pump_episodes():
    df, _ = load_pump()
    return extract_episodes(df, "pump", PUMP_EVENTS)

@st.cache_data
def load_exchanger_episodes():
    df, _ = load_exchanger()
    return extract_episodes(df, "exchanger", EXCH_EVENTS)

pump_df_raw,  pump_df_ep  = load_pump()
exch_df_raw,  exch_df_ep  = load_exchanger()


# ═════════════════════════════════════════════════════════════════════════════
# PLOT HELPERS
# ═════════════════════════════════════════════════════════════════════════════
def border(ax):
    for sp in ax.spines.values():
        sp.set_visible(True); sp.set_linewidth(1.3); sp.set_color("black")

def style_bar(ax):
    ax.set_facecolor(PLOT_BG)
    ax.grid(axis="y", linestyle="--", linewidth=0.5, alpha=0.6, color=GRID_CLR)
    ax.grid(axis="x", visible=False)
    ax.tick_params(colors="black", labelsize=6)
    border(ax)

def wrap_plot(title, draw_fn):
    """Render a bar/line chart inside a plot-box at the global FIGSIZE."""
    st.markdown(f'<div class="plot-box"><div class="plot-title">{title}</div>',
                unsafe_allow_html=True)
    fig, ax = plt.subplots(figsize=FIGSIZE, facecolor=PLOT_BG)
    fig.patch.set_facecolor(PLOT_BG)
    draw_fn(ax)
    plt.tight_layout(pad=0.3)
    st.pyplot(fig, use_container_width=True)
    plt.close(fig)
    st.markdown("</div>", unsafe_allow_html=True)

def get_shift(grouped, name, months_labels, events):
    try:    return grouped.xs(name, level=1).reindex(months_labels).fillna(0)
    except: return pd.DataFrame(0, index=months_labels, columns=events)

def safe_label(ax, xp, y_top, text, y_ceil, fontsize=5.8, color="#1e293b"):
    y = min(y_top + y_ceil*0.02, y_ceil*0.96)
    ax.text(xp, y, text, ha="center", va="bottom",
            fontsize=fontsize, fontweight="bold", color=color, clip_on=True)

def inner_label(ax, xp, y_base, height, text, fontsize=5.5, color="white"):
    yr = ax.get_ylim()[1] - ax.get_ylim()[0]
    if yr == 0 or height/yr < 0.07: return
    ax.text(xp, y_base+height/2, text, ha="center", va="center",
            fontsize=fontsize, fontweight="bold", color=color, zorder=6, clip_on=True)


# ─────────────────────────────────────────────────────────────────────────────
# DONUT  — always rendered at FIGSIZE, identical size to every bar chart
# ─────────────────────────────────────────────────────────────────────────────
def _top_n_others(series, colors, top_n=10):
    series = series[series > 0].sort_values(ascending=False)
    if series.empty: return pd.Series(dtype=float), {}, []
    if len(series) <= top_n:
        return series, {k: colors.get(k,"#94a3b8") for k in series.index}, []
    top = series.iloc[:top_n]; rest = series.iloc[top_n:]
    result = pd.concat([top, pd.Series({"Others": rest.sum()})])
    oc = {k: colors.get(k,"#94a3b8") for k in top.index}; oc["Others"] = "#94a3b8"
    return result, oc, list(rest.index)

def _top5_gt5pct(series, colors):
    tot = series.sum()
    if tot == 0: return pd.Series(dtype=float), {}
    filt = series[series/tot*100 > 5].nlargest(5)
    return filt, {k: colors.get(k,"#94a3b8") for k in filt.index}

def plot_donut(title, raw_series, all_colors, filter_top5=False, top_n=None):
    """
    Renders a donut chart at FIGSIZE (same as every bar chart).
    raw_series should already be episode-count sums so the "Total" in the
    centre and the legend percentages are all in episodes.
    """
    others_list = []
    if top_n is not None:
        data, colors, others_list = _top_n_others(raw_series, all_colors, top_n)
    elif filter_top5:
        data, colors = _top5_gt5pct(raw_series, all_colors)
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
    fig   = plt.figure(figsize=FIGSIZE, facecolor=PLOT_BG)
    fig.patch.set_facecolor(PLOT_BG)
    gs = gridspec.GridSpec(1, 2, figure=fig, width_ratios=[0.48, 0.52],
                           left=0.01, right=0.99, top=0.97, bottom=0.04, wspace=0.0)
    ax_pie = fig.add_subplot(gs[0]); ax_leg = fig.add_subplot(gs[1])
    ax_pie.set_facecolor(PLOT_BG)
    for sp in ax_pie.spines.values(): sp.set_visible(False)

    wedge_colors = [colors.get(k,"#94a3b8") for k in data.index]
    _, _, autotexts = ax_pie.pie(
        data, colors=wedge_colors, startangle=90,
        wedgeprops=dict(width=0.38, edgecolor="white", linewidth=0.6),
        autopct=lambda p: f"{p:.0f}%" if p >= 7 else "",
        pctdistance=0.75, radius=0.86, center=(0, 0.06),
    )
    for at in autotexts:
        at.set_fontsize(5.5); at.set_color("white"); at.set_fontweight("bold")
    ax_pie.text(0, 0.06, f"Total\n{int(total)}", ha="center", va="center",
                fontsize=7, fontweight="bold", color="#1e293b")

    ax_leg.set_facecolor(PLOT_BG); ax_leg.axis("off")
    ax_leg.set_xlim(0,1); ax_leg.set_ylim(0,1)
    n     = len(data)
    row_h = min(0.105, 0.90/max(n,1))
    pad_t = 0.95; hw = 0.08; hh = min(0.042, row_h*0.46)
    for i, (ft, val) in enumerate(data.items()):
        yc = pad_t - i*row_h
        if yc < 0.02: break
        c = colors.get(ft,"#94a3b8")
        ax_leg.add_patch(plt.Rectangle((0.01, yc-hh/2), hw, hh,
                                        transform=ax_leg.transAxes,
                                        color=c, clip_on=False, zorder=10))
        ax_leg.text(0.01+hw+0.04, yc,
                    f"{ft.replace('_',' ').title()}  {val/total*100:.0f}%",
                    transform=ax_leg.transAxes, fontsize=5.2,
                    va="center", color="#1e293b", clip_on=False, fontweight="600")
    if others_list:
        fig.text(0.01, 0.005, "Others: "+", ".join(e.replace("_"," ").title() for e in others_list),
                 fontsize=4.2, color="#64748b", ha="left", va="bottom")

    st.markdown(f'<div class="plot-box"><div class="plot-title">{title}</div>',
                unsafe_allow_html=True)
    st.pyplot(fig, use_container_width=True)
    plt.close(fig)
    st.markdown("</div>", unsafe_allow_html=True)


# ═════════════════════════════════════════════════════════════════════════════
# KPI CARDS  — all numbers from df_ep so they count episodes, not raw flags
# ═════════════════════════════════════════════════════════════════════════════
def render_kpi(df_ep, events, months_labels):
    ev_cols   = [e for e in events if e in df_ep.columns]
    total_ev  = int(df_ep[ev_cols].sum().sum())
    total_mon = len(months_labels)
    avg_pm    = round(total_ev / max(total_mon,1), 1)

    ev_by_mon = (df_ep.groupby("month")[ev_cols].sum()
                 .reindex(months_labels).fillna(0).sum(axis=1))
    peak_mon  = ev_by_mon.idxmax() if not ev_by_mon.empty and ev_by_mon.max()>0 else "—"
    peak_val  = int(ev_by_mon.max()) if not ev_by_mon.empty else 0

    ev_totals = df_ep[ev_cols].sum().sort_values(ascending=False)
    top_ev    = ev_totals.index[0].replace("_"," ").title() if len(ev_totals)>0 else "—"
    top_ev_c  = int(ev_totals.iloc[0]) if len(ev_totals)>0 else 0

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
        <div class="kpi-value" style="font-size:9.5px;padding-top:1px;">{peak_mon}</div>
        <div class="kpi-sub">{peak_val} episodes</div>
      </div>
      <div class="kpi-card c4">
        <div class="kpi-label">Top Event</div>
        <div class="kpi-value" style="font-size:9.5px;padding-top:1px;">{top_ev}</div>
        <div class="kpi-sub">{top_ev_c} episodes</div>
      </div>
    </div>""", unsafe_allow_html=True)


# ═════════════════════════════════════════════════════════════════════════════
# TITLE + NAV  (4 equal-width buttons)
# ═════════════════════════════════════════════════════════════════════════════
st.markdown("<div class='dash-title'>Equipment Reliability Dashboard</div>",
            unsafe_allow_html=True)

c0, c1, c2, c3, c4 = st.columns([0.9, 1, 1, 1, 1])
with c0:
    equip = st.selectbox("", ["Pump","Exchanger"],
                         key="equip_sel", label_visibility="collapsed")

nav_key = f"page_{equip}"
if nav_key not in st.session_state:
    st.session_state[nav_key] = "Overall"

with c1:
    if st.button("Overall Analysis",  key=f"btn_ov_{equip}"):
        st.session_state[nav_key]="Overall";       st.rerun()
with c2:
    if st.button("Monthly Analysis",  key=f"btn_mo_{equip}"):
        st.session_state[nav_key]="Monthly";       st.rerun()
with c3:
    if st.button(f"{equip} Analysis", key=f"btn_eq_{equip}"):
        st.session_state[nav_key]="Equipment";     st.rerun()
with c4:
    if st.button("Event Analysis",    key=f"btn_ev_{equip}"):
        st.session_state[nav_key]="EventAnalysis"; st.rerun()

page      = st.session_state[nav_key]
PAGE_KEYS = {
    "Overall":       f"btn_ov_{equip}",
    "Monthly":       f"btn_mo_{equip}",
    "Equipment":     f"btn_eq_{equip}",
    "EventAnalysis": f"btn_ev_{equip}",
}
BTN_TEXTS = {
    "Overall":       "Overall Analysis",
    "Monthly":       "Monthly Analysis",
    "Equipment":     f"{equip} Analysis",
    "EventAnalysis": "Event Analysis",
}
active_text = BTN_TEXTS[page]

st.markdown(f"""
<script>
(function(){{
  const at = "{active_text}";
  const all = ["Overall Analysis","Monthly Analysis","{equip} Analysis","Event Analysis"];
  function styleBtn(btn,active){{
    if(active){{
      btn.style.setProperty('background-color','#ffffff','important');
      btn.style.setProperty('border','2px solid #1e293b','important');
      btn.querySelectorAll('*').forEach(el=>el.style.setProperty('color','#1e293b','important'));
    }}else{{
      btn.style.setProperty('background-color','#1e293b','important');
      btn.style.setProperty('border','1px solid #334155','important');
      btn.querySelectorAll('*').forEach(el=>el.style.setProperty('color','#ffffff','important'));
    }}
  }}
  function apply(){{
    window.parent.document.querySelectorAll('.stButton button').forEach(btn=>{{
      const t=btn.innerText.trim();
      if(t===at){{ btn.dataset.navActive='1'; styleBtn(btn,true); }}
      else if(all.includes(t)){{ delete btn.dataset.navActive; styleBtn(btn,false); }}
    }});
  }}
  window.parent.document.addEventListener('mouseover',e=>{{const b=e.target.closest('button');if(b&&b.dataset.navActive==='1')styleBtn(b,true);}},true);
  window.parent.document.addEventListener('focusin',  e=>{{const b=e.target.closest('button');if(b&&b.dataset.navActive==='1')styleBtn(b,true);}},true);
  apply();
  [80,250,500,1000,2000].forEach(t=>setTimeout(apply,t));
  new MutationObserver(apply).observe(window.parent.document.body,{{childList:true,subtree:true}});
}})();
</script>
""", unsafe_allow_html=True)

st.markdown("<hr>", unsafe_allow_html=True)


# ═════════════════════════════════════════════════════════════════════════════
# ACTIVE CONFIG
# df     = episode-flagged dataframe (ALL charts + KPIs + donuts use this)
# df_raw = original flags            (Equipment History table only)
# ═════════════════════════════════════════════════════════════════════════════
if equip == "Pump":
    df_raw = pump_df_raw.copy(); df = pump_df_ep.copy()
    eq_col = "pump"; info_col = "pump_info"
    EVENTS = [e for e in PUMP_EVENTS if e in df.columns]
    COLORS = make_colors(EVENTS, PUMP_COLORS_MAP)
    COLORS_MAP = PUMP_COLORS_MAP
else:
    df_raw = exch_df_raw.copy(); df = exch_df_ep.copy()
    eq_col = "exchanger"; info_col = "exchanger_info"
    EVENTS = [e for e in EXCH_EVENTS if e in df.columns]
    COLORS = make_colors(EVENTS, EXCH_COLORS_MAP)
    COLORS_MAP = EXCH_COLORS_MAP

months_sorted = sorted(df["month_dt"].dropna().unique())
months_labels = [pd.to_datetime(m).strftime("%B-%Y") for m in months_sorted]
x = np.arange(len(months_labels))

# KPI — episode counts because df is already episode-flagged
render_kpi(df, EVENTS, months_labels)


# ══════════════════════════════════════════════════
# OVERALL ANALYSIS
# ══════════════════════════════════════════════════
if page == "Overall":

    if equip == "Exchanger":
        fa, fb, _ = st.columns([1.2, 1.5, 5.3])
        with fa: shift_on     = st.selectbox("Shift Bifurcation",["OFF","ON"],0,key=f"bif_{equip}")=="ON"
        with fb: cw_filter_ov = st.selectbox("CW Bifurcation",["All","CW Only","Non-CW Only"],0,key=f"cw_bif_ov_{equip}")
    else:
        fa, _ = st.columns([1.2, 6.8])
        with fa: shift_on = st.selectbox("Shift Bifurcation",["OFF","ON"],0,key=f"bif_{equip}")=="ON"
        cw_filter_ov = "All"

    if equip == "Exchanger":
        if cw_filter_ov=="CW Only":      df_donut=df[df["is_cw"]];  ds=" (CW Only)"
        elif cw_filter_ov=="Non-CW Only":df_donut=df[~df["is_cw"]]; ds=" (Non-CW Only)"
        else:                             df_donut=df;               ds=""
    else:
        df_donut=df; ds=""

    col1, col2 = st.columns(2, gap="small")
    with col1:
        if not shift_on:
            def draw_dn(ax):
                grp = df.groupby(["month","shift"])[EVENTS].sum()
                day   = get_shift(grp,"Day",  months_labels,EVENTS)
                night = get_shift(grp,"Night",months_labels,EVENTS)
                dt=day.sum(axis=1).values; nt=night.sum(axis=1).values
                y_max=max((dt+nt).max(),1); ax.set_ylim(0,y_max*1.15)
                ax.bar(x,dt,width=BAR_W,color=SHIFT_COLORS["Day"],  edgecolor="white",linewidth=0.5,label="Day")
                ax.bar(x,nt,width=BAR_W,bottom=dt,color=SHIFT_COLORS["Night"],edgecolor="white",linewidth=0.5,hatch="//",label="Night")
                for i in range(len(x)):
                    inner_label(ax,x[i],0,    dt[i],"D")
                    inner_label(ax,x[i],dt[i],nt[i],"N")
                ax.set_xticks(x); ax.set_xticklabels(months_labels,rotation=30,ha="right",fontsize=6)
                ax.set_ylabel("Episodes",fontsize=6,color="black")
                ax.legend(fontsize=6,loc="upper left",framealpha=0.9,edgecolor="black")
                style_bar(ax)
            wrap_plot("Monthly Episode Trend  (Day | Night)", draw_dn)
        else:
            def draw_dual(ax):
                grp = df.groupby(["month","shift"])[EVENTS].sum()
                day   = get_shift(grp,"Day",  months_labels,EVENTS)
                night = get_shift(grp,"Night",months_labels,EVENTS)
                w=BAR_W/2
                bd=np.zeros(len(months_labels)); bn=np.zeros(len(months_labels))
                for ev in EVENTS:
                    ax.bar(x-w/2,day[ev].values,  width=w,bottom=bd,color=COLORS[ev],edgecolor="white",linewidth=0.3)
                    ax.bar(x+w/2,night[ev].values,width=w,bottom=bn,color=COLORS[ev],edgecolor="white",linewidth=0.3)
                    bd+=day[ev].values; bn+=night[ev].values
                y_max=max(max(bd.max(),bn.max()),1); ax.set_ylim(0,y_max*1.15)
                for i in range(len(x)):
                    if bd[i]>0: safe_label(ax,x[i]-w/2,bd[i],"D",y_max*1.15)
                    if bn[i]>0: safe_label(ax,x[i]+w/2,bn[i],"N",y_max*1.15)
                ax.set_xticks(x); ax.set_xticklabels(months_labels,rotation=30,ha="right",fontsize=6)
                ax.set_ylabel("Episodes",fontsize=6,color="black"); style_bar(ax)
            wrap_plot("Monthly Episode Trend  (Shift × Event Type)", draw_dual)

    with col2:
        if equip=="Exchanger":
            plot_donut(f"Episode Distribution{ds}", df_donut[EVENTS].sum(), COLORS, top_n=10)
        else:
            plot_donut("Episode Distribution", df[EVENTS].sum(), COLORS, filter_top5=True)


# ══════════════════════════════════════════════════
# MONTHLY ANALYSIS
# ══════════════════════════════════════════════════
elif page == "Monthly":

    if equip == "Exchanger":
        fa, fb, _ = st.columns([1.5, 1.5, 5.0])
        with fa: selected_month = st.selectbox("Select Month",
                     df.sort_values("month_dt")["month"].dropna().unique(), key=f"mon_{equip}")
        with fb: cw_filter = st.selectbox("CW Filter",["All","CW Only","Non-CW Only"],0,key=f"cw_filter_{equip}")
    else:
        fa, _ = st.columns([1.5, 6.5])
        with fa: selected_month = st.selectbox("Select Month",
                     df.sort_values("month_dt")["month"].dropna().unique(), key=f"mon_{equip}")
        cw_filter = "All"

    fdf = df[df["month"]==selected_month].copy()
    if equip=="Exchanger":
        if cw_filter=="CW Only":       fdf=fdf[fdf["is_cw"]]
        elif cw_filter=="Non-CW Only": fdf=fdf[~fdf["is_cw"]]
    sfx = f" [{cw_filter}]" if equip=="Exchanger" and cw_filter!="All" else ""

    col1, col2 = st.columns(2, gap="small")
    with col1:
        if equip=="Exchanger" and cw_filter=="All":
            ga = fdf.groupby(eq_col)[EVENTS].sum()
            ga["_t"]=ga.sum(axis=1); ga=ga[ga["_t"]>0]
            top7=ga.sort_values("_t",ascending=False).head(7).index
            cw_v =np.array([int(fdf[fdf["is_cw"] &(fdf[eq_col]==e)][EVENTS].sum().sum()) for e in top7])
            ncw_v=np.array([int(fdf[~fdf["is_cw"]&(fdf[eq_col]==e)][EVENTS].sum().sum()) for e in top7])
            totals=cw_v+ncw_v
            def draw_mcw(ax):
                xi=np.arange(len(top7)); ym=max(totals.max(),1); ax.set_ylim(0,ym*1.18)
                ax.bar(xi,cw_v, width=BAR_W,color=CW_COLOR,   edgecolor="white",linewidth=0.5,label="CW")
                ax.bar(xi,ncw_v,width=BAR_W,bottom=cw_v,color=NONCW_COLOR,edgecolor="white",linewidth=0.5,hatch="//",label="Non-CW")
                gd=totals.sum()
                for i,tot in enumerate(totals):
                    inner_label(ax,xi[i],0,      cw_v[i], "CW",fontsize=5.2)
                    inner_label(ax,xi[i],cw_v[i],ncw_v[i],"NC",fontsize=5.2)
                    if tot>0 and gd>0: safe_label(ax,xi[i],tot,f"{tot/gd*100:.0f}%",ym*1.18,fontsize=5.5)
                ax.set_xticks(xi); ax.set_xticklabels(top7,rotation=25,ha="right",fontsize=6)
                ax.set_ylabel("Episodes",fontsize=6,color="black")
                ax.legend(fontsize=6,loc="upper right",framealpha=0.9,edgecolor="black"); style_bar(ax)
            wrap_plot(f"Top 7 Exchangers — CW/Non-CW  —  {selected_month}", draw_mcw)
        else:
            grp=fdf.groupby(eq_col)[EVENTS].sum()
            grp["_t"]=grp.sum(axis=1); grp=grp[grp["_t"]>0]
            top7n=grp.sort_values("_t",ascending=False).head(7).index
            ev_tot=fdf[EVENTS].sum().sort_values(ascending=False)
            top5=list(ev_tot[ev_tot>0].index[:5])
            t7df=grp.loc[top7n,[e for e in top5 if e in grp.columns]]
            def draw_ev(ax):
                ec=[e for e in top5 if e in t7df.columns]; bot=np.zeros(len(t7df))
                for ev in ec:
                    ax.bar(t7df.index,t7df[ev],bottom=bot,width=BAR_W,
                           color=COLORS.get(ev,"#94a3b8"),edgecolor="white",linewidth=0.4)
                    bot+=t7df[ev].values
                ym=max(bot.max(),1); ax.set_ylim(0,ym*1.18); gd=bot.sum()
                for i,tot in enumerate(bot):
                    if tot>0 and gd>0: safe_label(ax,i,tot,f"{tot/gd*100:.0f}%",ym*1.18,fontsize=5.5)
                ax.set_xticks(range(len(t7df))); ax.set_xticklabels(t7df.index,rotation=25,ha="right",fontsize=6)
                ax.set_ylabel("Episodes",fontsize=6,color="black"); style_bar(ax)
            lbl="Pumps" if equip=="Pump" else "Exchangers"
            wrap_plot(f"Top 7 {lbl} — Top 5 Events  —  {selected_month}{sfx}", draw_ev)

    with col2:
        if equip=="Exchanger":
            plot_donut(f"Top Events  —  {selected_month}{sfx}", fdf[EVENTS].sum(), COLORS, top_n=10)
        else:
            plot_donut(f"Top Events  —  {selected_month}", fdf[EVENTS].sum(), COLORS, filter_top5=True)


# ══════════════════════════════════════════════════
# EQUIPMENT ANALYSIS
# ══════════════════════════════════════════════════
elif page == "Equipment":

    if equip == "Exchanger":
        fa, fb, _ = st.columns([1.4, 1.6, 5.0])
        with fa: cw_eq = st.selectbox("CW Filter",["All","CW Only","Non-CW Only"],0,key=f"cw_eq_{equip}")
        eq_sub = df[df["is_cw"]] if cw_eq=="CW Only" else df[~df["is_cw"]] if cw_eq=="Non-CW Only" else df
        eq_list = eq_sub.groupby(eq_col)[EVENTS].sum().sum(axis=1).sort_values(ascending=False).index.tolist()
        with fb: selected_eq = st.selectbox("Select Exchanger", eq_list, key=f"sel_{equip}")
    else:
        fa, _ = st.columns([1.6, 6.4])
        eq_list = df.groupby(eq_col)[EVENTS].sum().sum(axis=1).sort_values(ascending=False).index.tolist()
        with fa: selected_eq = st.selectbox(f"Select {equip}", eq_list, key=f"sel_{equip}")

    # donut uses df (episode-flagged); history table uses df_raw
    eq_ep  = df[df[eq_col]==selected_eq]
    eq_raw = df_raw[df_raw[eq_col]==selected_eq]

    if equip=="Exchanger":
        cw_lbl = "CW" if is_cw(selected_eq) else "Non-CW"
        dt = f"Episode Dist — {selected_eq} [{cw_lbl}]"
    else:
        dt = f"Episode Dist — {selected_eq}"

    col1, col2 = st.columns(2, gap="small")
    with col1:
        st.markdown('<div class="plot-box"><div class="plot-title">Equipment History (all raw shifts)</div>',
                    unsafe_allow_html=True)
        hist = eq_raw[["date","shift",info_col]].sort_values("date").copy()
        hist.columns = ["Date","Shift","Event Info"]
        if hist.empty:
            st.markdown('<div class="no-data-msg">No data available</div>', unsafe_allow_html=True)
        else:
            hist["Date"] = hist["Date"].dt.strftime("%d-%b-%Y")
            ev_mask = eq_raw[EVENTS].sum(axis=1) > 0
            hist = hist[ev_mask.values].reset_index(drop=True)
            st.dataframe(hist, use_container_width=True, height=242)
        st.markdown("</div>", unsafe_allow_html=True)

    with col2:
        ev_sum = eq_ep[EVENTS].sum(); ev_sum = ev_sum[ev_sum>0]
        plot_donut(dt, ev_sum, make_colors(EVENTS, PUMP_COLORS_MAP if equip=="Pump" else EXCH_COLORS_MAP), top_n=10)


# ══════════════════════════════════════════════════
# EVENT ANALYSIS
# ══════════════════════════════════════════════════
elif page == "EventAnalysis":

    avail_evs  = [e for e in (PUMP_EVENTS if equip=="Pump" else EXCH_EVENTS)
                  if e in df.columns and int(df[e].sum())>0]
    ev_labels  = [e.replace("_"," ").title() for e in avail_evs]
    ev_lbl_map = dict(zip(ev_labels, avail_evs))

    if equip == "Exchanger":
        fa, fb, _ = st.columns([1.8, 1.5, 4.7])
        with fa: sel_ev_lbl  = st.selectbox("Select Event", ev_labels, key=f"evsel_{equip}")
        with fb: cw_ev_filt  = st.selectbox("CW Filter",["All","CW Only","Non-CW Only"],0,key=f"cw_evf_{equip}")
    else:
        fa, _ = st.columns([1.8, 6.2])
        with fa: sel_ev_lbl = st.selectbox("Select Event", ev_labels, key=f"evsel_{equip}")
        cw_ev_filt = "All"

    sel_ev   = ev_lbl_map[sel_ev_lbl]
    ev_color = COLORS_MAP.get(sel_ev, FALLBACK_COLORS[0])

    ep_all = load_pump_episodes() if equip=="Pump" else load_exchanger_episodes()
    ep_df  = ep_all[ep_all["Event"]==sel_ev_lbl].copy()

    if equip=="Exchanger" and cw_ev_filt!="All":
        cw_set = {e for e in ep_df["Equipment"].unique() if is_cw(e)}
        ep_df  = ep_df[ep_df["Equipment"].isin(cw_set)] if cw_ev_filt=="CW Only" \
                 else ep_df[~ep_df["Equipment"].isin(cw_set)]

    cw_sfx = f" [{cw_ev_filt}]" if equip=="Exchanger" and cw_ev_filt!="All" else ""
    col1, col2 = st.columns(2, gap="small")

    # ── Episode Log ───────────────────────────────
    with col1:
        st.markdown(f'<div class="plot-box"><div class="plot-title">Episode Log — {sel_ev_lbl}{cw_sfx}</div>',
                    unsafe_allow_html=True)
        if ep_df.empty:
            st.markdown('<div class="no-data-msg">No episodes found.</div>', unsafe_allow_html=True)
        else:
            disp = ep_df.drop(columns=["Shifts Open"],errors="ignore").reset_index(drop=True)
            def color_days(val):
                try:
                    v=float(val)
                    if v<=1:   return "background-color:#d1fae5;color:#064e3b;"
                    elif v<=3: return "background-color:#fef9c3;color:#713f12;"
                    elif v<=7: return "background-color:#fed7aa;color:#7c2d12;"
                    else:      return "background-color:#fecaca;color:#7f1d1d;"
                except: return ""
            styler = disp.style.format({"Days Open":"{:.1f}"})
            try:    styler = styler.map(color_days, subset=["Days Open"])
            except: styler = styler.applymap(color_days, subset=["Days Open"])
            st.dataframe(styler, use_container_width=True, height=242)
            avg_d = ep_df["Days Open"].mean()
            max_d = ep_df["Days Open"].max()
            max_q = ep_df.loc[ep_df["Days Open"].idxmax(),"Equipment"]
            st.markdown(
                f'<div style="font-size:9px;color:#475569;font-family:Times New Roman,serif;'
                f'text-align:right;padding:1px 3px;">'
                f'{len(ep_df)} episodes &nbsp;|&nbsp; Avg: <b>{avg_d:.1f}d</b>'
                f' &nbsp;|&nbsp; Longest: <b>{max_d:.1f}d</b> on {max_q}</div>',
                unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # ── Top-5 equipment bar chart ─────────────────
    with col2:
        ep_counts = (ep_df.groupby("Equipment").size()
                     .sort_values(ascending=False).head(5)) if not ep_df.empty else pd.Series(dtype=int)

        if ep_counts.empty:
            st.markdown(f'<div class="plot-box"><div class="plot-title">Top 5 {equip}s — {sel_ev_lbl}{cw_sfx}</div>'
                        f'<div class="no-data-msg">No data available</div></div>', unsafe_allow_html=True)
        else:
            def draw_top5(ax):
                eq_names=ep_counts.index.tolist(); ev_vals=ep_counts.values
                xi=np.arange(len(eq_names)); ym=max(ev_vals.max(),1)
                ax.bar(xi,ev_vals,width=BAR_W,color=ev_color,edgecolor="white",linewidth=0.6,zorder=3)
                ax.set_ylim(0,ym*1.22)
                for i,v in enumerate(ev_vals):
                    safe_label(ax,xi[i],v,f"{int(v)}",ym*1.22,fontsize=6.5)
                ax.set_xticks(xi); ax.set_xticklabels(eq_names,rotation=25,ha="right",fontsize=6.5)
                ax.set_ylabel("Episode Count",fontsize=6,color="black"); style_bar(ax)
            wrap_plot(f"Top 5 {equip}s — {sel_ev_lbl}{cw_sfx}", draw_top5)
