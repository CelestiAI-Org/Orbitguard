
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

export interface Satellite {
  id: string;
  name: string;
  type: string;
  rcs: string;
  excl_vol: number;
  sat2_count: number;
  total_cdms: number;
}

export interface RawSatellite {
  ID: number;
  NAME: string;
  OBJ_TYP: string;
  RCS: string;
  EXCL_VOL: number;
  SAT2_OBJ_COUNT: number;
  TOTAL_CDMS: number;
}

export interface CDMRecord {
  CDM_ID: string;
  CREATED: string;
  TCA: string;
  MIN_RNG: number;
  PC: number;
  RISK_LVL: string;
}

export interface SecondarySatellite {
  ID: number;
  NAME: string;
  RCS: string;
  OBJ_TYP: string;
  EXCL_VOL: string;
}

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

export interface ChartDataPoint {
  timestamp: string;
  value: number;
  range?: number;
  source: 'OBSERVED' | 'PREDICTED';
}

export interface DashboardStats {
  lastSync: string;
  apiStatus: 'ONLINE' | 'DEGRADED' | 'OFFLINE';
  modelStatus: 'NOMINAL' | 'RETRAINING' | 'OFFLINE';
  activeConjunctions: number;
  highRiskCount: number;
  maxProb72h: number;
}
