import type { Coordinates } from "@/lib/routesApi";

export interface Preset {
  title: string;
  start: Coordinates;
  end: Coordinates;
}

export const PRESETS: Preset[] = [
  {
    title: "Даллас → Хьюстон",
    start: { lat: 32.7767, lon: -96.797 },
    end: { lat: 29.7604, lon: -95.3698 },
  },
  {
    title: "Нью-Йорк → Лос-Анджелес",
    start: { lat: 40.7128, lon: -74.006 },
    end: { lat: 34.0522, lon: -118.2437 },
  },
  {
    title: "Сан-Франциско → Сиэтл",
    start: { lat: 37.7749, lon: -122.4194 },
    end: { lat: 47.6062, lon: -122.3321 },
  },
  {
    title: "Чикаго → Майами",
    start: { lat: 41.8781, lon: -87.6298 },
    end: { lat: 25.7617, lon: -80.1918 },
  },
];

