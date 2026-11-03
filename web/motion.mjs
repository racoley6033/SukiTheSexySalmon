/** Deterministic motion shared by playback and exported frames. Seconds are clip-local. */
export const CLIPS = ['still', 'idle', 'bounce', 'dance', 'travel'];
export const DURATION = 2;
export function sampleMotion(clip, seconds) {
  if (!CLIPS.includes(clip)) throw new Error(`Unknown clip: ${clip}`);
  if (!Number.isFinite(seconds)) throw new Error('Time must be finite');
  const p = ((seconds % DURATION) + DURATION) % DURATION / DURATION;
  const s = Math.sin(p * Math.PI * 2), c = Math.cos(p * Math.PI * 2);
  const pose = {x: 0, y: 0, angle: 0, sx: 1, sy: 1};
  if (clip === 'idle') { pose.y = -4 * (1-c); pose.angle = s * .018; }
  if (clip === 'bounce') { pose.y = -50 * Math.sin(p*Math.PI)**2; pose.sx = 1 + .035*c; pose.sy = 1-.035*c; }
  if (clip === 'dance') { pose.x = s*22; pose.y = -12*Math.sin(p*Math.PI*2)**2; pose.angle = s*.1; }
  if (clip === 'travel') { pose.x = s*95; pose.y = -8*Math.sin(p*Math.PI*4)**2; pose.angle = Math.sin(p*Math.PI*4)*.025; }
  return pose;
}
