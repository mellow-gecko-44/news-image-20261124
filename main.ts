// Entry point for the news-image-20261124 submission.
//
// The picture that makes up this entry sits next to this file as
// entry.png. All this program does is hand that picture to the grader:
// it confirms the file is within the competition's size gate and then
// copies it, untouched, into the output directory.
//
// The output directory comes from the MAKEFUN_OUTPUT_DIR environment
// variable; inside the grading container that variable is unset and
// the plain /output path is used instead.

import { copyFileSync, statSync } from "node:fs";
import { join } from "node:path";

// One mebibyte: the largest entry.png the gate accepts.
const SIZE_LIMIT_BYTES: number = 1048576;

// Resolve the picture relative to this module so the program works no
// matter which directory it happens to be launched from.
const picturePath: string = new URL("./entry.png", import.meta.url).pathname;

const pictureSize: number = statSync(picturePath).size;
if (pictureSize > SIZE_LIMIT_BYTES) {
  throw new Error(
    `entry.png weighs in at ${pictureSize} bytes, which is over the ${SIZE_LIMIT_BYTES}-byte limit`
  );
}

const destinationDir: string = process.env.MAKEFUN_OUTPUT_DIR ?? "/output";
copyFileSync(picturePath, join(destinationDir, "entry.png"));
