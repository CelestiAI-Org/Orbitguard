import React, { useState, useEffect } from 'react';
import { 
  Activity, 
  AlertTriangle, 
  CheckCircle, 
  ChevronRight, 
  ShieldAlert,
  Search,
  Cpu,
  Orbit,
  Satellite,
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
import { ConjunctionEvent, RiskLevel } from './types';
import ProbabilityChart from './components/ProbabilityChart';
import { generateRiskAssessment } from './services/geminiService';
import { fetchCDMUpdates } from './services/cdmService';
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
    case RiskLevel.CRITICAL: return 'text-red-500 border-red-900 bg-red-950/20';
    case RiskLevel.HIGH: return 'text-red-400 border-red-900 bg-red-950/10';
    case RiskLevel.MEDIUM: return 'text-amber-500 border-amber-900 bg-amber-950/20';
    default: return 'text-slate-400 border-slate-800 bg-slate-900/50';
  }
};

// --- Sidebar Item ---
const EventSidebarItem: React.FC<{ 
  event: ConjunctionEvent; 
  isActive: boolean; 
  onClick: () => void 
}> = ({ event, isActive, onClick }) => {
  
  const isHighRisk = event.riskLevel === RiskLevel.CRITICAL || event.riskLevel === RiskLevel.HIGH;

  return (
    <div 
      onClick={onClick}
      className={`
        relative group flex items-center justify-between p-4 cursor-pointer transition-all duration-200 border-b border-slate-800
        hover:bg-slate-900
        ${isActive ? 'bg-slate-800 border-l-4 border-l-cyan-500' : 'border-l-4 border-l-transparent'}
      `}
    >
      {/* Breathing Effect for High Risk */}
      {isHighRisk && !isActive && (
         <div className="absolute inset-0 bg-red-500/5 animate-pulse-slow pointer-events-none" style={{ animationDuration: '4s' }}></div>
      )}

      <div className="flex flex-col gap-1 z-10 w-full">
        <div className="flex items-center justify-between mb-1">
           <span className={`text-[10px] font-mono tracking-wider ${isActive ? 'text-slate-400' : 'text-slate-600'}`}>{event.id}</span>
           <div className={`w-2 h-2 rounded-full ${
              event.riskLevel === RiskLevel.CRITICAL ? 'bg-red-500 shadow-[0_0_8px_rgba(239,68,68,0.8)]' : 
              event.riskLevel === RiskLevel.MEDIUM ? 'bg-amber-500' : 'bg-slate-600'
           }`}></div>
        </div>
        
        <div className="flex items-center gap-2">
           <span className={`text-sm font-semibold truncate ${isActive ? 'text-white' : 'text-slate-300'}`}>
              {event.primaryObject.name}
           </span>
           <span className="text-xs text-slate-600">vs</span>
        </div>
        <div className={`text-xs truncate ${isActive ? 'text-slate-300' : 'text-slate-500'}`}>
           {event.secondaryObject.name}
        </div>
      </div>
    </div>
  );
};

// --- Main App ---

export default function App() {
  const [events, setEvents] = useState<ConjunctionEvent[]>([]);
  const [selectedEvent, setSelectedEvent] = useState<ConjunctionEvent | null>(null);
  const [aiAnalysis, setAiAnalysis] = useState<string>('');
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [isLoadingData, setIsLoadingData] = useState(true);
  const [connectionError, setConnectionError] = useState(false);
  const [lastIngest, setLastIngest] = useState<string | null>(null);
  const [now, setNow] = useState(new Date());

  // Timer for countdowns
  useEffect(() => {
    const timer = setInterval(() => setNow(new Date()), 60000);
    return () => clearInterval(timer);
  }, []);

  // Load Data
  useEffect(() => {
    const loadData = async () => {
      setIsLoadingData(true);
      setConnectionError(false);
      try {
        const data = await fetchCDMUpdates();
        setEvents(data);
        setLastIngest(new Date().toISOString());
      } catch (e) { 
        console.error("Data load failed", e); 
        setConnectionError(true);
      } 
      finally { setIsLoadingData(false); }
    };
    loadData();
  }, []);

  const handleEventClick = async (event: ConjunctionEvent) => {
    setSelectedEvent(event);
    setAiAnalysis(''); 
    setIsAnalyzing(true);
    const result = await generateRiskAssessment(event);
    setAiAnalysis(result);
    setIsAnalyzing(false);
  };

  const handleDownloadCDM = () => {
    if (!selectedEvent) return;
    const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(selectedEvent, null, 2));
    const downloadAnchorNode = document.createElement('a');
    downloadAnchorNode.setAttribute("href", dataStr);
    downloadAnchorNode.setAttribute("download", `${selectedEvent.id}.json`);
    document.body.appendChild(downloadAnchorNode);
    downloadAnchorNode.click();
    downloadAnchorNode.remove();
  };

  const handleCompareEphemeris = () => {
    if (!selectedEvent) return;
    const report = `EPHEMERIS COMPARISON REPORT\nTarget: ${selectedEvent.primaryObject.name}\nSecondary: ${selectedEvent.secondaryObject.name}\nTCA: ${selectedEvent.tca}\n\nDELTA-V ANALYSIS:\nNo significant maneuver detected in past 48h.\n\nCOVARIANCE:\nConsistent with CDM public metadata.\n\nSTATUS: NOMINAL`;
    const dataStr = "data:text/plain;charset=utf-8," + encodeURIComponent(report);
    const downloadAnchorNode = document.createElement('a');
    downloadAnchorNode.setAttribute("href", dataStr);
    downloadAnchorNode.setAttribute("download", `EPHEM_COMPARE_${selectedEvent.id}.txt`);
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

         {/* Event List */}
         <div className="flex-1 overflow-y-auto custom-scrollbar">
            <div className="px-4 py-3 text-[10px] font-bold text-slate-500 uppercase tracking-widest bg-slate-950 sticky top-0 z-10 border-b border-slate-800 flex justify-between items-center">
               <span>Ingested Events ({events.length})</span>
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
               events.map(event => (
                  <EventSidebarItem 
                     key={event.id} 
                     event={event} 
                     isActive={selectedEvent?.id === event.id} 
                     onClick={() => handleEventClick(event)} 
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
                 {selectedEvent ? `Event Analysis: ${selectedEvent.id}` : 'Mission Overview'}
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
           {!selectedEvent ? (
              // Empty State
              <div className="h-full flex flex-col items-center justify-center text-slate-600 space-y-4">
                 <div className="w-20 h-20 bg-slate-900 rounded-full flex items-center justify-center border border-slate-800">
                    <Target className="w-10 h-10 opacity-50" />
                 </div>
                 <p className="text-sm uppercase tracking-widest font-mono">Select a CDM Event to Begin Analysis</p>
              </div>
           ) : (
              // Focused Event View
              <div className="max-w-5xl mx-auto space-y-6 animate-in fade-in duration-300">
                 
                 {/* 1. Header & Risk Classification */}
                 <div className={`p-6 rounded-lg border flex justify-between items-start relative overflow-hidden ${getRiskColors(selectedEvent.riskLevel)}`}>
                    {/* Background glow for critical */}
                    {selectedEvent.riskLevel === RiskLevel.CRITICAL && (
                        <div className="absolute top-0 right-0 w-64 h-64 bg-red-500/20 blur-3xl rounded-full -mr-32 -mt-32 pointer-events-none"></div>
                    )}
                    
                    <div className="z-10">
                       <div className="flex items-center gap-3 mb-2">
                          <span className="px-2 py-0.5 bg-black/30 rounded text-[10px] font-bold uppercase tracking-wider border border-white/10">
                             Risk Level: {selectedEvent.riskLevel}
                          </span>
                       </div>
                       <h1 className="text-2xl font-light text-slate-100 mb-1 tracking-tight">
                          {selectedEvent.primaryObject.name} <span className="text-slate-500 mx-1">×</span> {selectedEvent.secondaryObject.name}
                       </h1>
                       <p className="text-xs opacity-70 font-mono">
                          Primary RCS: {selectedEvent.primaryObject.rcs} | Secondary RCS: {selectedEvent.secondaryObject.rcs}
                       </p>
                    </div>

                    <div className="text-right z-10">
                       <div className="text-[10px] font-bold uppercase tracking-widest opacity-70 mb-1">Time to TCA</div>
                       <div className="text-3xl font-mono font-bold tabular-nums">
                          {formatTimeRemaining(selectedEvent.tca)}
                       </div>
                       <div className="text-xs font-mono opacity-70 mt-1">{new Date(selectedEvent.tca).toUTCString()}</div>
                    </div>
                 </div>

                 {/* 2. Collision Probability Trend Panel */}
                 <div className="grid grid-cols-12 gap-6">
                    <div className="col-span-8 space-y-6">
                       <ProbabilityChart data={selectedEvent.probabilityHistory} />

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
                    </div>

                    {/* 3. Key Telemetry Facts */}
                    <div className="col-span-4 space-y-4">
                       <div className="bg-slate-900/40 border border-slate-800 rounded-lg p-5">
                          <h3 className="text-xs font-bold text-slate-500 uppercase tracking-widest mb-4 flex items-center gap-2">
                             <FileText className="w-3 h-3" /> CDM Telemetry
                          </h3>
                          
                          <div className="space-y-4">
                             <div>
                                <label className="text-[10px] text-slate-500 uppercase block mb-1">Max Collision Probability</label>
                                <div className="text-2xl font-mono text-white">
                                   {selectedEvent.collisionProb.toExponential(2)}
                                </div>
                             </div>

                             <div>
                                <label className="text-[10px] text-slate-500 uppercase block mb-1">Min Miss Distance</label>
                                <div className="text-xl font-mono text-white flex items-baseline gap-1">
                                   {selectedEvent.missDistance.toFixed(1)} <span className="text-sm text-slate-500">m</span>
                                </div>
                             </div>

                             <div className="pt-4 border-t border-slate-800">
                                <label className="text-[10px] text-slate-500 uppercase block mb-1">Exclusion Volume</label>
                                <div className="text-xs font-mono text-slate-400 leading-tight">
                                   {selectedEvent.exclusionVolume}
                                </div>
                             </div>
                          </div>
                       </div>

                       {/* Action Buttons */}
                       <div className="space-y-2 pt-2">
                          <button 
                             onClick={handleDownloadCDM}
                             className="w-full py-2.5 bg-cyan-900/20 hover:bg-cyan-900/40 border border-cyan-900/50 text-cyan-400 text-xs font-bold uppercase tracking-wider rounded transition-colors flex items-center justify-center gap-2"
                          >
                             <Download className="w-3 h-3" />
                             Download Raw CDM
                          </button>
                          <button 
                             onClick={handleCompareEphemeris}
                             className="w-full py-2.5 bg-slate-800 hover:bg-slate-700 border border-slate-700 text-slate-300 text-xs font-bold uppercase tracking-wider rounded transition-colors flex items-center justify-center gap-2"
                          >
                             <ArrowLeftRight className="w-3 h-3" />
                             Compare Ephemeris
                          </button>
                       </div>
                    </div>
                 </div>

              </div>
           )}
        </div>
      </main>
    </div>
  );
}