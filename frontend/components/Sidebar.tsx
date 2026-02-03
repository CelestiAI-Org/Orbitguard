
import React, { useState } from 'react';
import { 
  Search, 
  Satellite, 
  ChevronRight, 
  ChevronDown, 
  ShieldAlert, 
  Activity,
  AlertTriangle,
  CheckCircle,
  WifiOff,
  Cpu
} from 'lucide-react';
import { Satellite as SatelliteType, ConjunctionEventData } from '../types';

interface SidebarProps {
  satellites: SatelliteType[];
  selectedSatellite: SatelliteType | null;
  onSelectSatellite: (sat: SatelliteType) => void;
  isLoading: boolean;
  conjunctions: Record<string, ConjunctionEventData[]>;
  isLoadingCDMs: boolean;
  selectedEventIndex: number | null;
  onSelectEvent: (index: number) => void;
  error: boolean;
}

const Sidebar: React.FC<SidebarProps> = ({ 
  satellites, 
  selectedSatellite, 
  onSelectSatellite, 
  isLoading,
  conjunctions,
  isLoadingCDMs,
  selectedEventIndex,
  onSelectEvent,
  error
}) => {
  const [searchTerm, setSearchTerm] = useState('');

  const filteredSatellites = satellites.filter(sat => 
    sat.name.toLowerCase().includes(searchTerm.toLowerCase()) || 
    sat.id.includes(searchTerm)
  );

  return (
    <aside className="w-80 flex flex-col border-r border-slate-800 bg-slate-950 h-screen overflow-hidden">
      {/* Header */}
      <div className="p-4 border-b border-slate-800 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <div className="p-1.5 bg-cyan-950 rounded-md border border-cyan-800">
            <ShieldAlert className="w-5 h-5 text-cyan-400" />
          </div>
          <h1 className="text-sm font-bold tracking-tighter text-slate-100">ORBIT GUARD</h1>
        </div>
        <div className="flex items-center gap-1.5 px-2 py-0.5 rounded-full bg-slate-900 border border-slate-800">
          <div className={`w-1.5 h-1.5 rounded-full ${error ? 'bg-red-500 animate-pulse' : 'bg-green-500 shadow-[0_0_8px_rgba(34,197,94,0.6)]'}`} />
          <span className="text-[10px] text-slate-500 font-bold uppercase">{error ? 'OFFLINE' : 'LIVE'}</span>
        </div>
      </div>

      {/* Search */}
      <div className="p-4 bg-slate-900/30">
        <div className="relative">
          <Search className="absolute left-3 top-2.5 w-4 h-4 text-slate-500" />
          <input 
            type="text" 
            placeholder="Search payload ID/Name..."
            className="w-full bg-slate-900 border border-slate-800 rounded-md py-2 pl-9 pr-4 text-xs focus:outline-none focus:border-cyan-500 transition-colors"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
        </div>
      </div>

      {/* List */}
      <div className="flex-1 overflow-y-auto">
        {isLoading ? (
          <div className="p-6 space-y-4">
            {[1, 2, 3, 4, 5].map(i => (
              <div key={i} className="h-12 bg-slate-900/50 animate-pulse rounded" />
            ))}
          </div>
        ) : error ? (
          <div className="p-8 text-center">
            <WifiOff className="w-12 h-12 text-slate-700 mx-auto mb-4" />
            <p className="text-xs text-slate-500 uppercase font-bold">Network Connection Lost</p>
            <button 
              onClick={() => window.location.reload()}
              className="mt-4 px-4 py-2 bg-slate-800 hover:bg-slate-700 text-[10px] uppercase font-bold rounded"
            >
              Retry Connection
            </button>
          </div>
        ) : (
          <div className="divide-y divide-slate-900">
            {filteredSatellites.map(sat => {
              const isSelected = selectedSatellite?.id === sat.id;
              const satConjunctions = conjunctions[sat.id] || [];
              
              return (
                <div key={sat.id} className="group">
                  <button 
                    onClick={() => onSelectSatellite(sat)}
                    className={`w-full flex items-center p-4 hover:bg-slate-900/50 transition-colors text-left ${isSelected ? 'bg-slate-900' : ''}`}
                  >
                    <div className="flex-1">
                      <div className="flex items-center justify-between mb-1">
                        <span className="text-[10px] font-bold text-slate-500 uppercase tracking-widest">{sat.id}</span>
                        {sat.sat2_count > 0 && (
                          <span className="px-1.5 py-0.5 bg-red-950 text-red-500 border border-red-900 rounded text-[9px] font-bold">
                            {sat.sat2_count} EVENTS
                          </span>
                        )}
                      </div>
                      <h3 className={`text-xs font-bold ${isSelected ? 'text-cyan-400' : 'text-slate-300'} truncate uppercase`}>{sat.name}</h3>
                      <div className="flex items-center gap-2 mt-1 opacity-60">
                        <Activity className="w-3 h-3 text-slate-400" />
                        <span className="text-[9px] font-bold text-slate-400">{sat.type} • RCS: {sat.rcs}</span>
                      </div>
                    </div>
                    {isSelected ? <ChevronDown className="w-4 h-4 text-cyan-400 ml-2" /> : <ChevronRight className="w-4 h-4 text-slate-700 ml-2" />}
                  </button>

                  {/* Conjunction Events Sub-list */}
                  {isSelected && (
                    <div className="bg-slate-950/80 border-l border-cyan-900 ml-4 py-2 pr-2 space-y-1">
                      {isLoadingCDMs ? (
                        <div className="p-4 flex items-center gap-2 text-[10px] text-slate-600 animate-pulse">
                          <Activity className="w-3 h-3 animate-spin" /> FETCHING EVENT TELEMETRY...
                        </div>
                      ) : satConjunctions.length > 0 ? (
                        satConjunctions.map((event, idx) => {
                          const isEventSelected = selectedEventIndex === idx;
                          const statusColor = 
                            event.AI_STATUS === 'ESCALATING' ? 'text-red-500' :
                            event.AI_STATUS === 'RESOLVING' ? 'text-amber-500' :
                            event.AI_STATUS === 'STABLE' ? 'text-green-500' : 'text-slate-500';

                          return (
                            <button
                              key={idx}
                              onClick={() => onSelectEvent(idx)}
                              className={`w-full text-left p-3 rounded-r border-y border-r border-transparent hover:border-slate-800 transition-all ${isEventSelected ? 'bg-slate-900 border-slate-800' : ''}`}
                            >
                              <div className="flex items-center justify-between mb-1">
                                <span className="text-[9px] text-slate-500 uppercase font-bold truncate max-w-[120px]">vs {event.SAT_2.NAME}</span>
                                <div className={`w-1.5 h-1.5 rounded-full ${statusColor.replace('text', 'bg')} shadow-[0_0_5px_currentColor]`} />
                              </div>
                              <div className="flex items-center justify-between">
                                <span className={`text-[10px] font-bold uppercase ${statusColor}`}>{event.AI_STATUS}</span>
                                <span className="text-[9px] text-slate-400 font-mono">{(event.AI_RISK_PROB * 100).toFixed(4)}%</span>
                              </div>
                            </button>
                          );
                        })
                      ) : (
                        <div className="p-4 text-[10px] text-slate-600 uppercase italic">No current conjunction threats</div>
                      )}
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        )}
      </div>

      {/* Footer Info */}
      <div className="p-3 bg-slate-950 border-t border-slate-900 flex items-center justify-between text-[8px] text-slate-600 font-bold tracking-widest uppercase">
        <span>© ORBIT GUARD V.3.2</span>
        <div className="flex items-center gap-2">
          {/* Fix: Added missing 'Cpu' icon import from lucide-react */}
          <Cpu className="w-2.5 h-2.5" />
          <span>SYS NOMINAL</span>
        </div>
      </div>
    </aside>
  );
};

export default Sidebar;
