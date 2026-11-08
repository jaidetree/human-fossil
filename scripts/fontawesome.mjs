// Prepares Font Awesome for the Tailwind build:
//  - copies webfonts to static/webfonts (CSS references ../webfonts/*)
//  - writes static_src/css/fontawesome-base.css: the kit's all.css minus the
//    per-icon rules, which static_src/vendor/fontawesome.js provides as
//    utilities instead.
import { cpSync, readFileSync, writeFileSync } from 'node:fs';
import { createRequire } from 'node:module';
import path from 'node:path';

const require = createRequire(import.meta.url);
const { ICON_RULE, kitIconsDir } = require('./fontawesome-paths.cjs');

cpSync(path.join(kitIconsDir, 'webfonts'), 'static/webfonts', {
	recursive: true,
});

const all = readFileSync(path.join(kitIconsDir, 'css/all.css'), 'utf8');
writeFileSync(
	'static_src/css/fontawesome-base.css',
	all.replace(ICON_RULE, ''),
);
