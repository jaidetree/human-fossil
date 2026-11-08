// Tailwind plugin: makes every Font Awesome "fa-#{ICON}" class a utility so
// Tailwind IntelliSense autocompletes it and only the icons used get emitted.
// Style/base classes (.fa-regular, @font-face, ...) come from the generated
// fontawesome-base.css, see scripts/fontawesome.mjs.
const plugin = require("tailwindcss/plugin")
const fs = require("fs")
const path = require("path")
const { ICON_RULE, kitIconsDir } = require("../../scripts/fontawesome-paths.cjs")

module.exports = plugin(function({addUtilities}) {
  const css = fs.readFileSync(path.join(kitIconsDir, "css/all.css"), "utf8")
  const utilities = {}
  for (const [, name, codepoint] of css.matchAll(ICON_RULE)) {
    utilities[`.fa-${name}`] = {"--fa": codepoint}
  }
  addUtilities(utilities)
})
