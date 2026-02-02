import React from 'react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  ReferenceLine,
  Legend
} from 'recharts';
import { ProbabilityPoint } from '../types';

interface ChartDataPoint {
  timestamp: string;
  value: number;
  range?: number;
  source: 'OBSERVED' | 'PREDICTED';
}

interface Props {
  data: ChartDataPoint[];
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
    originalValue: d.value,
    // Range value (already in meters)
    rangeValue: d.range
  }));

  const logThreshold = Math.log10(threshold);
  
  // Calculate appropriate interval for X-axis ticks based on data length
  const tickInterval = Math.max(1, Math.floor(chartData.length / 10));

  // Check if we have range data
  const hasRangeData = data.some(d => d.range !== undefined);

  return (
    <div className="h-96 w-full bg-slate-900/50 border border-slate-700 rounded-md p-4 relative">
      <div className="flex justify-between items-end mb-4">
         <div>
             <h4 className="text-sm font-bold text-slate-200 uppercase tracking-widest">Collision Probability & Range Over Time</h4>
             <p className="text-[10px] text-slate-500 font-mono mt-1">Historical CDM probability trend (Left Y-axis: Collision Probability, Right Y-axis: Range in meters)</p>
         </div>
         <div className="flex gap-4 text-xs">
            <span className="flex items-center text-slate-400 font-mono"><div className="w-2 h-2 bg-cyan-400 rounded-full mr-2"></div> Probability</span>
            {hasRangeData && <span className="flex items-center text-slate-400 font-mono"><div className="w-2 h-2 bg-rose-400 rounded-full mr-2"></div> Range (m)</span>}
         </div>
      </div>
      <ResponsiveContainer width="100%" height="85%">
        <LineChart data={chartData} margin={{ top: 5, right: hasRangeData ? 60 : 20, left: 10, bottom: 25 }}>
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
            yAxisId="left"
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
          {hasRangeData && (
            <YAxis 
              yAxisId="right"
              orientation="right"
              domain={['auto', 'auto']} 
              stroke="#f43f5e" 
              tick={{fontSize: 10, fill: '#f87171'}}
              tickFormatter={(val) => `${val}m`}
              axisLine={false}
              tickLine={false}
              dx={5}
              width={55}
              label={{ value: 'Range (m)', angle: 90, position: 'insideRight', style: { fontSize: 10, fill: '#f87171' } }}
            />
          )}
          <Tooltip 
            contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', color: '#f8fafc', fontSize: '12px', padding: '8px 12px' }}
            formatter={(value: any, name: string, props: any) => {
              if (name === 'Probability') {
                const originalValue = props.payload.originalValue;
                return [originalValue.toExponential(6), 'Probability'];
              } else if (name === 'Range') {
                return [`${props.payload.rangeValue}m`, 'Range'];
              }
              return [value, name];
            }}
            labelFormatter={(label: any) => {
              const point = chartData[label];
              return point ? `Time: ${point.timestampDisplay}` : '';
            }}
            cursor={{ stroke: '#334155' }}
          />
          <ReferenceLine yAxisId="left" y={logThreshold} stroke="#ef4444" strokeDasharray="3 3" label={{ position: 'insideTopRight',  value: 'CRITICAL THRESHOLD', fill: '#ef4444', fontSize: 9, fontWeight: 'bold' }} />
          
          <Line 
            yAxisId="left"
            type="monotone" 
            dataKey="logValue" 
            stroke="#22d3ee" 
            strokeWidth={2}
            dot={{ r: 3, fill: '#0f172a', stroke: '#22d3ee', strokeWidth: 2 }}
            activeDot={{ r: 5, fill: '#22d3ee' }}
            name="Probability"
            connectNulls
            animationDuration={1500}
          />
          {hasRangeData && (
            <Line 
              yAxisId="right"
              type="monotone" 
              dataKey="rangeValue" 
              stroke="#f43f5e" 
              strokeWidth={2}
              dot={{ r: 3, fill: '#0f172a', stroke: '#f43f5e', strokeWidth: 2 }}
              activeDot={{ r: 5, fill: '#f43f5e' }}
              name="Range"
              connectNulls
              animationDuration={1500}
            />
          )}
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
};

export default ProbabilityChart;