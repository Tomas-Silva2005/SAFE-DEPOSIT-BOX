import { useEffect, useRef, useState } from 'react';

const WIDTH = 65;
const CENTER = (WIDTH - 1) / 2;
const SPREAD_DECAY = 0.935;
const DAMPING = 0.38;
const CENTER_DECAY = 0.87;
const IMPULSE_DECAY = 0.74;
const LATERAL_DECAY = 0.88;
const GAMMA = 0.82;

const LEVELS =
  " .':;!i|\\/-+=*#%@&8BWM░▒▓█▄▀▌▐│─┼┤├┬┴╋╬╫╪╩╦╠╣═▁▂▃▅▆▇";

function intensityToChar(value) {
  if (value <= 0.012) return LEVELS[0];
  const t = Math.pow(Math.min(1, value), GAMMA);
  const index = Math.min(
    LEVELS.length - 1,
    Math.floor(t * (LEVELS.length - 1)),
  );
  return LEVELS[index];
}

function MouseAsciiWave() {
  const [line, setLine] = useState(() => ' '.repeat(WIDTH));
  const bufferRef = useRef(new Float32Array(WIDTH));
  const scratchRef = useRef(new Float32Array(WIDTH));
  const impulseRef = useRef(0);
  const lateralRef = useRef(0);
  const phaseRef = useRef(0);
  const frameRef = useRef(null);
  useEffect(() => {
    let lastX = null;
    let lastY = null;

    const onMove = (event) => {
      if (lastX !== null) {
        const dx = event.clientX - lastX;
        const dy = event.clientY - lastY;
        const speed = Math.hypot(dx, dy);
        impulseRef.current = Math.min(
          1.35,
          impulseRef.current + speed * 0.024 + Math.abs(dy) * 0.006,
        );
        lateralRef.current = Math.max(
          -10,
          Math.min(10, lateralRef.current + dx * 0.05),
        );
      }
      lastX = event.clientX;
      lastY = event.clientY;
    };

    const tick = () => {
      const prev = bufferRef.current;
      const next = scratchRef.current;
      phaseRef.current += 0.045;
      const idle =
        0.028 + Math.sin(phaseRef.current) * 0.018 + Math.sin(phaseRef.current * 2.3) * 0.008;

      const hotspot = Math.max(
        0,
        Math.min(WIDTH - 1, CENTER + Math.round(lateralRef.current)),
      );
      lateralRef.current *= LATERAL_DECAY;

      next[hotspot] = Math.max(
        prev[hotspot] * CENTER_DECAY,
        impulseRef.current + idle,
      );
      if (hotspot !== CENTER) {
        next[CENTER] = Math.max(prev[CENTER] * CENTER_DECAY, idle * 0.6);
      }
      impulseRef.current *= IMPULSE_DECAY;

      for (let i = 0; i < WIDTH; i += 1) {
        if (i === hotspot || (hotspot !== CENTER && i === CENTER)) continue;

        const left = i > 0 ? prev[i - 1] : 0;
        const right = i < WIDTH - 1 ? prev[i + 1] : 0;
        const spread = (left + right) * 0.5 * SPREAD_DECAY;
        const local = prev[i] * (1 - DAMPING);
        next[i] = Math.max(spread, local);
      }

      bufferRef.current = next;
      scratchRef.current = prev;

      let out = '';
      for (let i = 0; i < WIDTH; i += 1) {
        const v = next[i];
        out += intensityToChar(v);
      }
      setLine(out);
      frameRef.current = requestAnimationFrame(tick);
    };

    frameRef.current = requestAnimationFrame(tick);
    window.addEventListener('mousemove', onMove, { passive: true });

    return () => {
      window.removeEventListener('mousemove', onMove);
      if (frameRef.current) cancelAnimationFrame(frameRef.current);
    };
  }, []);

  return (
    <p className="tagline ascii-wave" aria-hidden="true">
      {line}
    </p>
  );
}

export default MouseAsciiWave;
