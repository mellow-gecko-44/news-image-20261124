// Entry for make.fun's news-image-20261124: "Sum up 24 November's world news in one image".
//
// The image beside this file (entry.png) is the whole entry: a one-page broadsheet
// summing up Tuesday 24 November 2026, drawn by make_image.py with PIL. This program
// copies it to the grader's output directory, byte for byte, so both grading runs
// produce identical bytes.
//
// Outside the grader's container, MAKEFUN_OUTPUT_DIR stands in for /output:
//   mkdir -p out && MAKEFUN_OUTPUT_DIR=out node main.ts

import { copyFileSync, statSync } from 'node:fs';
import { join } from 'node:path';

const GATE_BYTES = 1048576; // the competition gate: at most 1 MiB
const source = new URL('./entry.png', import.meta.url);
const size = statSync(source).size;
if (size > GATE_BYTES) {
  throw new Error(`entry.png is ${size} bytes, over the ${GATE_BYTES}-byte gate`);
}

copyFileSync(source, join(process.env.MAKEFUN_OUTPUT_DIR ?? '/output', 'entry.png'));
