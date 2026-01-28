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
    
    def __init__(self, sequence_length: int = 5, log_level: str = "INFO"):
        self.sequence_length = sequence_length
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(log_level)
    
    def process(self, raw_data: List[Dict[str, Any]]) -> Tuple[List[np.ndarray], List[float], List[Dict[str, Any]], List[pd.DataFrame]]:
        """
        Convert raw CDM dictionaries into LSTM-ready sequences.
        """
        df = pd.DataFrame(raw_data)
        
        # 1. Clean and Parse Columns
        df = self._clean_dataframe(df)
        
        # 2. Group by Event (Pair + TCA)
        # We round TCA to nearest minute/hour to group updates referring to the same event
        df['TCA_GROUP'] = pd.to_datetime(df['TCA']).dt.floor('min') 
        
        grouped = df.groupby(['SAT_1_ID', 'SAT_2_ID', 'TCA_GROUP'])
        
        sequences = []
        targets = []
        meta_list = []
        history_list = []
        
        for name, group in grouped:
            # 3. Sort by creation time
            group = group.sort_values('CREATED')
            
            # 4. Extract Features
            features = self._extract_features(group)
            
            # 5. Create Sequence
            seq_array = self._pad_or_truncate_sequence(features)
            
            sequences.append(seq_array)
            
            # Target: The latest Risk (Prob)
            latest_pc = group['PC'].iloc[-1]
            targets.append(latest_pc)

            # Metadata
            sat1_id, sat2_id, tca_time = name
            meta_list.append({
                'SAT_1_ID': int(sat1_id),
                'SAT_2_ID': int(sat2_id),
                'TCA': tca_time.isoformat(),
                'LATEST_MIN_RNG': float(group['MIN_RNG'].iloc[-1]) if 'MIN_RNG' in group else None,
                'LATEST_PC': float(latest_pc),
                'LATEST_CREATED': group['CREATED'].iloc[-1].isoformat(),
                'KEY': f"{sat1_id}_{sat2_id}_{tca_time.isoformat()}" # Helper key to match backend
            })
            
            history_list.append(group[['CREATED', 'PC', 'MIN_RNG']].copy())
            
        return sequences, targets, meta_list, history_list

    def _clean_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        numeric_cols = ['PC', 'MIN_RNG', 'SAT_1_ID', 'SAT_2_ID'] # Fixed cols names (added underscores just in case)
        # Check actual cols in raw data: SAT_1_ID, SAT_2_ID
        
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        if 'PC' in df.columns:
            df['PC'] = df['PC'].fillna(0.0)
            
        df['CREATED'] = pd.to_datetime(df['CREATED'], format='mixed')
        df['TCA'] = pd.to_datetime(df['TCA'], format='mixed')
        
        return df

    def _extract_features(self, group: pd.DataFrame) -> np.ndarray:
        # Time_to_TCA = TCA - CREATED relative hours
        time_to_tca = (group['TCA'] - group['CREATED']).dt.total_seconds() / 3600.0
        
        # Log10(PC)
        epsilon = 1e-30
        pc = group['PC'].values
        pc_log = np.log10(np.maximum(pc, epsilon))
        
        # Log1p(Min Range)
        min_rng = group['MIN_RNG'].values
        min_rng = np.nan_to_num(min_rng, nan=100000.0)
        min_rng_log = np.log1p(min_rng)
        
        # Stack: [PC_Log, MinRng_Log, Time]
        features = np.column_stack((pc_log, min_rng_log, time_to_tca.values))
        return features

    def _pad_or_truncate_sequence(self, features: np.ndarray) -> np.ndarray:
        curr_len = len(features)
        num_features = features.shape[1]
        
        if curr_len >= self.sequence_length:
            return features[-self.sequence_length:]
        else:
            padding = np.zeros((self.sequence_length - curr_len, num_features))
            return np.vstack((padding, features))
