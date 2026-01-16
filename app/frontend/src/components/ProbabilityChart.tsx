import React from 'react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  ReferenceLine
} from 'recharts';
import { ProbabilityPoint } from '../types';

interface Props {
  data: ProbabilityPoint[];
  threshold?: number;
}

const ProbabilityChart: React.FC<Props> = ({ data, threshold = 1e-4 }) => {
  // Format data for Recharts
  const chartData = data.map(d => ({
    ...d,
    timestampDisplay: new Date(d.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    // Use log10 for better visualization of small probabilities
    logValue: Math.log10(d.value)
  }));

  const logThreshold = Math.log10(threshold);

  return (
    <div className="h-64 w-full bg-slate-900/50 border border-slate-700 rounded-md p-4 relative">
      <div className="flex justify-between items-end mb-4">
         <div>
             <h4 className="text-sm font-bold text-slate-200 uppercase tracking-widest">Collision Probability Trend</h4>
             <p className="text-[10px] text-slate-500 font-mono mt-1">Probability-based trend (derived from CDM update history, not kinematics)</p>
         </div>
         <div className="flex gap-4 text-xs">
            <span className="flex items-center text-slate-400 font-mono"><div className="w-2 h-2 bg-cyan-400 rounded-full mr-2"></div> CDM History</span>
            <span className="flex items-center text-slate-400 font-mono"><div className="w-2 h-2 bg-amber-400 rounded-full mr-2"></div> LSTM Forecast</span>
         </div>
      </div>
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={chartData}>
          <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" vertical={false} />
          <XAxis 
            dataKey="timestampDisplay" 
            stroke="#475569" 
            tick={{fontSize: 10, fill: '#64748b'}}
            axisLine={false}
            tickLine={false}
            dy={10}
          />
          <YAxis 
            domain={['auto', 'auto']} 
            stroke="#475569" 
            tick={{fontSize: 10, fill: '#64748b'}}
            tickFormatter={(val) => `10^${Math.round(val)}`}
            axisLine={false}
            tickLine={false}
            dx={-5}
            width={45} 
          />
          <Tooltip 
            contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', color: '#f8fafc', fontSize: '12px' }}
            formatter={(value: number) => [Math.pow(10, value).toExponential(2), 'Probability']}
            labelStyle={{ color: '#94a3b8', marginBottom: '4px' }}
            cursor={{ stroke: '#334155' }}
          />
          <ReferenceLine y={logThreshold} stroke="#ef4444" strokeDasharray="3 3" label={{ position: 'insideTopRight',  value: 'CRITICAL THRESHOLD', fill: '#ef4444', fontSize: 9, fontWeight: 'bold' }} />
          
          <Line 
            type="linear" 
            dataKey="logValue" 
            data={chartData.filter(d => d.source === 'OBSERVED')}
            stroke="#22d3ee" 
            strokeWidth={2}
            dot={{ r: 4, fill: '#0f172a', stroke: '#22d3ee', strokeWidth: 2 }}
            activeDot={{ r: 6, fill: '#22d3ee' }}
            name="Observed"
            connectNulls
            animationDuration={1500}
          />
           <Line 
            type="linear" 
            dataKey="logValue" 
            data={chartData.filter(d => d.source === 'PREDICTED' || d.timestamp === chartData.find(x => x.source === 'PREDICTED')?.timestamp)}
            stroke="#fbbf24" 
            strokeWidth={2}
            strokeDasharray="4 4"
            dot={{ r: 4, fill: '#0f172a', stroke: '#fbbf24', strokeWidth: 2 }}
            name="Predicted"
            animationDuration={1500}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
};

export default ProbabilityChart;