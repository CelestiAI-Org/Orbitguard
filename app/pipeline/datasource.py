from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
import json
import pandas as pd
from pathlib import Path

class CdmDataSource(ABC):
    """
    Abstract base class for CDM data sources.
    Defines the contract for fetching CDM data.
    """
    
    @abstractmethod
    def fetch_data(self) -> List[Dict[str, Any]]:
        """
        Fetch CDM data from the source.
        
        Returns:
            List of dictionaries, where each dictionary represents a CDM message.
        """
        pass

class JsonFileDataSource(CdmDataSource):
    """
    Data source for reading CDM data from a local JSON file.
    """
    
    def __init__(self, file_path: str):
        """
        Initialize the JSON file data source.
        
        Args:
            file_path: Path to the JSON file.
        """
        self.file_path = Path(file_path)
    
    def fetch_data(self) -> List[Dict[str, Any]]:
        """
        Read and parse the JSON file.
        
        Returns:
            List of CDM messages.
        
        Raises:
            FileNotFoundError: If the file does not exist.
            json.JSONDecodeError: If the file is not valid JSON.
        """
        if not self.file_path.exists():
            raise FileNotFoundError(f"JSON data file not found at: {self.file_path}")
            
        with open(self.file_path, 'r') as f:
            try:
                data = json.load(f)
                # The file might be a list of records or a dict with a key containing records.
                # Based on previous inspection, it looks like a list of dicts.
                if isinstance(data, list):
                    return data
                elif isinstance(data, dict):
                    # Fallback: try to find a key that holds the list
                    for key, value in data.items():
                        if isinstance(value, list):
                            return value
                    # If no list found, return the dict itself as a single item list if it looks like a record
                    return [data]
                else:
                    raise ValueError("Unexpected JSON format: Root element is not a list or dict.")
            except json.JSONDecodeError as e:
                raise ValueError(f"Failed to decode JSON file: {e}")

class SpaceTrackApiDataSource(CdmDataSource):
    """
    Placeholder for Space-Track API data source.
    """
    
    def __init__(self, credentials: Optional[Dict[str, str]] = None):
        self.credentials = credentials
        
    def fetch_data(self) -> List[Dict[str, Any]]:
        """
        Placeholder implementation. 
        In real implementation, this would authenticate and fetch data from Space-Track.org.
        """
        print("SpaceTrackApiDataSource: Fetching data from API (Placeholder)...")
        return []
