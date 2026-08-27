# Brechas de Salud Mental y Factores Estructurales Urbanos en Bogotá
### Caso del suicidio y la salud autopercibida — DataJam Edición 3, 2026

**Equipo:** GEMMA 2.0
**Evento:** DataJam Edición 3 — 2026, Alcaldía Mayor de Bogotá (DIPEA) / Universidad Nacional de Colombia / Universidad de La Salle / Escuela Colombiana de Ingeniería Julio Garavito

**Dashboard desplegado:** https://datajam-2026-mental-health-bogota-luugap.streamlit.app

---

## 1. Problema abordado

El deterioro de la salud mental y la percepción negativa de salud en Bogotá están fuertemente condicionados por determinantes estructurales: inseguridad alimentaria, tiempo de residencia, brechas de género en el cuidado y desigual acceso a infraestructura verde. Este proyecto explora dos dimensiones complementarias de esta problemática:

1. **Dimensión territorial:** ¿existe relación entre la infraestructura verde disponible y los eventos de conducta suicida por localidad?
2. **Dimensión individual/hogar:** ¿qué factores del hogar (tamaño, número de menores a cargo, rol familiar) se asocian con una peor salud autopercibida?

Este análisis retoma directamente la problemática destacada en la jornada de apertura del DataJam ("El Suicidio en Bogotá — Un Perfil Diferente"), ampliándola con un enfoque de determinantes sociales estructurales.

## 2. Pregunta analítica e hipótesis

**Pregunta:** ¿En qué medida la infraestructura verde disponible por localidad y los factores estructurales del hogar (composición familiar, carga de cuidado, rol dentro del hogar) se asocian con indicadores de salud mental en Bogotá (conducta suicida y salud autopercibida)?

**Hipótesis:** La vulnerabilidad en salud mental no depende de un único factor, sino de la convergencia de condiciones territoriales (acceso a espacio verde) y condiciones estructurales del hogar (composición, carga de cuidado y rol familiar).

## 3. Fuentes de datos utilizadas

| Fuente | Descripción | URL |
|---|---|---|
| Conducta suicida Bogotá (OSB) | Casos de ideación, intento y suicidio consumado 2023-2025 | https://datosabiertos.bogota.gov.co/dataset/tasa-de-suicidio-en-bogota-d-c |
| Encuesta Distrital de Percepción 2025 | Determinantes sociales de salud percibida | https://www.sdp.gov.co/gestion-estudios-estrategicos/informacion-estadisticas/encuesta-distrital-percepcion |
| Sistema Distrital de Parques y Escenarios Públicos / Indicador Espacio Público Ciudad, Bogotá D.C. | Inventario de parques y espacio público por localidad | https://datosabiertos.bogota.gov.co/dataset/sistema-distrital-de-parques-y-escenarios-publicos-deportivos y https://datosabiertos.bogota.gov.co/dataset/indicador-espacio-publico-ciudad-bogota-d-c |
| Límites Político-Administrativos (UPL y Localidades) | Límites geográficos oficiales de las localidades de Bogotá | https://datosabiertos.bogota.gov.co/dataset/localidad-bogota-d-c |
| Población en Bogotá D.C. 2005-2035 | Población por cada localidad de Bogotá | https://datosabiertos.bogota.gov.co/dataset/piramide-poblacional-bogota-d-c |

## 4. Metodología general

El análisis se desarrolló en dos notebooks secuenciales:

- **`001_pre_processing.ipynb`**: carga, limpieza y armonización de las cuatro fuentes de datos (corrección de encoding, normalización de nombres de localidades entre fuentes con convenciones distintas), cálculo de indicadores agregados por localidad, y construcción del dataset maestro geoespacial (`master_mental_health_bogota_2025.geojson`).
- **`002_post_processing_and_analysis.ipynb`**: cálculo de indicadores epidemiológicos (2023-2025), análisis de brecha de género en conducta suicida, análisis de correlación entre infraestructura verde y suicidios por localidad, y modelo de regresión logística binaria para identificar determinantes de la salud autopercibida (variable `A3`: tamaño del hogar, `A4`: menores de 18 años a cargo, `A6x2`: parentesco con el jefe de hogar).

Los resultados procesados se exportan a `data/processed/` y alimentan el dashboard interactivo (`app.py`), construido en Streamlit.

## 5. Principales hallazgos

- Existe una brecha de género marcada en los eventos de conducta suicida: los hombres representan la mayoría de los casos registrados en las 20 localidades, consistente con patrones epidemiológicos nacionales.
- El número de menores de 18 años a cargo (A4) se asocia de forma significativa (p<0.05) con mayor probabilidad de reportar salud deficiente, incluso controlando por parentesco y tamaño del hogar.
- El parentesco con el jefe del hogar (A6x2) es el determinante con mayor efecto en el modelo: ser suegra/suegro se asocia con la mayor reducción en probabilidad de mala salud percibida, mientras que ser hermana/o o hija/o del jefe de hogar se asocia con mayor probabilidad.
- La correlación entre área verde total y suicidios registrados a nivel de localidad es positiva, pero se documenta como probable efecto de confusión por tamaño poblacional (ver limitaciones en el dashboard), no como relación causal.

## 6. Limitaciones

- El modelo logit tiene un pseudo R² bajo (aproximadamente 0.012), esperable en modelos de salud percibida con datos transversales de encuesta — el objetivo es identificar asociaciones significativas, no maximizar poder predictivo.
- La correlación territorial (verde vs. suicidios) es a nivel agregado (n=20 localidades) y no controla por población, por lo que es susceptible a falacia ecológica.
- Categorías con muestra reducida (por ejemplo, hogares con 5 o más menores a cargo) fueron agrupadas para evitar estimaciones inestables.

## 7. Estructura del repositorio
```text
├── app.py                          # Dashboard interactivo (Streamlit)
├── requirements.txt                # Dependencias con versiones fijas
├── runtime.txt                     # Versión de Python para despliegue
│
├── data/
│   ├── raw/                        # Datos originales sin procesar
│   ├── raw_zips/                   # Archivos comprimidos originales
│   └── processed/                  # Datos limpios y agregados para el dashboard
│
├── notebooks/
│   ├── 001_pre_processing.ipynb    # Limpieza, integración y armonización
│   └── 002_post_processing_and_analysis.ipynb
│                                    # Indicadores, correlaciones y modelo logit
│
├── outputs/
│   ├── tables/                     # Tablas de resultados exportadas
│   └── figures/                    # Gráficos exportados
│
└── README.md
```

## 8. Instrucciones de ejecución

### Reproducibilidad del análisis (notebooks)

Este repositorio contiene los **outputs y datos ya procesados** (`data/processed/`, `outputs/`)
necesarios para el deploy del dashboard en Streamlit. **No los uses como punto de partida**
para reproducir el análisis, ya que ejecutar los notebooks sobre ellos los sobrescribirá.

Si tu objetivo es reproducir el experimento desde cero:

1. **No clones el repositorio completo.**
2. Abre directamente `notebooks/001_pre_processing.ipynb` desde GitHub en Google Colab:

   https://colab.research.google.com/github/ILuuI/datajam-2026-mental-health-bogota/blob/main/notebooks/001_pre_processing.ipynb

3. Ejecuta la **primera celda**, que:
   - Monta tu Google Drive.
   - Crea (o verifica) una carpeta de proyecto en tu Drive (`ej. DataJAM_Bogota_2026/`).
   - Descarga automáticamente solo lo estrictamente necesario (`notebooks/` y `data/raw_zips/`)
     mediante `git sparse-checkout`, sin incluir los resultados ya calculados.
   - Si la carpeta ya existe de una corrida previa, te preguntará si deseas sobrescribirla;
     si eliges no hacerlo, verificará que los archivos necesarios estén completos y descargará
     únicamente lo que falte.
4. Continúa ejecutando el notebook 1 de principio a fin (descomprime los datos crudos,
   los limpia y exporta el dataset maestro a `data/processed/`).
5. Abre y ejecuta `notebooks/002_post_processing_and_analysis.ipynb` de la misma forma.
   Este notebook incluye una celda de verificación que confirma que los archivos generados
   por el notebook 1 existen antes de continuar; si falta alguno, te indicará exactamente
   qué pasos seguir.

Esto garantiza que todos los resultados (GeoJSON maestro, indicadores, modelo logit,
figuras) se generen desde los datos crudos, en tu propio Google Drive, sin depender de
ni sobrescribir los archivos pre-calculados que usa el dashboard en producción.

### Dashboard (visualización)

Para simplemente **ver el dashboard**, no necesitas ejecutar nada: está desplegado
públicamente en:
https://datajam-2026-mental-health-bogota-luugap.streamlit.app

Si en cambio quieres **ejecutarlo o modificarlo localmente**, sí necesitas el repositorio
completo (a diferencia del flujo de reproducibilidad anterior), ya que `app.py` depende
de `data/processed/`, `requirements.txt` y `runtime.txt` tal como están en el repo:

```bash
git clone https://github.com/ILuuI/datajam-2026-mental-health-bogota.git
cd datajam-2026-mental-health-bogota

python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # Mac/Linux

pip install -r requirements.txt
streamlit run app.py
```

## 9. Equipo

GEMMA 2.0 — DataJam Edición 3, 2026.