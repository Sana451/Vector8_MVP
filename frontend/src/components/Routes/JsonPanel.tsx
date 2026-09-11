import { useState } from "react";
import type { RouteResult } from "@/lib/routesApi";

function highlight(obj: RouteResult): string {
  const json = JSON.stringify(obj, null, 2);
  return json
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/"(\w+)":/g, '<span class="json-key">"$1"</span>:')
    .replace(/: "([^"]*)"/g, ': <span class="json-str">"$1"</span>')
    .replace(/: (-?\d+\.?\d*)/g, ': <span class="json-num">$1</span>');
}

interface JsonPanelProps {
  result: RouteResult | null;
}

export function JsonPanel({ result }: JsonPanelProps) {
  const [copied, setCopied] = useState(false);

  if (!result) return null;

  const copy = () => {
    navigator.clipboard.writeText(JSON.stringify(result, null, 2)).then(() => {
      setCopied(true);
      setTimeout(() => setCopied(false), 1400);
    });
  };

  return (
    <section className="block json-block">
      <div className="json-head">
        <h2 className="block-title">Ответ API</h2>
        <button className={`copy-btn ${copied ? "copied" : ""}`} onClick={copy}>
          {copied ? "Скопировано" : "Копировать"}
        </button>
      </div>
      <pre
        className="json-view"
        dangerouslySetInnerHTML={{ __html: highlight(result) }}
      />
    </section>
  );
}

