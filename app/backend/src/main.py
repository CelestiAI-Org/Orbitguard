import argparse
import logging
import yaml
import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
import pandas as pd
from pathlib import Path

from src.pipeline.datasource import JsonFileDataSource
from src.pipeline.preprocessor import TimeSeriesPreprocessor
from src.model.lstm_model import CollisionRiskLSTM, CollisionRiskSkipLSTM, CertaintyEstimator
from src.pipeline.visualizer import RiskVisualizer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("../logs/app.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def load_config(config_path: str):
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)

def train(config):
    logger.info("Starting training pipeline...")
    
    # 1. Load Data
    data_path = config['data']['json_path']
    source = JsonFileDataSource(data_path)
    raw_data = source.fetch_data()
    logger.info(f"Loaded {len(raw_data)} records.")
    
    # 2. Preprocess
    seq_len = config['model']['sequence_length']
    preprocessor = TimeSeriesPreprocessor(sequence_length=seq_len)
    sequences, targets, _, _ = preprocessor.process(raw_data)
    
    if len(sequences) == 0:
        logger.error("No sequences generated. Exiting.")
        return

    # Convert to Tensor
    X = torch.tensor(np.array(sequences), dtype=torch.float32)
    y = torch.tensor(np.array(targets), dtype=torch.float32).view(-1, 1)
    
    # Split Train/Val (Simple 80/20)
    split_idx = int(len(X) * 0.8)
    X_train, X_val = X[:split_idx], X[split_idx:]
    y_train, y_val = y[:split_idx], y[split_idx:]
    
    # 3. Model Setup
    model_type = config['model'].get('type', 'LSTM')
    logger.info(f"Initializing model: {model_type}")
    
    if model_type == 'LSTM_SKIP':
        model = CollisionRiskSkipLSTM(
            input_size=3,
            hidden_size=config['model']['hidden_size'],
            num_layers=config['model']['num_layers']
        )
    else:
        model = CollisionRiskLSTM(
            input_size=3, # PC, MinRng, TimeToTCA
            hidden_size=config['model']['hidden_size'],
            num_layers=config['model']['num_layers']
        )
    
    criterion = nn.MSELoss()
    optimizer = optim.Adam(model.parameters(), lr=config['training']['learning_rate'])
    
    # 4. Training Loop
    epochs = config['training']['epochs']
    logger.info(f"Training for {epochs} epochs...")
    
    for epoch in range(epochs):
        model.train()
        optimizer.zero_grad()
        
        outputs = model(X_train)
        loss = criterion(outputs, y_train)
        
        loss.backward()
        optimizer.step()
        
        if (epoch + 1) % 10 == 0:
            model.eval()
            with torch.no_grad():
                val_out = model(X_val)
                val_loss = criterion(val_out, y_val)
            logger.info(f"Epoch [{epoch+1}/{epochs}], Train Loss: {loss.item():.6f}, Val Loss: {val_loss.item():.6f}")
    
    # 5. Save Model
    model_path = config['output']['model_path']
    torch.save(model.state_dict(), model_path)
    logger.info(f"Model saved to {model_path}")

def inference(config, no_plots=False):
    logger.info("Starting inference pipeline...")
    
    # 1. Load Data (same for now, assuming inference on full file)
    data_path = config['data']['json_path']
    source = JsonFileDataSource(data_path)
    raw_data = source.fetch_data()
    
    # 2. Preprocess
    seq_len = config['model']['sequence_length']
    preprocessor = TimeSeriesPreprocessor(sequence_length=seq_len)
    sequences, _, meta_list, histories = preprocessor.process(raw_data)
    
    X = torch.tensor(np.array(sequences), dtype=torch.float32)
    
    # 3. Load Model
    model_type = config['model'].get('type', 'LSTM')
    logger.info(f"Loading model architecture: {model_type}")
    
    if model_type == 'LSTM_SKIP':
        model = CollisionRiskSkipLSTM(
            input_size=3,
            hidden_size=config['model']['hidden_size'],
            num_layers=config['model']['num_layers']
        )
    else:
        model = CollisionRiskLSTM(
            input_size=3,
            hidden_size=config['model']['hidden_size'],
            num_layers=config['model']['num_layers']
        )
    model.load_state_dict(torch.load(config['output']['model_path']))
    model.eval()
    
    # 4. Predict
    logger.info("Predicting...")
    with torch.no_grad():
        predictions = model(X)
        
    # 5. Certainty Estimation
    logger.info("Estimating Certainty...")
    certainties = []
    for i in range(len(X)):
        if X[i:i+1].nelement() > 0:
            cert = CertaintyEstimator.calculate_uncertainty(model, X[i:i+1])
        else:
            cert = 0.0
        certainties.append(cert)
        
    # 6. Calculate Actionable Insights
    logger.info("Calculating Actionable Insights...")
    results = []
    
    # Load thresholds
    high_risk_thresh = config['thresholds']['high_risk']
    med_risk_thresh = config['thresholds']['medium_risk']
    reaction_time = config['thresholds']['reaction_time_hours']
    critical_dist = config['thresholds']['miss_distance_critical']
    
    # Current time simulation - No longer needed as we use per-event LATEST_CREATED
    # all_creation_dates = [] ...
    
    # Initialize Visualizer
    visualizer = RiskVisualizer(output_dir=config['output']['plots_dir'])
    
    for i in range(len(predictions)):
        pred_pc = predictions[i].item()
        meta = meta_list[i]
        
        # A. Traffic Light Status
        miss_dist = meta['LATEST_MIN_RNG']
        status = "GREEN"
        
        if pred_pc >= high_risk_thresh:
            status = "RED"
        elif miss_dist is not None and miss_dist < critical_dist:
             status = "RED" 
        elif pred_pc >= med_risk_thresh:
            status = "YELLOW"
            
        # B. Time of Last Opportunity (TLO)
        tca = meta['TCA']
        latest_msg_time = meta['LATEST_CREATED']
        tlo = tca - pd.Timedelta(hours=reaction_time)
        
        # Calculate time remaining relative to when the message was received
        # Positive = You have time capability. Negative = Too late.
        hours_remaining = (tlo - latest_msg_time).total_seconds() / 3600.0
        
        # C. Risk Trend
        hist = histories[i]
        trend = "STABLE"
        if len(hist) >= 1:
            curr_pc_raw = hist['PC'].iloc[-1]
            delta = pred_pc - curr_pc_raw
            if delta > (curr_pc_raw * 0.1): 
                trend = "INCREASING"
            elif delta < -(curr_pc_raw * 0.1):
                trend = "DECREASING"

        # D. Plotting (History of the Future)
        if status in ["RED", "YELLOW"] and not no_plots:
            # Sanitize filename
            s1 = str(meta['SAT_1_ID']).replace(" ", "")
            s2 = str(meta['SAT_2_ID']).replace(" ", "")
            fname = f"trend_event_{s1}_{s2}_{tca.date()}.png"
            
            thresholds_dict = {
                'high_risk': high_risk_thresh,
                'medium_risk': med_risk_thresh
            }
            
            visualizer.plot_risk_trend(
                history_df=hist,
                predicted_pc=pred_pc,
                tca=tca,
                thresholds=thresholds_dict,
                filename=fname,
                certainty=certainties[i]
            )
                
        results.append({
            "SAT_1": meta['SAT_1_ID'],
            "SAT_2": meta['SAT_2_ID'],
            "TCA": meta['TCA'],
            "Predicted_PC": pred_pc,
            "Latest_Reported_PC": meta['LATEST_PC'],
            "Certainty": certainties[i],
            "Risk_Status": status,
            "Hours_To_Decision": round(hours_remaining, 2),
            "Risk_Trend": trend
        })
        
    # Save results
    res_df = pd.DataFrame(results)
    res_path = Path(__file__).parent.parent / "results" / "predictions_dashboard.csv"
    res_df.to_csv(res_path, index=False)
    logger.info(f"Dashboard Data saved to {res_path}")
    print(res_df.head(10))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Collision Risk AI - LSTM")
    parser.add_argument("--mode", type=str, required=True, choices=["train", "inference"], help="Mode: train or inference")
    parser.add_argument("--config", type=str, default="config.yaml", help="Path to config file")
    parser.add_argument("--no-plots", action="store_true", help="Disable plot generation during inference")
    
    args = parser.parse_args()
    config = load_config(args.config)
    
    if args.mode == "train":
        train(config)
    elif args.mode == "inference":
        inference(config, no_plots=args.no_plots)
