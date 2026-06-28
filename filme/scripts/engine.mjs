// inemafilme/filme — MOTOR de montagem: BEATS -> imagens (flux2-klein) + .movie.yaml + timeline.json
// Reusável. A decupagem (templates/decupagem.template.mjs) importa daqui e só preenche BEATS + meta.
// A "inteligência de direção" (câmera por emoção, durações, white-flash, transições) mora AQUI.
import { generateImage } from '/home/nmaldaner/.claude/skills/pixflow-motion/cli/genimg.mjs';
import { writeFileSync, existsSync, mkdirSync } from 'node:fs';
import { spawnSync } from 'node:child_process';
import { join } from 'node:path';

export const C = (type, o = {}) => ({ type, ...o });
export const CAP = (body, accent = '#bfe3ff') => ({ body, position: 'bottom', align: 'center', accent });
export const TITLE = (title, kicker = '', accent = '#bfe3ff') => ({ title, kicker, position: 'center', align: 'center', accent });

// emoção do contrato historia -> "energia" (define o pool de câmera/ritmo)
export const ENERGIA = {
  tensao: 'tense', misterio: 'myst', medo: 'fear', melancolia: 'melan',
  ternura: 'tender', euforia: 'fury', furia: 'fury', esperanca: 'hope',
};
// pools de câmera por energia — usa os 18 primitivos do pixflow (VARIEDADE = dinamismo).
// Energias "quentes" (fear/fury) puxam câmeras de impacto: crash_zoom, whip_pan, dolly_zoom, handheld.
const POOLS = {
  tense: ['dolly', 'whip_pan', 'push_in', 'tracking', 'handheld', 'pan'],
  myst: ['push_in', 'float', 'pull_out', 'ken_burns', 'orbit', 'tilt'],
  fear: ['handheld', 'crash_zoom', 'whip_pan', 'dolly', 'tilt'],
  melan: ['pull_out', 'ken_burns', 'crane', 'float', 'pedestal'],
  tender: ['push_in', 'ken_burns', 'float', 'pedestal'],
  fury: ['crash_zoom', 'dolly_zoom', 'whip_pan', 'handheld', 'push_in', 'tracking'],
  hope: ['aerial', 'crane', 'pull_out', 'push_in', 'ken_burns'],
};
const INT = { tense: 0.95, myst: 0.7, fear: 1.05, melan: 0.65, tender: 0.6, fury: 1.35, hope: 0.8 };
const DUR = { tense: 1.6, myst: 1.8, fear: 1.4, melan: 2.1, tender: 2.1, fury: 1.05, hope: 1.9 };
const HORIZ = ['pan', 'tracking', 'truck', 'whip_pan'];
const VERT = ['tilt', 'pedestal', 'crane'];
const energiaDe = (b) => b.energy || ENERGIA[b.emocao] || 'tense';
const camFor = (e, i) => {
  const pool = POOLS[e]; const t = pool[i % pool.length];
  const o = { intensity: +(INT[e] + ((i % 3) - 1) * 0.1).toFixed(2) };
  if (HORIZ.includes(t)) o.direction = ['left', 'right'][i % 2];
  else if (VERT.includes(t)) o.direction = e === 'hope' ? 'up' : ['up', 'down'][i % 2];
  else if (t === 'dolly') o.direction = ['forward', 'forward', 'back'][i % 3];
  if (e === 'fury') o.amplitude = 'dramatico';
  else if (['pull_out', 'ken_burns', 'float', 'crane'].includes(t)) o.amplitude = 'medio';
  return C(t, o);
};
const durFor = (e, i) => +(DUR[e] + (i % 3) * 0.15).toFixed(2);

// BEATS -> SHOTS (fan-out: cada imagem vira 1 plano; white-flash onde pedido; cartela inicial+final)
export function shotsFromBeats(BEATS, { title = 'FILME', kicker = '' } = {}) {
  const SHOTS = [{ id: 's000', kind: 'black', cam: C('push_in', { intensity: 0.4 }), look: 'noir-film', dur: 2.4, cap: TITLE(title, kicker), tout: { type: 'dip_to_black', duration: 0.5 } }];
  for (const b of BEATS) {
    const e = energiaDe(b);
    b.imgs.forEach((p, i) => {
      const id = `${b.key}_${String(i).padStart(2, '0')}`;
      const last = i === b.imgs.length - 1;
      const tout = last
        ? (['melan', 'tender', 'hope', 'myst'].includes(e) ? { type: 'crossfade', duration: 0.5 } : { type: 'dip_to_black', duration: 0.4 })
        : { type: 'cut' };
      const shot = { id, prompt: p, cam: camFor(e, i), look: b.look, dur: durFor(e, i), tout };
      if (b.caps && b.caps[i] !== undefined) shot.cap = CAP(b.caps[i]);
      SHOTS.push(shot);
      if (b.flash && b.flash.includes(i)) SHOTS.push({ id: `${b.key}_f${i}`, kind: 'white', cam: C('static', {}), look: 'acao-epico', dur: 0.1, tout: { type: 'cut' } });
    });
  }
  SHOTS.push({ id: 'sZZZ', kind: 'ember', cam: C('push_in', { intensity: 0.5 }), look: 'acao-epico', dur: 3.0, cap: TITLE(title, kicker), tout: { type: 'cut' } });
  return SHOTS;
}

const EMBER = 'dark cinematic background of glowing blue and teal embers and floating sparks rising through black mist, deep pure black background, atmospheric particles, no text, empty center';
function solidColor(path, color) {
  if (existsSync(path)) return;
  const r = spawnSync('ffmpeg', ['-y', '-loglevel', 'error', '-f', 'lavfi', '-i', `color=c=${color}:s=1280x720`, '-frames:v', '1', path]);
  if (r.status !== 0) throw new Error('ffmpeg solid ' + color);
}

// monta tudo: gera imagens + escreve yaml + timeline. opts: { root, project, title, kicker, style, width, height, fps, noImg }
export async function montarFilme(BEATS, opts) {
  const { root, project, title = 'FILME', kicker = '', width = 1280, height = 720, fps = 30, noImg = false } = opts;
  const style = opts.style || 'cinematic, hyperrealistic, epic dramatic volumetric lighting, vibrant colors, high detail, film grain, shallow depth of field, strong foreground / midground / deep background separation for parallax, dynamic composition, no text';
  const ASSETS = join(root, 'assets'); mkdirSync(ASSETS, { recursive: true });
  const SHOTS = shotsFromBeats(BEATS, { title, kicker });

  if (!noImg) {
    if (SHOTS.some((s) => s.kind === 'ember')) { const e = join(ASSETS, 'ember.png'); if (!existsSync(e)) { process.stdout.write('-> ember ... '); await generateImage(e, EMBER, { model: 'flux2-klein', width, height, steps: 4, seed: 700 }); console.log('ok'); } }
    if (SHOTS.some((s) => s.kind === 'black')) solidColor(join(ASSETS, 'black.png'), 'black');
    if (SHOTS.some((s) => s.kind === 'white')) solidColor(join(ASSETS, 'white.png'), 'white');
    let seed = 1000;
    for (const s of SHOTS) {
      seed++;
      if (s.reuse || s.kind) continue;
      const out = join(ASSETS, `${s.id}.png`);
      if (existsSync(out)) { console.log(`-> ${s.id} (ja existe)`); continue; }
      process.stdout.write(`-> ${s.id} ... `);
      await generateImage(out, `${s.prompt}, ${style}`, { model: 'flux2-klein', width, height, steps: 4, seed });
      console.log('ok');
    }
  }

  const fileFor = (s) => s.kind === 'ember' ? 'assets/ember.png' : s.kind === 'black' ? 'assets/black.png' : s.kind === 'white' ? 'assets/white.png' : s.reuse ? `assets/${s.reuse}.png` : `assets/${s.id}.png`;
  const y = (o) => JSON.stringify(o);
  const imgs = SHOTS.map((s) => `    - { id: ${s.id}, file: ${fileFor(s)} }`).join('\n');
  const scenes = SHOTS.map((s) => {
    const lines = [`  - id: ${s.id}`, `    image: ${s.id}`, `    look: ${s.look}`, `    duration: ${s.dur}`, `    camera: ${y(s.cam)}`];
    if (s.cap) lines.push(`    caption: ${y(s.cap)}`);
    lines.push(`    transition_out: ${y(s.tout || { type: 'cut' })}`);
    return lines.join('\n');
  }).join('\n\n');
  const yaml = `# ${title} — pixflow.movie/v1 (inemafilme/filme)
schema: pixflow.movie/v1
meta: { title: ${title}, author: nmaldaner }
output: { resolution: ${width}x${height}, fps: ${fps}, filename: ${project}.mp4 }
defaults: { look: cinema-dramatico, transition_out: { type: cut } }
audio: { track: trilha.wav, volume: 0.9 }
assets:
  images:
${imgs}
scenes:
${scenes}
`;
  writeFileSync(join(root, `${project}.movie.yaml`), yaml);

  // timeline (mesma lógica do layout) — expõe MARCOS p/ o áudio (climaxStart etc.)
  const sec = (v) => Math.max(1, Math.round((v || 0) * fps));
  let cursor = 0; const tl = [];
  SHOTS.forEach((s, i) => {
    const durF = sec(s.dur); const prev = SHOTS[i - 1];
    const tName = prev?.tout?.type; const tDur = prev?.tout?.duration ?? 0.5;
    const fadeIn = (i > 0 && tName && tName !== 'cut') ? sec(tDur) : 0;
    const from = i === 0 ? 0 : cursor - fadeIn;
    tl.push({ id: s.id, start: +(from / fps).toFixed(3), dur: s.dur, kind: s.kind || 'img', beat: s.id.split('_')[0] });
    cursor = from + durF;
  });
  const beatStart = {};
  for (const b of BEATS) { const f = tl.find((x) => x.id === `${b.key}_00`); if (f) beatStart[b.key] = f.start; }
  const find = (id) => tl.find((x) => x.id === id)?.start;
  const timeline = { fps, totalSec: +(cursor / fps).toFixed(3), scenes: tl, beatStart, marks: { worldStart: find(`${BEATS[0]?.key}_00`), titleFinal: find('sZZZ') } };
  writeFileSync(join(root, 'timeline.json'), JSON.stringify(timeline, null, 2));

  const imgCount = SHOTS.filter((s) => !s.kind && !s.reuse).length;
  console.log(`\nYAML + timeline. ${SHOTS.length} planos, ${imgCount} imagens, total ~${timeline.totalSec}s.`);
  return timeline;
}
