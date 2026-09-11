import { useEffect, useState } from "react";

export function useCountUp(
  target: number,
  decimals: number = 0,
  duration: number = 600
): string {
  const [current, setCurrent] = useState(0);

  useEffect(() => {
    if (target === 0) {
      setCurrent(0);
      return;
    }

    const startTime = Date.now();
    const startValue = current;
    const difference = target - startValue;

    const interval = setInterval(() => {
      const elapsed = Date.now() - startTime;
      const progress = Math.min(elapsed / duration, 1);

      const newValue = startValue + difference * progress;
      setCurrent(newValue);

      if (progress === 1) {
        clearInterval(interval);
      }
    }, 16); // ~60fps

    return () => clearInterval(interval);
  }, [target, current, duration, decimals]);

  return current.toFixed(decimals);
}

