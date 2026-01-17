import { ConjunctionEvent } from "../types";
import { API_BASE_URL } from "../constants";

export const fetchCDMUpdates = async (): Promise<ConjunctionEvent[]> => {
  try {
    // Expecting backend to return a list of ConjunctionEvents
    const response = await fetch(`${API_BASE_URL}/cdms`);
    
    if (!response.ok) {
      throw new Error(`Backend API Error: ${response.status} ${response.statusText}`);
    }

    const data = await response.json();
    return data;
  } catch (error) {
    console.error("Failed to fetch CDMs from backend:", error);
    // Propagate error to let UI handle "Offline" state
    throw error;
  }
};

// Optional: Health check endpoint if backend provides it
export const checkSystemHealth = async () => {
    try {
        const response = await fetch(`${API_BASE_URL}/health`); 
        return response.ok ? 'ONLINE' : 'DEGRADED';
    } catch {
        return 'OFFLINE';
    }
};
