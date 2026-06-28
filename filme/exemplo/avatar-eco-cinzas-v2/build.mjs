// inemafilme — Avatar: O Eco das Cinzas — build V2 (mais dinamico: ~92 imagens, camera variada, white-flash)
import { generateImage } from '/home/nmaldaner/.claude/skills/pixflow-motion/cli/genimg.mjs';
import { writeFileSync, existsSync, mkdirSync } from 'node:fs';
import { spawnSync } from 'node:child_process';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = dirname(fileURLToPath(import.meta.url));
const ASSETS = join(ROOT, 'assets');
mkdirSync(ASSETS, { recursive: true });
const NOIMG = process.argv.includes('--no-img');

const PROJECT = 'avatar-eco-cinzas-v2';
const TITLE_TEXT = 'AVATAR — O ECO DAS CINZAS';
const STYLE = 'cinematic, hyperrealistic, Pandora-like alien world, bioluminescent, tall blue-skinned Na\'vi people with amber eyes, ' +
  'epic dramatic volumetric lighting, vibrant colors, high detail, film grain, shallow depth of field, ' +
  'strong foreground / midground / deep background separation for parallax, dynamic composition, no text';

const C = (type, o = {}) => ({ type, ...o });
const CAP = (body, accent = '#bfe3ff') => ({ body, position: 'bottom', align: 'center', accent });
const TITLE = (title, kicker = '', accent = '#bfe3ff') => ({ title, kicker, position: 'center', align: 'center', accent });

// pools de camera por energia (variedade = dinamismo)
const POOLS = {
  tense: ['dolly', 'pan', 'push_in', 'aerial', 'handheld'],
  myst: ['push_in', 'float', 'pull_out', 'ken_burns', 'aerial'],
  fear: ['handheld', 'push_in', 'pan', 'dolly'],
  melan: ['pull_out', 'ken_burns', 'push_in', 'float'],
  tender: ['push_in', 'ken_burns', 'float'],
  fury: ['push_in', 'dolly', 'pan', 'handheld', 'aerial'],
  hope: ['aerial', 'pull_out', 'push_in', 'ken_burns', 'float'],
};
const INT = { tense: 0.95, myst: 0.7, fear: 1.0, melan: 0.65, tender: 0.6, fury: 1.3, hope: 0.8 };
const DUR = { tense: 1.6, myst: 1.8, fear: 1.4, melan: 2.1, tender: 2.1, fury: 1.1, hope: 1.9 };
const DIRS = ['left', 'right', 'forward'];
const camFor = (e, i) => {
  const pool = POOLS[e]; const t = pool[i % pool.length];
  const o = { intensity: +(INT[e] + ((i % 3) - 1) * 0.1).toFixed(2) };
  if (t === 'pan' || t === 'dolly') o.direction = DIRS[i % 3];
  if (['pull_out', 'ken_burns', 'float'].includes(t)) o.amplitude = 'medio';
  return C(t, o);
};
const durFor = (e, i) => +(DUR[e] + (i % 3) * 0.15).toFixed(2);

const BEATS = [
  { key: 'b1', look: 'noir-film', energy: 'tense', imgs: [
    'vast petrified gray forest stretching to the horizon, dead and silent under a dim bruised sky',
    'colossal rusted alien war machine half-sunk in gray ash, dead petrified trees around it',
    'extreme close-up of cracked dead earth with a faint blue pulse glowing beneath the surface',
    'skeletal petrified trees coated in thick gray ash, eerie stillness, low fog',
    'a field of broken rusted mechs draped in ash under a colorless sky',
    'underground veins of dim blue light throbbing beneath cracked gray soil',
    'a dead river of gray ash winding between fallen war machines',
    'sweeping aerial of a scar of gray ashes cutting through a glowing bioluminescent forest',
    'ominous low-angle of a toppled colossal war machine against a stormy sky',
  ] },
  { key: 'b2', look: 'sonho-etereo', energy: 'myst', caps: { 8: 'Todos diziam que era loucura.' }, imgs: [
    'young Na\'vi girl with blue skin and gray ash birthmarks standing at the border between glowing living forest and dead gray ashland, listening',
    'close-up of the girl\'s amber glowing eyes with bioluminescent forest reflected in them',
    'the girl\'s marked hand reaching toward the gray ashland as glowing pollen drifts by',
    'over-the-shoulder view across the vast gray dead zone, a faint distant glow calling',
    'the girl silhouetted against luminescent blue flora, head tilted as if hearing something',
    'macro of glowing spores and gray ash mixing along a glowing border line',
    'her face half lit by warm forest glow, half by cold gray ash light',
    'wide shot of the tiny girl before an immense dead gray expanse',
    'her ash-gray marked arm faintly glowing in the dark, mysterious',
  ] },
  { key: 'b3', look: 'cinema-dramatico', energy: 'fear', imgs: [
    'a young Na\'vi hunter walking out of gray mist, his eyes dull and empty without any glow',
    'extreme close-up of hollow empty Na\'vi eyes, no inner light, no soul',
    'frightened villagers recoiling from the empty-eyed returnee in the gloom',
    'living glowing trees rapidly withering to pale gray, decay spreading outward fast',
    'a glowing branch turning to gray ash in fast decay, crumbling',
    'the hunter\'s vacant face lit by dying forest light',
    'wide of sick gray blight creeping into a luminous forest',
    'a young Na\'vi child watching the forest die, terrified',
    'close of trembling glowing leaves going gray and crumbling to dust',
    'the empty hunter standing motionless as life drains from everything around him',
  ] },
  { key: 'b4', look: 'sonho-etereo', energy: 'melan', caps: { 1: 'Eywa cortou um galho de si mesma.' }, imgs: [
    'a blind elderly Na\'vi shaman with white tattoos touching a young girl\'s forehead beneath a weak flickering Tree of Souls',
    'ancient weakened Tree of Souls with drooping dim flickering glowing tendrils, deep night',
    'close-up of the shaman\'s blind milky eyes, serene and sorrowful',
    'glowing roots of the sacred tree, dim and flickering in the darkness',
    'a haunting vision of Eywa severing a glowing branch of herself during the war',
    'the severed glowing branch falling into the gray ashes, its light fading',
    'the two small figures beneath the immense dim sacred tree',
    'close of the girl\'s awed, sorrowful face lit by faint tree light',
    'dim sacred glowing seeds drifting like dying fireflies in the dark',
    'wide reverent shot of the dying Tree of Souls against the night sky',
  ] },
  { key: 'b5', look: 'cinema-dramatico', energy: 'tender', imgs: [
    'extreme close-up of an elderly Na\'vi hand braiding a shining silver hair strand into a young girl\'s braids, warm firelight',
    'the girl kneeling and tenderly holding the empty-eyed friend\'s face by a low fire',
    'close-up of the silver strand shining within the dark braid',
    'firelit faces of the shaman and the girl in a quiet farewell',
    'the girl\'s determined, teary eyes lit by the fire',
    'the empty-eyed friend staring blankly as she holds his face',
    'warm embers rising from a small fire into the dark',
    'the girl rising to leave, her silhouette against the firelight',
  ] },
  { key: 'b6', look: 'sci-fi-cyberpunk', energy: 'tense', caps: { 5: 'O silencio comia as lembrancas.' }, imgs: [
    'a lone Na\'vi figure walking deep into a gray ashen wasteland of dead colossal machines',
    'dead colossal machines flickering faintly back to life around the lone figure',
    'the girl\'s silhouette beginning to lose color, her edges dissolving into gray ash',
    'close-up of her hand turning translucent and gray, ash particles peeling away',
    'glitching distorted memories flashing around her, fragments of faces and forest',
    'her footsteps fading as gray ash swallows the path behind her',
    'towering rusted machines looming overhead, blue circuits sparking',
    'her flickering face, forgetting, eyes searching the gray void',
    'a long corridor of dead machines stretching into gray nothingness',
    'distorted glitch of a forest memory dissolving into static and ash',
    'the girl smaller and grayer, almost gone, deep in the ashes',
    'a swirling vortex of ash and faint blue light pulling inward',
  ] },
  { key: 'b7', look: 'sonho-etereo', energy: 'myst', imgs: [
    'an ancient abandoned human-avatar body fused with machine cables, faint blue eyes slowly opening',
    'close-up of the pale fused avatar face, dim blue glowing eyes, immense loneliness',
    'wide metal cathedral of dead machines with a single lonely blue glow at its heart',
    'cables merging into the avatar\'s pale skin, dripping faint light',
    'the girl and the pale fused being facing each other across the void',
    'the being reaching out a trembling cabled hand',
    'flashes of others it pulled in, frozen gray figures in the dark',
    'close of its sorrowful glowing eyes, lonely not monstrous',
    'the vast lonely heart of the ashes, a dim glowing cathedral',
    'the girl\'s fading face filling with compassion as she understands',
    'the pale being surrounded by drifting ash, utterly alone',
  ] },
  { key: 'b8', look: 'acao-epico', energy: 'fury', caps: { 7: 'Em vez de fugir, ela o ouviu.' }, flash: [1, 4, 8], imgs: [
    'the girl almost fully faded to gray, gripping a shining silver strand at the last instant',
    'a burst of golden light and memory exploding outward from the girl',
    'a shockwave of light tearing through the dead machines, debris flying',
    'her amber eyes blazing back to life, full of fierce resolve',
    'a wave of memory radiating from her, sparks and embers everywhere',
    'she steps forward instead of fleeing, fierce and unafraid',
    'dead machines collapsing in cascading golden light',
    'the girl pressing her forehead to the pale being\'s forehead, light flowing between them',
    'brilliant energy surging between the two figures',
    'the being\'s lonely eyes flooding with warm golden light',
    'the collapsing core erupting in golden bioluminescence',
    'the two figures haloed in radiant light at the heart of the storm',
  ] },
  { key: 'b9', look: 'sonho-etereo', energy: 'hope', imgs: [
    'the dead gray ashland reigniting with threads of bioluminescent light at dawn',
    'fresh green glowing sprouts emerging between rusted machine wrecks',
    'a single glowing green sprout rising from cracked ash, dew drops, dawn light',
    'the Na\'vi hunter lifting his head, his eyes glowing alive again',
    'the whole scar of ashes blooming with new light, sweeping aerial at dawn',
    'the pale being dissolving peacefully into gentle warm light',
    'villagers emerging to witness the rebirth, hopeful faces',
    'the marked girl standing as a living bridge between healed forest and awakening ashland',
    'bioluminescent forest and former ashland merging in glow at dawn',
    'wide triumphant golden dawn over a healing Pandora',
  ] },
];

// ---- gera SHOTS ----
const SHOTS = [];
SHOTS.push({ id: 's000', kind: 'black', cam: C('push_in', { intensity: 0.4 }), look: 'noir-film', dur: 2.4, cap: TITLE('AVATAR', 'O Eco das Cinzas'), tout: { type: 'dip_to_black', duration: 0.5 } });
for (const b of BEATS) {
  b.imgs.forEach((p, i) => {
    const id = `${b.key}_${String(i).padStart(2, '0')}`;
    const last = i === b.imgs.length - 1;
    const tout = last
      ? (['melan', 'tender', 'hope', 'myst'].includes(b.energy) ? { type: 'crossfade', duration: 0.5 } : { type: 'dip_to_black', duration: 0.4 })
      : { type: 'cut' };
    const shot = { id, prompt: p, cam: camFor(b.energy, i), look: b.look, dur: durFor(b.energy, i), tout };
    if (b.caps && b.caps[i] !== undefined) shot.cap = CAP(b.caps[i]);
    SHOTS.push(shot);
    if (b.flash && b.flash.includes(i)) SHOTS.push({ id: `${b.key}_f${i}`, kind: 'white', cam: C('static', {}), look: 'acao-epico', dur: 0.1, tout: { type: 'cut' } });
  });
}
SHOTS.push({ id: 'sZZZ', kind: 'ember', cam: C('push_in', { intensity: 0.5 }), look: 'acao-epico', dur: 3.0, cap: TITLE('AVATAR', 'O Eco das Cinzas'), tout: { type: 'cut' } });

const EMBER = 'dark cinematic background of glowing blue and teal embers and floating bioluminescent sparks rising through black mist, deep pure black background, atmospheric particles, no text, empty center';
function solidColor(path, color) {
  if (existsSync(path)) return;
  const r = spawnSync('ffmpeg', ['-y', '-loglevel', 'error', '-f', 'lavfi', '-i', `color=c=${color}:s=1280x720`, '-frames:v', '1', path]);
  if (r.status !== 0) throw new Error('ffmpeg solid ' + color);
}
async function ensureImages() {
  if (NOIMG) return;
  if (SHOTS.some((s) => s.kind === 'ember')) { const e = join(ASSETS, 'ember.png'); if (!existsSync(e)) { process.stdout.write('-> ember ... '); await generateImage(e, `${EMBER}`, { model: 'flux2-klein', width: 1280, height: 720, steps: 4, seed: 700 }); console.log('ok'); } }
  if (SHOTS.some((s) => s.kind === 'black')) solidColor(join(ASSETS, 'black.png'), 'black');
  if (SHOTS.some((s) => s.kind === 'white')) solidColor(join(ASSETS, 'white.png'), 'white');
  let seed = 1000;
  for (const s of SHOTS) {
    seed++;
    if (s.reuse || s.kind) continue;
    const out = join(ASSETS, `${s.id}.png`);
    if (existsSync(out)) { console.log(`-> ${s.id} (ja existe)`); continue; }
    process.stdout.write(`-> ${s.id} ... `);
    await generateImage(out, `${s.prompt}, ${STYLE}`, { model: 'flux2-klein', width: 1280, height: 720, steps: 4, seed });
    console.log('ok');
  }
}

function fileFor(s) {
  if (s.kind === 'ember') return 'assets/ember.png';
  if (s.kind === 'black') return 'assets/black.png';
  if (s.kind === 'white') return 'assets/white.png';
  if (s.reuse) return `assets/${s.reuse}.png`;
  return `assets/${s.id}.png`;
}
const y = (o) => JSON.stringify(o);
function buildYaml() {
  const imgs = SHOTS.map((s) => `    - { id: ${s.id}, file: ${fileFor(s)} }`).join('\n');
  const scenes = SHOTS.map((s) => {
    const tout = s.tout || { type: 'cut' };
    const lines = [`  - id: ${s.id}`, `    image: ${s.id}`, `    look: ${s.look}`, `    duration: ${s.dur}`, `    camera: ${y(s.cam)}`];
    if (s.cap) lines.push(`    caption: ${y(s.cap)}`);
    lines.push(`    transition_out: ${y(tout)}`);
    return lines.join('\n');
  }).join('\n\n');
  return `# ${TITLE_TEXT} V2 — pixflow.movie/v1
schema: pixflow.movie/v1
meta: { title: ${TITLE_TEXT}, author: nmaldaner }
output: { resolution: 1280x720, fps: 30, filename: ${PROJECT}.mp4 }
defaults: { look: cinema-dramatico, transition_out: { type: cut } }
audio: { track: trilha.wav, volume: 0.9 }
assets:
  images:
${imgs}
scenes:
${scenes}
`;
}
function buildTimeline() {
  const fps = 30; const sec = (v) => Math.max(1, Math.round((v || 0) * fps));
  let cursor = 0; const scenes = [];
  SHOTS.forEach((s, i) => {
    const durF = sec(s.dur); const prev = SHOTS[i - 1];
    const tName = prev?.tout?.type; const tDur = prev?.tout?.duration ?? 0.5;
    const fadeIn = (i > 0 && tName && tName !== 'cut') ? sec(tDur) : 0;
    const from = i === 0 ? 0 : cursor - fadeIn;
    scenes.push({ id: s.id, start: +(from / fps).toFixed(3), dur: s.dur, toutType: s.tout?.type || 'cut', kind: s.kind || 'img' });
    cursor = from + durF;
  });
  const find = (id) => scenes.find((x) => x.id === id)?.start;
  return { fps, totalSec: +(cursor / fps).toFixed(3), scenes, marks: {
    worldStart: find('b1_00'), climaxStart: find('b8_00'), payoffStart: find('b9_00'), titleFinal: find('sZZZ'),
  } };
}
const run = async () => {
  await ensureImages();
  writeFileSync(join(ROOT, `${PROJECT}.movie.yaml`), buildYaml());
  const tl = buildTimeline();
  writeFileSync(join(ROOT, 'timeline.json'), JSON.stringify(tl, null, 2));
  const imgCount = SHOTS.filter((s) => !s.kind && !s.reuse).length;
  console.log(`\nYAML + timeline. ${SHOTS.length} planos, ${imgCount} imagens, total ~${tl.totalSec}s.`);
};
run().catch((e) => { console.error('FALHOU:', e.message); process.exit(1); });
