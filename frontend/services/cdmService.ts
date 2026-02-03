
import { API_BASE_URL } from '../constants';
import { RawSatellite, Satellite, ConjunctionEventData } from '../types';

export const fetchSatellites = async (): Promise<Satellite[]> => {
  try {
    const response = await fetch(`${API_BASE_URL}/init`);
    if (!response.ok) throw new Error('Failed to fetch satellites');
    const data: RawSatellite[] = await response.json();
    
    return data.map((sat) => ({
      id: String(sat.ID),
      name: sat.NAME,
      type: sat.OBJ_TYP,
      rcs: sat.RCS,
      excl_vol: sat.EXCL_VOL,
      sat2_count: sat.SAT2_OBJ_COUNT || 0,
      total_cdms: sat.TOTAL_CDMS || 0
    }));
  } catch (err) {
    console.error('fetchSatellites error:', err);
    throw err;
  }
};

export const fetchCDMsForSatellite = async (satId: string): Promise<ConjunctionEventData[]> => {
  try {
    const response = await fetch(`${API_BASE_URL}/cdms?sat_id=${satId}`);
    if (!response.ok) throw new Error('Failed to fetch CDMs');
    return await response.json();
  } catch (err) {
    console.error('fetchCDMsForSatellite error:', err);
    throw err;
  }
};

export const checkSystemHealth = async (): Promise<'ONLINE' | 'DEGRADED' | 'OFFLINE'> => {
  try {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 3000);
    const response = await fetch(`${API_BASE_URL}/health`, { signal: controller.signal });
    clearTimeout(timeoutId);
    return response.ok ? 'ONLINE' : 'DEGRADED';
  } catch {
    return 'OFFLINE';
  }
};
