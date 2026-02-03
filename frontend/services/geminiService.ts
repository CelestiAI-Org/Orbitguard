
import { API_BASE_URL } from '../constants';

export const generateRiskAssessment = async (satId: string): Promise<string> => {
  try {
    // TODO: Needs to get all cdms for the satellite within the event window and summarize risk levels
    const response = await fetch(`${API_BASE_URL}/risk-summary?sat_id=${satId}`);
    if (!response.ok) throw new Error('Risk assessment service unavailable');
    const data = await response.json();
    return data.summary || data.text || "Assessment data unavailable for this event window.";
  } catch (error) {
    console.error('Risk assessment error:', error);
    return "Intelligence Subsystem Offline. Direct operator interpretation required.";
  }
};
