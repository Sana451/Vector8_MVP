import { useCallback, useState } from "react";
import {
  callBackend,
  callOsrmDirect,
  fetchRouteGeometry,
  pingBackend,
  type Coordinates,
  type RouteResult,
} from "@/lib/routesApi";

export interface StatusInfo {
  kind: "checking" | "live" | "demo";
  label: string;
}

export function useRouteBuilder(apiBase: string, timeoutMs: number) {
  const [status, setStatus] = useState<StatusInfo>({
    kind: "checking",
    label: "проверка бэкенда…",
  });
  const [result, setResult] = useState<RouteResult | null>(null);
  const [geometry, setGeometry] = useState<Array<[number, number]> | null>(
    null
  );
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [source, setSource] = useState<"backend" | "demo" | null>(null);

  const checkBackend = useCallback(async () => {
    const ok = await pingBackend(apiBase);
    setStatus(
      ok
        ? { kind: "live", label: `бэкенд на ${apiBase}` }
        : { kind: "demo", label: "демо-режим (прямой вызов OSRM)" }
    );
    return ok;
  }, [apiBase]);

  const build = useCallback(
    async (start: Coordinates, end: Coordinates) => {
      setLoading(true);
      setError("");
      setGeometry(null);

      let res: RouteResult;
      let src: "backend" | "demo";
      try {
        res = await callBackend(apiBase, start, end, timeoutMs);
        src = "backend";
        setStatus({ kind: "live", label: `бэкенд на ${apiBase}` });
      } catch {
        try {
          res = await callOsrmDirect(start, end);
          src = "demo";
          setStatus({
            kind: "demo",
            label: "демо-режим (прямой вызов OSRM)",
          });
        } catch (err) {
          const message = err instanceof Error ? err.message : String(err);
          setError("Не удалось построить маршрут: " + message);
          setLoading(false);
          return;
        }
      }

      setResult(res);
      setSource(src);
      setLoading(false);

      fetchRouteGeometry(start, end).then(setGeometry);
    },
    [apiBase, timeoutMs]
  );

  return { status, result, geometry, loading, error, source, build, checkBackend };
}

