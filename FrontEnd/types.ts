export enum RiskLevel {
  LOW = 'LOW',
  MEDIUM = 'MEDIUM',
  HIGH = 'HIGH',
  CRITICAL = 'CRITICAL'
}

export enum Trend {
  INCREASING = 'INCREASING',
  DECREASING = 'DECREASING',
  STABLE = 'STABLE'
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