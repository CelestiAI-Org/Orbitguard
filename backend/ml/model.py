import torch
import torch.nn as nn
from typing import Tuple

class CollisionRiskSkipLSTM(nn.Module):
    """
    LSTM Model with Residual Skip Connection.
    Prediction = LSTM_Output(Trend) + Latest_Input_PC
    """
    def __init__(self, input_size: int = 3, hidden_size: int = 64, num_layers: int = 2, output_size: int = 1):
        super(CollisionRiskSkipLSTM, self).__init__()
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        
        # LSTM Layer
        self.lstm = nn.LSTM(input_size, hidden_size, num_layers, batch_first=True, dropout=0.2)
        
        # Fully Connected Layer to predict the DELTA (Change in Risk)
        self.fc = nn.Linear(hidden_size, output_size)
        
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # x shape: (batch, seq_len, 3) where index 0 is PC
        
        # Initialize hidden state
        h0 = torch.zeros(self.num_layers, x.size(0), self.hidden_size).to(x.device)
        c0 = torch.zeros(self.num_layers, x.size(0), self.hidden_size).to(x.device)
        
        # LSTM Forward
        out, _ = self.lstm(x, (h0, c0))
        
        # Predicted Delta from hidden state
        delta = self.fc(out[:, -1, :])
        
        # Latest known Probability (Skip Connection)
        # x[:, -1, 0] gets the last timestep, first feature (PC)
        latest_pc = x[:, -1, 0].unsqueeze(1) 
        
        # Final Prediction = Last_Known + Predicted_Change
        return latest_pc + delta
