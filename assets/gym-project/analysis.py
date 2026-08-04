"""
Analisis y visualizaciones - Perfil de Miembro y Retencion (Gimnasio)
Genera los graficos clave en charts/ a partir de gym_members_clean.csv
"""
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns

sns.set_theme(style="whitegrid", font_scale=1.0)
PALETTE = {"Baja (1-2 dias)": "#E76F51", "Media (3 dias)": "#E9C46A", "Alta (4-5 dias)": "#2A9D8F"}
RISK_PALETTE = {"Alto riesgo": "#E63946", "Riesgo medio": "#F4A261", "Bajo riesgo": "#2A9D8F"}

df = pd.read_csv("gym_members_clean.csv")

age_order = ["18-25", "26-35", "36-45", "46-55", "56+"]
eng_order = ["Baja (1-2 dias)", "Media (3 dias)", "Alta (4-5 dias)"]
risk_order = ["Alto riesgo", "Riesgo medio", "Bajo riesgo"]
exp_order = ["Principiante", "Intermedio", "Avanzado"]

# ---------------------------------------------------------------
# 1. Distribucion de miembros por grupo etario y genero
# ---------------------------------------------------------------
fig, ax = plt.subplots(figsize=(8, 5))
ct = pd.crosstab(df["age_group"], df["gender"]).reindex(age_order)
ct.plot(kind="bar", ax=ax, color=["#E76F51", "#264653"])
ax.set_title("Miembros por grupo etario y genero")
ax.set_xlabel("Grupo etario")
ax.set_ylabel("Cantidad de miembros")
plt.xticks(rotation=0)
plt.tight_layout()
plt.savefig("charts/01_miembros_por_edad_genero.png", dpi=150)
plt.close()

# ---------------------------------------------------------------
# 2. Nivel de engagement (frecuencia semanal) por grupo etario
# ---------------------------------------------------------------
fig, ax = plt.subplots(figsize=(8, 5))
ct2 = pd.crosstab(df["age_group"], df["engagement_level"], normalize="index").reindex(age_order)[eng_order] * 100
ct2.plot(kind="bar", stacked=True, ax=ax, color=[PALETTE[c] for c in eng_order])
ax.set_title("Nivel de engagement (frecuencia semanal) por grupo etario")
ax.set_xlabel("Grupo etario")
ax.set_ylabel("% de miembros")
ax.legend(title="Engagement", bbox_to_anchor=(1.02, 1), loc="upper left")
plt.xticks(rotation=0)
plt.tight_layout()
plt.savefig("charts/02_engagement_por_edad.png", dpi=150)
plt.close()

# ---------------------------------------------------------------
# 3. Segmento de riesgo de abandono (retention_risk) - tamano y perfil
# ---------------------------------------------------------------
fig, axes = plt.subplots(1, 2, figsize=(11, 5))
risk_counts = df["retention_risk"].value_counts().reindex(risk_order)
axes[0].bar(risk_counts.index, risk_counts.values, color=[RISK_PALETTE[c] for c in risk_order])
axes[0].set_title("Miembros por segmento de riesgo de abandono")
axes[0].set_ylabel("Cantidad de miembros")
for i, v in enumerate(risk_counts.values):
    axes[0].text(i, v + 5, str(v), ha="center")

grp = df.groupby("retention_risk")[["session_duration_hours", "calories_burned"]].mean().reindex(risk_order)
ax2 = axes[1]
ax2b = ax2.twinx()
ax2.bar([x - 0.2 for x in range(3)], grp["session_duration_hours"], width=0.4, color="#264653", label="Duracion sesion (hs)")
ax2b.bar([x + 0.2 for x in range(3)], grp["calories_burned"], width=0.4, color="#E9C46A", label="Calorias quemadas")
ax2.set_xticks(range(3))
ax2.set_xticklabels(risk_order)
ax2.set_ylabel("Duracion promedio (hs)")
ax2b.set_ylabel("Calorias promedio")
ax2.set_title("Duracion y calorias promedio por segmento de riesgo")
lines1, labels1 = ax2.get_legend_handles_labels()
lines2, labels2 = ax2b.get_legend_handles_labels()
ax2.legend(lines1 + lines2, labels1 + labels2, loc="upper left", fontsize=8)
plt.tight_layout()
plt.savefig("charts/03_segmento_riesgo_abandono.png", dpi=150)
plt.close()

# ---------------------------------------------------------------
# 4. Experiencia vs frecuencia / duracion / calorias (driver de retencion)
# ---------------------------------------------------------------
fig, ax = plt.subplots(figsize=(8, 5))
exp_grp = df.groupby("experience_label")[["workout_frequency_days", "session_duration_hours"]].mean().reindex(exp_order)
x = range(len(exp_order))
ax.bar([i - 0.2 for i in x], exp_grp["workout_frequency_days"], width=0.4, label="Frecuencia (dias/sem)", color="#2A9D8F")
ax2 = ax.twinx()
ax2.bar([i + 0.2 for i in x], exp_grp["session_duration_hours"], width=0.4, label="Duracion sesion (hs)", color="#F4A261")
ax.set_xticks(x)
ax.set_xticklabels(exp_order)
ax.set_title("Nivel de experiencia vs frecuencia y duracion de entrenamiento")
ax.set_ylabel("Frecuencia promedio (dias/semana)")
ax2.set_ylabel("Duracion promedio (hs)")
lines1, labels1 = ax.get_legend_handles_labels()
lines2, labels2 = ax2.get_legend_handles_labels()
ax.legend(lines1 + lines2, labels1 + labels2, loc="upper left")
plt.tight_layout()
plt.savefig("charts/04_experiencia_vs_frecuencia.png", dpi=150)
plt.close()

# ---------------------------------------------------------------
# 5. Tipo de entrenamiento preferido por segmento de riesgo
# ---------------------------------------------------------------
fig, ax = plt.subplots(figsize=(8, 5))
ct5 = pd.crosstab(df["retention_risk"], df["workout_type"], normalize="index").reindex(risk_order) * 100
ct5.plot(kind="bar", ax=ax, color=["#264653", "#2A9D8F", "#E9C46A", "#E76F51"])
ax.set_title("Tipo de entrenamiento preferido por segmento de riesgo")
ax.set_xlabel("Segmento de riesgo de abandono")
ax.set_ylabel("% dentro del segmento")
plt.xticks(rotation=0)
ax.legend(title="Tipo de entrenamiento", bbox_to_anchor=(1.02, 1), loc="upper left")
plt.tight_layout()
plt.savefig("charts/05_tipo_entrenamiento_por_riesgo.png", dpi=150)
plt.close()

# ---------------------------------------------------------------
# 6. BMI vs Fat% coloreado por engagement (salud vs constancia)
# ---------------------------------------------------------------
fig, ax = plt.subplots(figsize=(8, 6))
for lvl in eng_order:
    sub = df[df["engagement_level"] == lvl]
    ax.scatter(sub["bmi"], sub["fat_percentage"], s=18, alpha=0.55, label=lvl, color=PALETTE[lvl])
ax.set_xlabel("BMI")
ax.set_ylabel("% de grasa corporal")
ax.set_title("BMI vs % de grasa corporal, por nivel de engagement")
ax.legend(title="Engagement")
plt.tight_layout()
plt.savefig("charts/06_bmi_vs_grasa_por_engagement.png", dpi=150)
plt.close()

print("Graficos generados en charts/:")
import os
for f in sorted(os.listdir("charts")):
    print(" -", f)
