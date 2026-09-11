import type { Coordinates } from "@/lib/routesApi";

interface CoordFormProps {
  start: Coordinates;
  end: Coordinates;
  onChange: (side: "start" | "end", field: "lat" | "lon", value: string) => void;
  onSubmit: () => void;
  loading: boolean;
  error: string;
}

export function CoordForm({
  start,
  end,
  onChange,
  onSubmit,
  loading,
  error,
}: CoordFormProps) {
  return (
    <div className="coord-grid">
      <div className="coord-field">
        <label>Начало маршрута</label>
        <div className="coord-inputs">
          <input
            type="number"
            step="0.0001"
            placeholder="Широта"
            value={start.lat}
            onChange={(e) => onChange("start", "lat", e.target.value)}
            disabled={loading}
          />
          <input
            type="number"
            step="0.0001"
            placeholder="Долгота"
            value={start.lon}
            onChange={(e) => onChange("start", "lon", e.target.value)}
            disabled={loading}
          />
        </div>
      </div>

      <div className="coord-field">
        <label>Конец маршрута</label>
        <div className="coord-inputs">
          <input
            type="number"
            step="0.0001"
            placeholder="Широта"
            value={end.lat}
            onChange={(e) => onChange("end", "lat", e.target.value)}
            disabled={loading}
          />
          <input
            type="number"
            step="0.0001"
            placeholder="Долгота"
            value={end.lon}
            onChange={(e) => onChange("end", "lon", e.target.value)}
            disabled={loading}
          />
        </div>
      </div>

      <button
        className="build-btn"
        onClick={onSubmit}
        disabled={loading}
      >
        {loading ? "Расчёт маршрута…" : "Построить маршрут"}
      </button>

      <p className="error-line">{error}</p>
    </div>
  );
}

