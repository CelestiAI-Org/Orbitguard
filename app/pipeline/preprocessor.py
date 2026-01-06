from typing import List, Dict, Any, Tuple, Optional
import pandas as pd
import numpy as np
from datetime import datetime
import logging

class TimeSeriesPreprocessor:
    """
    Preprocesses CDM data into time-series sequences for LSTM.
    Groups by (SAT_1_ID, SAT_2_ID, TCA).
    """
    
    def __init__(self, sequence_length: int = 10, log_level: str = "INFO"):
        self.sequence_length = sequence_length
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(log_level)
    
    def process(self, raw_data: List[Dict[str, Any]]) -> Tuple[List[np.ndarray], List[float], List[Dict[str, Any]], List[pd.DataFrame]]:
        """
        Convert raw CDM dictionaries into LSTM-ready sequences.
        
        Args:
            raw_data: List of CDM dictionaries.
            
        Returns:
            X: List of sequences (numpy arrays of shape [seq_len, num_features])
            y: List of target values (e.g., final probability or risk)
            meta: List of metadata dicts for each event (TCA, SAT_IDs)
            histories: List of DataFrames containing the full history for each event (for trend analysis)
        """
        df = pd.DataFrame(raw_data)
        
        # 1. Clean and Parse Columns
        df = self._clean_dataframe(df)
        
        # 2. Group by Event (Pair + TCA)
        # We round TCA to nearest minute/hour to group updates referring to the same event
        # strict equality might fail if TCA shifts slightly in updates.
        # For now, we'll try exact string match or round to minute.
        df['TCA_GROUP'] = pd.to_datetime(df['TCA']).dt.floor('min') 
        
        grouped = df.groupby(['SAT_1_ID', 'SAT_2_ID', 'TCA_GROUP'])
        
        sequences = []
        targets = []
        meta_list = []
        history_list = []
        
        for name, group in grouped:
            # 3. Sort by creation time (evolution of the event)
            group = group.sort_values('CREATED')
            
            # 4. Extract Features
            # Features: PC (Prob), MIN_RNG (Range), Time_to_TCA_hours
            features = self._extract_features(group)
            
            # 5. Create Sequence
            # If sequence is shorter than required, pad it.
            # If longer, take the latest `sequence_length` updates.
            seq_array = self._pad_or_truncate_sequence(features)
            
            sequences.append(seq_array)
            
            # Target: The latest Risk (Prob)
            latest_pc = group['PC'].iloc[-1]
            targets.append(latest_pc)

            # Metadata for dashboard
            sat1_id, sat2_id, tca_time = name
            meta_list.append({
                'SAT_1_ID': sat1_id,
                'SAT_2_ID': sat2_id,
                'TCA': tca_time,
                'LATEST_MIN_RNG': group['MIN_RNG'].iloc[-1] if 'MIN_RNG' in group else None,
                'LATEST_PC': latest_pc,
                'LATEST_CREATED': group['CREATED'].iloc[-1]
            })
            
            # Keep history for trend calculations
            history_list.append(group[['CREATED', 'PC', 'MIN_RNG']].copy())
            
        return sequences, targets, meta_list, history_list

    def _clean_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """Parse dates and handle missing values."""
        # Convert numeric columns
        numeric_cols = ['PC', 'MIN_RNG', 'SAT1_ID', 'SAT2_ID']
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # Fill missing PC with 0 (assuming missing often means low risk/undefined)
        # BUT check 'MIN_RNG', if it's very low, missing PC might be alarming.
        # For this hackathon dataset, let's assume fillna(0) for PC.
        if 'PC' in df.columns:
            df['PC'] = df['PC'].fillna(0.0)
            
        # Parse Dates
        df['CREATED'] = pd.to_datetime(df['CREATED'])
        df['TCA'] = pd.to_datetime(df['TCA'])
        
        return df

    def _extract_features(self, group: pd.DataFrame) -> np.ndarray:
        """
        Extract numerical features from a sorted group of CDMs.
        Features:
        0. PC (Probability)
        1. MIN_RNG (Miss Distance)
        2. Time_to_TCA (Hours)
        
        Future: Add RCS encoding, specific covariance fields.
        """
        # Calculate time difference
        # Time_to_TCA = TCA - CREATED
        time_to_tca = (group['TCA'] - group['CREATED']).dt.total_seconds() / 3600.0
        
        # Normalization (Simple min-max or log scaling would be better in production)
        # Here we just pass raw for now, or simple scaling.
        pc = group['PC'].values
        min_rng = group['MIN_RNG'].values
        # Replace NaNs in min_rng if any (unlikely if prefiltered)
        min_rng = np.nan_to_num(min_rng, nan=100000.0)
        
        # Log scale Min Range to compress dynamic range
        min_rng_log = np.log1p(min_rng)
        
        features = np.column_stack((pc, min_rng_log, time_to_tca.values))
        return features

    def _pad_or_truncate_sequence(self, features: np.ndarray) -> np.ndarray:
        """Pad with zeros (pre-padding) or truncate to fixed length."""
        curr_len = len(features)
        num_features = features.shape[1]
        
        if curr_len >= self.sequence_length:
            return features[-self.sequence_length:]
        else:
            # Pad with zeros at the beginning
            padding = np.zeros((self.sequence_length - curr_len, num_features))
            return np.vstack((padding, features))
