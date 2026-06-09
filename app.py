# =========================================================
# AIR TRAFFIC EXECUTIVE PLATFORM
# FINAL VERSION (SMOOTH AREA CHART - NO CLUTTER)
# STREAMLIT + PLOTLY
# =========================================================

# =========================================================
# LIBRARIES
# =========================================================

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="Air Traffic Executive Platform",
    page_icon="✈️",
    layout="wide"
)

# =========================================================
# CUSTOM CSS
# =========================================================

st.markdown("""
<style>

/* BACKGROUND */

.main {
    background-color: #F4F7FB;
}

/* SPACING */

.block-container {
    padding-top: 2rem;
    padding-bottom: 3rem;
    padding-left: 2.5rem;
    padding-right: 2.5rem;
}

/* SIDEBAR */

section[data-testid="stSidebar"] {
    background-color: #0B1220;
    border-right: 1px solid #1E293B;
}

section[data-testid="stSidebar"] * {
    color: #F8FAFC !important;
    font-weight: 600;
}

/* KPI CARDS */

div[data-testid="metric-container"] {
    background-color: white;
    border: 1px solid #CBD5E1;
    padding: 20px;
    border-radius: 18px;
    box-shadow: 0px 3px 12px rgba(0,0,0,0.06);
}

div[data-testid="metric-container"] label {
    color: #475569 !important;
    font-size: 15px !important;
    font-weight: 700 !important;
}

div[data-testid="metric-container"] div[data-testid="stMetricValue"] {
    color: #0F172A !important;
    font-size: 30px !important;
    font-weight: 800 !important;
}

/* HEADERS */

h1 {
    color: #0F172A;
    font-weight: 800;
}

h2 {
    color: #1E293B;
    font-weight: 700;
}

h3 {
    color: #334155;
    font-weight: 700;
}

/* TEXT */

p, span, div {
    color: #334155;
}

/* DATAFRAMES */

[data-testid="stDataFrame"] {
    border-radius: 14px;
    overflow: hidden;
    border: 1px solid #CBD5E1;
}

/* TABS */

button[data-baseweb="tab"] {
    font-size: 15px;
    font-weight: 700;
    color: #1E293B";
}

/* PLOTLY */

.js-plotly-plot .plotly text {
    fill: #111827 !important;
    font-weight: 700 !important;
}

</style>
""", unsafe_allow_html=True)

# =========================================================
# LOAD DATA
# =========================================================

# RUTA ACTUALIZADA
ruta = r"operaciones_2026.xlsx"

df = pd.read_excel(ruta)

# =========================================================
# DATA PREPARATION
# =========================================================

# --- CONVERSION DE HORARIO ZULU A COLOMBIA ---
# Lista original exacta de columnas (mezcla de mayusculas/minusculas del Excel)
zulu_columns_original = [
    '0000z','0100z','0200z','0300z','0400z','0500z',
    '0600z','0700z','0800z','0900z',
    '1000z','1100Z','1200Z','1300Z','1400Z',
    '1500Z','1600Z','1700Z','1800Z','1900Z',
    '2000Z','2100Z','2200Z','2300Z'
]

# Mapeo y renombramiento
mapping_dict = {}
columnas_horas = []

for i, col in enumerate(zulu_columns_original):
    # Calculo: Hora UTC (0-23) - 5 horas = Hora Colombia
    # Usamos modulo 24 para manejar el cambio de dia (ej: 00:00 UTC -> 19:00 Colombia)
    hora_colombia = (i - 5) % 24
    
    # Formato nuevo "HH:mm"
    nuevo_nombre = f"{hora_colombia:02d}:00"
    
    mapping_dict[col] = nuevo_nombre
    columnas_horas.append(nuevo_nombre)

# Aplicar el renombramiento al DataFrame
df.rename(columns=mapping_dict, inplace=True)
# ---------------------------------------------------

df["Fecha"] = pd.to_datetime(df["Fecha"])

df["TOTAL_OPERACIONES"] = df[columnas_horas].sum(axis=1)

# --- PREPARACION MESES ---
df['MES_NUM'] = df['Fecha'].dt.month

mapeo_meses = {
    1: 'Enero', 2: 'Febrero', 3: 'Marzo', 4: 'Abril',
    5: 'Mayo', 6: 'Junio', 7: 'Julio', 8: 'Agosto',
    9: 'Septiembre', 10: 'Octubre', 11: 'Noviembre', 12: 'Diciembre'
}

df['MES'] = df['MES_NUM'].map(mapeo_meses)

# --- PREPARACION DIAS ---
df["DIA_SEMANA"] = df["Fecha"].dt.day_name()

mapeo_dias = {
    'Monday': 'Lunes', 'Tuesday': 'Martes', 'Wednesday': 'Miércoles',
    'Thursday': 'Jueves', 'Friday': 'Viernes', 'Saturday': 'Sábado', 'Sunday': 'Domingo'
}

df['DIA_SEMANA'] = df['DIA_SEMANA'].map(mapeo_dias)

orden_dias_correcto = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
df['DIA_SEMANA'] = pd.Categorical(df['DIA_SEMANA'], categories=orden_dias_correcto, ordered=True)


# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:

    # -----------------------------------------------------
    # LOGO / HEADER
    # -----------------------------------------------------

    st.markdown("""
    ## ✈️ AIR OPS
    ### Executive Platform
    """)

    st.markdown("---")

    # -----------------------------------------------------
    # FILTERS
    # -----------------------------------------------------

    st.markdown("### 🎯 Filters")

    tipos = st.multiselect(
        "Operation Type",
        options=df["TIPO"].unique(),
        default=df["TIPO"].unique()
    )

    # -----------------------------------------------------
    # APPLY FILTER
    # -----------------------------------------------------

    df = df[df["TIPO"].isin(tipos)]

    # -----------------------------------------------------
    # SIDEBAR KPIs
    # -----------------------------------------------------

    total_sidebar = int(df["TOTAL_OPERACIONES"].sum())

    peak_sidebar = (
        df[columnas_horas]
        .sum()
        .idxmax()
    )

    st.markdown("---")

    st.markdown("### 📌 Quick Status")

    st.metric(
        "Total Operations",
        f"{total_sidebar:,}"
    )

    st.metric(
        "Peak Hour",
        peak_sidebar
    )

    st.metric(
        "Operation Types",
        len(tipos)
    )

    # -----------------------------------------------------
    # INFO BOX
    # -----------------------------------------------------

    st.markdown("---")

    st.info(
        """
        All operational hours were converted:

        UTC/Zulu → Colombia Local Time (UTC-5)
        """
    )

    # -----------------------------------------------------
    # FOOTER
    # -----------------------------------------------------

    st.markdown("---")

    st.caption(
        "Air Traffic Executive Platform v1.0"
    )

# =========================================================
# FILTER APPLICATION
# =========================================================


# =========================================================
# KPIS
# =========================================================

total_operaciones = int(df["TOTAL_OPERACIONES"].sum())

promedio_diario = int(df["TOTAL_OPERACIONES"].mean())

hora_pico = (
    df[columnas_horas]
    .sum()
    .idxmax()
)

tipo_dominante = (
    df.groupby("TIPO")["TOTAL_OPERACIONES"]
    .sum()
    .idxmax()
)

max_daily_ops = int(
    df.groupby("Fecha")["TOTAL_OPERACIONES"]
    .sum()
    .max()
)

# =========================================================
# HEADER
# =========================================================

st.title("✈️ AIR TRAFFIC EXECUTIVE PLATFORM")

st.markdown("""
### Executive Operational Intelligence Dashboard  
Professional air traffic operational analysis. (Time: Colombia Local)
""")

# =========================================================
# KPI SECTION
# =========================================================

k1, k2, k3, k4, k5 = st.columns(5)

k1.metric("TOTAL OPS", f"{total_operaciones:,}")

k2.metric("DAILY AVG", f"{promedio_diario:,}")

k3.metric("PEAK HOUR", hora_pico)

k4.metric("DOMINANT TYPE", tipo_dominante)

k5.metric("MAX DAILY OPS", f"{max_daily_ops:,}")

st.markdown("---")

# =========================================================
# TABS
# =========================================================

tabs = st.tabs([
    "📈 Executive Overview",
    "🔥 Traffic Intelligence",
    "📊 Peak Hours",
    "📅 Monthly Evolution",
    "📉 Traffic Distribution",
    "🛬 Operations by Type",
    "📆 Daily Behavior",
    "🕒 Hourly Dynamics",
    "📋 Operational Tables",
    "🧠 Executive Insights"
])

# =========================================================
# GLOBAL STYLES
# =========================================================

layout_style = dict(
    paper_bgcolor="white",
    plot_bgcolor="white",
    font=dict(
        color="#111827",
        size=13
    ),
    title_font=dict(
        color="#0F172A",
        size=20
    ),
    hoverlabel=dict(
        bgcolor="white",
        bordercolor="#CBD5E1",
        font_size=13,
        font_family="Arial",
        font_color="#0F172A"
    )
)

axis_style = dict(
    xaxis=dict(
        showgrid=False,
        tickfont=dict(color="#111827", size=12),
        title_font=dict(color="#111827", size=15)
    ),
    yaxis=dict(
        gridcolor="rgba(148,163,184,0.20)",
        tickfont=dict(color="#111827", size=12),
        title_font=dict(color="#111827", size=15)
    )
)

color_versus = {
    "Aterrizaje": "#2563EB", # Azul
    "Despegue": "#EA580C"   # Naranja
}

# =========================================================
# TAB 1
# =========================================================

with tabs[0]:

    st.subheader("Operational Trend")

    # =====================================================
    # DAILY TREND
    # =====================================================

    serie = (
        df.groupby("Fecha")["TOTAL_OPERACIONES"]
        .sum()
        .reset_index()
    )

    fig1 = go.Figure()

    fig1.add_trace(
        go.Scatter(
            x=serie["Fecha"],
            y=serie["TOTAL_OPERACIONES"],
            mode="lines",
            fill="tozeroy",
            line=dict(
                color="#2563EB",
                width=4
            ),
            fillcolor="rgba(37,99,235,0.18)",
            hovertemplate=
            "<b>Date:</b> %{x}<br>" +
            "<b>Operations:</b> %{y:,}<extra></extra>"
        )
    )

    fig1.update_layout(
        title="Daily Operational Trend",
        height=520,
        margin=dict(l=20, r=20, t=60, b=80),

        paper_bgcolor="white",
        plot_bgcolor="white",

        font=dict(
            color="#111827",
            size=13
        ),

        title_font=dict(
            color="#0F172A",
            size=22
        ),

        hoverlabel=dict(
            bgcolor="white",
            bordercolor="#CBD5E1",
            font=dict(
                color="#111827",
                size=13
            )
        ),

        xaxis=dict(
            showgrid=False,
            tickfont=dict(
                color="#111827",
                size=12
            )
        ),

        yaxis=dict(
            gridcolor="rgba(148,163,184,0.20)",
            tickfont=dict(
                color="#111827",
                size=12
            )
        )
    )

    fig1.update_xaxes(tickangle=-25)

    st.plotly_chart(
        fig1,
        use_container_width=True
    )

    st.markdown("")

    # =====================================================
    # MONTHLY PIE + TABLE
    # =====================================================

    st.subheader("Monthly Operations Distribution")

    mensual_total = (
        df.groupby(["MES_NUM", "MES"])["TOTAL_OPERACIONES"]
        .sum()
        .reset_index()
        .sort_values("MES_NUM")
    )

    mensual_total["PERCENTAGE"] = (
        mensual_total["TOTAL_OPERACIONES"]
        / mensual_total["TOTAL_OPERACIONES"].sum()
    ) * 100

    c1, c2 = st.columns([1.6, 1])

    # =====================================================
    # PIE CHART
    # =====================================================

    with c1:

        fig_pie = go.Figure(
            data=[
                go.Pie(
                    labels=mensual_total["MES"],
                    values=mensual_total["TOTAL_OPERACIONES"],
                    hole=0.45,

                    textinfo="percent+label",

                    textfont=dict(
                        size=13,
                        color="#111827"
                    ),

                    marker=dict(
                        colors=[
                            "#2563EB",
                            "#3B82F6",
                            "#60A5FA",
                            "#93C5FD",
                            "#BFDBFE",
                            "#1D4ED8",
                            "#1E40AF",
                            "#1E3A8A",
                            "#EA580C",
                            "#F97316",
                            "#FB923C",
                            "#FDBA74"
                        ],
                        line=dict(
                            color="white",
                            width=2
                        )
                    ),

                    hovertemplate=
                    "<b>%{label}</b><br>" +
                    "Operations: %{value:,}<br>" +
                    "Percentage: %{percent}<extra></extra>"
                )
            ]
        )

        fig_pie.update_layout(
            title="Operations Share by Month",

            height=500,

            paper_bgcolor="white",
            plot_bgcolor="white",

            font=dict(
                color="#111827",
                size=13
            ),

            title_font=dict(
                color="#0F172A",
                size=20
            ),

            hoverlabel=dict(
                bgcolor="white",
                bordercolor="#CBD5E1",
                font=dict(
                    color="#111827",
                    size=13
                )
            ),

            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=-0.18,
                xanchor="center",
                x=0.5
            ),

            margin=dict(
                t=60,
                b=80,
                l=20,
                r=20
            )
        )

        st.plotly_chart(
            fig_pie,
            use_container_width=True
        )

    # =====================================================
    # SUPPORT TABLE
    # =====================================================

    with c2:

        tabla_mensual = mensual_total[
            ["MES", "TOTAL_OPERACIONES", "PERCENTAGE"]
        ].copy()

        tabla_mensual.columns = [
            "Month",
            "Operations",
            "Share %"
        ]

        tabla_mensual["Operations"] = (
            tabla_mensual["Operations"]
            .map(lambda x: f"{x:,}")
        )

        tabla_mensual["Share %"] = (
            tabla_mensual["Share %"]
            .map(lambda x: f"{x:.2f}%")
        )

        st.markdown("### Monthly Support Table")

        st.dataframe(
            tabla_mensual,
            use_container_width=True,
            height=500
        )
# =========================================================
# TAB 2
# =========================================================
# TAB 2
# =========================================================

with tabs[1]:

    st.subheader("Operational Intelligence")

    # =====================================================
    # DATA PREPARATION
    # =====================================================

    # Normalizar tipos
    df_aterrizaje = df[df["TIPO"].str.upper() == "ATERRIZAJE"]
    df_despegue = df[df["TIPO"].str.upper() == "DESPEGUE"]

    # Heatmap aterrizajes
    heatmap_aterrizaje = (
        df_aterrizaje
        .groupby("DIA_SEMANA", observed=True)[columnas_horas]
        .mean()
        .reindex(orden_dias_correcto)
    )

    # Heatmap despegues
    heatmap_despegue = (
        df_despegue
        .groupby("DIA_SEMANA", observed=True)[columnas_horas]
        .mean()
        .reindex(orden_dias_correcto)
    )

    # =====================================================
    # HEATMAP 1 - LANDINGS
    # =====================================================

    st.markdown("#### 1. Density: Landings (Aterrizajes)")

    fig3_aterrizaje = go.Figure(
        data=go.Heatmap(
            z=heatmap_aterrizaje.values,
            x=heatmap_aterrizaje.columns,
            y=heatmap_aterrizaje.index,
            colorscale=[
                [0, "#DBEAFE"],
                [0.5, "#2563EB"],
                [1, "#1E3A8A"]
            ],
            text=np.round(heatmap_aterrizaje.values, 1),
            texttemplate="%{text}",
            textfont=dict(
                size=11,
                color="#111827"
            ),
            colorbar=dict(
                title="Avg Ops",
                thickness=20
            ),
            hovertemplate=
            "<b>Day:</b> %{y}<br>" +
            "<b>Hour:</b> %{x}<br>" +
            "<b>Average Ops:</b> %{z:.1f}<extra></extra>"
        )
    )

    fig3_aterrizaje.update_layout(
        title="Landing Density Heatmap",
        height=700,
        margin=dict(
            l=20,
            r=20,
            t=60,
            b=20
        ),
        **layout_style
    )

    st.plotly_chart(
        fig3_aterrizaje,
        use_container_width=True
    )

    st.dataframe(
        heatmap_aterrizaje,
        use_container_width=True
    )

    st.markdown("---")

    # =====================================================
    # HEATMAP 2 - TAKEOFFS
    # =====================================================

    st.markdown("#### 2. Density: Takeoffs (Despegues)")

    fig3_despegue = go.Figure(
        data=go.Heatmap(
            z=heatmap_despegue.values,
            x=heatmap_despegue.columns,
            y=heatmap_despegue.index,
            colorscale=[
                [0, "#FFF7ED"],
                [0.5, "#EA580C"],
                [1, "#9A3412"]
            ],
            text=np.round(heatmap_despegue.values, 1),
            texttemplate="%{text}",
            textfont=dict(
                size=11,
                color="#111827"
            ),
            colorbar=dict(
                title="Avg Ops",
                thickness=20
            ),
            hovertemplate=
            "<b>Day:</b> %{y}<br>" +
            "<b>Hour:</b> %{x}<br>" +
            "<b>Average Ops:</b> %{z:.1f}<extra></extra>"
        )
    )

    fig3_despegue.update_layout(
        title="Takeoff Density Heatmap",
        height=700,
        margin=dict(
            l=20,
            r=20,
            t=60,
            b=20
        ),
        **layout_style
    )

    st.plotly_chart(
        fig3_despegue,
        use_container_width=True
    )

    st.dataframe(
        heatmap_despegue,
        use_container_width=True
    )

# =========================================================
# TAB 3
# =========================================================

with tabs[2]:

    st.subheader("Top Operational Hours")

    horas = (
        df[columnas_horas]
        .sum()
        .sort_values(ascending=False)
        .reset_index()
    )

    horas.columns = [
        "Hour (Local)",
        "Operations"
    ]

    c3, c4 = st.columns([2,1])

    with c3:

        fig4 = px.bar(
            horas.head(10),
            x="Hour (Local)",
            y="Operations",
            text="Operations",
            color="Operations",
            color_continuous_scale=[
                "#BFDBFE",
                "#60A5FA",
                "#1D4ED8"
            ]
        )

        fig4.update_traces(
            textposition="outside",
            textfont=dict(
                color="#111827",
                size=12
            )
        )

        fig4.update_layout(
            title="Top 10 Operational Hours",
            height=520,
            coloraxis_showscale=False,
            **layout_style,
            **axis_style
        )

        st.plotly_chart(
            fig4,
            use_container_width=True
        )

    with c4:

        st.dataframe(
            horas.head(10),
            use_container_width=True,
            height=520
        )

# =========================================================
# TAB 4
# =========================================================

with tabs[3]:

    st.subheader("Monthly Evolution")

    mensual_tipo = (
        df.groupby(["MES_NUM", "MES", "TIPO"])["TOTAL_OPERACIONES"]
        .sum()
        .reset_index()
        .sort_values("MES_NUM")
    )

    # --- ESTRATEGIA VISUAL: BASELINE EN CERO ---
    max_val = mensual_tipo['TOTAL_OPERACIONES'].max()
    y_axis_range = [0, max_val * 1.15]

    fig5 = go.Figure()

    # Linea 1: Aterrizajes
    df_aterrizajes = mensual_tipo[mensual_tipo['TIPO'] == 'Aterrizaje']
    fig5.add_trace(
        go.Scatter(
            x=df_aterrizajes['MES'],
            y=df_aterrizajes['TOTAL_OPERACIONES'],
            mode='lines+markers',
            name='Aterrizajes',
            line=dict(color='#2563EB', width=4),
            marker=dict(size=10, color='#2563EB')
        )
    )

    # Linea 2: Despegues
    df_despegues = mensual_tipo[mensual_tipo['TIPO'] == 'Despegue']
    fig5.add_trace(
        go.Scatter(
            x=df_despegues['MES'],
            y=df_despegues['TOTAL_OPERACIONES'],
            mode='lines+markers',
            name='Despegues',
            line=dict(color='#EA580C', width=4), 
            marker=dict(size=10, color='#EA580C')
        )
    )

    fig5.update_layout(
        title="Monthly Operational Trend (Landings vs Takeoffs)",
        height=520,
        hovermode="x unified",
        xaxis=dict(
            title="",
            tickfont=dict(size=14, color="#111827"),
            showgrid=False
        ),
        yaxis=dict(
            title="Total Operations",
            title_font=dict(size=14, color="#111827"),
            gridcolor="rgba(148,163,184,0.20)",
            tickfont=dict(color="#111827", size=12),
            range=y_axis_range
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        **layout_style
    )

    st.plotly_chart(
        fig5,
        use_container_width=True
    )

    # =====================================================
    # ANÁLISIS ESTADÍSTICO (SIN HTML - 100% NATIVO SEGURO)
    # =====================================================

    st.markdown("---")
    st.subheader("📊 Análisis de Variabilidad Mensual")

    # 1. Separar datos
    df_at = mensual_tipo[mensual_tipo['TIPO'] == 'Aterrizaje'].sort_values('MES_NUM').reset_index(drop=True)
    df_de = mensual_tipo[mensual_tipo['TIPO'] == 'Despegue'].sort_values('MES_NUM').reset_index(drop=True)

    # 2. Resumen Picos y Valles (Usando st.metric nativo)
    col_pico_at, col_pico_de = st.columns(2, gap="large")
    
    with col_pico_at:
        st.metric(label="Aterrizajes", value=f"Pico: {df_at['TOTAL_OPERACIONES'].max():,} ops", delta=f"Valle: {df_at['TOTAL_OPERACIONES'].min():,}")

    with col_pico_de:
        st.metric(label="Despegues", value=f"Pico: {df_de['TOTAL_OPERACIONES'].max():,} ops", delta=f"Valle: {df_de['TOTAL_OPERACIONES'].min():,}")

    st.markdown("#### 📉 Desglose Mes a Mes:")

    # 3. Bucle para mostrar variaciones (Usando st.success y st.error)
    for i in range(1, len(df_at)):
        mes_actual = df_at.iloc[i]['MES']
        
        # Obtener valores actuales y anteriores
        ops_at_act = df_at.iloc[i]['TOTAL_OPERACIONES']
        ops_de_act = df_de.iloc[i]['TOTAL_OPERACIONES']
        ops_at_ant = df_at.iloc[i-1]['TOTAL_OPERACIONES']
        ops_de_ant = df_de.iloc[i-1]['TOTAL_OPERACIONES']

        # Calcular variación porcentual
        var_at = ((ops_at_act - ops_at_ant) / ops_at_ant) * 100
        var_de = ((ops_de_act - ops_de_ant) / ops_de_ant) * 100

        # Crear dos columnas para Aterrizaje y Despegue
        c1, c2 = st.columns(2, gap="medium")
        
        with c1:
            if var_at > 0:
                st.success(f"**{mes_actual} - Aterrizajes:** Creció +{var_at:.1f}% vs mes anterior")
            else:
                st.error(f"**{mes_actual} - Aterrizajes:** Cayó {var_at:.1f}% vs mes anterior")
        
        with c2:
            if var_de > 0:
                st.success(f"**{mes_actual} - Despegues:** Creció +{var_de:.1f}% vs mes anterior")
            else:
                st.error(f"**{mes_actual} - Despegues:** Cayó {var_de:.1f}% vs mes anterior")

    st.markdown("---")

    # Tabla de soporte
    st.dataframe(
        mensual_tipo.pivot(index='MES', columns='TIPO', values='TOTAL_OPERACIONES'),
        use_container_width=True
    )

# =========================================================
# TAB 5 (MEJORA: CURVAS SUAVES - SIN RUIDO)
# =========================================================

with tabs[4]:

    st.subheader("Traffic Volume Shape")

    # Preparar datos: Contar frecuencia de cada valor exacto
    freq_df = df.groupby(['TOTAL_OPERACIONES', 'TIPO']).size().reset_index(name='count')

    fig6 = px.area(
        freq_df,
        x="TOTAL_OPERACIONES",
        y="count",
        color="TIPO",
        line_shape="spline", 
        color_discrete_map=color_versus
    )

    # Configurar la transparencia para que se vea la superposicion
    fig6.update_traces(
        fill='tozeroy',
        opacity=0.6,
        line=dict(width=3)
    )

    fig6.update_layout(
        title="Most Common Daily Volumes",
        height=520,
        xaxis_title="Total Daily Operations",
        yaxis_title="Frequency (Days)",
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        # Simplificar el eje X para no ver cada numero individualmente si son muchos
        xaxis=dict(
            tickmode='auto',
            nticks=10,
            title_font=dict(size=14)
        ),
        **layout_style
    )

    st.plotly_chart(
        fig6,
        use_container_width=True
    )

    st.info("""
    💡 **Interpretación Simple:**
    Observa las "montañas". Donde la montaña es más alta (pico), es el volumen de operaciones más **común** (normal). 
    Donde la montaña es baja, son volúmenes raros (pocos días). 
    Si las montañas Azul y Naranja están alineadas, significa que Aterrizajes y Despegues suelen tener el mismo volumen diario.
    """)

# =========================================================
# TAB 6
# =========================================================

with tabs[5]:

    st.subheader("Operations by Type")

    operaciones_tipo = (
        df.groupby("TIPO")["TOTAL_OPERACIONES"]
        .sum()
        .reset_index()
    )

    fig7 = px.bar(
        operaciones_tipo,
        x="TIPO",
        y="TOTAL_OPERACIONES",
        text="TOTAL_OPERACIONES",
        color="TIPO",
        color_discrete_map=color_versus
    )

    fig7.update_traces(
        textfont=dict(
            color="#111827",
            size=12
        )
    )

    fig7.update_layout(
        title="Operations by Type",
        height=520,
        showlegend=False,
        **layout_style,
        **axis_style
    )

    st.plotly_chart(
        fig7,
        use_container_width=True
    )

    st.dataframe(
        operaciones_tipo,
        use_container_width=True
    )

# =========================================================
# TAB 7
# =========================================================

with tabs[6]:

    st.subheader("Daily Operational Behavior")

    diario = (
        df.groupby("DIA_SEMANA", observed=True)["TOTAL_OPERACIONES"]
        .mean()
        .reset_index()
    )
    
    diario = diario.set_index("DIA_SEMANA").reindex(orden_dias_correcto).reset_index()

    fig8 = px.bar(
        diario,
        x="DIA_SEMANA",
        y="TOTAL_OPERACIONES",
        text="TOTAL_OPERACIONES",
        color="TOTAL_OPERACIONES",
        color_continuous_scale=[
            "#DBEAFE",
            "#60A5FA",
            "#1D4ED8"
        ]
    )

    fig8.update_traces(
        textfont=dict(
            color="#111827",
            size=12
        )
    )

    fig8.update_layout(
        title="Average Operations by Day",
        height=520,
        coloraxis_showscale=False,
        **layout_style,
        **axis_style
    )

    st.plotly_chart(
        fig8,
        use_container_width=True
    )

    st.dataframe(
        diario,
        use_container_width=True
    )

# =========================================================
# TAB 8
# =========================================================

with tabs[7]:

    st.subheader("Hourly Dynamics (Landings vs Takeoffs)")

    id_vars = ["Fecha", "TIPO", "TOTAL_OPERACIONES"] 
    df_melt = df.melt(id_vars=id_vars, value_vars=columnas_horas, var_name="HORA", value_name="VOLUMEN")

    hourly_data = df_melt.groupby(["HORA", "TIPO"])["VOLUMEN"].sum().reset_index()

    fig9 = px.line(
        hourly_data,
        x="HORA",
        y="VOLUMEN",
        color="TIPO",
        markers=True,
        color_discrete_map=color_versus
    )

    fig9.update_traces(
        line=dict(width=4),
        marker=dict(size=8)
    )

    fig9.update_layout(
        title="Hourly Volume Breakdown by Type",
        height=520,
        xaxis=dict(
            title="Hour (Local)",
            tickfont=dict(size=11),
            showgrid=False
        ),
        yaxis=dict(
            title="Total Operations",
            gridcolor="rgba(148,163,184,0.20)",
            tickfont=dict(color="#111827", size=12)
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        **layout_style
    )

    st.plotly_chart(
        fig9,
        use_container_width=True
    )

    st.dataframe(
        hourly_data.pivot(index='HORA', columns='TIPO', values='VOLUMEN'),
        use_container_width=True
    )

# =========================================================
# TAB 9
# =========================================================

with tabs[8]:

    st.subheader("Operational Tables")

    c5, c6 = st.columns(2)

    with c5:

        st.write("### Top Traffic Days")

        top_dias = (
            df.groupby("Fecha")["TOTAL_OPERACIONES"]
            .sum()
            .sort_values(ascending=False)
            .head(10)
        )

        st.dataframe(
            top_dias,
            use_container_width=True
        )

    with c6:

        st.write("### Top Operational Hours")

        st.dataframe(
            horas.head(10),
            use_container_width=True
        )

# =========================================================
# TAB 10
# =========================================================

with tabs[9]:

    st.subheader("Insights")

    st.markdown("""
# Hallazgos

### 1. Estabilidad Operacional Durante el Período Evaluado

El análisis de la tendencia operacional evidencia un comportamiento relativamente estable del tráfico aéreo durante el período evaluado. Las variaciones diarias se mantienen dentro de rangos operacionales esperados, lo que sugiere consistencia en la actividad aeroportuaria y en la gestión del flujo de tráfico.

---

### 2. Identificación de Horas Pico Críticas

El análisis horario permitió identificar franjas específicas con alta concentración operacional. Estas ventanas representan períodos críticos para la coordinación de pista, gestión de tráfico aéreo y asignación eficiente de recursos operacionales.

---

### 3. Balance Entre Aterrizajes y Despegues

Los datos muestran una distribución equilibrada entre operaciones de aterrizaje y despegue, lo que refleja estabilidad en la dinámica operacional del aeropuerto y un uso eficiente de la capacidad disponible.

---

### 4. Comportamiento Estacional del Tráfico

La distribución mensual de operaciones evidencia patrones de estacionalidad operacional. Algunos meses concentran un mayor porcentaje del tráfico total, indicando períodos de incremento en la demanda aeroportuaria.

---

### 5. Concentración Operacional en Ventanas Específicas

El análisis de densidad operacional permite observar patrones recurrentes de concentración en determinados días y horarios. Este comportamiento podría representar puntos de presión operacional y posibles cuellos de botella en escenarios de alta demanda.

---

### 6. Consistencia en los Volúmenes Operacionales Diarios

La distribución de tráfico muestra que la mayoría de los días operacionales se mantienen dentro de rangos de volumen recurrentes. Esta estabilidad permite identificar patrones previsibles útiles para procesos de planificación y proyección operacional.
    """)

st.markdown("---")

st.caption(
    "Air Traffic Executive Platform • Streamlit + Plotly"
)