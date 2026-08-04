"""
Limpieza y enriquecimiento de gym_members_exercise_tracking.csv
Proyecto: Perfil de Miembro y Retencion - Gimnasio
"""
import pandas as pd
import numpy as np

RAW_PATH = "raw_gym_members.csv"

df = pd.read_csv(RAW_PATH)

log = []
log.append(f"Filas originales: {len(df)}")
log.append(f"Columnas originales: {list(df.columns)}")

# 1. Nulos y duplicados
n_nulls = df.isnull().sum().sum()
n_dupes = df.duplicated().sum()
log.append(f"Valores nulos encontrados: {n_nulls}")
log.append(f"Filas duplicadas encontradas: {n_dupes}")
if n_dupes > 0:
    df = df.drop_duplicates()
    log.append(f"-> Se eliminaron {n_dupes} duplicados")

# 2. Normalizar nombres de columnas (sin espacios/parentesis, snake_case)
rename_map = {
    "Age": "age",
    "Gender": "gender",
    "Weight (kg)": "weight_kg",
    "Height (m)": "height_m",
    "Max_BPM": "max_bpm",
    "Avg_BPM": "avg_bpm",
    "Resting_BPM": "resting_bpm",
    "Session_Duration (hours)": "session_duration_hours",
    "Calories_Burned": "calories_burned",
    "Workout_Type": "workout_type",
    "Fat_Percentage": "fat_percentage",
    "Water_Intake (liters)": "water_intake_liters",
    "Workout_Frequency (days/week)": "workout_frequency_days",
    "Experience_Level": "experience_level",
    "BMI": "bmi",
}
df = df.rename(columns=rename_map)

# 3. Validacion de rangos logicos
range_checks = {
    "age": (18, 100),
    "weight_kg": (30, 250),
    "height_m": (1.2, 2.3),
    "max_bpm": (100, 220),
    "avg_bpm": (60, 200),
    "resting_bpm": (30, 100),
    "session_duration_hours": (0.1, 4),
    "calories_burned": (50, 3500),
    "fat_percentage": (3, 60),
    "water_intake_liters": (0.5, 6),
    "workout_frequency_days": (0, 7),
    "experience_level": (1, 3),
    "bmi": (10, 60),
}
out_of_range_total = 0
for col, (lo, hi) in range_checks.items():
    mask = ~df[col].between(lo, hi)
    n = mask.sum()
    if n > 0:
        out_of_range_total += n
        log.append(f"-> {col}: {n} valores fuera de rango [{lo}, {hi}]")
log.append(f"Total valores fuera de rango detectados: {out_of_range_total}")

# 4. Normalizar texto categorico
df["gender"] = df["gender"].str.strip().str.title()
workout_type_map = {"yoga": "Yoga", "hiit": "HIIT", "cardio": "Cardio", "strength": "Strength"}
df["workout_type"] = df["workout_type"].str.strip().str.lower().map(workout_type_map).fillna(df["workout_type"])

# 5. Verificacion cruzada de BMI (weight / height^2) - deteccion de inconsistencias, no se sobreescribe
bmi_calc = df["weight_kg"] / (df["height_m"] ** 2)
bmi_diff = (df["bmi"] - bmi_calc).abs()
inconsistent_bmi = (bmi_diff > 1.0).sum()
log.append(f"Filas con BMI inconsistente vs peso/altura (diferencia > 1.0): {inconsistent_bmi}")

# 6. Columnas derivadas para el analisis de perfil y retencion
def age_group(a):
    if a < 26: return "18-25"
    if a < 36: return "26-35"
    if a < 46: return "36-45"
    if a < 56: return "46-55"
    return "56+"
df["age_group"] = df["age"].apply(age_group)

def bmi_category(b):
    if b < 18.5: return "Bajo peso"
    if b < 25: return "Normal"
    if b < 30: return "Sobrepeso"
    return "Obesidad"
df["bmi_category"] = df["bmi"].apply(bmi_category)

def engagement_level(freq):
    if freq <= 2: return "Baja (1-2 dias)"
    if freq <= 3: return "Media (3 dias)"
    return "Alta (4-5 dias)"
df["engagement_level"] = df["workout_frequency_days"].apply(engagement_level)

exp_labels = {1: "Principiante", 2: "Intermedio", 3: "Avanzado"}
df["experience_label"] = df["experience_level"].map(exp_labels)

df["calories_per_hour"] = (df["calories_burned"] / df["session_duration_hours"]).round(1)

# Proxy de "riesgo de abandono": baja frecuencia + nivel principiante
df["retention_risk"] = np.where(
    (df["workout_frequency_days"] <= 2) & (df["experience_level"] == 1),
    "Alto riesgo",
    np.where(df["workout_frequency_days"] >= 4, "Bajo riesgo", "Riesgo medio")
)

# Reordenar columnas
cols_order = [
    "age", "age_group", "gender", "weight_kg", "height_m", "bmi", "bmi_category",
    "max_bpm", "avg_bpm", "resting_bpm",
    "workout_type", "session_duration_hours", "calories_burned", "calories_per_hour",
    "fat_percentage", "water_intake_liters",
    "workout_frequency_days", "engagement_level",
    "experience_level", "experience_label", "retention_risk",
]
df = df[cols_order]

df.to_csv("gym_members_clean.csv", index=False)

with open("cleaning_log.txt", "w") as f:
    f.write("\n".join(log))

print("\n".join(log))
print("\nFilas finales:", len(df))
print(df.head(3).to_string())
