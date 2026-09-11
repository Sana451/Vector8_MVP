import type { Preset } from "@/lib/routePresets";

interface PresetChipsProps {
  presets: Preset[];
  activeIndex: number;
  onSelect: (index: number) => void;
}

export function PresetChips({ presets, activeIndex, onSelect }: PresetChipsProps) {
  return (
    <div className="presets">
      {presets.map((preset, i) => (
        <button
          key={i}
          className={`preset-chip ${activeIndex === i ? "active" : ""}`}
          onClick={() => onSelect(i)}
        >
          {preset.title}
        </button>
      ))}
    </div>
  );
}

