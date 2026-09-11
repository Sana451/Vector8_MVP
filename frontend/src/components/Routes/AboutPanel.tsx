import { useState } from "react";
import { ChevronDown, Info } from "lucide-react";

const POINTS = [
  [
    "Архитектура",
    "FastAPI + SQLAlchemy 2.0 (async) + asyncpg, миграции через Alembic. Роуты, сервисы и модели разнесены по слоям — не один main.py.",
  ],
  [
    "Внешний вызов",
    "Маршрут считает публичный OSRM (router.project-osrm.org), результат сохраняется в PostgreSQL 16.",
  ],
  [
    "Контракт",
    "POST /api/v1/routes/ принимает {start_lat, start_lon, end_lat, end_lon}, возвращает дистанцию (м/мили) и время (с/часы) плюс полную геометрию GeoJSON.",
  ],
  [
    "Деплой",
    "Backend и frontend — два независимых контейнера в одном docker-compose, адрес API задаётся через переменные окружения.",
  ],
];

export function AboutPanel() {
  const [open, setOpen] = useState(false);

  return (
    <section className="block about-block">
      <button
        className="about-toggle"
        onClick={() => setOpen((o) => !o)}
      >
        <Info size={14} />
        <span>О проекте</span>
        <ChevronDown size={14} className={`chev ${open ? "open" : ""}`} />
      </button>
      {open && (
        <dl className="about-list">
          {POINTS.map(([k, v]) => (
            <div className="about-row" key={k}>
              <dt>{k}</dt>
              <dd>{v}</dd>
            </div>
          ))}
        </dl>
      )}
    </section>
  );
}

