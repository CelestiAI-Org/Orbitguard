
import React from 'react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  ReferenceLine,
} from 'recharts';
import { ChartDataPoint } from '../types';

interface Props {
  data: ChartDataPoint[];
  threshold?: number;
}

const CustomTooltip = ({ active, payload, label }: any) => {
  if (active && payload && payload.length) {
    return (
      <div className="bg-slate-900 border border-slate-700 p-3 shadow-xl rounded-sm">
        <p className="text-xs text-slate-400 mb-1">{new Date(label).toLocaleString()}</p>
        <p className="text-sm font-bold text-cyan-400">
          PC: {payload[0].value.toExponential(4)}
        </p>
        {payload[1] && (
          <p className="text-sm font-bold text-rose-400">
            Range: {payload[1].value.toLocaleString()}m
          </p>
        )}
      </div>
    );
  }
  return null;
};

const ProbabilityChart: React.FC<Props> = ({ data, threshold = 1e-4 }) => {
  if (!data || data.length === 0) {
    return (
      <div className="h-64 flex items-center justify-center border border-dashed border-slate-800 rounded bg-slate-900/30 text-slate-500 italic">
        Insufficient telemetry for trend analysis
      </div>
    );
  }

  return (
    <div className="w-full h-80 bg-slate-950/50 p-4 rounded-lg border border-slate-800 shadow-inner">
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={data}>
          <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
          <XAxis 
            dataKey="timestamp" 
            stroke="#64748b" 
            tick={{ fontSize: 10 }}
            tickFormatter={(val) => new Date(val).toLocaleDateString([], { month: 'short', day: 'numeric' })}
          />
          <YAxis 
            yAxisId="left"
            orientation="left"
            stroke="#22d3ee" 
            tick={{ fontSize: 10 }}
            domain={[0, 'auto']}
            scale="auto"
            name="Probability"
          />
          <YAxis 
            yAxisId="right"
            orientation="right"
            stroke="#fb7185" 
            tick={{ fontSize: 10 }}
            name="Range"
          />
          <Tooltip content={<CustomTooltip />} />
          <Legend wrapperStyle={{ paddingTop: '10px', fontSize: '10px' }} />
          <ReferenceLine 
            yAxisId="left" 
            y={threshold} 
            stroke="#ef4444" 
            strokeDasharray="5 5"
            label={{ position: 'right', value: 'High Risk', fill: '#ef4444', fontSize: 10 }}
          />
          <Line
            yAxisId="left"
            type="monotone"
            dataKey="value"
            name="Collision Prob."
            stroke="#22d3ee"
            strokeWidth={2}
            dot={{ r: 3, fill: '#22d3ee' }}
            activeDot={{ r: 5 }}
          />
          <Line
            yAxisId="right"
            type="monotone"
            dataKey="range"
            name="Miss Distance (m)"
            stroke="#fb7185"
            strokeWidth={1}
            strokeDasharray="3 3"
            dot={{ r: 2 }}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
};

export default ProbabilityChart;
