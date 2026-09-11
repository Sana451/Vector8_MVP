import { useCountUp } from "@/hooks/useCountUp";
import type { RouteResult } from "@/lib/routesApi";

interface StatsPanelProps {
  result: RouteResult | null;
}

export function StatsPanel({ result }: StatsPanelProps) {
  const miles = useCountUp(result?.distance_miles ?? 0, 1);
  const hours = useCountUp(result?.duration_hours ?? 0, 2);

  if (!result) return null;

  return (
    <section className="block stats-block">
      <h2 className="block-title">Результат</h2>
      <div className="stats-grid">
        <div className="stat">
          <span className="stat-value">{miles}</span>
          <span className="stat-unit">миль</span>
          <span className="stat-sub">
            {Math.round(result.distance_meters).toLocaleString("ru-RU")} м
          </span>
        </div>
        <div className="stat">
          <span className="stat-value">{hours}</span>
          <span className="stat-unit">часов в пути</span>
          <span className="stat-sub">
            {Math.round(result.duration_seconds).toLocaleString("ru-RU")} сек
          </span>
        </div>
      </div>
    </section>
  );
}

