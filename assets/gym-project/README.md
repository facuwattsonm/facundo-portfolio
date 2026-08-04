# Perfil de Miembro y Retención — Gimnasio

Análisis del dataset **Gym Members Exercise Tracking** (973 miembros, Kaggle) enfocado en entender qué caracteriza a los miembros que entrenan de forma consistente frente a los que muestran señales de bajo compromiso, como insumo para estrategias de retención de un gimnasio.

## ¿Qué problema podemos solucionar?

Un gimnasio necesita saber **a quién dirigir sus esfuerzos de retención** y **en qué momento del recorrido del socio intervenir**. Este dataset no tiene fechas de alta/baja (es una foto puntual, no una serie temporal de membresías), así que en lugar de medir churn real, se construyó un **proxy de riesgo de abandono** a partir de dos señales de comportamiento disponibles: frecuencia semanal de entrenamiento y nivel de experiencia. Con eso se puede responder: ¿qué perfil de socio entrena poco y es nuevo (alto riesgo), y qué lo diferencia del socio consistente?

## ¿Qué podemos comprender de los datos?

- **973 miembros**, edad promedio 38.7 años, distribución pareja entre géneros (511 hombres / 462 mujeres) y entre franjas etarias (18-25 hasta 56+).
- **1 de cada 5 miembros (20.2%, 197 personas)** cae en el segmento de "alto riesgo": entrena 2 días o menos por semana y tiene nivel de experiencia principiante. Este grupo entrena sesiones más cortas (1.0h vs 1.49h del segmento de bajo riesgo) y quema menos calorías por sesión (726 vs 1068).
- **La experiencia es el driver más fuerte de consistencia**, mucho más que el tipo de entrenamiento o el género: a medida que sube el nivel de experiencia, sube la frecuencia semanal (2.48 → 3.53 → 4.53 días) y las calorías quemadas (726 → 902 → 1265). Esto sugiere que la ventana crítica de retención está en los primeros meses, antes de que el socio se vuelva "intermedio".
- El **tipo de entrenamiento no es un factor diferencial de riesgo**: las 4 disciplinas (Cardio, Fuerza, HIIT, Yoga) se reparten de forma similar en los tres segmentos de riesgo (ligera sobre-representación de Cardio en alto riesgo, 32% vs ~24-25% en los demás).
- El **BMI/estado físico tampoco predice bajo compromiso**: incluso dentro de la categoría "Obesidad", la mayoría de los miembros está en el grupo de alta frecuencia de entrenamiento, no en el de baja.
- Diferencias por género: los hombres queman más calorías en promedio (944 vs 862 kcal) con frecuencia similar; las mujeres muestran mayor % de grasa corporal promedio (27.7% vs 22.6%), consistente con diferencias fisiológicas esperadas.

**Conclusión práctica:** la palanca de retención más clara no es cambiar la oferta de clases, sino acompañar al socio nuevo/principiante en sus primeras semanas (frecuencia y duración de sesión), ya que ese es el segmento con mayor riesgo y el que más mejora a medida que gana experiencia.

## Estructura del proyecto

```
gym_project/
├── raw_gym_members.csv          # dataset original (973 filas, sin cambios)
├── clean_data.py                # script de limpieza y enriquecimiento
├── gym_members_clean.csv        # dataset limpio, con columnas derivadas
├── gym_members_clean.xlsx       # Excel: datos limpios + KPIs con fórmulas en vivo + notas de limpieza
├── cleaning_log.txt             # log del proceso de depuración
├── load_db.py                   # carga el CSV limpio a SQLite
├── gym_members.db               # base SQLite (tabla: gym_members)
├── queries.sql                  # 10 queries SQL usadas en el análisis
├── analysis.py                  # script de Python (pandas/matplotlib/seaborn) que genera los gráficos
├── charts/                      # gráficos generados (PNG)
├── build_bi_export.py           # genera el archivo listo para Looker Studio / Power BI
├── gym_members_bi_ready.csv     # archivo plano para importar en Looker Studio o Power BI
└── README.md                    # este archivo
```

## 1. Limpieza de datos

El dataset original ya venía sin nulos ni duplicados. El proceso de limpieza (`clean_data.py`) igual aplicó:

- Validación de rangos lógicos en las 13 columnas numéricas (edad, peso, altura, BPM, duración, calorías, etc.) — 0 valores fuera de rango.
- Verificación cruzada del BMI (peso / altura²) contra la columna original — sin inconsistencias.
- Normalización de texto (género, tipo de entrenamiento).
- Columnas derivadas agregadas para el análisis: `age_group`, `bmi_category`, `engagement_level`, `experience_label`, `calories_per_hour`, `retention_risk`.

El resultado se guardó en `gym_members_clean.csv` / `gym_members_clean.xlsx` (esta última con una hoja de KPIs calculados con fórmulas en vivo sobre la hoja de datos, y las notas de limpieza documentadas).

## 2. SQL (SQLite)

`gym_members.db` contiene la tabla `gym_members` con el dataset limpio. `queries.sql` incluye 10 queries: panorama general, distribución demográfica, engagement por edad, perfil de riesgo de abandono, relación experiencia-frecuencia, tipo de entrenamiento por segmento de riesgo, comparación por género, BMI vs engagement, eficiencia calórica por segmento, y el listado detallado de miembros de alto riesgo.

## 3. Dashboard (Looker Studio / Power BI)

No se construyó el dashboard interactivo dentro de esta sesión (no hay integración directa con Looker Studio ni Power BI en este entorno). En su lugar, `gym_members_bi_ready.csv` deja el dataset limpio y enriquecido listo para conectar directamente como fuente de datos en Looker Studio o Power BI: nombres de columna legibles, un `Member ID` único por fila, y todas las columnas categóricas/derivadas (Age Group, BMI Category, Engagement Level, Retention Risk, etc.) ya calculadas para usar como filtros o dimensiones.

Sugerencia de estructura para el dashboard (siguiendo el estilo de tus proyectos anteriores en el portfolio):
- Página 1 — Overview: scorecards de Total de miembros, Edad promedio, Frecuencia promedio, % en riesgo alto; gráfico de barras por grupo etario y género.
- Página 2 — Retención: distribución de `Retention Risk`, relación experiencia vs frecuencia/calorías, filtro desplegable por `Age Group`.
- Página 3 — Entrenamiento: `Workout Type` por segmento de riesgo, calorías por hora por segmento demográfico.

## 4. Python

`analysis.py` genera 6 gráficos en `charts/`: distribución por edad/género, engagement por grupo etario, tamaño y perfil del segmento de riesgo de abandono, experiencia vs frecuencia/duración, tipo de entrenamiento por segmento de riesgo, y BMI vs % de grasa por nivel de engagement.

## 5. Fuente y reproducibilidad

Dataset original: *Gym Members Exercise Tracking Dataset* (Kaggle). Para reproducir el proyecto: `python clean_data.py` → `python load_db.py` → `python analysis.py` → `python build_bi_export.py` → (opcional) recalcular `gym_members_clean.xlsx` con LibreOffice/Excel al abrirlo.
