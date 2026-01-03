import torch
import torch.nn as nn
from typing import Tuple

class CollisionRiskLSTM(nn.Module):
    """
    LSTM Model for predicting collision risk (Probability of Collision).
    
    Input: Sequence of [PC, MinRange, TimeToTCA] (Shape: Batch x Seq_Len x 3)
    Output: Predicted PC (Shape: Batch x 1)
    """
    def __init__(self, input_size: int = 3, hidden_size: int = 64, num_layers: int = 2, output_size: int = 1):
        super(CollisionRiskLSTM, self).__init__()
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        
        # LSTM Layer
        self.lstm = nn.LSTM(input_size, hidden_size, num_layers, batch_first=True, dropout=0.2)
        
        # Fully Connected Layer to map hidden state to output
        self.fc = nn.Linear(hidden_size, output_size)
        
        # Sigmoid activation for probability output (0-1)
        # However, PC is usually very small (1e-5), so Sigmoid might vanish.
        # Maybe we predict Log(PC) or just raw value if we scale target?
        # Let's stick to Sigmoid if we treat it as "Risk Score" (0-1), 
        # or Linear if we regress the PC value directly.
        # Given the "Certainty" requirement, let's use Sigmoid to bound it 
        # and maybe map PC -> [0,1] risk score separately.
        # For this implementation, I'll use Linear to predict the PC value directly (regression).
        # self.activation = nn.Sigmoid() 
        
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # Initialize hidden state with zeros
        h0 = torch.zeros(self.num_layers, x.size(0), self.hidden_size).to(x.device)
        c0 = torch.zeros(self.num_layers, x.size(0), self.hidden_size).to(x.device)
        
        # Forward propagate LSTM
        # out: tensor of shape (batch_size, seq_length, hidden_size)
        out, _ = self.lstm(x, (h0, c0))
        
        # Decode the hidden state of the last time step
        out = self.fc(out[:, -1, :])
        
        return out

class CertaintyEstimator:
    """
    Helper to estimate certainty from model predictions.
    """
    @staticmethod
    def calculate_uncertainty(model: nn.Module, x: torch.Tensor, num_samples: int = 10) -> float:
        """
        Estimate uncertainty using MC Dropout (running forward pass multiple times with dropout).
        """
        model.train() # Enable dropout
        outputs = []
        with torch.no_grad():
            for _ in range(num_samples):
                outputs.append(model(x).item())
        
        # Calculate variance or std dev
        std_dev = torch.tensor(outputs).std().item()
        
        # Certainty can be inverse of uncertainty (normalized)
        # This is a heuristic.
        certainty = 1.0 / (1.0 + std_dev * 100) # Scaling factor
        return certainty
