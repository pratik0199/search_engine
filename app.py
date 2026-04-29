import pandas as pd
import numpy as np
import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.gridspec as gridspec
import matplotlib.ticker as mticker

st.set_page_config(layout="wide")

# ─────────────────────────────────────────────────
# CSS
# ─────────────────────────────────────────────────
st.markdown("""
<style>
.block-container {
    padding-top: 0.4rem !important;
    padding-bottom: 0rem !important;
    padding-left: 1.2rem !important;
    padding-right: 1.2rem !important;
    max-width: 100% !important;
}
html, body, [class*="css"] { font-family: "Times New Roman", serif; }
div[data-testid="stVerticalBlock"] > div { gap: 0rem !important; }

div.stButton > button {
    width: 100%;
    border-radius: 4px;
    height: 32px;
    font-weight: 600;
    font-size: 12px;
    background-color: #1e293b;
    border: 1px solid #334155;
    color: white !important;
    transition: background-color 0.15s, color 0.15s;
}
div.stButton > button p,
div.stButton > button span,
div.stButton > button div {
    color: white !important;
    font-weight: 600 !important;
    font-size: 12px !important;
}
div.stButton > button:hover { background-color: #0f172a; }

div[data-baseweb="select"] { max-width: 220px; }
div[data-baseweb="select"] > div {
    min-height: 32px !important;
    background-color: #ffffff !important;
    border: 1.5px solid #1e293b !important;
    border-radius: 4px !important;
}
div[data-baseweb="select"] > div:hover { border-color: #475569 !important; }
div[data-baseweb="select"] svg { fill: #1e293b !important; }
div[data-baseweb="select"] [class*="placeholder"],
div[data-baseweb="select"] [class*="singleValue"] {
    color: #1e293b !important;
    font-family: "Times New Roman", serif !important;
    font-size: 12px !important;
    font-weight: 600 !important;
}
div[data-baseweb="select"] input { color: #1e293b !important; font-size: 12px !important; }
div[data-testid="stSelectbox"] label {
    font-family: "Times New Roman", serif !important;
    font-size: 12px !important;
    font-weight: 600 !important;
    color: #1e293b !important;
}

/* ── KPI CARDS ── */
.kpi-row { display:flex; gap:8px; margin-bottom:6px; margin-top:2px; }
.kpi-card {
    flex: 1;
    background: #f8fafc;
    border: 2px solid #1e293b;
    border-left: 4px solid #1e293b;
    border-radius: 6px;
    padding: 7px 12px 6px 12px;
    min-width: 0;
    font-family: "Times New Roman", serif;
    text-align: center;
}
.kpi-label {
    font-size: 8px; font-weight: 900; color: #1e293b;
    text-transform: uppercase; letter-spacing: 1px; margin-bottom: 3px;
    text-align: center;
}
.kpi-value {
    font-size: 20px; font-weight: 700; color: #1e293b;
    line-height: 1; font-family: "Times New Roman", serif;
    text-align: center;
}
.kpi-sub { font-size:8px; color:#94a3b8; margin-top:2px; font-family:"Times New Roman",serif; text-align:center; }
.kpi-card.c1 { border-left-color:#2563eb; } .kpi-card.c1 .kpi-value { color:#2563eb; }
.kpi-card.c2 { border-left-color:#65a30d; } .kpi-card.c2 .kpi-value { color:#65a30d; }
.kpi-card.c3 { border-left-color:#d97706; } .kpi-card.c3 .kpi-value { color:#d97706; }
.kpi-card.c4 { border-left-color:#7c3aed; } .kpi-card.c4 .kpi-value { color:#7c3aed; }

/* ── PLOT BOX ── */
.plot-box {
    border: 2px solid black; border-radius: 6px;
    padding: 4px 6px 2px 6px; background: #f8fafc; margin-bottom: 4px;
}
.plot-title {
    font-size:12px; font-weight:700; color:#1e293b;
    margin-bottom:1px; font-family:"Times New Roman",serif;
    text-align: center;
}
.no-data-msg { color:#64748b; font-size:13px; font-family:"Times New Roman",serif; text-align:center; padding:40px 8px; }
.badge-cw {
    display:inline-block; background:#0891b2; color:white; font-size:10px; font-weight:700;
    padding:1px 7px; border-radius:10px; margin-left:6px; vertical-align:middle; font-family:"Times New Roman",serif;
}
.badge-noncw {
    display:inline-block; background:#d97706; color:white; font-size:10px; font-weight:700;
    padding:1px 7px; border-radius:10px; margin-left:6px; vertical-align:middle; font-family:"Times New Roman",serif;
}
h2 { margin-bottom:0.2rem !important; margin-top:0 !important; }
hr { margin:0.2rem 0 0.3rem 0 !important; }
header { visibility:hidden; }
footer { visibility:hidden; }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────
# CW LIST
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
# FIX 5: Pump events — vibration removed, maintenance_pm kept
# ─────────────────────────────────────────────────
PUMP_ALL_EVENTS = [
    "seal_failure", "low_level", "pump_swap", "startup", "shutdown",
    "trip_fault", "low_pressure", "oil_lubrication", "steam_issue",
    "strainer_clean", "maintenance_pm",
]
# For pump, ALL events are shown everywhere (maintenance_pm included in Overall/Monthly too)
PUMP_EVENTS_FULL_SET = PUMP_ALL_EVENTS

EXCH_ALL_EVENTS = [
    "tube_leak", "tube_plug", "tube_repair", "tube_bundle_replace",
    "tube_installed", "tube_cleaning", "hydroblast_cleaning",
    "installing_plates", "gasket_installed", "pressure_test",
    "temp_cooler_replace", "transmitter_blowdown", "drained_oil",
    "bypass_isolation", "sv_repair_replacement", "steam_issue",
    "n2_purging", "dew_point_check", "install_heater",
    "capital_project", "cleaning", "work_completed",
]
EXCH_EXCLUDE = {"maintenance"}
EXCH_EVENTS_FULL_SET = EXCH_ALL_EVENTS + list(EXCH_EXCLUDE)

# ─────────────────────────────────────────────────
# COLOUR MAPS
# ─────────────────────────────────────────────────
PUMP_COLORS_MAP = {
    "seal_failure":"#2563eb",   "low_level":"#6366f1",
    "pump_swap":"#d97706",      "startup":"#059669",
    "shutdown":"#64748b",       "trip_fault":"#7c3aed",
    "low_pressure":"#0891b2",   "oil_lubrication":"#be185d",
    "steam_issue":"#ea580c",    "strainer_clean":"#65a30d",
    "maintenance_pm":"#78350f",
}
EXCH_COLORS_MAP = {
    "tube_leak":"#dc2626",              "tube_plug":"#f59e0b",
    "tube_repair":"#2563eb",            "tube_bundle_replace":"#7c3aed",
    "tube_installed":"#0284c7",         "tube_cleaning":"#06b6d4",
    "hydroblast_cleaning":"#059669",    "installing_plates":"#84cc16",
    "gasket_installed":"#d97706",       "pressure_test":"#f97316",
    "temp_cooler_replace":"#be185d",    "transmitter_blowdown":"#0891b2",
    "drained_oil":"#64748b",            "bypass_isolation":"#475569",
    "sv_repair_replacement":"#be185d",  "steam_issue":"#ea580c",
    "n2_purging":"#65a30d",             "dew_point_check":"#0d9488",
    "install_heater":"#92400e",         "capital_project":"#92400e",
    "cleaning":"#4d7c0f",               "maintenance":"#334155",
    "work_completed":"#1d4ed8",
}
FALLBACK_COLORS = [
    "#6366f1","#f43f5e","#10b981","#f97316","#8b5cf6",
    "#06b6d4","#84cc16","#ec4899","#14b8a6","#ef4444",
]

CW_COLOR    = "#0891b2"
NONCW_COLOR = "#d97706"
SHIFT_COLORS = {"Day":"#0d9488","Night":"#475569"}
PLOT_BG   = "#f8fafc"
GRID_CLR  = "#cbd5e1"
PLOT_FIGSIZE = (6.0, 3.2)
BAR_WIDTH = 0.50


def make_colors(events, color_map):
    out = {}; fi = 0
    for e in events:
        if e in color_map: out[e] = color_map[e]
        else: out[e] = FALLBACK_COLORS[fi % len(FALLBACK_COLORS)]; fi += 1
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
    for col in PUMP_EVENTS_FULL_SET:
        if col not in df.columns: df[col] = 0
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).astype(int)
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
    for col in EXCH_EVENTS_FULL_SET:
        if col not in df.columns: df[col] = 0
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).astype(int)
    return df

pump_df = load_pump()
exch_df = load_exchanger()


# ─────────────────────────────────────────────────
# PLOT HELPERS
# ─────────────────────────────────────────────────
def apply_black_border(ax):
    for sp in ax.spines.values():
        sp.set_visible(True); sp.set_linewidth(2.0); sp.set_color("black")

def style_bar(ax):
    ax.set_facecolor(PLOT_BG)
    ax.grid(axis='y', linestyle='--', linewidth=0.7, alpha=0.6, color=GRID_CLR)
    ax.grid(axis='x', visible=False)
    ax.tick_params(colors="black", labelsize=7)
    apply_black_border(ax)

def get_shift(grouped, name, months_labels, events):
    try: return grouped.xs(name, level=1).reindex(months_labels).fillna(0)
    except Exception: return pd.DataFrame(0, index=months_labels, columns=events)

def plot_compartment(title, draw_fn, figsize=PLOT_FIGSIZE):
    st.markdown(f'<div class="plot-box"><div class="plot-title">{title}</div>',
                unsafe_allow_html=True)
    fig, ax = plt.subplots(figsize=figsize, facecolor=PLOT_BG)
    fig.patch.set_facecolor(PLOT_BG)
    draw_fn(ax)
    plt.tight_layout(pad=0.8)
    st.pyplot(fig, use_container_width=True)
    plt.close(fig)
    st.markdown('</div>', unsafe_allow_html=True)


# ─────────────────────────────────────────────────
# FIX 1 HELPER: safe bar label — clamp to axis limits
# ─────────────────────────────────────────────────
def safe_bar_label(ax, x_pos, y_val, text, y_max_data,
                   fontsize=6, color="black", bold=True):
    """Place a text label above a bar, never exceeding the visible axis top."""
    margin = y_max_data * 0.04
    y_text = min(y_val + margin, y_max_data * 0.97)
    ax.text(x_pos, y_text, text,
            ha="center", va="bottom",
            fontsize=fontsize, fontweight="bold" if bold else "normal",
            color=color, clip_on=True)


# ─────────────────────────────────────────────────
# DONUT
# ─────────────────────────────────────────────────
def top_n_with_others(series, colors, top_n=10):
    series = series[series > 0].sort_values(ascending=False)
    if series.empty: return pd.Series(dtype=float), {}, []
    if len(series) <= top_n:
        return series, {k: colors.get(k,"#94a3b8") for k in series.index}, []
    top  = series.iloc[:top_n]
    rest = series.iloc[top_n:]
    result = pd.concat([top, pd.Series({"Others": rest.sum()})])
    out_colors = {k: colors.get(k,"#94a3b8") for k in top.index}
    out_colors["Others"] = "#94a3b8"
    return result, out_colors, list(rest.index)

def top5_above5pct(series, colors):
    total = series.sum()
    if total == 0: return pd.Series(dtype=float), {}
    pct  = series / total * 100
    filt = series[pct > 5].nlargest(5)
    return filt, {k: colors.get(k,"#94a3b8") for k in filt.index}

def plot_donut(title, raw_series, all_colors,
               filter_top5=False, top_n=None, figsize=PLOT_FIGSIZE):
    others_list = []
    if top_n is not None:
        data, colors, others_list = top_n_with_others(raw_series, all_colors, top_n)
    elif filter_top5:
        data, colors = top5_above5pct(raw_series, all_colors)
    else:
        data   = raw_series.reindex(list(all_colors.keys())).fillna(0)
        data   = data[data > 0]
        colors = {k: all_colors.get(k,"#94a3b8") for k in data.index}

    if data.empty:
        st.markdown(
            f'<div class="plot-box"><div class="plot-title">{title}</div>'
            f'<div class="no-data-msg">No data available</div></div>',
            unsafe_allow_html=True)
        return

    total = data.sum()
    fig   = plt.figure(figsize=figsize, facecolor=PLOT_BG)
    fig.patch.set_facecolor(PLOT_BG)
    gs    = gridspec.GridSpec(1, 2, figure=fig,
                              width_ratios=[0.50, 0.50],
                              left=0.01, right=0.99,
                              top=0.97, bottom=0.06, wspace=0.0)
    ax_pie = fig.add_subplot(gs[0])
    ax_leg = fig.add_subplot(gs[1])

    ax_pie.set_facecolor(PLOT_BG)
    for sp in ax_pie.spines.values(): sp.set_visible(False)

    wedge_colors = [colors.get(k,"#94a3b8") for k in data.index]
    wedges, _, autotexts = ax_pie.pie(
        data, colors=wedge_colors, startangle=90,
        wedgeprops=dict(width=0.40, edgecolor="white", linewidth=0.8),
        autopct=lambda p: f"{p:.0f}%" if p >= 7 else "",
        pctdistance=0.76, radius=0.88, center=(0, 0.06),
    )
    for at in autotexts:
        at.set_fontsize(6.5); at.set_color("white"); at.set_fontweight("bold")

    ax_pie.text(0, 0.06, f"Total\n{int(total)}",
                ha="center", va="center",
                fontsize=8, fontweight="bold", color="#1e293b")

    ax_leg.set_facecolor(PLOT_BG); ax_leg.axis("off")
    ax_leg.set_xlim(0, 1); ax_leg.set_ylim(0, 1)

    n     = len(data)
    row_h = min(0.12, 0.90 / max(n, 1))
    pad_t = 0.96
    hw = 0.10; hh = min(0.050, row_h * 0.50)

    for i, (ft, val) in enumerate(data.items()):
        yc = pad_t - i * row_h
        if yc < 0.02: break
        c = colors.get(ft, "#94a3b8")
        ax_leg.add_patch(plt.Rectangle(
            (0.01, yc - hh / 2), hw, hh,
            transform=ax_leg.transAxes,
            color=c, clip_on=False, zorder=10
        ))
        pct_val = val / total * 100
        label   = ft.replace("_", " ").title()
        ax_leg.text(0.01 + hw + 0.05, yc,
                    f"{label}  {pct_val:.0f}%",
                    transform=ax_leg.transAxes,
                    fontsize=5.8, va="center", color="#1e293b",
                    clip_on=False, fontweight="600")

    if others_list:
        others_str = ", ".join(e.replace("_"," ").title() for e in others_list)
        fig.text(0.01, 0.01, f"Others: {others_str}",
                 fontsize=4.8, color="#64748b", ha="left", va="bottom")

    st.markdown(f'<div class="plot-box"><div class="plot-title">{title}</div>',
                unsafe_allow_html=True)
    st.pyplot(fig, use_container_width=True)
    plt.close(fig)
    st.markdown('</div>', unsafe_allow_html=True)


# ─────────────────────────────────────────────────
# FIX 3A: OVERALL CW bifurcation — checkbox toggle for donut
# ─────────────────────────────────────────────────
def plot_cw_overall_donut(df, events, colors):
    """Side-by-side CW / Non-CW donuts for Overall page."""
    cw_tot  = int(df[df["is_cw"]][events].sum().sum())
    ncw_tot = int(df[~df["is_cw"]][events].sum().sum())
    total   = cw_tot + ncw_tot
    if total == 0:
        st.markdown('<div class="plot-box"><div class="plot-title">CW vs Non-CW Distribution</div>'
                    '<div class="no-data-msg">No data available</div></div>',
                    unsafe_allow_html=True)
        return

    fig = plt.figure(figsize=PLOT_FIGSIZE, facecolor=PLOT_BG)
    fig.patch.set_facecolor(PLOT_BG)
    gs  = gridspec.GridSpec(1, 2, figure=fig,
                            left=0.04, right=0.96,
                            top=0.84, bottom=0.14, wspace=0.35)
    for idx, (label, val, color) in enumerate([
        ("CW", cw_tot, CW_COLOR), ("Non-CW", ncw_tot, NONCW_COLOR)
    ]):
        ax = fig.add_subplot(gs[idx])
        ax.set_facecolor(PLOT_BG)
        for sp in ax.spines.values(): sp.set_visible(False)
        rem = total - val
        ax.pie([val, rem], colors=[color, "#e2e8f0"], startangle=90,
               wedgeprops=dict(width=0.38, edgecolor="white", linewidth=0.8),
               radius=0.88, center=(0, 0))
        pct = val / total * 100 if total > 0 else 0
        ax.text(0, 0.10, f"{val}",    ha="center", va="center", fontsize=11, fontweight="bold", color=color)
        ax.text(0, -0.20, f"{pct:.1f}%", ha="center", va="center", fontsize=8, color="#475569")
        ax.set_title(label, fontsize=9, fontweight="bold", color=color, pad=3)

    st.markdown('<div class="plot-box"><div class="plot-title">CW vs Non-CW Distribution</div>',
                unsafe_allow_html=True)
    st.pyplot(fig, use_container_width=True)
    plt.close(fig)
    st.markdown('</div>', unsafe_allow_html=True)


# ─────────────────────────────────────────────────
# FIX 3B: MONTHLY — single stacked bar CW/Non-CW bifurcated by colour
# ─────────────────────────────────────────────────
def plot_monthly_cw_combined(fdf, events, eq_col, selected_month, suffix=""):
    """
    Single stacked bar chart: each equipment bar is split CW (solid) / Non-CW (hatched).
    FIX 1 applied: labels clamped within axes.
    FIX 2 applied: equipment with zero total filtered out.
    """
    grp_cw  = fdf[fdf["is_cw"]].groupby(eq_col)[events].sum()
    grp_ncw = fdf[~fdf["is_cw"]].groupby(eq_col)[events].sum()

    all_eq  = fdf.groupby(eq_col)[events].sum()
    all_eq["Total"] = all_eq.sum(axis=1)
    # FIX 2: keep only equipment with at least 1 event
    all_eq  = all_eq[all_eq["Total"] > 0]
    top7    = all_eq.sort_values("Total", ascending=False).head(7).index

    cw_vals  = grp_cw.reindex(top7).fillna(0).sum(axis=1).values
    ncw_vals = grp_ncw.reindex(top7).fillna(0).sum(axis=1).values
    totals   = cw_vals + ncw_vals

    def draw(ax):
        x = np.arange(len(top7))
        bars_cw  = ax.bar(x, cw_vals,  width=BAR_WIDTH, color=CW_COLOR,
                          edgecolor="white", linewidth=0.6, label="CW")
        bars_ncw = ax.bar(x, ncw_vals, width=BAR_WIDTH, bottom=cw_vals,
                          color=NONCW_COLOR, edgecolor="white", linewidth=0.6,
                          hatch="//", label="Non-CW")
        y_max = max(totals.max(), 1)
        ax.set_ylim(0, y_max * 1.18)   # FIX 1: headroom so labels fit
        grand = totals.sum()
        for i, tot in enumerate(totals):
            if tot > 0:
                pct = tot / grand * 100 if grand > 0 else 0
                safe_bar_label(ax, x[i], tot, f"{pct:.0f}%", y_max * 1.18,
                               fontsize=6.5, color="#1e293b")
        ax.set_xticks(x)
        ax.set_xticklabels(top7, rotation=25, ha='right', fontsize=7)
        ax.set_ylabel("Event Count", fontsize=7, color="black")
        ax.legend(fontsize=7, loc='upper right', framealpha=0.9, edgecolor="black")
        style_bar(ax)

    lbl = "Exchanger"
    plot_compartment(f"Top 7 {lbl}s — CW/Non-CW  —  {selected_month}{suffix}", draw)


def plot_monthly_pump_top7(fdf, events, colors, eq_col, selected_month):
    """
    Monthly pump bar — top 5 events stacked, % label on top.
    FIX 1 + FIX 2 applied.
    """
    grp = fdf.groupby(eq_col)[events].sum()
    grp["Total"] = grp.sum(axis=1)
    # FIX 2: only equipment with >0 events
    grp = grp[grp["Total"] > 0]
    top7_names = grp.sort_values("Total", ascending=False).head(7).index

    ev_totals_month = fdf[events].sum().sort_values(ascending=False)
    top5_events = list(ev_totals_month[ev_totals_month > 0].index[:5])
    top7_df = grp.loc[top7_names, [e for e in top5_events if e in grp.columns]]

    def draw(ax):
        ev_cols = [e for e in top5_events if e in top7_df.columns]
        bot = np.zeros(len(top7_df))
        for ev in ev_cols:
            ax.bar(top7_df.index, top7_df[ev], bottom=bot,
                   width=BAR_WIDTH, color=colors.get(ev,"#94a3b8"),
                   edgecolor="white", linewidth=0.5)
            bot += top7_df[ev].values
        y_max = max(bot.max(), 1)
        ax.set_ylim(0, y_max * 1.18)   # FIX 1: headroom
        grand = bot.sum()
        for i, tot in enumerate(bot):
            if tot > 0:
                pct = tot / grand * 100 if grand > 0 else 0
                safe_bar_label(ax, i, tot, f"{pct:.0f}%", y_max * 1.18,
                               fontsize=6.5, color="#1e293b")
        ax.set_xticks(range(len(top7_df)))
        ax.set_xticklabels(top7_df.index, rotation=25, ha='right', fontsize=7)
        ax.set_ylabel("Event Count", fontsize=7, color="black")
        style_bar(ax)

    plot_compartment(f"Top 7 Pumps — Top 5 Events  —  {selected_month}", draw)


# ─────────────────────────────────────────────────
# CW TREND (Overall exchanger)
# ─────────────────────────────────────────────────
def plot_cw_noncw_trend(df, months_labels, events):
    x = np.arange(len(months_labels))
    cw_mon  = (df[df["is_cw"]].groupby("month")[events].sum()
               .reindex(months_labels).fillna(0).sum(axis=1).values)
    ncw_mon = (df[~df["is_cw"]].groupby("month")[events].sum()
               .reindex(months_labels).fillna(0).sum(axis=1).values)

    def draw(ax):
        ax.bar(x, cw_mon,  width=BAR_WIDTH, color=CW_COLOR,
               edgecolor="white", linewidth=0.6, label="CW")
        ax.bar(x, ncw_mon, width=BAR_WIDTH, bottom=cw_mon,
               color=NONCW_COLOR, edgecolor="white", linewidth=0.6,
               hatch="//", label="Non-CW")
        y_max = max((cw_mon + ncw_mon).max(), 1)
        ax.set_ylim(0, y_max * 1.12)
        for i in range(len(x)):
            if cw_mon[i]  > 0: ax.text(x[i], cw_mon[i]/2,            "CW", ha="center", va="center", fontsize=5.5, fontweight="bold", color="white", zorder=6)
            if ncw_mon[i] > 0: ax.text(x[i], cw_mon[i]+ncw_mon[i]/2, "NC", ha="center", va="center", fontsize=5.5, fontweight="bold", color="white", zorder=6)
        ax.set_xticks(x)
        ax.set_xticklabels(months_labels, rotation=30, ha='right', fontsize=7)
        ax.set_ylabel("Event Count", fontsize=7, color="black")
        ax.legend(fontsize=7, loc='upper left', framealpha=0.9, edgecolor="black")
        style_bar(ax)

    plot_compartment("Monthly Trend  — CW vs Non-CW", draw)


def plot_cw_event_breakdown(df, events, colors, cw_flag, title):
    sub = df[df["is_cw"]] if cw_flag else df[~df["is_cw"]]
    plot_donut(title, sub[events].sum(), colors, top_n=10)


# ─────────────────────────────────────────────────
# KPI CARDS
# ─────────────────────────────────────────────────
def render_kpi(df, events, months_labels):
    total_ev  = int(df[events].sum().sum())
    total_mon = len(months_labels)
    avg_pm    = round(total_ev / max(total_mon, 1), 1)
    ev_by_mon = (df.groupby("month")[events].sum()
                 .reindex(months_labels).fillna(0).sum(axis=1))
    peak_mon  = ev_by_mon.idxmax() if not ev_by_mon.empty else "—"
    peak_val  = int(ev_by_mon.max()) if not ev_by_mon.empty else 0
    ev_totals = df[events].sum().sort_values(ascending=False)
    top_ev    = ev_totals.index[0].replace("_"," ").title() if len(ev_totals)>0 else "—"
    top_ev_cnt= int(ev_totals.iloc[0]) if len(ev_totals)>0 else 0

    st.markdown(f"""
    <div class="kpi-row">
      <div class="kpi-card c1">
        <div class="kpi-label"><b>Total Events</b></div>
        <div class="kpi-value">{total_ev:,}</div>
        <div class="kpi-sub">All periods combined</div>
      </div>
      <div class="kpi-card c2">
        <div class="kpi-label"><b>Avg Events / Month</b></div>
        <div class="kpi-value">{avg_pm}</div>
        <div class="kpi-sub">Across {total_mon} months</div>
      </div>
      <div class="kpi-card c3">
        <div class="kpi-label"><b>Peak Month</b></div>
        <div class="kpi-value" style="font-size:11px;padding-top:4px;">{peak_mon}</div>
        <div class="kpi-sub">{peak_val} events recorded</div>
      </div>
      <div class="kpi-card c4">
        <div class="kpi-label"><b>Top Event Type</b></div>
        <div class="kpi-value" style="font-size:11px;padding-top:4px;">{top_ev}</div>
        <div class="kpi-sub">{top_ev_cnt} occurrences</div>
      </div>
    </div>
    """, unsafe_allow_html=True)


# ─────────────────────────────────────────────────
# TITLE + NAVIGATION
# ─────────────────────────────────────────────────
st.markdown(
    "<h2 style='text-align:center;color:#1e293b;font-family:Times New Roman,serif;'>"
    "Equipment Reliability Dashboard</h2>",
    unsafe_allow_html=True,
)

c0, c1, c2, c3, _ = st.columns([2.2, 1.1, 1.1, 1.1, 2.0])
with c0:
    equip = st.selectbox("", ["Pump", "Exchanger"],
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
PAGE_KEYS = {
    "Overall":   f"btn_ov_{equip}",
    "Monthly":   f"btn_mo_{equip}",
    "Equipment": f"btn_eq_{equip}",
}
active_key = PAGE_KEYS[page]

st.markdown(f"""
<script>
(function(){{
    const activeKey = "{active_key}";
    const pageMap = {{
        "Overall Analysis": "{PAGE_KEYS['Overall']}",
        "Monthly Analysis": "{PAGE_KEYS['Monthly']}",
        "{equip} Analysis": "{PAGE_KEYS['Equipment']}"
    }};
    function applyActive(){{
        window.parent.document.querySelectorAll('.stButton button').forEach(function(btn){{
            const txt = btn.innerText.trim();
            if (pageMap[txt] === activeKey) {{
                btn.style.setProperty('background-color','#ffffff','important');
                btn.style.setProperty('color','#1e293b','important');
                btn.style.setProperty('border','2px solid #1e293b','important');
                btn.style.setProperty('font-weight','700','important');
                btn.querySelectorAll('*').forEach(el => {{
                    el.style.setProperty('color','#1e293b','important');
                }});
            }} else if (pageMap[txt]) {{
                btn.style.setProperty('background-color','#1e293b','important');
                btn.style.setProperty('color','#ffffff','important');
                btn.style.setProperty('border','1px solid #334155','important');
                btn.querySelectorAll('*').forEach(el => {{
                    el.style.setProperty('color','#ffffff','important');
                }});
            }}
        }});
    }}
    applyActive();
    [100,300,600,1200].forEach(t => setTimeout(applyActive, t));
    new MutationObserver(applyActive).observe(
        window.parent.document.body, {{childList:true, subtree:true}}
    );
}})();
</script>
""", unsafe_allow_html=True)

st.markdown("<hr style='margin:0.2rem 0 0.3rem 0;border-color:#94a3b8;'>",
            unsafe_allow_html=True)


# ─────────────────────────────────────────────────
# ACTIVE CONFIG
# ─────────────────────────────────────────────────
if equip == "Pump":
    df           = pump_df.copy()
    eq_col       = "pump"
    info_col     = "pump_info"
    color_map    = PUMP_COLORS_MAP
    # FIX 5: all 11 pump events used everywhere
    EVENTS       = [e for e in PUMP_ALL_EVENTS if e in df.columns]
    COLORS       = make_colors(EVENTS, color_map)
    EVENTS_FULL  = EVENTS
    COLORS_FULL  = COLORS
else:
    df           = exch_df.copy()
    eq_col       = "exchanger"
    info_col     = "exchanger_info"
    color_map    = EXCH_COLORS_MAP
    EVENTS       = [e for e in EXCH_ALL_EVENTS if e in df.columns]
    COLORS       = make_colors(EVENTS, color_map)
    EVENTS_FULL  = [e for e in EXCH_EVENTS_FULL_SET if e in df.columns]
    COLORS_FULL  = make_colors(EVENTS_FULL, color_map)

months_sorted = sorted(df["month_dt"].dropna().unique())
months_labels = [pd.to_datetime(m).strftime("%B-%Y") for m in months_sorted]
x             = np.arange(len(months_labels))

render_kpi(df, EVENTS, months_labels)


# ══════════════════════════════════════════════════
# OVERALL ANALYSIS
# ══════════════════════════════════════════════════
if page == "Overall":

    if equip == "Exchanger":
        colA, colB, colC, _ = st.columns([1.2, 1.2, 1.4, 4])
        with colA: bif     = st.selectbox("Shift Bifurcation", ["OFF","ON"], index=0, key=f"bif_{equip}")
        with colB: cw_mode = st.selectbox("CW Bifurcation",   ["OFF","ON"], index=0, key=f"cw_bif_{equip}")
        # FIX 3A: checkbox to show CW/Non-CW donut (Overall exchanger)
        with colC: show_cw_donut = st.checkbox("Show CW/Non-CW Donut", value=False, key=f"cw_donut_{equip}")
        shift_on = bif == "ON"; cw_on = cw_mode == "ON"
    else:
        colA, _ = st.columns([1, 5])
        with colA: bif = st.selectbox("Shift Bifurcation", ["OFF","ON"], index=0, key=f"bif_{equip}")
        shift_on = bif == "ON"; cw_on = False; show_cw_donut = False

    # ── CW bifurcation ON ─────────────────────────────────────────────────
    if equip == "Exchanger" and cw_on:
        col1, col2 = st.columns(2, gap="small")
        with col1: plot_cw_noncw_trend(df, months_labels, EVENTS)
        with col2:
            # FIX 3A: show donut only if checkbox ticked, otherwise event breakdown
            if show_cw_donut:
                plot_cw_overall_donut(df, EVENTS, COLORS)
            else:
                plot_cw_event_breakdown(df, EVENTS, COLORS, cw_flag=True,
                                        title="CW Exchangers — Top Events")
        if not show_cw_donut:
            col3, col4 = st.columns(2, gap="small")
            with col3: pass  # CW breakdown already shown above
            with col4:
                plot_cw_event_breakdown(df, EVENTS, COLORS, cw_flag=False,
                                        title="Non-CW Exchangers — Top Events")

    # ── Normal (shift OFF) ────────────────────────────────────────────────
    elif not shift_on:
        col1, col2 = st.columns(2, gap="small")
        with col1:
            def draw_dn(ax):
                grp   = df.groupby(["month","shift"])[EVENTS].sum()
                day   = get_shift(grp,"Day",  months_labels, EVENTS)
                night = get_shift(grp,"Night",months_labels, EVENTS)
                dt    = day.sum(axis=1).values
                nt    = night.sum(axis=1).values
                ax.bar(x, dt, width=BAR_WIDTH, color=SHIFT_COLORS["Day"],
                       edgecolor="white", linewidth=0.6, label="Day")
                ax.bar(x, nt, width=BAR_WIDTH, bottom=dt,
                       color=SHIFT_COLORS["Night"], edgecolor="white",
                       linewidth=0.6, hatch="//", label="Night")
                y_max = max((dt + nt).max(), 1)
                ax.set_ylim(0, y_max * 1.12)   # FIX 1
                for i in range(len(x)):
                    if dt[i]>0: ax.text(x[i], dt[i]/2,       "D", ha="center", va="center", fontsize=6, fontweight="bold", color="white", zorder=6)
                    if nt[i]>0: ax.text(x[i], dt[i]+nt[i]/2, "N", ha="center", va="center", fontsize=6, fontweight="bold", color="white", zorder=6)
                ax.set_xticks(x)
                ax.set_xticklabels(months_labels, rotation=30, ha='right', fontsize=7)
                ax.set_ylabel("Event Count", fontsize=7, color="black")
                ax.legend(fontsize=7, loc='upper left', framealpha=0.9, edgecolor="black")
                style_bar(ax)
            plot_compartment("Monthly Event Trend  (Day | Night)", draw_dn)

        with col2:
            if equip == "Exchanger":
                if show_cw_donut:
                    plot_cw_overall_donut(df, EVENTS, COLORS)
                else:
                    plot_donut("Overall Event Distribution", df[EVENTS].sum(), COLORS, top_n=10)
            else:
                plot_donut("Overall Event Distribution", df[EVENTS].sum(), COLORS, filter_top5=True)

    # ── Shift bifurcation ON ──────────────────────────────────────────────
    else:
        col1, col2 = st.columns(2, gap="small")
        with col1:
            def draw_dual(ax):
                grp   = df.groupby(["month","shift"])[EVENTS].sum()
                day   = get_shift(grp,"Day",  months_labels, EVENTS)
                night = get_shift(grp,"Night",months_labels, EVENTS)
                w  = BAR_WIDTH / 2
                bd = np.zeros(len(months_labels))
                bn = np.zeros(len(months_labels))
                for ev in EVENTS:
                    ax.bar(x-w/2, day[ev].values,   width=w, bottom=bd, color=COLORS[ev], edgecolor="white", linewidth=0.4)
                    ax.bar(x+w/2, night[ev].values, width=w, bottom=bn, color=COLORS[ev], edgecolor="white", linewidth=0.4)
                    bd += day[ev].values; bn += night[ev].values
                y_max = max(max(bd.max(), bn.max()), 1)
                ax.set_ylim(0, y_max * 1.12)   # FIX 1
                for i in range(len(x)):
                    if bd[i]>0: safe_bar_label(ax, x[i]-w/2, bd[i], "D", y_max*1.12, fontsize=6, color="black")
                    if bn[i]>0: safe_bar_label(ax, x[i]+w/2, bn[i], "N", y_max*1.12, fontsize=6, color="black")
                ax.set_xticks(x)
                ax.set_xticklabels(months_labels, rotation=30, ha='right', fontsize=7)
                ax.set_ylabel("Event Count", fontsize=7, color="black")
                style_bar(ax)
            plot_compartment("Monthly Event Trend  (Shift × Event Type)", draw_dual)

        with col2:
            if equip == "Exchanger":
                if show_cw_donut:
                    plot_cw_overall_donut(df, EVENTS, COLORS)
                else:
                    plot_donut("Overall Event Distribution", df[EVENTS].sum(), COLORS, top_n=10)
            else:
                plot_donut("Overall Event Distribution", df[EVENTS].sum(), COLORS, filter_top5=True)


# ══════════════════════════════════════════════════
# MONTHLY ANALYSIS
# ══════════════════════════════════════════════════
elif page == "Monthly":

    if equip == "Exchanger":
        colA, colB, _ = st.columns([1.2, 1.2, 5])
        with colA:
            month_list     = df.sort_values("month_dt")["month"].dropna().unique()
            selected_month = st.selectbox("Select Month", month_list, key=f"mon_{equip}")
        with colB:
            cw_filter = st.selectbox("CW Filter", ["All","CW Only","Non-CW Only"],
                                     index=0, key=f"cw_filter_{equip}")
    else:
        colA, _ = st.columns([1, 5])
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
        if equip == "Exchanger":
            if cw_filter == "All":
                # FIX 3B: single stacked bar with CW/Non-CW colour split
                plot_monthly_cw_combined(fdf, EVENTS, eq_col, selected_month)
            else:
                # Filtered: show normal top-7 bar for the subset
                grp = fdf.groupby(eq_col)[EVENTS].sum()
                grp["Total"] = grp.sum(axis=1)
                grp = grp[grp["Total"] > 0]   # FIX 2
                top7_names = grp.sort_values("Total", ascending=False).head(7).index
                ev_totals_m = fdf[EVENTS].sum().sort_values(ascending=False)
                top5_ev = list(ev_totals_m[ev_totals_m > 0].index[:5])
                top7_df = grp.loc[top7_names, [e for e in top5_ev if e in grp.columns]]

                def draw_filtered(ax):
                    ev_cols = [e for e in top5_ev if e in top7_df.columns]
                    bot = np.zeros(len(top7_df))
                    for ev in ev_cols:
                        ax.bar(top7_df.index, top7_df[ev], bottom=bot,
                               width=BAR_WIDTH, color=COLORS.get(ev,"#94a3b8"),
                               edgecolor="white", linewidth=0.5)
                        bot += top7_df[ev].values
                    y_max = max(bot.max(), 1)
                    ax.set_ylim(0, y_max * 1.18)
                    grand = bot.sum()
                    for i, tot in enumerate(bot):
                        if tot > 0:
                            pct = tot/grand*100 if grand>0 else 0
                            safe_bar_label(ax, i, tot, f"{pct:.0f}%", y_max*1.18,
                                           fontsize=6.5, color="#1e293b")
                    ax.set_xticks(range(len(top7_df)))
                    ax.set_xticklabels(top7_df.index, rotation=25, ha='right', fontsize=7)
                    ax.set_ylabel("Event Count", fontsize=7, color="black")
                    style_bar(ax)

                plot_compartment(
                    f"Top 7 Exchangers — Top 5 Events  —  {selected_month}{suffix}",
                    draw_filtered)
        else:
            plot_monthly_pump_top7(fdf, EVENTS, COLORS, eq_col, selected_month)

    with col2:
        if equip == "Exchanger":
            plot_donut(f"Top Events  —  {selected_month}{suffix}",
                       fdf[EVENTS].sum(), COLORS, top_n=10)
        else:
            plot_donut(f"Top Events  —  {selected_month}",
                       fdf[EVENTS].sum(), COLORS, filter_top5=True)


# ══════════════════════════════════════════════════
# EQUIPMENT ANALYSIS
# FIX 4: only 2 plots (history table + donut) — bottom 2 removed
# ══════════════════════════════════════════════════
elif page == "Equipment":

    if equip == "Exchanger":
        colA, colB, _ = st.columns([1.2, 1.2, 5])
        with colA:
            cw_eq_filter = st.selectbox("CW Filter", ["All","CW Only","Non-CW Only"],
                                        index=0, key=f"cw_eq_{equip}")
        eq_sub = df.copy()
        if cw_eq_filter == "CW Only":       eq_sub = df[df["is_cw"]]
        elif cw_eq_filter == "Non-CW Only": eq_sub = df[~df["is_cw"]]
        eq_list = (eq_sub.groupby(eq_col)[EVENTS_FULL].sum()
                   .sum(axis=1).sort_values(ascending=False).index.tolist())
        with colB:
            selected_eq = st.selectbox("Select Exchanger", eq_list, key=f"sel_{equip}")
    else:
        colA, _ = st.columns([1, 5])
        eq_list = (df.groupby(eq_col)[EVENTS_FULL].sum()
                   .sum(axis=1).sort_values(ascending=False).index.tolist())
        with colA:
            selected_eq = st.selectbox(f"Select {equip}", eq_list, key=f"sel_{equip}")

    eq_df = df[df[eq_col] == selected_eq]

    if equip == "Exchanger":
        is_cw_flag  = is_cw(selected_eq)
        cw_label    = "CW" if is_cw_flag else "Non-CW"
        donut_title = f"Top Events  —  {selected_eq}  [{cw_label}]"
    else:
        donut_title = f"Top Events  —  {selected_eq}"

    # FIX 4: only these 2 plots — no monthly trend, no all-events breakdown below
    col1, col2 = st.columns(2, gap="small")

    with col1:
        st.markdown('<div class="plot-box"><div class="plot-title">Equipment History</div>',
                    unsafe_allow_html=True)
        hist = eq_df[["date","shift",info_col]].sort_values("date").copy()
        hist.columns = ["Date","Shift","Event Info"]
        if hist.empty:
            st.markdown('<div class="no-data-msg">No data available</div>',
                        unsafe_allow_html=True)
        else:
            st.dataframe(hist, use_container_width=True, height=240)
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        plot_donut(donut_title, eq_df[EVENTS_FULL].sum(), COLORS_FULL, filter_top5=True)
