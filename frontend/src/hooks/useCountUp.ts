import { useEffect, useRef, useState } from "react";

export function useCountUp(
  target: number,
  decimals: number = 0,
  duration: number = 600
): string {
  const [current, setCurrent] = useState(0);
  // Read via ref instead of the `current` state so the animation's own
  // setCurrent() calls don't feed back into this effect's dependencies —
  // that self-triggering restart was resetting the animation on every
  // ~16ms tick, so it only ever crept toward `target` asymptotically and
  // the interval churned forever without ever hitting the progress===1
  // exit.
  const currentRef = useRef(0);

  useEffect(() => {
    if (target === 0) {
      currentRef.current = 0;
      setCurrent(0);
      return;
    }

    const startTime = Date.now();
    const startValue = currentRef.current;
    const difference = target - startValue;

    const interval = setInterval(() => {
      const elapsed = Date.now() - startTime;
      const progress = Math.min(elapsed / duration, 1);

      const newValue = startValue + difference * progress;
      currentRef.current = newValue;
      setCurrent(newValue);

      if (progress === 1) {
        clearInterval(interval);
      }
    }, 16); // ~60fps

    return () => clearInterval(interval);
  }, [target, duration]);

  return current.toFixed(decimals);
}

