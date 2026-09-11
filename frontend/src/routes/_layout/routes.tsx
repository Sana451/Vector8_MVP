import { useEffect, useState } from "react";
import { createFileRoute } from "@tanstack/react-router";
import { TopBar } from "@/components/Routes/TopBar";
import { MapPanel } from "@/components/Routes/MapPanel";
import { PresetChips } from "@/components/Routes/PresetChips";
import { CoordForm } from "@/components/Routes/CoordForm";
import { StatsPanel } from "@/components/Routes/StatsPanel";
import { JsonPanel } from "@/components/Routes/JsonPanel";
import { AboutPanel } from "@/components/Routes/AboutPanel";
import { PRESETS } from "@/lib/routePresets";
import { useRouteBuilder } from "@/hooks/useRouteBuilder";
import "@/styles/routes.css";
import type { Coordinates } from "@/lib/routesApi";

export const Route = createFileRoute("/_layout/routes")({
  component: RoutesPage,
});

function RoutesPage() {
  const API_BASE_URL = "http://localhost:8000";
  const TIMEOUT_MS = 5000;

  const [activeIndex, setActiveIndex] = useState(0);
  const [coords, setCoords] = useState<{
    start: Coordinates;
    end: Coordinates;
  }>({ start: PRESETS[0].start, end: PRESETS[0].end });

  const { status, result, geometry, loading, error, source, build, checkBackend } =
    useRouteBuilder(API_BASE_URL, TIMEOUT_MS);

  useEffect(() => {
    checkBackend();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // Build the first preset once on load so the preview never opens empty.
  useEffect(() => {
    build(PRESETS[0].start, PRESETS[0].end);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const selectPreset = (i: number) => {
    setActiveIndex(i);
    setCoords({ start: PRESETS[i].start, end: PRESETS[i].end });
    build(PRESETS[i].start, PRESETS[i].end);
  };

  const handleChange = (side: "start" | "end", field: "lat" | "lon", value: string) => {
    setActiveIndex(-1);
    setCoords((c) => ({
      ...c,
      [side]: { ...c[side], [field]: parseFloat(value) },
    }));
  };

  const handleSubmit = () => {
    const { start, end } = coords;
    if ([start.lat, start.lon, end.lat, end.lon].some((v) => Number.isNaN(v))) return;
    build(start, end);
  };

  const caption = loading
    ? "Запрашиваем маршрут…"
    : error
      ? "Ошибка запроса"
      : source === "backend"
        ? "Маршрут получен и сохранён через route-service API"
        : source === "demo"
          ? "Демо-режим: маршрут запрошен напрямую у OSRM (тот же расчёт, что и в бэкенде)"
          : "Выберите точки маршрута, чтобы увидеть результат";

  return (
    <div className="app-shell">
      <TopBar status={status} />
      <main className="layout">
        <MapPanel start={coords.start} end={coords.end} geometry={geometry} caption={caption} />
        <aside className="console-panel">
          <section className="block">
            <h2 className="block-title">Маршрут</h2>
            <PresetChips presets={PRESETS} activeIndex={activeIndex} onSelect={selectPreset} />
            <CoordForm
              start={coords.start}
              end={coords.end}
              onChange={handleChange}
              onSubmit={handleSubmit}
              loading={loading}
              error={error}
            />
          </section>
          <StatsPanel result={result} />
          <JsonPanel result={result} />
          <AboutPanel />
        </aside>
      </main>
    </div>
  );
}

