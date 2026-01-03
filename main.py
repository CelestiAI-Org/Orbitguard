import argparse
import logging
import yaml
import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
from pathlib import Path

from app.pipeline.datasource import JsonFileDataSource
from app.pipeline.preprocessor import TimeSeriesPreprocessor
from app.model.lstm_model import CollisionRiskLSTM, CertaintyEstimator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("logs/app.log"),
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
    sequences, targets = preprocessor.process(raw_data)
    
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

def inference(config):
    logger.info("Starting inference pipeline...")
    
    # 1. Load Data (same for now, assuming inference on full file)
    data_path = config['data']['json_path']
    source = JsonFileDataSource(data_path)
    raw_data = source.fetch_data()
    
    # 2. Preprocess
    seq_len = config['model']['sequence_length']
    preprocessor = TimeSeriesPreprocessor(sequence_length=seq_len)
    sequences, _ = preprocessor.process(raw_data)
    
    X = torch.tensor(np.array(sequences), dtype=torch.float32)
    
    # 3. Load Model
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
        cert = CertaintyEstimator.calculate_uncertainty(model, X[i:i+1])
        certainties.append(cert)
        
    # Output results
    results = []
    for i in range(len(predictions)):
        results.append({
            "Predicted_PC": predictions[i].item(),
            "Certainty": certainties[i]
        })
        
    # Save results (simple CSV print)
    import pandas as pd
    res_df = pd.DataFrame(results)
    res_path = "results/predictions_lstm.csv"
    res_df.to_csv(res_path, index=False)
    logger.info(f"Predictions saved to {res_path}")
    print(res_df.head())

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Collision Risk AI - LSTM")
    parser.add_argument("--mode", type=str, required=True, choices=["train", "inference"], help="Mode: train or inference")
    parser.add_argument("--config", type=str, default="config.yaml", help="Path to config file")
    
    args = parser.parse_args()
    config = load_config(args.config)
    
    if args.mode == "train":
        train(config)
    elif args.mode == "inference":
        inference(config)
