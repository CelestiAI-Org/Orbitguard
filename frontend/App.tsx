
import React, { useState, useEffect, useCallback } from 'react';
import { 
  RefreshCw, 
  Target, 
  Download, 
  FileText, 
  Clock, 
  BarChart3, 
  Cpu, 
  AlertTriangle,
  Server,
  Orbit,
  ExternalLink,
  ChevronRight
} from 'lucide-react';
import Sidebar from './components/Sidebar';
import ProbabilityChart from './components/ProbabilityChart';
import OrbitalViz from './components/OrbitalViz';
import { 
  Satellite, 
  ConjunctionEventData, 
  ChartDataPoint 
} from './types';
import { 
  fetchSatellites, 
  fetchCDMsForSatellite, 
  checkSystemHealth 
} from './services/cdmService';
import { generateRiskAssessment } from './services/geminiService';

const App: React.FC = () => {
  // State
  const [satellites, setSatellites] = useState<Satellite[]>([]);
  const [selectedSatellite, setSelectedSatellite] = useState<Satellite | null>(null);
  const [conjunctions, setConjunctions] = useState<Record<string, ConjunctionEventData[]>>({});
  const [selectedEventIndex, setSelectedEventIndex] = useState<number | null>(null);
  const [aiAnalysis, setAiAnalysis] = useState<string>('');
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [isLoadingData, setIsLoadingData] = useState(true);
  const [isLoadingCDMs, setIsLoadingCDMs] = useState(false);
  const [connectionError, setConnectionError] = useState(false);
  const [lastIngest, setLastIngest] = useState<string | null>(null);
  const [countdown, setCountdown] = useState<string>('--:--:--');

  // Initialization
  useEffect(() => {
    const initApp = async () => {
      try {
        const health = await checkSystemHealth();
        if (health === 'OFFLINE') {
          setConnectionError(true);
          setIsLoadingData(false);
          return;
        }

        const data = await fetchSatellites();
        setSatellites(data);
        setLastIngest(new Date().toISOString());
        setIsLoadingData(false);
      } catch (err) {
        console.error('App init error:', err);
        setConnectionError(true);
        setIsLoadingData(false);
      }
    };
    initApp();
  }, []);

  // Handle Satellite Selection
  const handleSelectSatellite = async (sat: Satellite) => {
    if (selectedSatellite?.id === sat.id) {
      setSelectedSatellite(null);
      setSelectedEventIndex(null);
      return;
    }
    
    setSelectedSatellite(sat);
    setSelectedEventIndex(null);
    setAiAnalysis('');
    
    if (!conjunctions[sat.id]) {
      setIsLoadingCDMs(true);
      try {
        const events = await fetchCDMsForSatellite(sat.id);
        setConjunctions(prev => ({ ...prev, [sat.id]: events }));
      } catch (err) {
        console.error('CDM fetch error:', err);
      } finally {
        setIsLoadingCDMs(false);
      }
    }
  };

  const selectedEvent = (selectedSatellite && selectedEventIndex !== null) 
    ? conjunctions[selectedSatellite.id]?.[selectedEventIndex] 
    : null;

  // Countdown timer for TCA
  useEffect(() => {
    if (!selectedEvent) return;
    
    const interval = setInterval(() => {
      const tca = new Date(selectedEvent.TCA).getTime();
      const now = new Date().getTime();
      const diff = tca - now;
      
      if (diff <= 0) {
        setCountdown("ENCOUNTER REACHED");
        return;
      }
      
      const hours = Math.floor(diff / (1000 * 60 * 60));
      const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));
      const seconds = Math.floor((diff % (1000 * 60)) / 1000);
      setCountdown(`${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`);
    }, 1000);
    
    return () => clearInterval(interval);
  }, [selectedEvent]);

  // Transform CDMs for Charting
  const chartData: ChartDataPoint[] = selectedEvent?.CDMS.map(cdm => ({
    timestamp: cdm.CREATED,
    value: cdm.PC,
    range: cdm.MIN_RNG,
    source: 'OBSERVED'
  })) || [];

  const handleFetchAiAnalysis = async () => {
    if (!selectedSatellite) return;
    setIsAnalyzing(true);
    setAiAnalysis('');
    try {
      const summary = await generateRiskAssessment(selectedSatellite.id);
      setAiAnalysis(summary);
    } catch (err) {
      setAiAnalysis("AI Diagnostic Error: Response timeout.");
    } finally {
      setIsAnalyzing(false);
    }
  };

  const handleDownloadJSON = () => {
    if (!selectedEvent) return;
    const blob = new Blob([JSON.stringify(selectedEvent, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `OrbitGuard_CDM_${selectedEvent.SAT_2.NAME}_${selectedEvent.TCA}.json`;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="flex h-screen w-full mission-gradient overflow-hidden">
      <Sidebar 
        satellites={satellites}
        selectedSatellite={selectedSatellite}
        onSelectSatellite={handleSelectSatellite}
        isLoading={isLoadingData}
        conjunctions={conjunctions}
        isLoadingCDMs={isLoadingCDMs}
        selectedEventIndex={selectedEventIndex}
        onSelectEvent={setSelectedEventIndex}
        error={connectionError}
      />

      <main className="flex-1 flex flex-col min-w-0">
        {/* Top Header Bar */}
        <header className="h-16 border-b border-slate-800 bg-slate-950/80 backdrop-blur-sm flex items-center justify-between px-6 z-10">
          <div className="flex items-center gap-6">
            <div className="flex flex-col">
              <span className="text-[9px] font-bold text-slate-500 uppercase tracking-widest">System Time (UTC)</span>
              <span className="text-sm font-mono text-slate-300">
                {new Date().toISOString().split('T')[1].slice(0, 8)}
              </span>
            </div>
            <div className="h-8 w-px bg-slate-800" />
            <div className="flex flex-col">
              <span className="text-[9px] font-bold text-slate-500 uppercase tracking-widest">Last Telemetry Ingest</span>
              <span className="text-sm font-mono text-slate-300">
                {lastIngest ? new Date(lastIngest).toLocaleTimeString() : '---'}
              </span>
            </div>
          </div>

          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2 px-3 py-1.5 rounded bg-slate-900 border border-slate-800">
              <Server className="w-3 h-3 text-cyan-400" />
              <span className="text-[10px] font-bold text-slate-300">MODEL v4.02 NOMINAL</span>
            </div>
            <button 
              className="p-2 hover:bg-slate-900 rounded-full transition-colors"
              onClick={() => window.location.reload()}
            >
              <RefreshCw className="w-4 h-4 text-slate-500" />
            </button>
          </div>
        </header>

        {/* Content Area */}
        <div className="flex-1 overflow-y-auto p-6 space-y-6">
          {!selectedEvent ? (
            <div className="h-full flex flex-col items-center justify-center text-center">
              <div className="w-20 h-20 border-2 border-slate-800 rounded-full flex items-center justify-center mb-6 relative">
                <Orbit className="w-10 h-10 text-slate-700 animate-pulse" />
                <div className="absolute inset-0 border-2 border-cyan-500/20 rounded-full animate-ping" />
              </div>
              <h2 className="text-xl font-bold text-slate-300 mb-2 uppercase tracking-tighter">Satellite Monitoring Offline</h2>
              <p className="text-slate-500 max-w-md text-xs uppercase tracking-wider leading-relaxed">
                Select a primary asset from the mission control sidebar to begin real-time conjunction analysis and risk assessment.
              </p>
              
              <div className="mt-12 grid grid-cols-3 gap-8 w-full max-w-2xl">
                {[
                  { label: 'Active Payloads', val: satellites.length, icon: Target },
                  { label: 'Network Latency', val: '14ms', icon: Clock },
                  { label: 'Pending CDMs', val: satellites.reduce((acc, s) => acc + s.total_cdms, 0), icon: FileText }
                ].map((stat, i) => (
                  <div key={i} className="bg-slate-900/40 p-4 rounded border border-slate-800/50 flex flex-col items-center">
                    <stat.icon className="w-5 h-5 text-slate-600 mb-3" />
                    <span className="text-2xl font-bold text-slate-300">{stat.val}</span>
                    <span className="text-[9px] font-bold text-slate-500 uppercase mt-1 tracking-widest">{stat.label}</span>
                  </div>
                ))}
              </div>
            </div>
          ) : (
            <div className="animate-in fade-in slide-in-from-bottom-2 duration-500 space-y-6">
              {/* Event Header & KPI Row */}
              <div className="flex flex-wrap items-stretch gap-4">
                <div className="flex-1 bg-slate-900/50 border border-slate-800 rounded-lg p-5 flex flex-col justify-between">
                  <div className="flex justify-between items-start mb-4">
                    <div>
                      <div className="flex items-center gap-2 mb-1">
                        <Target className="w-4 h-4 text-cyan-400" />
                        <span className="text-[10px] font-bold text-slate-500 uppercase tracking-widest">Encounter Details</span>
                      </div>
                      <h2 className="text-lg font-bold text-slate-100 flex items-center gap-3">
                        {selectedSatellite?.name} <ChevronRight className="w-4 h-4 text-slate-700" /> {selectedEvent.SAT_2.NAME}
                      </h2>
                    </div>
                    <div className={`px-4 py-2 text-xs font-black rounded border-2 shadow-lg flex flex-col items-center ${
                      selectedEvent.AI_STATUS === 'ESCALATING' ? 'bg-red-500/10 border-red-500 text-red-500' :
                      selectedEvent.AI_STATUS === 'RESOLVING' ? 'bg-amber-500/10 border-amber-500 text-amber-500' :
                      'bg-green-500/10 border-green-500 text-green-500'
                    }`}>
                      <span className="text-[8px] opacity-70 mb-0.5">RISK STATE</span>
                      {selectedEvent.AI_STATUS}
                    </div>
                  </div>
                  
                  <div className="grid grid-cols-4 gap-4 mt-auto">
                    {[
                      { label: 'Max Probability', value: selectedEvent.MAX_PC.toExponential(4), sub: 'Observed' },
                      { label: 'Min Range', value: `${selectedEvent.MIN_RANGE.toFixed(1)}m`, sub: 'Distance' },
                      { label: 'AI Certainty', value: `${(selectedEvent.AI_CERTAINTY * 100).toFixed(0)}%`, sub: 'Confidence' },
                      { label: 'Messages', value: selectedEvent.MSG_COUNT, sub: 'CDM Count' }
                    ].map((item, idx) => (
                      <div key={idx} className="bg-slate-950/50 p-3 rounded border border-slate-800">
                        <div className="text-[9px] font-bold text-slate-500 uppercase mb-1">{item.label}</div>
                        <div className="text-sm font-mono font-bold text-slate-200">{item.value}</div>
                        <div className="text-[8px] text-slate-600 font-bold uppercase mt-1">{item.sub}</div>
                      </div>
                    ))}
                  </div>
                </div>

                <div className="w-72 bg-slate-900/50 border border-slate-800 rounded-lg p-5 flex flex-col items-center justify-center text-center">
                  <Clock className="w-6 h-6 text-slate-600 mb-3" />
                  <span className="text-[10px] font-bold text-slate-500 uppercase tracking-widest mb-1">Time to TCA</span>
                  <div className="text-3xl font-mono font-bold text-slate-100 mb-2">{countdown}</div>
                  <div className="text-[10px] text-slate-400 font-mono">
                    {new Date(selectedEvent.TCA).toLocaleString()}
                  </div>
                </div>
              </div>

              {/* Main Visualizations Row */}
              <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                <div className="lg:col-span-2 space-y-4">
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center gap-2">
                      <BarChart3 className="w-4 h-4 text-cyan-400" />
                      <h3 className="text-xs font-bold text-slate-400 uppercase tracking-widest">Encounter Probability Trend</h3>
                    </div>
                    <div className="flex items-center gap-3">
                      <div className="flex items-center gap-1.5">
                        <div className="w-2 h-2 rounded-full bg-cyan-400" />
                        <span className="text-[10px] text-slate-500">PC (Log)</span>
                      </div>
                      <div className="flex items-center gap-1.5">
                        <div className="w-2 h-2 rounded-full bg-rose-400" />
                        <span className="text-[10px] text-slate-500">Range (m)</span>
                      </div>
                    </div>
                  </div>
                  <ProbabilityChart data={chartData} />
                </div>
                
                <div className="space-y-4">
                  <h3 className="text-xs font-bold text-slate-400 uppercase tracking-widest">Relative Orbital Dynamics</h3>
                  <OrbitalViz id={selectedEvent.SAT_2.ID.toString()} missDistance={selectedEvent.MIN_RANGE} />
                  <div className="p-4 bg-slate-900/30 border border-slate-800 rounded text-[10px] leading-relaxed text-slate-500">
                    <div className="flex items-center gap-2 mb-2 text-slate-400 font-bold">
                      <AlertTriangle className="w-3 h-3 text-amber-500" />
                      COVARIANCE WARNING
                    </div>
                    Collision probability computed using 3D spatial encounter modeling. Covariance ellipsoids represent 3-sigma position uncertainty based on TLE propagation accuracy.
                  </div>
                </div>
              </div>

              {/* AI Analysis and Data Table */}
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <div className="bg-slate-900/40 border border-slate-800 rounded-lg p-5 flex flex-col">
                  <div className="flex items-center justify-between mb-6">
                    <div className="flex items-center gap-2">
                      <Cpu className="w-4 h-4 text-cyan-400" />
                      <h3 className="text-xs font-bold text-slate-300 uppercase tracking-widest">AI Risk Interpreter</h3>
                    </div>
                    <button 
                      onClick={handleFetchAiAnalysis}
                      disabled={isAnalyzing}
                      className="px-3 py-1.5 bg-cyan-950 border border-cyan-800 text-cyan-400 rounded text-[10px] font-bold uppercase hover:bg-cyan-900 transition-colors disabled:opacity-50"
                    >
                      {isAnalyzing ? 'GENERATING...' : 'RERUN ASSESSMENT'}
                    </button>
                  </div>
                  
                  <div className="flex-1 min-h-[160px] bg-slate-950/50 rounded border border-slate-800 p-4 font-mono text-[11px] leading-relaxed text-slate-400 overflow-y-auto">
                    {aiAnalysis ? (
                      <p className="animate-in fade-in duration-700">{aiAnalysis}</p>
                    ) : isAnalyzing ? (
                      <div className="flex flex-col gap-2">
                        <div className="h-2 w-full bg-slate-800 rounded animate-pulse" />
                        <div className="h-2 w-[90%] bg-slate-800 rounded animate-pulse" />
                        <div className="h-2 w-[95%] bg-slate-800 rounded animate-pulse" />
                        <div className="h-2 w-[70%] bg-slate-800 rounded animate-pulse" />
                      </div>
                    ) : (
                      <div className="flex flex-col items-center justify-center h-full opacity-30 italic">
                        Click "Run Assessment" for automated orbital interpretation
                      </div>
                    )}
                  </div>
                </div>

                <div className="bg-slate-900/40 border border-slate-800 rounded-lg p-5">
                  <div className="flex items-center justify-between mb-4">
                    <div className="flex items-center gap-2">
                      <FileText className="w-4 h-4 text-slate-400" />
                      <h3 className="text-xs font-bold text-slate-300 uppercase tracking-widest">CDM Ledger</h3>
                    </div>
                    <div className="flex gap-2">
                      <button 
                        onClick={handleDownloadJSON}
                        className="flex items-center gap-2 px-3 py-1 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded text-[10px] font-bold uppercase transition-colors"
                      >
                        <Download className="w-3 h-3" /> JSON
                      </button>
                    </div>
                  </div>
                  
                  <div className="overflow-hidden border border-slate-800 rounded">
                    <table className="w-full text-[10px] text-left">
                      <thead className="bg-slate-950 text-slate-500 font-bold uppercase">
                        <tr>
                          <th className="px-3 py-2 border-b border-slate-800">CDM ID</th>
                          <th className="px-3 py-2 border-b border-slate-800">Telemetry Date</th>
                          <th className="px-3 py-2 border-b border-slate-800 text-right">Range (m)</th>
                          <th className="px-3 py-2 border-b border-slate-800 text-right">Prob.</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-slate-800">
                        {selectedEvent.CDMS.map((record, i) => (
                          <tr key={i} className="hover:bg-slate-900/80 transition-colors">
                            <td className="px-3 py-2 font-mono text-slate-400">{record.CDM_ID}</td>
                            <td className="px-3 py-2 text-slate-500">{new Date(record.CREATED).toLocaleDateString()}</td>
                            <td className="px-3 py-2 text-right text-slate-300">{record.MIN_RNG.toLocaleString()}</td>
                            <td className="px-3 py-2 text-right text-cyan-400 font-mono">{record.PC.toExponential(2)}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              </div>
              
              {/* Secondary Satellite Metadata */}
              <div className="p-4 bg-cyan-950/10 border border-cyan-900/50 rounded-lg flex items-center justify-between">
                <div className="flex items-center gap-4">
                  <div className="p-2 bg-cyan-950 rounded border border-cyan-800">
                    <AlertTriangle className="w-5 h-5 text-cyan-400" />
                  </div>
                  <div>
                    <h4 className="text-xs font-bold text-cyan-100 uppercase mb-1">SECONDARY OBJECT PROFILE: {selectedEvent.SAT_2.NAME}</h4>
                    <p className="text-[10px] text-cyan-500 uppercase font-bold tracking-widest">
                      ID: {selectedEvent.SAT_2.ID} • TYPE: {selectedEvent.SAT_2.OBJ_TYP} • RCS: {selectedEvent.SAT_2.RCS} • EXCL_VOL: {selectedEvent.SAT_2.EXCL_VOL}
                    </p>
                  </div>
                </div>
                <button className="flex items-center gap-2 px-4 py-2 text-[10px] font-bold text-cyan-400 uppercase border border-cyan-800 hover:bg-cyan-900/50 transition-all rounded">
                  <ExternalLink className="w-3 h-3" /> Space-Track.org Profile
                </button>
              </div>
            </div>
          )}
        </div>
      </main>
    </div>
  );
};

export default App;
