import psycopg2
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from config import DB_CONFIG

def create_tables():
    """Create all 5 tables"""
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    
    # Drop existing tables (for clean reset)
    cur.execute("DROP TABLE IF EXISTS injury_predictions CASCADE")
    cur.execute("DROP TABLE IF EXISTS injury_history CASCADE")
    cur.execute("DROP TABLE IF EXISTS training_metrics CASCADE")
    cur.execute("DROP TABLE IF EXISTS game_stats CASCADE")
    cur.execute("DROP TABLE IF EXISTS players CASCADE")
    
    # Players table
    cur.execute("""
        CREATE TABLE players (
            player_id SERIAL PRIMARY KEY,
            player_name VARCHAR(100) NOT NULL,
            team VARCHAR(50),
            position VARCHAR(10),
            height_cm DECIMAL(5,2),
            weight_kg DECIMAL(6,2),
            age INT
        )
    """)
    
    # Game Statistics
    cur.execute("""
        CREATE TABLE game_stats (
            stat_id SERIAL PRIMARY KEY,
            player_id INT REFERENCES players(player_id),
            game_date DATE NOT NULL,
            minutes_played DECIMAL(4,2),
            field_goals_attempted INT,
            field_goals_made INT,
            rebounds INT,
            assists INT
        )
    """)
    
    # Training Metrics
    cur.execute("""
        CREATE TABLE training_metrics (
            metric_id SERIAL PRIMARY KEY,
            player_id INT REFERENCES players(player_id),
            week_start_date DATE NOT NULL,
            training_load_hours DECIMAL(5,2),
            intensity_avg DECIMAL(3,2),
            sessions_count INT,
            recovery_score DECIMAL(3,2),
            fatigue_level DECIMAL(3,2)
        )
    """)
    
    # Injury History
    cur.execute("""
        CREATE TABLE injury_history (
            injury_id SERIAL PRIMARY KEY,
            player_id INT REFERENCES players(player_id),
            injury_date DATE NOT NULL,
            injury_type VARCHAR(100),
            severity VARCHAR(20),
            recovery_days INT,
            reinjury_risk DECIMAL(3,2)
        )
    """)
    
    # Injury Predictions
    cur.execute("""
        CREATE TABLE injury_predictions (
            prediction_id SERIAL PRIMARY KEY,
            player_id INT REFERENCES players(player_id),
            prediction_date DATE NOT NULL,
            risk_score DECIMAL(5,4),
            risk_category VARCHAR(20),
            model_version VARCHAR(10)
        )
    """)
    
    # Create indexes
    cur.execute("CREATE INDEX idx_game_stats_date ON game_stats(player_id, game_date)")
    cur.execute("CREATE INDEX idx_training_metrics_date ON training_metrics(player_id, week_start_date)")
    cur.execute("CREATE INDEX idx_injury_history_date ON injury_history(player_id, injury_date)")
    cur.execute("CREATE INDEX idx_predictions_date ON injury_predictions(player_id, prediction_date)")
    
    conn.commit()
    cur.close()
    conn.close()
    print("✓ Tables created")

def load_players():
    """Load 20 NBA players"""
    players = [
        ('LeBron James', 'Lakers', 'SF', 203.2, 113.4, 40),
        ('Luka Doncic', 'Lakers', 'SG', 200.7, 103.9, 25),
        ('Giannis Antetokounmpo', 'Bucks', 'PF', 211.4, 109.8, 30),
        ('Kevin Durant', 'Rockets', 'SF', 208.3, 107.3, 36),
        ('Jayson Tatum', 'Celtics', 'SF', 203.2, 104.3, 26),
        ('Damian Lillard', 'Trail Blazers', 'PG', 190.5, 100.2, 34),
        ('Stephen Curry', 'Warriors', 'PG', 188.0, 86.2, 36),
        ('Devin Booker', 'Suns', 'SG', 198.1, 97.5, 28),
        ('Trae Young', 'Hawks', 'PG', 185.4, 85.7, 26),
        ('Shai Gilgeous-Alexander', 'Thunder', 'SG', 198.1, 88.5, 26),
        ('Tyrese Haliburton', 'Pacers', 'PG', 193.0, 79.4, 24),
        ('Paolo Banchero', 'Magic', 'SF', 203.2, 102.1, 22),
        ('Donovan Mitchell', 'Cavaliers', 'SG', 198.1, 97.5, 28),
        ('Kawhi Leonard', 'Clippers', 'SF', 201.9, 101.6, 33),
        ('Nikola Jokic', 'Nuggets', 'C', 211.4, 129.3, 29),
        ('Karl-Anthony Towns', 'Knicks', 'C', 212.1, 103.9, 29),
        ('Anthony Davis', 'Mavericks', 'PF', 208.3, 115.7, 31),
        ('Jimmy Butler', 'Warriors', 'SF', 201.9, 103.9, 35),
        ('Kyrie Irving', 'Mavericks', 'PG', 188.0, 88.5, 32),
        ('Zion Williamson', 'Pelicans', 'PF', 198.1, 129.3, 24),
    ]
    
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    
    for name, team, pos, height, weight, age in players:
        cur.execute(
            "INSERT INTO players (player_name, team, position, height_cm, weight_kg, age) "
            "VALUES (%s, %s, %s, %s, %s, %s)",
            (name, team, pos, height, weight, age)
        )
    
    conn.commit()
    cur.close()
    conn.close()
    print(f"✓ Loaded {len(players)} players")

def load_training_metrics():
    """Generate 52 weeks of training data for 20 players"""
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    
    base_date = datetime(2024, 1, 1)
    count = 0
    
    for player_id in range(1, 21):
        for week in range(52):
            week_date = base_date + timedelta(weeks=week)
            
            training_load = np.random.normal(10, 2)
            intensity = np.random.uniform(0.6, 0.95)
            sessions = np.random.randint(4, 7)
            recovery = np.random.uniform(0.4, 0.95)
            fatigue = np.random.uniform(0.2, 0.9)
            
            cur.execute(
                "INSERT INTO training_metrics "
                "(player_id, week_start_date, training_load_hours, intensity_avg, "
                "sessions_count, recovery_score, fatigue_level) "
                "VALUES (%s, %s, %s, %s, %s, %s, %s)",
                (player_id, week_date, training_load, intensity, sessions, recovery, fatigue)
            )
            count += 1
    
    conn.commit()
    cur.close()
    conn.close()
    print(f"✓ Loaded {count} training records (52 weeks × 20 players)")

def load_injuries():
    """Create realistic injury distribution"""
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    
    base_date = datetime(2024, 1, 1)
    injury_types = ['Ankle Sprain', 'Hamstring', 'Knee', 'Shoulder', 'Lower Back', 'Wrist', 'Calf']
    count = 0
    
    for player_id in range(1, 21):
        for week in range(52):
            if np.random.random() < 0.18:  # 18% injury rate
                injury_date = base_date + timedelta(weeks=week)
                injury_type = np.random.choice(injury_types)
                severity = np.random.choice(['Minor', 'Moderate', 'Severe'])
                recovery_days = np.random.randint(3, 30)
                
                cur.execute(
                    "INSERT INTO injury_history "
                    "(player_id, injury_date, injury_type, severity, recovery_days, reinjury_risk) "
                    "VALUES (%s, %s, %s, %s, %s, %s)",
                    (player_id, injury_date, injury_type, severity, recovery_days, np.random.uniform(0.1, 0.8))
                )
                count += 1
    
    conn.commit()
    cur.close()
    conn.close()
    print(f"✓ Loaded {count} injury records")

if __name__ == "__main__":
    print("Loading data...")
    create_tables()
    load_players()
    load_training_metrics()
    load_injuries()
    print("\n✅ DATABASE READY!")