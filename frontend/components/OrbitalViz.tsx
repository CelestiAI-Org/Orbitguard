
import React, { useEffect, useRef } from 'react';
import * as d3 from 'd3';

interface Props {
  id: string;
  missDistance: number;
}

const OrbitalViz: React.FC<Props> = ({ id, missDistance }) => {
  const svgRef = useRef<SVGSVGElement | null>(null);

  useEffect(() => {
    if (!svgRef.current) return;

    const width = 300;
    const height = 300;
    const center = { x: width / 2, y: height / 2 };
    const maxRange = 2000; // Visualization boundary in meters
    const scale = d3.scaleLinear().domain([0, maxRange]).range([0, width / 2.5]);

    const svg = d3.select(svgRef.current);
    svg.selectAll('*').remove();

    // Create radar circles
    const circles = [500, 1000, 1500, 2000];
    svg.selectAll('.grid-circle')
      .data(circles)
      .enter()
      .append('circle')
      .attr('cx', center.x)
      .attr('cy', center.y)
      .attr('r', d => scale(d))
      .attr('fill', 'none')
      .attr('stroke', '#1e293b')
      .attr('stroke-width', 1);

    // Crosshairs
    svg.append('line')
      .attr('x1', center.x - width/2)
      .attr('y1', center.y)
      .attr('x2', center.x + width/2)
      .attr('y2', center.y)
      .attr('stroke', '#0f172a');
    svg.append('line')
      .attr('x1', center.x)
      .attr('y1', center.y - height/2)
      .attr('x2', center.x)
      .attr('y2', center.y + height/2)
      .attr('stroke', '#0f172a');

    // Labels for range
    svg.selectAll('.label')
      .data(circles)
      .enter()
      .append('text')
      .attr('x', center.x + scale(50))
      .attr('y', d => center.y - scale(d) - 2)
      .text(d => `${d}m`)
      .attr('fill', '#334155')
      .attr('font-size', '8px');

    // Primary Satellite (Center)
    svg.append('circle')
      .attr('cx', center.x)
      .attr('cy', center.y)
      .attr('r', 6)
      .attr('fill', '#22d3ee')
      .attr('filter', 'drop-shadow(0 0 5px #22d3ee)');
    
    svg.append('text')
      .attr('x', center.x + 10)
      .attr('y', center.y + 4)
      .text('PRIMARY')
      .attr('fill', '#22d3ee')
      .attr('font-size', '10px')
      .attr('font-weight', 'bold');

    // Calculate secondary position (random but deterministic for this ID)
    const seed = id.split('').reduce((acc, char) => acc + char.charCodeAt(0), 0);
    const angle = (seed % 360) * (Math.PI / 180);
    const cappedDistance = Math.min(missDistance, maxRange);
    const secX = center.x + scale(cappedDistance) * Math.cos(angle);
    const secY = center.y + scale(cappedDistance) * Math.sin(angle);

    // Covariance Ellipsoid (Mockup)
    svg.append('ellipse')
      .attr('cx', secX)
      .attr('cy', secY)
      .attr('rx', 25)
      .attr('ry', 15)
      .attr('transform', `rotate(${angle * (180/Math.PI)}, ${secX}, ${secY})`)
      .attr('fill', '#ef444433')
      .attr('stroke', '#ef4444')
      .attr('stroke-dasharray', '2 2');

    // Secondary Object
    svg.append('rect')
      .attr('x', secX - 4)
      .attr('y', secY - 4)
      .attr('width', 8)
      .attr('height', 8)
      .attr('fill', '#f43f5e');

    svg.append('text')
      .attr('x', secX + 10)
      .attr('y', secY + 4)
      .text('SECONDARY')
      .attr('fill', '#f43f5e')
      .attr('font-size', '10px');

    // Miss Vector Line
    svg.append('line')
      .attr('x1', center.x)
      .attr('y1', center.y)
      .attr('x2', secX)
      .attr('y2', secY)
      .attr('stroke', '#64748b')
      .attr('stroke-width', 1)
      .attr('stroke-dasharray', '4 4');

    // Distance Badge
    svg.append('rect')
      .attr('x', (center.x + secX)/2 - 30)
      .attr('y', (center.y + secY)/2 - 10)
      .attr('width', 60)
      .attr('height', 20)
      .attr('rx', 4)
      .attr('fill', '#020617')
      .attr('stroke', '#1e293b');

    svg.append('text')
      .attr('x', (center.x + secX)/2)
      .attr('y', (center.y + secY)/2 + 4)
      .attr('text-anchor', 'middle')
      .text(`${missDistance.toFixed(1)}m`)
      .attr('fill', '#94a3b8')
      .attr('font-size', '10px');

  }, [id, missDistance]);

  return (
    <div className="flex flex-col items-center bg-slate-900/50 rounded-lg border border-slate-800 p-4">
      <h4 className="text-[10px] tracking-widest text-slate-500 uppercase mb-2">Conjunction Proximity Viz</h4>
      <svg ref={svgRef} width="300" height="300" className="max-w-full h-auto" />
    </div>
  );
};

export default OrbitalViz;
