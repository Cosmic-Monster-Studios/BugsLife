// Bug's Life model builder for Blockbench (run through the Blockbench MCP `risky_eval` tool).
// Installs window.BL with build(spec) and exportAll(). Specs are produced by tools/blockbench/bugs.py.
window.BL = (function () {
  function rng(seed) {
    let s = seed >>> 0 || 1;
    return () => ((s = (s * 1664525 + 1013904223) >>> 0) / 4294967296);
  }
  function hex(c) {
    c = c.replace('#', '');
    if (c.length === 6) c += 'ff';
    return [0, 2, 4, 6].map(i => parseInt(c.substr(i, 2), 16));
  }
  function mix(a, b, t) { return a.map((v, i) => Math.round(v + (b[i] - v) * t)); }
  function shade(c, f) { return [clamp(c[0] * f), clamp(c[1] * f), clamp(c[2] * f), c[3]]; }
  function clamp(v) { return Math.max(0, Math.min(255, Math.round(v))); }
  function hsl2rgb(h, s, l) {
    const k = n => (n + h / 30) % 12, a = s * Math.min(l, 1 - l);
    const f = n => l - a * Math.max(-1, Math.min(k(n) - 3, Math.min(9 - k(n), 1)));
    return [clamp(f(0) * 255), clamp(f(8) * 255), clamp(f(4) * 255), 255];
  }

  const FACE_SHADE = { up: 1.12, down: 0.72, north: 1.0, south: 0.92, east: 0.9, west: 0.9 };

  // Paints one face rectangle into an ImageData buffer.
  function paintFace(img, W, rect, face, p, rand, mask) {
    const x0 = Math.min(rect[0], rect[2]), y0 = Math.min(rect[1], rect[3]);
    const w = Math.abs(rect[2] - rect[0]), h = Math.abs(rect[3] - rect[1]);
    if (w < 1 || h < 1) return;
    const q = Object.assign({}, p, (p.faces && p.faces[face]) || {});
    if (q.skip) return;
    const c1 = hex(q.c || '#ff00ff'), c2 = hex(q.c2 || q.c || '#000000');
    const noise = q.n === undefined ? 10 : q.n;
    const sh = q.flat ? 1 : FACE_SHADE[face];
    const pat = q.pat || 'solid';
    const per = q.per || 2;
    const spots = [];
    if (pat === 'spots') {
      const count = Math.max(1, Math.round(w * h * (q.d || 0.12)));
      for (let i = 0; i < count; i++) spots.push([Math.floor(rand() * w), Math.floor(rand() * h)]);
    }
    for (let yy = 0; yy < h; yy++) {
      for (let xx = 0; xx < w; xx++) {
        let c = c1;
        const edge = xx === 0 || yy === 0 || xx === w - 1 || yy === h - 1;
        switch (pat) {
          case 'stripe': c = (yy % per) < (q.sw || 1) ? c2 : c1; break;
          case 'vstripe': c = (xx % per) < (q.sw || 1) ? c2 : c1; break;
          case 'grad': c = mix(c1, c2, h > 1 ? yy / (h - 1) : 0); break;
          case 'hgrad': c = mix(c1, c2, w > 1 ? xx / (w - 1) : 0); break;
          case 'edge': c = edge ? c2 : c1; break;
          case 'check': c = ((xx + yy) % 2) ? c2 : c1; break;
          case 'spots': c = spots.some(s => s[0] === xx && s[1] === yy) ? c2 : c1; break;
          case 'iri': {
            const t = ((xx + yy) / Math.max(1, w + h - 2)) + (rand() - 0.5) * (q.j === undefined ? 0.25 : q.j);
            c = mix(c1, c2, Math.max(0, Math.min(1, t)));
            break;
          }
          case 'wing': {
            // translucent membrane with opaque border and veins
            const vein = (q.veins !== false) && ((xx + yy) % (q.per || 3) === 0 && rand() > 0.35);
            c = edge ? c2 : (vein ? mix(c2, c1, 0.4) : c1);
            if (q.eye && Math.abs(xx - w * 0.7) < 1.2 && Math.abs(yy - h * 0.5) < 1.2) c = hex(q.eye);
            break;
          }
          case 'monarch': {
            // orange cells separated by black veins, black border with white dots
            const border = xx === 0 || yy === 0 || xx === w - 1 || yy === h - 1 || xx === 1 && yy % 2 === 0;
            const vein = !border && ((xx + Math.floor(yy / 2)) % 3 === 0);
            c = border ? ((xx + yy) % 3 === 0 && (xx === 0 || yy === 0) ? hex('#f5f0e0') : c2) : (vein ? c2 : c1);
            break;
          }
        }
        let a = c[3];
        if (q.alpha !== undefined && !(pat === 'wing' && edge)) a = Math.round(255 * q.alpha);
        if (mask && !(q.glow === true || (q.glow === 'c2' && c === c2))) { rand(); continue; }
        let f = sh * (1 + (noise ? (rand() - 0.5) * noise / 100 : 0));
        if (q.hl && yy === 0) f *= 1.15; // highlight top row
        const col = shade(c, f);
        const i = ((y0 + yy) * W + (x0 + xx)) * 4;
        img.data[i] = col[0]; img.data[i + 1] = col[1]; img.data[i + 2] = col[2]; img.data[i + 3] = a;
      }
    }
    // explicit detail pixels: [x, y, color] relative to the face rect (negative = from far edge)
    for (const d of (q.px || [])) {
      const xx = d[0] < 0 ? w + d[0] : d[0], yy = d[1] < 0 ? h + d[1] : d[1];
      if (xx < 0 || yy < 0 || xx >= w || yy >= h) continue;
      if (mask && !(q.glow === true || d[3] === 'glow')) continue;
      const col = hex(d[2]);
      const i = ((y0 + yy) * W + (x0 + xx)) * 4;
      img.data[i] = col[0]; img.data[i + 1] = col[1]; img.data[i + 2] = col[2]; img.data[i + 3] = col[3];
    }
  }

  // Shelf-packs box-UV footprints; returns {w,h,offsets}
  function pack(cubes) {
    const items = cubes.map((c, i) => {
      const [w, h, d] = c.s.map(v => Math.ceil(v));
      return { i, fw: Math.max(1, 2 * (d + w)), fh: Math.max(1, d + h) };
    }).sort((a, b) => b.fh - a.fh || b.fw - a.fw);
    for (const W of [16, 32, 64, 128, 256]) {
      let x = 0, y = 0, rowH = 0; const off = {};
      let ok = true;
      for (const it of items) {
        if (it.fw > W) { ok = false; break; }
        if (x + it.fw > W) { x = 0; y += rowH; rowH = 0; }
        off[it.i] = [x, y];
        x += it.fw; rowH = Math.max(rowH, it.fh);
      }
      const H = y + rowH;
      if (!ok) continue;
      let TH = 16; while (TH < H) TH *= 2;
      if (TH <= W) return { w: W, h: TH, offsets: off };
    }
    throw new Error('texture too large');
  }

  function build(spec) {
    const before = new Set(ModelProject.all.map(p => p.uuid));
    newProject(Formats.bedrock);
    const proj = ModelProject.all.find(p => !before.has(p.uuid));
    if (!proj) throw new Error('could not create a new project');
    proj.select();
    Project.name = spec.id;
    Project.geometry_name = spec.id;
    Project.visible_box = spec.visible_box || [1, 1, 0];

    const allCubes = [];
    spec.bones.forEach(b => (b.cubes || []).forEach(c => allCubes.push(c)));
    const packed = pack(allCubes);
    Project.texture_width = packed.w;
    Project.texture_height = packed.h;

    const groups = {};
    let ci = 0;
    const made = [];
    for (const b of spec.bones) {
      const g = new Group({ name: b.name, origin: b.pivot || [0, 0, 0], rotation: b.rot || [0, 0, 0] });
      g.addTo(b.parent ? groups[b.parent] : undefined).init();
      groups[b.name] = g;
      for (const c of (b.cubes || [])) {
        const from = c.o, to = [c.o[0] + c.s[0], c.o[1] + c.s[1], c.o[2] + c.s[2]];
        const cube = new Cube({
          name: c.name || (b.name + '_' + ci),
          from, to,
          origin: c.p || b.pivot || [0, 0, 0],
          rotation: c.r || [0, 0, 0],
          inflate: c.inflate || 0,
          mirror_uv: !!c.mirror,
          box_uv: true,
          uv_offset: packed.offsets[ci]
        }).addTo(g).init();
        made.push([cube, c.paint || {}, ci]);
        ci++;
      }
    }
    Canvas.updateAll();

    // paint
    const W = packed.w, H = packed.h;
    const canvas = document.createElement('canvas'); canvas.width = W; canvas.height = H;
    const ctx = canvas.getContext('2d');
    const img = ctx.createImageData(W, H);
    const gcanvas = document.createElement('canvas'); gcanvas.width = W; gcanvas.height = H;
    const gctx = gcanvas.getContext('2d');
    const gimg = gctx.createImageData(W, H);
    let hasGlow = false;
    for (const [cube, paint, idx] of made) {
      for (const f of ['north', 'south', 'east', 'west', 'up', 'down']) {
        const face = cube.faces[f];
        if (!face || !face.uv) continue;
        const fp = Object.assign({}, paint, (paint.faces && paint.faces[f]) || {});
        const r1 = rng((spec.seed || 7) * 1000 + idx * 97 + f.length * 7);
        paintFace(img, W, face.uv, f, paint, r1, false);
        const glowy = fp.glow || (fp.px || []).some(d => d[3] === 'glow');
        if (glowy) {
          hasGlow = true;
          const r2 = rng((spec.seed || 7) * 1000 + idx * 97 + f.length * 7);
          paintFace(gimg, W, face.uv, f, paint, r2, true);
        }
      }
    }
    ctx.putImageData(img, 0, 0);
    gctx.putImageData(gimg, 0, 0);
    const tex = new Texture({ name: spec.id + '.png', width: W, height: H }).fromDataURL(canvas.toDataURL('image/png')).add(false);
    Cube.all.forEach(c => c.applyTexture(tex, true));

    // animations
    for (const [name, a] of Object.entries(spec.anims || {})) {
      const anim = new Animation({
        name: 'animation.' + spec.id + '.' + name,
        loop: a.loop === false ? 'once' : (a.loop === 'hold' ? 'hold' : 'loop'),
        length: a.len
      }).add(false);
      for (const [bone, chans] of Object.entries(a.bones)) {
        const g = groups[bone];
        if (!g) throw new Error('anim ' + name + ' references missing bone ' + bone);
        const ba = anim.getBoneAnimator(g);
        for (const [chan, kfs] of Object.entries(chans)) {
          for (const kf of kfs) {
            ba.addKeyframe({
              channel: chan, time: kf[0],
              data_points: [{ x: kf[1][0], y: kf[1][1], z: kf[1][2] }],
              interpolation: kf[2] || 'linear'
            });
          }
        }
      }
    }
    if (Animation.all.length) Animation.all[0].select();
    Canvas.updateAll();
    lastGlow = hasGlow ? gcanvas.toDataURL('image/png') : null;
    return {
      uuid: proj.uuid, tex: [W, H], cubes: made.length, bones: Object.keys(groups).length,
      glow: hasGlow
    };
  }

  let lastGlow = null;
  function exportAll() {
    const glowData = lastGlow;
    let geo = Codecs.bedrock.compile();
    if (typeof geo !== 'string') geo = JSON.stringify(geo, null, 2);
    const anim = Animation.all.length ? JSON.stringify(Animator.buildFile(), null, 2) : null;
    const bb = Codecs.project.compile({ raw: false });
    return {
      geo, anim,
      png: Texture.all[0].getDataURL(),
      glow: glowData || null,
      bbmodel: typeof bb === 'string' ? bb : JSON.stringify(bb)
    };
  }

  function closeProject(uuid, name) {
    const p = ModelProject.all.find(p => p.uuid === uuid && p.name === name);
    if (p) { p.saved = true; p.close(true); }
    return ModelProject.all.map(p => p.name);
  }

  return { build, exportAll, closeProject };
})();
'installed';
