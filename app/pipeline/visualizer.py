import matplotlib.pyplot as plt
import pandas as pd
import logging
from pathlib import Path
from typing import Dict, Optional

class RiskVisualizer:
    """
    Visualizes the evolution of collision risk (History of the Future).
    """
    def __init__(self, output_dir: str = "plots"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.logger = logging.getLogger(__name__)

    def plot_risk_trend(self, 
                        history_df: pd.DataFrame, 
                        predicted_pc: float, 
                        tca: pd.Timestamp,
                        thresholds: Dict[str, float], 
                        filename: str):
        """
        Generates and saves a plot of PC evolution vs Time.
        
        Args:
            history_df: DataFrame containing 'CREATED' and 'PC' columns.
            predicted_pc: The model's predicted PC.
            tca: Time of Closest Approach (for context).
            thresholds: Dict containing 'high_risk', 'medium_risk'.
            filename: Name of the file to save (e.g., 'event_123.png').
        """
        try:
            plt.figure(figsize=(10, 6))
            
            # 1. Plot History
            # Sort by time just in case
            hist = history_df.sort_values('CREATED')
            plt.plot(hist['CREATED'], hist['PC'], marker='o', linestyle='-', label='Reported History')
            
            # 2. Plot Prediction
            # Handle log scale for 0 probability
            plot_val = predicted_pc if predicted_pc > 1e-30 else 1e-30
            
            # We plot the prediction at the "current simulated time" (which is effectively the last history point or slightly after)
            last_time = hist['CREATED'].max()
            plt.plot(last_time, plot_val, marker='*', markersize=15, color='purple', label='AI Prediction', linestyle='None')
            
            # 3. Thresholds
            plt.axhline(y=thresholds['high_risk'], color='red', linestyle='--', label='High Risk Threshold')
            plt.axhline(y=thresholds['medium_risk'], color='orange', linestyle='--', label='Medium Risk Threshold')
            
            # 4. Formatting
            plt.yscale('log') # Probability is usually log-scale
            
            # Ensure y-limits show the star if it's very low or high
            current_ylim = plt.ylim()
            # Check if plot_val is outside
            if plot_val < current_ylim[0]:
                plt.ylim(bottom=plot_val * 0.1)
            if plot_val > current_ylim[1]:
                plt.ylim(top=plot_val * 10)
            plt.ylabel('Collision Probability (Log Scale)')
            plt.xlabel('Report Creation Date')
            plt.title(f'Risk Trend (TCA: {tca})')
            plt.grid(True, which="both", ls="-", alpha=0.5)
            plt.legend()
            
            # Save
            save_path = self.output_dir / filename
            plt.savefig(save_path)
            plt.close()
            self.logger.info(f"Saved risk trend plot to {save_path}")
            
        except Exception as e:
            self.logger.error(f"Failed to plot risk trend: {e}")
            plt.close()
