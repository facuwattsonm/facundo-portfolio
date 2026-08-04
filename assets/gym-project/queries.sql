-- ============================================================
-- Proyecto: Perfil de Miembro y Retencion - Gimnasio
-- Motor: SQLite (gym_members.db, tabla gym_members)
-- Dataset: gym_members_exercise_tracking.csv (Kaggle, 973 miembros)
-- ============================================================

-- 1) Panorama general del gimnasio
SELECT
    COUNT(*)                                   AS total_miembros,
    ROUND(AVG(age), 1)                         AS edad_promedio,
    ROUND(AVG(workout_frequency_days), 2)      AS frecuencia_promedio_dias,
    ROUND(AVG(session_duration_hours), 2)      AS duracion_sesion_promedio_hs,
    ROUND(AVG(calories_burned), 0)             AS calorias_promedio
FROM gym_members;


-- 2) Distribucion de miembros por genero y grupo etario
SELECT
    age_group,
    gender,
    COUNT(*) AS miembros,
    ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM gym_members), 1) AS pct_del_total
FROM gym_members
GROUP BY age_group, gender
ORDER BY age_group, gender;


-- 3) Nivel de engagement (frecuencia semanal) por grupo etario
--    Retencion proxy: qué franja etaria entrena con mayor frecuencia
SELECT
    age_group,
    engagement_level,
    COUNT(*) AS miembros,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (PARTITION BY age_group), 1) AS pct_dentro_del_grupo
FROM gym_members
GROUP BY age_group, engagement_level
ORDER BY age_group,
    CASE engagement_level
        WHEN 'Baja (1-2 dias)' THEN 1
        WHEN 'Media (3 dias)'  THEN 2
        WHEN 'Alta (4-5 dias)' THEN 3
    END;


-- 4) Perfil de riesgo de abandono (retention_risk) - conteo y perfil promedio
SELECT
    retention_risk,
    COUNT(*)                                AS miembros,
    ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM gym_members), 1) AS pct_del_total,
    ROUND(AVG(age), 1)                      AS edad_promedio,
    ROUND(AVG(session_duration_hours), 2)   AS duracion_sesion_prom,
    ROUND(AVG(calories_burned), 0)          AS calorias_prom,
    ROUND(AVG(fat_percentage), 1)           AS pct_grasa_prom,
    ROUND(AVG(bmi), 1)                      AS bmi_prom
FROM gym_members
GROUP BY retention_risk
ORDER BY
    CASE retention_risk WHEN 'Alto riesgo' THEN 1 WHEN 'Riesgo medio' THEN 2 ELSE 3 END;


-- 5) Relacion entre experiencia y frecuencia de entrenamiento
--    (¿a mayor experiencia, mayor frecuencia semanal? -> indicio de retencion)
SELECT
    experience_label,
    ROUND(AVG(workout_frequency_days), 2) AS frecuencia_promedio,
    ROUND(AVG(session_duration_hours), 2) AS duracion_promedio,
    ROUND(AVG(calories_burned), 0)        AS calorias_promedio,
    COUNT(*)                              AS miembros
FROM gym_members
GROUP BY experience_label
ORDER BY
    CASE experience_label WHEN 'Principiante' THEN 1 WHEN 'Intermedio' THEN 2 ELSE 3 END;


-- 6) Tipo de entrenamiento preferido por segmento de riesgo de abandono
SELECT
    retention_risk,
    workout_type,
    COUNT(*) AS miembros,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (PARTITION BY retention_risk), 1) AS pct_dentro_del_segmento
FROM gym_members
GROUP BY retention_risk, workout_type
ORDER BY retention_risk, miembros DESC;


-- 7) Genero: frecuencia, duracion y calorias promedio
SELECT
    gender,
    COUNT(*)                              AS miembros,
    ROUND(AVG(workout_frequency_days), 2) AS frecuencia_promedio,
    ROUND(AVG(session_duration_hours), 2) AS duracion_promedio,
    ROUND(AVG(calories_burned), 0)        AS calorias_promedio,
    ROUND(AVG(fat_percentage), 1)         AS pct_grasa_promedio
FROM gym_members
GROUP BY gender;


-- 8) Categoria de BMI vs nivel de engagement (¿el estado fisico se relaciona con la constancia?)
SELECT
    bmi_category,
    engagement_level,
    COUNT(*) AS miembros
FROM gym_members
GROUP BY bmi_category, engagement_level
ORDER BY bmi_category,
    CASE engagement_level
        WHEN 'Baja (1-2 dias)' THEN 1
        WHEN 'Media (3 dias)'  THEN 2
        WHEN 'Alta (4-5 dias)' THEN 3
    END;


-- 9) Top segmento demografico con mayor calorias quemadas por hora (eficiencia de entrenamiento)
SELECT
    age_group,
    gender,
    workout_type,
    ROUND(AVG(calories_per_hour), 1) AS calorias_por_hora_prom,
    COUNT(*) AS miembros
FROM gym_members
GROUP BY age_group, gender, workout_type
HAVING COUNT(*) >= 10
ORDER BY calorias_por_hora_prom DESC
LIMIT 10;


-- 10) Miembros de "alto riesgo" de abandono: listado de perfil detallado
--     (para segmentacion / campañas de retencion)
SELECT
    age, age_group, gender, workout_type, experience_label,
    workout_frequency_days, session_duration_hours, calories_burned, bmi_category
FROM gym_members
WHERE retention_risk = 'Alto riesgo'
ORDER BY age;
