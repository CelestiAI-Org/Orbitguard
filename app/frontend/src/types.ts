export enum RiskLevel {
  STABLE = 'STABLE',
  RESOLVING = 'RESOLVING',
  ESCALATING = 'ESCALATING'
}

export enum Trend {
  INCREASING = 'INCREASING',
  DECREASING = 'DECREASING',
  STABLE = 'STABLE'
}

// New init.json format
export interface Satellite {
  id: string;
  name: string;
  type: string;
  rcs: string;
  excl_vol: number;
}

// Raw satellite from API
export interface RawSatellite {
  ID: number;
  NAME: string;
  OBJ_TYP: string;
  RCS: string;
  EXCL_VOL: number;
}

// Individual CDM record within an event
export interface CDMRecord {
  CDM_ID: string;
  CREATED: string;
  TCA: string;
  MIN_RNG: number;
  PC: number;
  RISK_LVL: string;
}

// Secondary satellite info
export interface SecondarySatellite {
  ID: number;
  NAME: string;
  RCS: string;
  OBJ_TYP: string;
  EXCL_VOL: string;
}

// Full conjunction event from /cdms endpoint
export interface ConjunctionEventData {
  SAT_2: SecondarySatellite;
  CDMS: CDMRecord[];
  TCA: string;
  AI_RISK_LOG10: number;
  AI_STATUS: string;
  AI_CERTAINTY: number;
  AI_RISK_PROB: number;
  MAX_PC: number;
  MIN_RANGE: number;
  MSG_COUNT: number;
}

// Legacy CDMEvent for backwards compatibility
export interface CDMEvent {
  CDM_ID: string;
  RISK_LEVEL: string;
  CREATED: string;
  TCA: string;
  MIN_RANGE_M: string;
  PC: string;
  SAT_2_ID: string;
  SAT_2_NAME: string;
  SAT2_OBJECT_TYPE: string;
  SAT2_RCS: string;
  SAT_2_EXCL_VOL: string;
}

export interface OrbitalObject {
  id: string;
  name: string;
  type: 'PAYLOAD' | 'DEBRIS' | 'ROCKET_BODY';
  rcs: string; // Radar Cross Section (e.g., LARGE, MED, SMALL)
}

export interface ProbabilityPoint {
  timestamp: string; // ISO string
  value: number; // 0-1
  source: 'OBSERVED' | 'PREDICTED';
}

export interface ConjunctionEvent {
  id: string;
  primaryObject: OrbitalObject;
  secondaryObject: OrbitalObject;
  tca: string; // Time of Closest Approach
  missDistance: number; // meters (MIN_RNG)
  collisionProb: number; // current PC
  predictedProb: number; // LSTM 72h max
  riskLevel: RiskLevel;
  trend: Trend;
  probabilityHistory: ProbabilityPoint[];
  exclusionVolume: string; // e.g. "Screening Volume: 5x5x2 km"
}

export interface DashboardStats {
  lastSync: string;
  apiStatus: 'ONLINE' | 'DEGRADED' | 'OFFLINE';
  modelStatus: 'NOMINAL' | 'RETRAINING' | 'OFFLINE';
  activeConjunctions: number;
  highRiskCount: number;
  maxProb72h: number;
}