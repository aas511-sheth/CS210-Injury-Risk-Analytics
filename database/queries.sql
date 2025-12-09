CREATE VIEW player_weekly_features AS
SELECT 
    tm.player_id,
    p.player_name,
    p.position,
    tm.week_start_date,
    tm.training_load_hours,
    tm.intensity_avg,
    tm.recovery_score,
    tm.fatigue_level,

    AVG(tm.training_load_hours) OVER (PARTITION BY tm.player_id ORDER BY tm.week_start_date 
        ROWS BETWEEN 3 PRECEDING AND CURRENT ROW) AS avg_load_4week,

    LAG(tm.training_load_hours) OVER (PARTITION BY tm.player_id ORDER BY tm.week_start_date) AS prev_load,

    CASE WHEN ih.injury_id IS NOT NULL THEN 1 ELSE 0 END AS injury_occurred
FROM training_metrics tm
JOIN players p ON tm.player_id = p.player_id
LEFT JOIN injury_history ih ON tm.player_id = ih.player_id 
    AND ih.injury_date BETWEEN tm.week_start_date AND tm.week_start_date + 14
ORDER BY tm.player_id, tm.week_start_date;

SELECT 
    p.player_name,
    p.position,
    p.team,
    AVG(ip.risk_score) as avg_risk,
    MAX(ip.risk_score) as max_risk,
    COUNT(CASE WHEN ip.risk_category = 'High' THEN 1 END) as high_risk_weeks
FROM injury_predictions ip
JOIN players p ON ip.player_id = p.player_id
GROUP BY p.player_id, p.player_name, p.position, p.team
HAVING AVG(ip.risk_score) > 0.6
ORDER BY avg_risk DESC;

SELECT 
    p.position,
    COUNT(DISTINCT p.player_id) as player_count,
    AVG(ip.risk_score) as avg_risk_score,
    STDDEV(ip.risk_score) as risk_stddev,
    MAX(ip.risk_score) as max_risk
FROM injury_predictions ip
JOIN players p ON ip.player_id = p.player_id
GROUP BY p.position
ORDER BY avg_risk_score DESC;