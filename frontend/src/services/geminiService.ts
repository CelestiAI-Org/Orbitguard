import { ConjunctionEvent } from "../types";
import { API_BASE_URL } from "../constants";

// The frontend no longer communicates with LLMs directly.
// It requests a processed summary from the Python backend.

export const generateRiskAssessment = async (event: ConjunctionEvent): Promise<string> => {
  try {
    const response = await fetch(`${API_BASE_URL}/risk-summary?cdm_id=${event.id}`);
    
    if (!response.ok) {
      console.warn("Risk summary endpoint returned error", response.status);
      return "Automated risk interpretation unavailable.";
    }

    const data = await response.json();
    // Assuming backend returns { "summary": "..." } or raw string
    return data.summary || data.text || "No analysis content returned.";
  } catch (error) {
    console.error("Failed to fetch risk assessment:", error);
    return "Analysis Subsystem Offline.";
  }
};
