import torch
import os
import logging
from typing import List, Dict, Any
from .preprocessor import TimeSeriesPreprocessor
from .model import CollisionRiskSkipLSTM

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MLRunner:
    def __init__(self, model_path: str = "models/lstm_skip_v1.pth"):
        self.device = torch.device("cpu") # Force CPU for backend compatibility
        self.preprocessor = TimeSeriesPreprocessor(sequence_length=5)
        
        # Initialize Model (Skip LSTM)
        # Config: input=3, hidden=64, layers=2
        self.model = CollisionRiskSkipLSTM(
            input_size=3,
            hidden_size=64,
            num_layers=2,
            output_size=1
        ).to(self.device)
        
        # Load Weights
        abs_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), model_path)
        if os.path.exists(abs_path):
            try:
                state_dict = torch.load(abs_path, map_location=self.device)
                self.model.load_state_dict(state_dict)
                self.model.eval()
                logger.info(f"ML Model loaded successfully from {abs_path}")
                self.ready = True
            except Exception as e:
                logger.error(f"Failed to load ML model: {e}")
                self.ready = False
        else:
            logger.warning(f"ML Model not found at {abs_path}. Predictions will be skipped.")
            self.ready = False
            
    def predict(self, raw_data: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
        """
        Runs the full ML pipeline on raw CDM data.
        Returns a dictionary mapping Event KEY -> Prediction Result.
        """
        if not self.ready or not raw_data:
            return {}
            
        try:
            # 1. Preprocess
            sequences, targets, meta_list, _ = self.preprocessor.process(raw_data)
            
            if not sequences:
                return {}
                
            # 2. Inference
            X = torch.tensor(sequences, dtype=torch.float32).to(self.device)
            
            with torch.no_grad():
                outputs = self.model(X)
                
            predictions = outputs.squeeze(1).numpy().tolist()
            
            # 3. Format Results
            results = {}
            for i, pred_risk in enumerate(predictions):
                meta = meta_list[i]
                key = meta['KEY'] # e.g. "SAT1_SAT2_TCA"
                
                # Determine Status (Thresholds from Config/Antigravity)
                # High Risk: > 1e-4 (-4.0 log)
                # Medium Risk: > 1e-5 (-5.0 log)
                status = "GREEN"
                if pred_risk >= -4.0:
                    status = "RED"
                elif pred_risk >= -5.0:
                    status = "YELLOW"
                
                results[key] = {
                    "AI_RISK_LOG10": float(pred_risk), # It's already log scale
                    "AI_RISK_PROB": float(10**pred_risk),
                    "AI_STATUS": status,
                    "AI_CERTAINTY": 0.95 # Placeholder until MC Dropout is integrated
                }
                
            logger.info(f"Generated predictions for {len(results)} events.")
            return results
            
        except Exception as e:
            logger.error(f"Error during ML inference: {e}")
            return {}
