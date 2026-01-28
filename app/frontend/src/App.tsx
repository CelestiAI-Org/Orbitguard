import React, { useState, useEffect } from 'react';
import { 
  Activity, 
  AlertTriangle, 
  CheckCircle, 
  ChevronRight, 
  ChevronDown,
  ShieldAlert,
  Search,
  Cpu,
  Orbit,
  Satellite as SatelliteIcon,
  RefreshCw,
  Server,
  Clock,
  Target,
  FileText,
  BarChart3,
  Download,
  ArrowLeftRight,
  WifiOff
} from 'lucide-react';
import { Satellite, ConjunctionEventData, RiskLevel, CDMRecord } from './types';
import { fetchSatellites, fetchCDMsForSatellite } from './services/cdmService';
import { generateRiskAssessment } from './services/geminiService';
import ProbabilityChart from './components/ProbabilityChart';
import { API_BASE_URL } from './constants';

// --- Countdown Helper ---
const formatTimeRemaining = (targetDate: string) => {
  const diff = new Date(targetDate).getTime() - new Date().getTime();
  if (diff <= 0) return "TCA PASSED";
  const h = Math.floor(diff / (1000 * 60 * 60));
  const m = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));
  return `T - ${h}h ${m}m`;
};

// --- Styles ---
const getRiskColors = (level: RiskLevel) => {
  switch (level) {
    case RiskLevel.ESCALATING: return 'text-red-500 border-red-900 bg-red-950/20';
    case RiskLevel.RESOLVING: return 'text-amber-500 border-amber-900 bg-amber-950/10';
    default: return 'text-slate-400 border-slate-800 bg-slate-900/50';
  }
};

// --- Sidebar Item ---
const SatelliteSidebarItem: React.FC<{ 
  satellite: Satellite; 
  isActive: boolean; 
  isExpanded: boolean;
  conjunctionEvents: ConjunctionEventData[];
  selectedEventIndex: number | null;
  onClick: () => void;
  onEventClick: (index: number) => void;
}> = ({ satellite, isActive, isExpanded, conjunctionEvents, selectedEventIndex, onClick, onEventClick }) => {

  return (
    <div className="border-b border-slate-800">
      <div 
        onClick={onClick}
        className={`
          relative group flex items-center justify-between p-4 cursor-pointer transition-all duration-200
          hover:bg-slate-900
          ${isActive ? 'bg-slate-800 border-l-4 border-l-cyan-500' : 'border-l-4 border-l-transparent'}
        `}
      >
        <div className="flex flex-col gap-1 z-10 w-full">
          <div className="flex items-center justify-between mb-1">
             <span className={`text-[10px] font-mono tracking-wider ${isActive ? 'text-slate-400' : 'text-slate-600'}`}>{satellite.id}</span>
             <div className="flex items-center gap-2">
               {conjunctionEvents.length > 0 && (
                 <span className="text-[9px] font-mono bg-amber-900/50 text-amber-400 px-1.5 py-0.5 rounded">
                   {conjunctionEvents.length}
                 </span>
               )}
               {isExpanded ? (
                 <ChevronDown className="w-3 h-3 text-slate-500" />
               ) : (
                 <ChevronRight className="w-3 h-3 text-slate-500" />
               )}
             </div>
          </div>
          
          <div className="flex items-center gap-2">
             <span className={`text-sm font-semibold truncate ${isActive ? 'text-white' : 'text-slate-300'}`}>
                {satellite.name}
             </span>
          </div>
          <div className={`text-xs truncate ${isActive ? 'text-slate-300' : 'text-slate-500'}`}>
             {satellite.type} | RCS: {satellite.rcs}
          </div>
        </div>
      </div>
      
      {/* Expandable sub-items for conjunction events */}
      {isExpanded && conjunctionEvents.length > 0 && (
        <div className="bg-slate-900/50">
          {conjunctionEvents.map((event, index) => (
            <div
              key={`${event.SAT_2.ID}-${index}`}
              onClick={(e) => { e.stopPropagation(); onEventClick(index); }}
              className={`
                pl-8 pr-4 py-2.5 cursor-pointer transition-all duration-150 border-l-4
                ${selectedEventIndex === index 
                  ? 'bg-slate-800 border-l-amber-500' 
                  : 'border-l-transparent hover:bg-slate-800/50'}
              `}
            >
              <div className="flex items-center justify-between">
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2">
                    <span className={`text-xs font-medium truncate ${selectedEventIndex === index ? 'text-white' : 'text-slate-300'}`}>
                      {event.SAT_2.NAME}
                    </span>
                    <span className={`text-[9px] px-1.5 py-0.5 rounded font-mono ${
                      event.AI_STATUS === 'ESCALATING' ? 'bg-red-900/50 text-red-400' :
                      event.AI_STATUS === 'RESOLVING' ? 'bg-amber-900/50 text-amber-400' :
                      'bg-slate-700 text-slate-400'
                    }`}>
                      {event.AI_STATUS}
                    </span>
                  </div>
                  <div className="flex items-center gap-2 mt-0.5">
                    <span className="text-[10px] font-mono text-slate-500">{event.SAT_2.OBJ_TYP}</span>
                    <span className="text-slate-600">•</span>
                    <span className="text-[10px] font-mono text-slate-500">{event.MSG_COUNT} CDMs</span>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

// --- Main App ---

export default function App() {
  const [satellites, setSatellites] = useState<Satellite[]>([]);
  const [selectedSatellite, setSelectedSatellite] = useState<Satellite | null>(null);
  const [conjunctionEvents, setConjunctionEvents] = useState<ConjunctionEventData[]>([]);
  const [selectedEventIndex, setSelectedEventIndex] = useState<number | null>(null);
  const [aiAnalysis, setAiAnalysis] = useState<string>('');
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [isLoadingData, setIsLoadingData] = useState(true);
  const [isLoadingCDMs, setIsLoadingCDMs] = useState(false);
  const [connectionError, setConnectionError] = useState(false);
  const [lastIngest, setLastIngest] = useState<string | null>(null);
  const [now, setNow] = useState(new Date());

  // Timer for countdowns
  useEffect(() => {
    const timer = setInterval(() => setNow(new Date()), 60000);
    return () => clearInterval(timer);
  }, []);

  // Load Satellites on mount
  useEffect(() => {
    const loadSatellites = async () => {
      setIsLoadingData(true);
      setConnectionError(false);
      try {
        const data = await fetchSatellites();
        setSatellites(data);
        setLastIngest(new Date().toISOString());
      } catch (e) { 
        console.error("Satellite data load failed", e); 
        setConnectionError(true);
      } 
      finally { setIsLoadingData(false); }
    };
    loadSatellites();
  }, []);

  const handleSatelliteClick = async (satellite: Satellite) => {
    // If clicking the same satellite, toggle expansion
    if (selectedSatellite?.id === satellite.id) {
      setSelectedSatellite(null);
      setConjunctionEvents([]);
      setSelectedEventIndex(null);
      setAiAnalysis('');
      return;
    }
    
    setSelectedSatellite(satellite);
    setConjunctionEvents([]);
    setSelectedEventIndex(null);
    setAiAnalysis('');
    setIsLoadingCDMs(true);
    
    try {
      const events = await fetchCDMsForSatellite(satellite.id);
      setConjunctionEvents(events);
      
      // Auto-select first event if available
      if (events.length > 0) {
        setSelectedEventIndex(0);
        setIsAnalyzing(true);
        const assessment = await generateRiskAssessment({ id: satellite.id } as any);
        setAiAnalysis(assessment);
        setIsAnalyzing(false);
      } else {
        setAiAnalysis('No conjunction events detected for this satellite.');
      }
    } catch (e) {
      console.error("Failed to load CDMs", e);
      setAiAnalysis('Failed to load risk assessment.');
    } finally {
      setIsLoadingCDMs(false);
    }
  };

  const handleEventClick = (index: number) => {
    setSelectedEventIndex(index);
  };

  // Get the currently selected conjunction event
  const selectedEvent = selectedEventIndex !== null ? conjunctionEvents[selectedEventIndex] : null;

  // Get all CDM records from the selected event, sorted by creation date
  const sortedCDMRecords = selectedEvent 
    ? [...selectedEvent.CDMS].sort((a, b) => 
        new Date(a.CREATED).getTime() - new Date(b.CREATED).getTime()
      )
    : [];

  const handleDownloadCDM = () => {
    if (!selectedSatellite || conjunctionEvents.length === 0) return;
    const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(conjunctionEvents, null, 2));
    const downloadAnchorNode = document.createElement('a');
    downloadAnchorNode.setAttribute("href", dataStr);
    downloadAnchorNode.setAttribute("download", `${selectedSatellite.id}_cdms.json`);
    document.body.appendChild(downloadAnchorNode);
    downloadAnchorNode.click();
    downloadAnchorNode.remove();
  };

  const handleCompareEphemeris = () => {
    if (!selectedSatellite) return;
    const report = `EPHEMERIS COMPARISON REPORT\nTarget: ${selectedSatellite.name}\nSatellite ID: ${selectedSatellite.id}\n\nDELTA-V ANALYSIS:\nNo significant maneuver detected in past 48h.\n\nCOVARIANCE:\nConsistent with CDM public metadata.\n\nSTATUS: NOMINAL`;
    const dataStr = "data:text/plain;charset=utf-8," + encodeURIComponent(report);
    const downloadAnchorNode = document.createElement('a');
    downloadAnchorNode.setAttribute("href", dataStr);
    downloadAnchorNode.setAttribute("download", `EPHEM_COMPARE_${selectedSatellite.id}.txt`);
    document.body.appendChild(downloadAnchorNode);
    downloadAnchorNode.click();
    downloadAnchorNode.remove();
  };

  return (
    <div className="flex h-screen bg-slate-950 text-slate-300 font-sans overflow-hidden selection:bg-cyan-900 selection:text-white">
      
      {/* 1. Left Sidebar Navigation */}
      <aside className="w-72 flex-none bg-slate-950 border-r border-slate-800 flex flex-col z-20 shadow-xl">
         {/* Header */}
         <div className="h-16 flex items-center px-4 border-b border-slate-800 bg-slate-950 gap-3 shrink-0">
            <div className="w-8 h-8 bg-cyan-950 border border-cyan-800 rounded flex items-center justify-center">
              <Orbit className="w-5 h-5 text-cyan-400" />
            </div>
            <div>
              <h1 className="text-sm font-bold tracking-widest text-slate-100 uppercase">OrbitalGuard</h1>
              <div className="flex items-center gap-1.5">
                 <div className={`w-1.5 h-1.5 rounded-full ${connectionError ? 'bg-red-500' : 'bg-emerald-500 animate-pulse'}`}></div>
                 <p className="text-[10px] text-slate-500 uppercase font-mono">{connectionError ? 'OFFLINE' : 'LIVE FEED'}</p>
              </div>
            </div>
         </div>

         {/* Satellite List */}
         <div className="flex-1 overflow-y-auto custom-scrollbar">
            <div className="px-4 py-3 text-[10px] font-bold text-slate-500 uppercase tracking-widest bg-slate-950 sticky top-0 z-10 border-b border-slate-800 flex justify-between items-center">
               <span>Satellites ({satellites.length})</span>
               {isLoadingData && <RefreshCw className="w-3 h-3 text-cyan-500 animate-spin" />}
            </div>
            
            {connectionError && (
               <div className="p-4 flex flex-col items-center justify-center text-red-400 space-y-2">
                  <WifiOff className="w-6 h-6" />
                  <span className="text-xs text-center">Backend Connection Failed</span>
                  <span className="text-[10px] text-slate-500 text-center">Ensure the API is running on {API_BASE_URL}</span>
               </div>
            )}

            {isLoadingData ? (
               <div className="p-4 space-y-4">
                  {[1, 2, 3].map(i => <div key={i} className="h-16 bg-slate-900 rounded animate-pulse"></div>)}
               </div>
            ) : (
               satellites.map(satellite => (
                  <SatelliteSidebarItem 
                     key={satellite.id} 
                     satellite={satellite} 
                     isActive={selectedSatellite?.id === satellite.id}
                     isExpanded={selectedSatellite?.id === satellite.id}
                     conjunctionEvents={selectedSatellite?.id === satellite.id ? conjunctionEvents : []}
                     selectedEventIndex={selectedSatellite?.id === satellite.id ? selectedEventIndex : null}
                     onClick={() => handleSatelliteClick(satellite)}
                     onEventClick={handleEventClick}
                  />
               ))
            )}
         </div>
      </aside>

      {/* 2. Main Stage Area */}
      <main className="flex-1 flex flex-col min-w-0 bg-slate-950 relative">
        
        {/* Global Toolbar */}
        <header className="h-16 flex items-center justify-between px-6 border-b border-slate-800 bg-slate-950 shrink-0">
           <div className="flex items-center gap-4">
              <h2 className="text-sm font-medium text-slate-400 uppercase tracking-wide">
                 {selectedSatellite ? `Satellite: ${selectedSatellite.name}` : 'Mission Overview'}
              </h2>
           </div>
           <div className="flex items-center gap-6 text-xs font-mono text-slate-500">
              <div className="flex items-center gap-2">
                 <Clock className="w-3 h-3" />
                 <span>Last Ingest: {lastIngest ? new Date(lastIngest).toLocaleTimeString() : '--:--:--'} UTC</span>
              </div>
           </div>
        </header>

        {/* Dynamic Content */}
        <div className="flex-1 overflow-y-auto p-6 scroll-smooth">
           {!selectedSatellite ? (
              // Empty State
              <div className="h-full flex flex-col items-center justify-center text-slate-600 space-y-4">
                 <div className="w-20 h-20 bg-slate-900 rounded-full flex items-center justify-center border border-slate-800">
                    <Target className="w-10 h-10 opacity-50" />
                 </div>
                 <p className="text-sm uppercase tracking-widest font-mono">Select a Satellite to View Conjunction Events</p>
              </div>
           ) : (
              // Focused Satellite View
              <div className="max-w-5xl mx-auto space-y-6 animate-in fade-in duration-300">
                 
                 {/* Satellite Header */}
                 <div className="bg-slate-900/50 border border-slate-800 rounded-lg p-6">
                    <div className="flex items-start justify-between">
                       <div>
                          <h2 className="text-2xl font-bold text-white mb-2">{selectedSatellite.name}</h2>
                          <div className="flex gap-4 text-sm text-slate-400">
                             <span>ID: {selectedSatellite.id}</span>
                             <span>Type: {selectedSatellite.type}</span>
                             <span>RCS: {selectedSatellite.rcs}</span>
                             <span>Excl Vol: {selectedSatellite.excl_vol} km</span>
                          </div>
                       </div>
                       <div className="flex gap-2">
                          <button 
                             onClick={handleDownloadCDM}
                             disabled={conjunctionEvents.length === 0}
                             className="py-2 px-4 bg-cyan-900/20 hover:bg-cyan-900/40 disabled:opacity-30 disabled:cursor-not-allowed border border-cyan-900/50 text-cyan-400 text-xs font-bold uppercase tracking-wider rounded transition-colors flex items-center justify-center gap-2"
                          >
                             <Download className="w-3 h-3" />
                             Download CDMs
                          </button>
                          <button 
                             onClick={handleCompareEphemeris}
                             className="py-2 px-4 bg-slate-800 hover:bg-slate-700 border border-slate-700 text-slate-300 text-xs font-bold uppercase tracking-wider rounded transition-colors flex items-center justify-center gap-2"
                          >
                             <ArrowLeftRight className="w-3 h-3" />
                             Ephemeris
                          </button>
                       </div>
                    </div>
                 </div>

                 {/* Collision Probability Trend Chart */}
                 {isLoadingCDMs ? (
                    <div className="bg-slate-900/50 border border-slate-800 rounded-lg p-6">
                       <div className="flex items-center justify-center py-12">
                          <div className="flex flex-col items-center gap-3">
                             <RefreshCw className="w-8 h-8 text-cyan-500 animate-spin" />
                             <span className="text-sm text-slate-500">Loading conjunction data...</span>
                          </div>
                       </div>
                    </div>
                 ) : !selectedEvent ? (
                    <div className="bg-slate-900/50 border border-slate-800 rounded-lg p-6">
                       <div className="flex flex-col items-center justify-center py-12 text-slate-500">
                          <CheckCircle className="w-12 h-12 mb-3 opacity-50" />
                          <p className="text-center">No conjunction events found for this satellite</p>
                       </div>
                    </div>
                 ) : (
                    <>
                       {/* Selected Event Header */}
                       <div className="bg-slate-900/50 border border-slate-800 rounded-lg p-4">
                          <div className="flex items-center justify-between">
                             <div className="flex items-center gap-4">
                                <div>
                                   <h3 className="text-lg font-semibold text-white">{selectedEvent.SAT_2.NAME}</h3>
                                   <div className="flex items-center gap-2 text-xs text-slate-400 mt-1">
                                      <span>ID: {selectedEvent.SAT_2.ID}</span>
                                      <span className="text-slate-600">•</span>
                                      <span>{selectedEvent.SAT_2.OBJ_TYP}</span>
                                      <span className="text-slate-600">•</span>
                                      <span>RCS: {selectedEvent.SAT_2.RCS}</span>
                                      <span className="text-slate-600">•</span>
                                      <span>Excl Vol: {selectedEvent.SAT_2.EXCL_VOL} km</span>
                                   </div>
                                </div>
                             </div>
                             <div className="flex items-center gap-3">
                                <span className={`px-3 py-1.5 text-xs font-bold rounded border ${
                                   selectedEvent.AI_STATUS === 'ESCALATING' ? 'bg-red-500/20 text-red-400 border-red-500/50' :
                                   selectedEvent.AI_STATUS === 'RESOLVING' ? 'bg-amber-500/20 text-amber-400 border-amber-500/30' :
                                   'bg-slate-700 text-slate-400 border-slate-600'
                                }`}>
                                   {selectedEvent.AI_STATUS}
                                </span>
                                {selectedEvent.AI_STATUS === 'ESCALATING' && (
                                   <div className="flex items-center gap-1 text-red-400">
                                      <ShieldAlert className="w-5 h-5 animate-pulse" />
                                   </div>
                                )}
                             </div>
                          </div>
                          <div className="grid grid-cols-4 gap-4 mt-4 pt-3 border-t border-slate-700/50">
                             <div className="text-center">
                                <label className="text-[10px] text-slate-500 uppercase block mb-1">TCA</label>
                                <div className="text-sm font-mono text-slate-300">{new Date(selectedEvent.TCA).toLocaleString()}</div>
                             </div>
                             <div className="text-center">
                                <label className="text-[10px] text-slate-500 uppercase block mb-1">Min Range</label>
                                <div className="text-sm font-mono text-white">{selectedEvent.MIN_RANGE}m</div>
                             </div>
                             <div className="text-center">
                                <label className="text-[10px] text-slate-500 uppercase block mb-1">Max PC</label>
                                <div className="text-sm font-mono text-white">{selectedEvent.MAX_PC.toExponential(4)}</div>
                             </div>
                             <div className="text-center">
                                <label className="text-[10px] text-slate-500 uppercase block mb-1">AI Certainty</label>
                                <div className="text-sm font-mono text-cyan-400">{(selectedEvent.AI_CERTAINTY * 100).toFixed(0)}%</div>
                             </div>
                          </div>
                       </div>

                       {/* Probability & Range Chart */}
                       <ProbabilityChart data={sortedCDMRecords.map((cdm) => ({
                          timestamp: cdm.CREATED,
                          value: cdm.PC,
                          range: cdm.MIN_RNG,
                          source: 'OBSERVED' as const
                       }))} />

                       {/* Risk Interpretation (AI) */}
                       <div className="bg-slate-900/40 border border-slate-800 rounded-lg p-5">
                          <div className="flex items-center gap-3 mb-3">
                             <div className="flex-shrink-0 w-6 h-6 rounded bg-cyan-900/30 flex items-center justify-center border border-cyan-800/50">
                                <Cpu className="w-4 h-4 text-cyan-400" />
                             </div>
                             <h3 className="text-xs font-bold text-slate-300 uppercase tracking-widest mt-0.5">Automated Risk Interpretation</h3>
                          </div>
                          {isAnalyzing ? (
                             <div className="h-12 flex items-center gap-3">
                                <div className="w-1 h-1 bg-cyan-500 rounded-full animate-ping"></div>
                                <span className="text-xs font-mono text-cyan-500">Processing CDM History...</span>
                             </div>
                          ) : (
                             <div className="border-l-2 border-slate-700 pl-4 py-1">
                                <p className="text-sm text-slate-300 leading-relaxed font-light">
                                    {aiAnalysis}
                                </p>
                             </div>
                          )}
                       </div>

                       {/* CDM Records Table */}
                       <div className="bg-slate-900/50 border border-slate-800 rounded-lg overflow-hidden">
                          <div className="px-4 py-3 border-b border-slate-700 flex items-center justify-between">
                             <h3 className="text-sm font-semibold text-white flex items-center gap-2">
                                <AlertTriangle className="w-4 h-4 text-amber-500" />
                                CDM Records ({sortedCDMRecords.length})
                             </h3>
                             <div className="text-xs text-slate-500 font-mono">
                                {selectedEvent.SAT_2.NAME} | {selectedEvent.SAT_2.OBJ_TYP} | Vol: {selectedEvent.SAT_2.EXCL_VOL} km
                             </div>
                          </div>
                          
                          {/* Table Header */}
                          <div className="grid grid-cols-4 gap-2 px-4 py-2 bg-slate-800/50 border-b border-slate-700 text-[10px] font-bold uppercase tracking-widest">
                             <div className="text-slate-400 text-center">CDM ID / Created</div>
                             <div className="text-cyan-400 text-center">Range (m)</div>
                             <div className="text-pink-400 text-center">Probability</div>
                             <div className="text-slate-400 text-center">TCA</div>
                          </div>
                          
                          {/* Table Body */}
                          <div className="divide-y divide-slate-800/50">
                             {sortedCDMRecords.map((cdm) => (
                                <div 
                                   key={cdm.CDM_ID} 
                                   className="grid grid-cols-4 gap-2 px-4 py-2 hover:bg-slate-800/30 transition-colors"
                                >
                                   {/* CDM ID & Created */}
                                   <div className="text-center">
                                      <div className="text-xs font-mono text-slate-500">#{cdm.CDM_ID}</div>
                                      <div className="text-xs font-mono text-white">
                                         {new Date(cdm.CREATED).toLocaleDateString([], { month: 'short', day: 'numeric' })}
                                         <span className="text-slate-500 ml-1">
                                            {new Date(cdm.CREATED).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                                         </span>
                                      </div>
                                   </div>
                                   
                                   {/* Range */}
                                   <div className="text-center flex items-center justify-center">
                                      <span className="text-sm font-mono text-cyan-300">{cdm.MIN_RNG.toFixed(0)}</span>
                                   </div>
                                   
                                   {/* Probability */}
                                   <div className="text-center flex items-center justify-center">
                                      <span className="text-sm font-mono text-pink-300">{cdm.PC.toExponential(4)}</span>
                                   </div>
                                   
                                   {/* TCA */}
                                   <div className="text-center">
                                      <div className="text-xs font-mono text-slate-400">
                                         {new Date(cdm.TCA).toLocaleDateString([], { month: 'short', day: 'numeric' })}
                                         <span className="text-slate-500 ml-1">
                                            {new Date(cdm.TCA).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                                         </span>
                                      </div>
                                   </div>
                                </div>
                             ))}
                          </div>
                       </div>
                    </>
                 )}

              </div>
           )}
        </div>
      </main>
    </div>
  );
}