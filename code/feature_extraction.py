import pandas as pd
import psycopg2
from psycopg2.extras import RealDictCursor
import numpy as np
from config import DB_CONFIG

def extract_features():
    """Extract ML-ready features from database"""
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    # Get all training metrics with injury flag
    cur.execute("""
        SELECT 
            tm.player_id,
            p.player_name,
            p.position,
            tm.week_start_date,
            tm.training_load_hours,
            tm.intensity_avg,
            tm.recovery_score,
            tm.fatigue_level,
            LAG(tm.training_load_hours) OVER (PARTITION BY tm.player_id ORDER BY tm.week_start_date) as prev_load,
            AVG(tm.training_load_hours) OVER (PARTITION BY tm.player_id ORDER BY tm.week_start_date 
                ROWS BETWEEN 3 PRECEDING AND CURRENT ROW) as avg_load_4week,
            CASE WHEN ih.injury_id IS NOT NULL THEN 1 ELSE 0 END as injury_occurred
        FROM training_metrics tm
        JOIN players p ON tm.player_id = p.player_id
        LEFT JOIN injury_history ih ON tm.player_id = ih.player_id 
            AND ih.injury_date = tm.week_start_date + 7
        ORDER BY tm.player_id, tm.week_start_date
    """)
    
    df = pd.DataFrame(cur.fetchall())
    cur.close()
    conn.close()
    
    # Feature engineering
    df['workload_ratio'] = df['training_load_hours'] / (df['prev_load'].fillna(df['training_load_hours']) + 0.1)
    df['workload_ratio'] = df['workload_ratio'].clip(0.5, 2.0)
    
    # Fill NaNs
    df.fillna(df.mean(), inplace=True)
    
    # Drop unnecessary columns
    df = df[['player_id', 'player_name', 'position', 'training_load_hours', 'workload_ratio', 
             'intensity_avg', 'recovery_score', 'fatigue_level', 'avg_load_4week', 'injury_occurred']]
    
    print(f"Extracted {len(df)} feature records")
    print(f"Injury rate: {df['injury_occurred'].mean()*100:.1f}%")
    
    df.to_csv('data/features_for_ml.csv', index=False)
    return df

if __name__ == "__main__":
    extract_features()
    print("✓ Features exported to data/features_for_ml.csv")