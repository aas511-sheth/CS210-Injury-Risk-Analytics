-- Drop existing tables if rerunning
DROP TABLE IF EXISTS injury_predictions CASCADE;
DROP TABLE IF EXISTS injuries CASCADE;
DROP TABLE IF EXISTS training_metrics CASCADE;
DROP TABLE IF EXISTS game_stats CASCADE;
DROP TABLE IF EXISTS players CASCADE;

-- Table 1: Players
CREATE TABLE players (
    player_id SERIAL PRIMARY KEY,
    player_name VARCHAR(100) NOT NULL,
    position VARCHAR(20) NOT NULL,  -- PG, SG, SF, PF, C
    team VARCHAR(50) NOT NULL,
    height_cm DECIMAL(5,2),
    weight_kg DECIMAL(5,2),
    age INT,
    draft_year INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table 2: Game Statistics
CREATE TABLE game_stats (
    game_id SERIAL PRIMARY KEY,
    player_id INT NOT NULL REFERENCES players(player_id),
    game_date DATE NOT NULL,
    minutes_played INT,
    points INT,
    rebounds INT,
    assists INT,
    field_goal_percentage DECIMAL(5,2),
    three_point_percentage DECIMAL(5,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table 3: Training Metrics (Wearable sensor data)
CREATE TABLE training_metrics (
    metric_id SERIAL PRIMARY KEY,
    player_id INT NOT NULL REFERENCES players(player_id),
    training_date DATE NOT NULL,
    training_load_hours DECIMAL(5,2),  -- Hours of intense training
    heart_rate_avg INT,
    heart_rate_max INT,
    hrv_score DECIMAL(6,2),  -- Heart rate variability
    fatigue_level INT,  -- 1-10 scale
    recovery_score INT,  -- 1-100 scale
    sleep_hours DECIMAL(4,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table 4: Injuries
CREATE TABLE injuries (
    injury_id SERIAL PRIMARY KEY,
    player_id INT NOT NULL REFERENCES players(player_id),
    injury_date DATE NOT NULL,
    injury_type VARCHAR(100),  -- ACL tear, ankle sprain, etc.
    severity VARCHAR(20),  -- Minor, Moderate, Severe
    games_missed INT,
    return_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table 5: Injury Predictions (Model output)
CREATE TABLE injury_predictions (
    prediction_id SERIAL PRIMARY KEY,
    player_id INT NOT NULL REFERENCES players(player_id),
    prediction_date DATE NOT NULL,
    risk_score DECIMAL(5,4),  -- 0.0 to 1.0
    risk_category VARCHAR(20),  -- Low, Medium, High
    predicted_probability DECIMAL(5,4),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create Indexes for Performance
CREATE INDEX idx_players_position ON players(position);
CREATE INDEX idx_players_team ON players(team);
CREATE INDEX idx_game_stats_player ON game_stats(player_id);
CREATE INDEX idx_game_stats_date ON game_stats(game_date);
CREATE INDEX idx_training_metrics_player ON training_metrics(player_id);
CREATE INDEX idx_training_metrics_date ON training_metrics(training_date);
CREATE INDEX idx_injuries_player ON injuries(player_id);
CREATE INDEX idx_injuries_date ON injuries(injury_date);
CREATE INDEX idx_predictions_player ON injury_predictions(player_id);
CREATE INDEX idx_predictions_date ON injury_predictions(prediction_date);

-- Verify schema
SELECT 'Players' AS table_name, COUNT(*) AS row_count FROM players
UNION ALL
SELECT 'Game Stats', COUNT(*) FROM game_stats
UNION ALL
SELECT 'Training Metrics', COUNT(*) FROM training_metrics
UNION ALL
SELECT 'Injuries', COUNT(*) FROM injuries
UNION ALL
SELECT 'Predictions', COUNT(*) FROM injury_predictions;
