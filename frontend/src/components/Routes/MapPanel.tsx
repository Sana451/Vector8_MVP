import { useEffect, useRef } from "react";
import L from "leaflet";
import "leaflet/dist/leaflet.css";

const markerIcon = (color: string) =>
  L.divIcon({
    className: "",
    html: `<div style="width:14px;height:14px;border-radius:50%;background:${color};border:2px solid #14171a;box-shadow:0 0 0 2px ${color}55;"></div>`,
    iconSize: [14, 14],
    iconAnchor: [7, 7],
  });

interface MapPanelProps {
  start: { lat: number; lon: number } | null;
  end: { lat: number; lon: number } | null;
  geometry: Array<[number, number]> | null;
  caption: string;
}

export function MapPanel({ start, end, geometry, caption }: MapPanelProps) {
  const elRef = useRef<HTMLDivElement>(null);
  const mapRef = useRef<L.Map | null>(null);
  const startMarkerRef = useRef<L.Marker | null>(null);
  const endMarkerRef = useRef<L.Marker | null>(null);
  const lineRef = useRef<L.Polyline | null>(null);

  // Map instance is created once and lives for the component's lifetime.
  useEffect(() => {
    if (!elRef.current) return;
    const map = L.map(elRef.current, { zoomControl: true }).setView([34, -98], 4);
    L.tileLayer("https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png", {
      attribution: "&copy; OpenStreetMap &copy; CARTO",
      subdomains: "abcd",
      maxZoom: 19,
    }).addTo(map);
    mapRef.current = map;
    return () => {
      map.remove();
    };
  }, []);

  // Markers follow the current start/end coordinates.
  useEffect(() => {
    const map = mapRef.current;
    if (!map || !start || !end) return;
    if (startMarkerRef.current) map.removeLayer(startMarkerRef.current);
    if (endMarkerRef.current) map.removeLayer(endMarkerRef.current);
    startMarkerRef.current = L.marker([start.lat, start.lon], {
      icon: markerIcon("#2fa96b"),
    })
      .bindTooltip("Старт", { className: "route-tooltip" })
      .addTo(map);
    endMarkerRef.current = L.marker([end.lat, end.lon], {
      icon: markerIcon("#ffb020"),
    })
      .bindTooltip("Финиш", { className: "route-tooltip" })
      .addTo(map);
  }, [start, end]);

  // Route line redraws (with a single draw-in animation) whenever geometry changes.
  useEffect(() => {
    const map = mapRef.current;
    if (!map) return;
    if (lineRef.current) {
      map.removeLayer(lineRef.current);
      lineRef.current = null;
    }
    if (!geometry || !geometry.length) return;

    const line = L.polyline(geometry, {
      color: "#ffb020",
      weight: 4,
      opacity: 0.95,
      lineJoin: "round",
    }).addTo(map);
    lineRef.current = line;

    const path = line.getElement() as SVGPathElement | null;
    if (path) {
      const length = path.getTotalLength ? path.getTotalLength() : 2000;
      path.style.transition = "none";
      path.style.strokeDasharray = `${length}`;
      path.style.strokeDashoffset = `${length}`;
      requestAnimationFrame(() => {
        path.style.transition = "stroke-dashoffset 900ms ease";
        path.style.strokeDashoffset = "0";
      });
    }

    map.fitBounds(line.getBounds(), { padding: [40, 40] });
  }, [geometry]);

  return (
    <section className="map-panel">
      <div ref={elRef} className="map-el" />
      <div className="map-caption">
        <span>{caption}</span>
      </div>
    </section>
  );
}


