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
  // Format data for Recharts - add index for proper sequencing
  const chartData = data.map((d, index) => ({
    ...d,
    index: index,
    timestampDisplay: new Date(d.timestamp).toLocaleString([], { 
      month: 'short', 
      day: 'numeric',
      hour: '2-digit', 
      minute: '2-digit' 
    }),
    // Use log10 for better visualization of small probabilities
    logValue: Math.log10(d.value),
    // Keep original value for tooltip
    originalValue: d.value
  }));

  const logThreshold = Math.log10(threshold);
  
  // Calculate appropriate interval for X-axis ticks based on data length
  const tickInterval = Math.max(1, Math.floor(chartData.length / 10));

  return (
    <div className="h-80 w-full bg-slate-900/50 border border-slate-700 rounded-md p-4 relative">
      <div className="flex justify-between items-end mb-4">
         <div>
             <h4 className="text-sm font-bold text-slate-200 uppercase tracking-widest">Collision Probability Over Time</h4>
             <p className="text-[10px] text-slate-500 font-mono mt-1">Historical CDM probability trend (X-axis: Time, Y-axis: Collision Probability)</p>
         </div>
         <div className="flex gap-4 text-xs">
            <span className="flex items-center text-slate-400 font-mono"><div className="w-2 h-2 bg-cyan-400 rounded-full mr-2"></div> CDM Events</span>
         </div>
      </div>
      <ResponsiveContainer width="100%" height="85%">
        <LineChart data={chartData} margin={{ top: 5, right: 20, left: 10, bottom: 25 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" vertical={false} />
          <XAxis 
            dataKey="index"
            stroke="#475569" 
            tick={{fontSize: 9, fill: '#64748b'}}
            axisLine={false}
            tickLine={false}
            dy={8}
            interval={tickInterval}
            tickFormatter={(value) => {
              const point = chartData[value];
              return point ? new Date(point.timestamp).toLocaleDateString([], { month: 'short', day: 'numeric' }) : '';
            }}
            label={{ value: 'Time (chronological order)', position: 'insideBottom', offset: -20, style: { fontSize: 10, fill: '#64748b' } }}
          />
          <YAxis 
            domain={['auto', 'auto']} 
            stroke="#475569" 
            tick={{fontSize: 10, fill: '#64748b'}}
            tickFormatter={(val) => `10^${Math.round(val)}`}
            axisLine={false}
            tickLine={false}
            dx={-5}
            width={50}
            label={{ value: 'Collision Probability', angle: -90, position: 'insideLeft', style: { fontSize: 10, fill: '#64748b' } }}
          />
          <Tooltip 
            contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', color: '#f8fafc', fontSize: '12px', padding: '8px 12px' }}
            formatter={(value: any, name: string, props: any) => {
              const originalValue = props.payload.originalValue;
              return [originalValue.toFixed(10), 'Probability'];
            }}
            labelFormatter={(label: any) => {
              const point = chartData[label];
              return point ? `Time: ${point.timestampDisplay}` : '';
            }}
            cursor={{ stroke: '#334155' }}
          />
          <ReferenceLine y={logThreshold} stroke="#ef4444" strokeDasharray="3 3" label={{ position: 'insideTopRight',  value: 'CRITICAL THRESHOLD', fill: '#ef4444', fontSize: 9, fontWeight: 'bold' }} />
          
          <Line 
            type="monotone" 
            dataKey="logValue" 
            stroke="#22d3ee" 
            strokeWidth={2}
            dot={{ r: 3, fill: '#0f172a', stroke: '#22d3ee', strokeWidth: 2 }}
            activeDot={{ r: 5, fill: '#22d3ee' }}
            name="Observed"
            connectNulls
            animationDuration={1500}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
};

export default ProbabilityChart;