import streamlit as st
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import seaborn as sns
import folium
from streamlit_folium import st_folium
import mapclassify
import branca.colormap as bcm

st.set_page_config(
    page_title="Salud Mental y Espacio Verde - Bogotá",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Global style configuration ---
FONT_SIZE_TITLE = "30px"
FONT_SIZE_TAB = "16px"
FONT_SIZE_SUBHEADER = "26px"
FONT_SIZE_CAPTION = "16px"
FONT_SIZE_METRIC_LABEL = "15px"

st.markdown(f"""
    <style>
        .stCaption, [data-testid="stCaptionContainer"] p {{
            font-size: {FONT_SIZE_CAPTION} !important;
        }}
        h1 {{ 
            font-size: {FONT_SIZE_TITLE} !important; 
            text-align: center !important;
        }}
        h3 {{ font-size: {FONT_SIZE_SUBHEADER} !important; }}
        [data-testid="stMetricLabel"] {{
            font-size: {FONT_SIZE_METRIC_LABEL} !important;
            justify-content: center;
        }}
        [data-testid="stMetricDelta"] {{
            display: flex;
            justify-content: center;
        }}
        button[data-baseweb="tab"] p {{
            font-size: {FONT_SIZE_TAB} !important;
        }}
        [data-testid="stMetric"] {{
            text-align: center;
            display: flex;
            flex-direction: column;
            align-items: center;
        }}
    </style>
""", unsafe_allow_html=True)

# data loading (cached)
@st.cache_data
def load_data():
    master_gdf = gpd.read_file("data/processed/master_mental_health_bogota_2025.geojson")
    suicide_summary_df = pd.read_csv("data/processed/suicide_summary.csv")
    perception_a4_df = pd.read_csv("data/processed/perception_a4.csv")
    ame_df = pd.read_csv("data/processed/ame_summary.csv")
    model_fit_stats_df = pd.read_csv("data/processed/model_fit_stats.csv")
    model_coefficients_df = pd.read_csv("data/processed/model_coefficients.csv")
    with open("data/processed/logit_summary.txt") as f:
        logit_summary_text = f.read()
    return (master_gdf, suicide_summary_df, perception_a4_df, ame_df,
            model_fit_stats_df, model_coefficients_df, logit_summary_text)

(master_gdf, suicide_summary_df, perception_a4_df, ame_df,
 model_fit_stats_df, model_coefficients_df, logit_summary_text) = load_data()

# sidebar
with st.sidebar:
    st.header("Sobre este análisis")
    st.write("**Equipo:** GEMMA 2.0")
    st.write("**Evento:** DataJam Edición 3 — 2026")
    st.write("**Fuentes:** Datos Abiertos Bogotá, Encuesta Distrital de Percepción, IDECA")
    st.markdown("[Repositorio en GitHub](https://github.com/ILuuI/datajam-2026-mental-health-bogota)")
    st.markdown("---")
    st.caption(
        "Este dashboard resume los hallazgos principales del análisis. "
        "El proceso completo de limpieza, integración de datos y modelado "
        "está documentado en los notebooks del repositorio."
    )

# header
st.markdown(
    "<h1 style='text-align: center;'>Relación entre Infraestructura Verde y "
    "Salud Mental en Bogotá (2023-2025)</h1>",
    unsafe_allow_html=True
)
st.markdown("**DataJam Edición 3 — 2026** | Equipo: GEMMA 2.0")

# quick KPIs
col1, col2, col3 = st.columns(3)
col1.metric("Localidades analizadas", "20")
col2.metric(
    "Suicidios registrados (2023-2025)",
    f"{int(suicide_summary_df['total_suicides_2023_2025'].sum())}"
)
col3.metric("Fuentes de datos integradas", "4+")

st.markdown("---")

# tabs
tab1, tab2, tab3, tab4 = st.tabs([
    "Mapa: Infraestructura Verde",
    "Brecha de Género",
    "Verde vs. Suicidios",
    "Modelo: Determinantes de Salud"
])

with tab1:
    st.subheader("Distribución de Área Verde por Localidad")

    quantile_bins = mapclassify.Quantiles(master_gdf["total_green_area_sqm"], k=5).bins
    bins = [master_gdf["total_green_area_sqm"].min()] + list(quantile_bins)

    green_colors = ["#c7e9c0", "#a1d99b", "#74c476", "#31a354", "#006d2c"]
    colormap = bcm.StepColormap(
        colors=green_colors,
        index=bins,
        vmin=bins[0],
        vmax=bins[-1],
    )

    def style_function(feature):
        value = feature["properties"]["total_green_area_sqm"]
        return {
            "fillColor": colormap(value),
            "fillOpacity": 0.85,
            "color": "#333333",
            "weight": 0.8,
        }

    m = folium.Map(location=[4.65, -74.1], zoom_start=10, tiles="OpenStreetMap")

    folium.GeoJson(
        master_gdf,
        style_function=style_function,
        tooltip=folium.GeoJsonTooltip(
            fields=["locality_clean", "total_green_area_sqm"],
            aliases=["Localidad:", "Área verde (m²):"],
            localize=True,
        ),
    ).add_to(m)

    map_col, legend_col = st.columns([3, 1])
    with map_col:
        st_folium(m, width=700, height=500, returned_objects=[])
    with legend_col:
        st.markdown("**Área verde total (m²)**")
        for i in range(len(green_colors)):
            lower = f"{bins[i]:.0f}"
            upper = f"{bins[i + 1]:.0f}"
            st.markdown(
                f'<div style="display:flex;align-items:center;margin-bottom:4px;">'
                f'<div style="width:16px;height:16px;background-color:{green_colors[i]};'
                f'border:1px solid #333;margin-right:8px;"></div>'
                f'<span style="font-size:13px;">{lower} – {upper}</span>'
                f"</div>",
                unsafe_allow_html=True,
            )

    top_locality_row = master_gdf.loc[master_gdf["total_green_area_sqm"].idxmax()]
    bottom_locality_row = master_gdf.loc[master_gdf["total_green_area_sqm"].idxmin()]
    total_parks = int(master_gdf["parks_count"].sum()) if "parks_count" in master_gdf.columns else None

    m1, m2, m3 = st.columns(3)
    m1.metric("Mayor área verde", top_locality_row["locality_clean"].title(),
        f"{top_locality_row['total_green_area_sqm']:.0f} m²",
        delta_color="off")
    m2.metric("Menor área verde", bottom_locality_row["locality_clean"].title(),
        f"{bottom_locality_row['total_green_area_sqm']:.0f} m²",
        delta_color="off")
    if total_parks is not None:
        m3.metric("Parques catalogados (total ciudad)", f"{total_parks}")

    st.caption(
        "Área verde total (m²) por localidad, clasificada en quintiles para "
        "resaltar diferencias relativas entre localidades."
    )

    st.caption(
        "Fuente: Sistema Distrital de Parques (IDECA/DADEP)."
    )

    with st.expander("Nota sobre calidad de datos"):
        st.markdown(
            "Durante el preprocesamiento se detectaron y corrigieron discrepancias "
            "de nomenclatura entre fuentes (p. ej. 'MARTIRES' vs. 'LOS MARTIRES', "
            "'SANTAFE' vs. 'SANTA FE', 'RAFAEL URIBE' vs. 'RAFAEL URIBE URIBE', y "
            "'CANDELARIA' vs. 'LA CANDELARIA'). Sin esta armonización, estas "
            "localidades habrían quedado con área verde en cero por error de cruce, "
            "no por ausencia real de datos."
        )


with tab2:
    st.subheader("Brecha de género en eventos de suicidio por localidad")

    sorted_suicide_df = suicide_summary_df.sort_values(
        by="total_suicides_2023_2025", ascending=False
    ).reset_index(drop=True)

    fig, ax = plt.subplots(figsize=(14, 7))
    sorted_suicide_df.plot(
        x="LOCALIDAD_DEL_HECHO", y=["hombre", "mujer"], kind="bar",
        color=["#2b8cbe", "#f03b20"], ax=ax, width=0.8
    )
    ax.set_title(
        "Brecha de Género en Eventos de Suicidio por Localidad\nBogotá D.C. (2023-2025)",
        fontsize=14, fontweight="bold", pad=15
    )
    ax.set_xlabel("Localidad del Hecho", fontsize=11, fontweight="bold")
    ax.set_ylabel("Cantidad de Eventos", fontsize=11, fontweight="bold")
    ax.legend(title="Sexo de la Víctima", fontsize=11, title_fontsize=12)
    plt.xticks(rotation=45, ha="right")
    ax.grid(axis="y", linestyle="--", alpha=0.5)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    plt.tight_layout()
    st.pyplot(fig, use_container_width=True)
    plt.close(fig)

    total_male = int(suicide_summary_df["hombre"].sum())
    total_female = int(suicide_summary_df["mujer"].sum())
    total_events = total_male + total_female
    male_pct = total_male / total_events * 100
    top_locality_row_g = sorted_suicide_df.iloc[0]

    m1, m2, m3 = st.columns(3)
    m1.metric("Total de eventos (2023-2025)", f"{total_events}")
    m2.metric("Proporción en hombres", f"{male_pct:.1f}%")
    m3.metric("Localidad con más eventos", top_locality_row_g["LOCALIDAD_DEL_HECHO"].title(),
               f"{int(top_locality_row_g['total_suicides_2023_2025'])} casos")

    st.caption(
        f"En el periodo 2023-2025 se registraron {total_events} eventos de "
        f"conducta suicida en Bogotá, de los cuales el {male_pct:.1f}% "
        "corresponden a hombres — consistente con patrones epidemiológicos "
        "nacionales, donde los hombres presentan mayor letalidad en intentos "
        "y consumación, mientras las mujeres presentan mayor prevalencia de "
        "ideación e intento (no consumado)."
    )
    st.caption(
        "Fuente: Base de datos de Conducta Suicida - Observatorio de Salud "
        "de Bogotá (OSB)."
    )


with tab3:
    st.subheader("Relación entre infraestructura verde y suicidios")

    merged_df = master_gdf.merge(
        suicide_summary_df,
        left_on="locality_clean", right_on="LOCALIDAD_DEL_HECHO",
        how="inner"
    )
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.regplot(
        data=merged_df, x="total_green_area_sqm", y="total_suicides_2023_2025",
        scatter_kws={"s": 70, "color": "#1f77b4", "alpha": 0.8},
        line_kws={"color": "#d62728", "linewidth": 2}, ax=ax,
    )
    for i in range(len(merged_df)):
        ax.annotate(
            merged_df["locality_clean"].iloc[i],
            (merged_df["total_green_area_sqm"].iloc[i], merged_df["total_suicides_2023_2025"].iloc[i]),
            xytext=(5, 5), textcoords="offset points", fontsize=8, alpha=0.8,
        )
    ax.set_title("Relación entre Infraestructura Verde y Eventos Epidemiológicos (2023-2025)", fontweight="bold")
    ax.set_xlabel("Área Verde Total en Metros Cuadrados (m²)")
    ax.set_ylabel("Total de Suicidios Registrados (2023-2025)")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    plt.tight_layout()
    st.pyplot(fig, use_container_width=True)
    plt.close(fig)

    correlation_coef = merged_df["total_green_area_sqm"].corr(merged_df["total_suicides_2023_2025"])

    m1, m2 = st.columns(2)
    m1.metric("Localidades incluidas", f"{len(merged_df)}")
    m2.metric("Correlación de Pearson (r)", f"{correlation_coef:.3f}")

    st.caption(
        f"Se observa una correlación positiva (r = {correlation_coef:.3f}) entre área "
        "verde total y número de suicidios registrados a nivel de localidad. "
        "**Esta relación es contraintuitiva respecto a la literatura**, que "
        "generalmente asocia más espacio verde con mejor salud mental — sin "
        "embargo, aquí probablemente refleja un efecto de confusión por "
        "**tamaño poblacional**: las localidades más grandes y pobladas "
        "(Kennedy, Suba, Engativá) tienden a tener más área verde total *y* "
        "más eventos en términos absolutos, simplemente por tener más "
        "habitantes. Un análisis más riguroso requeriría normalizar ambas "
        "variables por población (tasas per cápita) en vez de valores absolutos."
    )
    with st.expander("Limitaciones de esta correlación"):
        st.markdown("""
        - **Falacia ecológica:** la correlación es a nivel agregado (n=20 localidades), 
          no a nivel individual. No implica que las personas con más acceso a áreas 
          verdes tengan más riesgo.
        - **Variable de confusión no controlada:** población total por localidad, 
          que probablemente explica gran parte de esta relación espuria.
        - **No es causal:** correlación no implica causalidad en ninguna dirección.
        """)


with tab4:
    st.subheader("Efecto del número de menores a cargo en la salud percibida")
    st.caption(
        "Variable A4 de la Encuesta Distrital de Percepción 2025: "
        "*'¿Cuántas personas de su hogar tienen menos de 18 años?'*"
    )
    group_sizes = perception_a4_df.groupby("A4_agrupada")["poor_health"].count()
    category_order = ["0", "1", "2", "3", "4", "5+"]

    fig, ax = plt.subplots(figsize=(9, 5))
    sns.barplot(
        data=perception_a4_df, x="A4_agrupada", y="poor_health", order=category_order,
        estimator=lambda x: sum(x) / len(x) * 100,
        errorbar=("ci", 95), palette="mako", capsize=0.1,
        err_kws={"linewidth": 1.5, "color": "#333333"}, ax=ax,
    )
    for i, category in enumerate(category_order):
        n = group_sizes.get(category, 0)
        ax.text(i, 3, f"n={n}", ha="center", va="bottom", fontsize=8, color="white", fontweight="bold")
    ax.set_title("Efecto del Trabajo de Cuidado en la Salud Percibida", fontsize=14, fontweight="bold")
    ax.set_xlabel("Cantidad de Menores a Cargo (Variable A4)")
    ax.set_ylabel("Proporción con Salud Deficiente (%)")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    plt.tight_layout()
    st.pyplot(fig, use_container_width=True)
    plt.close(fig)
    st.caption(
        "Las categorías de 5, 6 y 7 menores a cargo fueron agrupadas en '5+' "
        "debido al bajo tamaño muestral (n=10, n=2, n=1 respectivamente). "
        "El número de observaciones (n) se anota sobre cada barra."
    )

    st.markdown("#### Resultados del modelo: determinantes de la salud percibida")
    st.caption(
        "Modelo de regresión logística binaria sobre la variable "
        "**IND_SALUD_101** (indicador de percepción del estado de salud), "
        "estimado con la Encuesta Distrital de Percepción 2025."
    )

    with st.expander("Diccionario de variables del modelo"):
        st.markdown("""
        | Variable | Pregunta original de la encuesta |
        |---|---|
        | **A3** | ¿Cuántas personas conforman su hogar? |
        | **A4** | ¿Cuántas personas de su hogar tienen menos de 18 años? |
        | **A6x2** | Parentesco con el jefe del hogar |
        | **poor_health** (var. dependiente) | Derivada de IND_SALUD_101: indicador de percepción del estado de salud |
        
        *Fuente: Diccionario de Datos — Encuesta Distrital de Percepción 2025.*
        """)

    fit_col1, fit_col2, fit_col3 = st.columns(3)
    fit_col1.metric("Observaciones", f"{int(model_fit_stats_df['N_obs'].iloc[0])}")
    fit_col2.metric("Pseudo R²", f"{model_fit_stats_df['Pseudo_R2'].iloc[0]:.3f}")
    fit_col3.metric(
        "Significancia global del modelo",
        "Sí" if model_fit_stats_df["LLR_pvalue"].iloc[0] < 0.05 else "No",
        help=f"LLR p-value = {model_fit_stats_df['LLR_pvalue'].iloc[0]:.2e}"
    )
    st.caption(
        "El pseudo R² bajo es esperable en modelos de salud percibida con datos "
        "de encuesta transversal: el objetivo aquí es identificar asociaciones "
        "significativas, no maximizar poder predictivo."
    )

    st.markdown("##### Coeficientes del modelo")
    st.caption(
        "El **Odds Ratio (OR)** indica cuántas veces cambian las probabilidades "
        "(*odds*) de reportar mala salud por cada unidad adicional de la variable. "
        "OR > 1 indica mayor riesgo; OR < 1, menor riesgo."
    )

    coefficients_display_df = model_coefficients_df.copy()
    coefficients_display_df["Significativo"] = coefficients_display_df["P_Value"].apply(
        lambda p: "Sí (p<0.05)" if p < 0.05 else "No"
    )
    coefficients_display_df["Coeficiente"] = coefficients_display_df["Coeficiente"].round(4)
    coefficients_display_df["Odds Ratio"] = coefficients_display_df["Odds_Ratio"].round(3)
    coefficients_display_df["P-valor"] = coefficients_display_df["P_Value"].round(4)

    st.dataframe(
        coefficients_display_df[["Variable", "Coeficiente", "Odds Ratio", "P-valor", "Significativo"]],
        use_container_width=True,
        hide_index=True,
    )

    st.markdown("##### Efectos marginales promedio (AME)")
    st.caption(
        "Cuántos puntos porcentuales (p.p.) cambia la probabilidad de reportar "
        "mala salud por cada unidad de la variable — más interpretable que el "
        "coeficiente crudo del logit, especialmente para comunicar hallazgos "
        "a audiencias no técnicas."
    )

    ame_display_df = ame_df.copy()
    ame_display_df["Significativo"] = ame_display_df["P_Value"].apply(
        lambda p: "Sí" if p < 0.05 else "No"
    )
    ame_display_df["Efecto (p.p.)"] = (ame_display_df["Efecto_Marginal"] * 100).round(2)
    ame_display_df["P-valor"] = ame_display_df["P_Value"].round(3)

    st.dataframe(
        ame_display_df[["Variable", "Efecto (p.p.)", "P-valor", "Significativo"]],
        use_container_width=True,
        hide_index=True,
    )

    with st.expander("Ver salida técnica completa (statsmodels)"):
        st.text(logit_summary_text)