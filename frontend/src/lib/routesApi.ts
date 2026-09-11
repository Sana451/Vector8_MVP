const OSRM_URL = "https://router.project-osrm.org";
const METERS_PER_MILE = 1609.344;

export async function pingBackend(apiBase: string): Promise<boolean> {
  try {
    const ctrl = new AbortController();
    const t = setTimeout(() => ctrl.abort(), 1500);
    const res = await fetch(`${apiBase}/docs`, {
      signal: ctrl.signal,
      mode: "cors",
    });
    clearTimeout(t);
    return res.ok;
  } catch {
    return false;
  }
}

export interface Coordinates {
  lat: number;
  lon: number;
}

export interface RouteResult {
  distance_meters: number;
  distance_miles: number;
  duration_seconds: number;
  duration_hours: number;
  id?: string;
  geometry?: {
    type: string;
    coordinates: Array<[number, number]>;
  };
}

export async function callBackend(
  apiBase: string,
  start: Coordinates,
  end: Coordinates,
  timeoutMs: number
): Promise<RouteResult> {
  const ctrl = new AbortController();
  const t = setTimeout(() => ctrl.abort(), timeoutMs);
  try {
    const res = await fetch(`${apiBase}/api/v1/routes/`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        start_lat: start.lat,
        start_lon: start.lon,
        end_lat: end.lat,
        end_lon: end.lon,
      }),
      signal: ctrl.signal,
    });
    clearTimeout(t);
    if (!res.ok) throw new Error(`backend ${res.status}`);
    const data = await res.json();
    return {
      distance_meters: data.distance_meters,
      distance_miles: data.distance_meters / METERS_PER_MILE,
      duration_seconds: data.duration_seconds,
      duration_hours: data.duration_seconds / 3600,
      id: data.id,
      geometry: data.geometry,
    };
  } catch (err) {
    clearTimeout(t);
    throw err;
  }
}

// Mirrors the backend's own formulas exactly — used only when the
// backend container isn't reachable, so the preview still works standalone.
export async function callOsrmDirect(
  start: Coordinates,
  end: Coordinates
): Promise<RouteResult> {
  const url =
    `${OSRM_URL}/route/v1/driving/` +
    `${start.lon},${start.lat};${end.lon},${end.lat}` +
    `?overview=false`;
  const res = await fetch(url);
  if (!res.ok) throw new Error(`OSRM ${res.status}`);
  const data = await res.json();
  if (!data.routes || !data.routes.length)
    throw new Error("нет маршрута между точками");
  const route = data.routes[0];
  return {
    distance_meters: route.distance,
    distance_miles: route.distance / METERS_PER_MILE,
    duration_seconds: route.duration,
    duration_hours: route.duration / 3600,
  };
}

// Geometry isn't part of the backend's response schema yet, so it's always
// fetched separately, purely to draw the line on the map.
export async function fetchRouteGeometry(
  start: Coordinates,
  end: Coordinates
): Promise<Array<[number, number]> | null> {
  const url =
    `${OSRM_URL}/route/v1/driving/` +
    `${start.lon},${start.lat};${end.lon},${end.lat}` +
    `?overview=full&geometries=geojson`;
  const res = await fetch(url);
  if (!res.ok) return null;
  const data = await res.json();
  const coords = data.routes?.[0]?.geometry?.coordinates;
  if (!coords) return null;
  return coords.map(([lon, lat]: [number, number]) => [lat, lon]);
}

