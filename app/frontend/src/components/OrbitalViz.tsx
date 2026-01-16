import React, { useEffect, useRef } from 'react';
import * as d3 from 'd3';

interface Props {
  id: string; // Use ID to seed the random visual angle
  missDistance: number;
}

const OrbitalViz: React.FC<Props> = ({ id, missDistance }) => {
  const svgRef = useRef<SVGSVGElement>(null);

  useEffect(() => {
    if (!svgRef.current) return;

    const svg = d3.select(svgRef.current);
    svg.selectAll("*").remove();

    const width = 300;
    const height = 200;
    const centerX = width / 2;
    const centerY = height / 2;

    // Background Grid (Radar style)
    const rings = [50, 100, 150]; // Arbitrary scale units
    rings.forEach(r => {
      svg.append("circle")
        .attr("cx", centerX)
        .attr("cy", centerY)
        .attr("r", r * 0.8)
        .attr("fill", "none")
        .attr("stroke", "#1e293b")
        .attr("stroke-width", 1);
    });

    // Crosshairs
    svg.append("line")
      .attr("x1", centerX - 140).attr("y1", centerY)
      .attr("x2", centerX + 140).attr("y2", centerY)
      .attr("stroke", "#1e293b");
    
    svg.append("line")
      .attr("x1", centerX).attr("y1", centerY - 90)
      .attr("x2", centerX).attr("y2", centerY + 90)
      .attr("stroke", "#1e293b");

    // Primary Object (Center) - The Asset
    svg.append("circle")
      .attr("cx", centerX)
      .attr("cy", centerY)
      .attr("r", 6)
      .attr("fill", "#22d3ee")
      .attr("stroke", "#0891b2")
      .attr("stroke-width", 2);
    
    svg.append("text")
      .attr("x", centerX + 10)
      .attr("y", centerY + 4)
      .text("ASSET")
      .attr("fill", "#22d3ee")
      .attr("font-size", "10px")
      .attr("font-family", "monospace");

    // Secondary Object (Calculated schematic position)
    // We generate a stable pseudo-random angle based on the ID string
    const idSum = id.split('').reduce((acc, char) => acc + char.charCodeAt(0), 0);
    const angleRad = (idSum % 360) * (Math.PI / 180);

    // Scale: Let 150px = 2km (2000m) for visualization
    const scale = 120 / 2000; 
    const visualDist = Math.min(missDistance * scale, 130); // Clamp to view

    const secX = centerX + Math.cos(angleRad) * visualDist;
    const secY = centerY + Math.sin(angleRad) * visualDist;
    
    // Covariance Ellipsoid Representation (Schematic)
    // Rotated to face the center
    const rotationDeg = (idSum % 90); 

    svg.append("ellipse")
      .attr("cx", secX)
      .attr("cy", secY)
      .attr("rx", 22)
      .attr("ry", 10)
      .attr("transform", `rotate(${rotationDeg}, ${secX}, ${secY})`)
      .attr("fill", "rgba(239, 68, 68, 0.15)")
      .attr("stroke", "#ef4444")
      .attr("stroke-width", 1)
      .attr("stroke-dasharray", "4 2");

    // Secondary Point
    svg.append("circle")
      .attr("cx", secX)
      .attr("cy", secY)
      .attr("r", 4)
      .attr("fill", "#ef4444");

    // Vector line (Miss Vector)
    svg.append("line")
      .attr("x1", centerX)
      .attr("y1", centerY)
      .attr("x2", secX)
      .attr("y2", secY)
      .attr("stroke", "#475569")
      .attr("stroke-dasharray", "2 2");

    // Text Label
    svg.append("text")
      .attr("x", secX + 12)
      .attr("y", secY)
      .text(`OBJECT (${Math.round(missDistance)}m)`)
      .attr("fill", "#ef4444")
      .attr("font-size", "10px")
      .attr("font-family", "monospace");

  }, [id, missDistance]);

  return <svg ref={svgRef} width="100%" height="200" className="bg-slate-900/50 rounded border border-slate-700" />;
};

export default OrbitalViz;