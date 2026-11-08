const path = require('path');

// Matches single-declaration icon rules, e.g. `.fa-xmark { --fa: "\f00d"; }`
const ICON_RULE = /^\.fa-([a-z0-9-]+)\s*\{\s*--fa:\s*("[^"]*");\s*\}\s*$/gm;

const kitIconsDir = path.join(
	__dirname,
	'../node_modules/@awesome.me/kit-ab3c4f3ba9/icons',
);

module.exports = { ICON_RULE, kitIconsDir };
