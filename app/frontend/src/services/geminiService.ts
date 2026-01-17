import { ConjunctionEvent } from "../types";
import { API_BASE_URL } from "../constants";

// The frontend no longer communicates with LLMs directly.
// It requests a processed summary from the Python backend.

/**
 * Generates a risk assessment summary for a given conjunction event by querying the backend API.
 * 
 * This function expects a **JSON** response from the API endpoint. The response should contain
 * either a `summary` or `text` property with the risk assessment content.
 * 
 * @param event - The conjunction event for which to generate a risk assessment
 * @returns A promise that resolves to a string containing the risk assessment summary,
 *          or an error message if the request fails
 * 
 * @remarks
 * Expected API response format as either of the following:
 * ```json
 * {
 *   "summary": "Risk assessment text...",
 *   "text": "Alternative risk assessment text..."
 * }
 * ```
 */
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
