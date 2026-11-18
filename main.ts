// news-image-20261117 entry (Node 22, standard library only).
//
// The entry is one image, entry.png, committed beside this file: a broadsheet
// front page that sums up the world news of Tuesday 17 November 2026. The
// picture itself is drawn by make_image.py at build time; this program's only
// job at grade time is to place those exact bytes at /output/entry.png, so
// both grader runs produce a byte-identical file.
//
// Outside the grader's container, MAKEFUN_OUTPUT_DIR stands in for /output:
//   mkdir -p out && MAKEFUN_OUTPUT_DIR=out node main.ts

import { copyFileSync, mkdirSync, readFileSync, statSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const here = dirname(fileURLToPath(import.meta.url));
const source = join(here, 'entry.png');
const outDir = process.env.MAKEFUN_OUTPUT_DIR ?? '/output';
const target = join(outDir, 'entry.png');

mkdirSync(outDir, { recursive: true });
copyFileSync(source, target);

const bytes = statSync(target).size;
if (bytes === 0 || bytes > 1_048_576) {
  throw new Error(`entry.png is ${bytes} bytes; the gate allows at most 1048576`);
}
const head = readFileSync(target).subarray(0, 8);
const isPng = head.equals(Buffer.from([0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a]));
const isJpeg = head[0] === 0xff && head[1] === 0xd8;
if (!isPng && !isJpeg) {
  throw new Error('entry.png is neither a PNG nor a JPEG by its first bytes');
}
console.log(`entry.png written to ${target} (${bytes} bytes)`);
