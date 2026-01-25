import { Satellite, CDMEvent } from "../types";
import { API_BASE_URL } from "../constants";

export const fetchSatellites = async (): Promise<Satellite[]> => {
  try {
    const response = await fetch(`${API_BASE_URL}/init`);
    
    if (!response.ok) {
      throw new Error(`Backend API Error: ${response.status} ${response.statusText}`);
    }

    const data = await response.json();
    return data;
  } catch (error) {
    console.error("Failed to fetch satellites from backend:", error);
    throw error;
  }
};

export const fetchCDMsForSatellite = async (satId: string): Promise<CDMEvent[]> => {
  try {
    const response = await fetch(`${API_BASE_URL}/cdms?sat_id=${satId}`);
    
    if (!response.ok) {
      throw new Error(`Backend API Error: ${response.status} ${response.statusText}`);
    }

    const data = await response.json();
    return data;
  } catch (error) {
    console.error(`Failed to fetch CDMs for satellite ${satId}:`, error);
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
