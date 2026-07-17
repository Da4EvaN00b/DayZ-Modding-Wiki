// Gera public/llms.txt (convenção llmstxt.org) a partir da definição do sidebar em
// .vitepress/config.mts — NUNCA editar public/llms.txt à mão; ele é derivado para não
// divergir da navegação humana. Inglês apenas (en/ é o canônico).
// Uso: node scripts/gen-llms.mjs
import fs from 'node:fs'
import path from 'node:path'
import { fileURLToPath } from 'node:url'

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..')
// URL pública do GitHub Pages (host + base do config.mts)
const SITE = 'https://stardz-team.github.io/DayZ-Modding-Wiki'

const config = fs.readFileSync(path.join(ROOT, '.vitepress', 'config.mts'), 'utf8')

// extrai o corpo da função sidebar() e percorre grupos { text: 'Part ...', items: [...] }
const groups = []
const groupRe = /text:\s*'([^']+)',\s*\n\s*collapsed:[^\n]*\n\s*items:\s*\[([\s\S]*?)\]\s*\n\s*\}/g
let g
while ((g = groupRe.exec(config)) !== null) {
  const items = [...g[2].matchAll(/text:\s*'([^']+)',\s*link:\s*`\$\{l\}\/([^`]+)`/g)]
    .map(m => ({ text: m[1], link: m[2] }))
  if (items.length) groups.push({ title: g[1], items })
}

if (groups.length === 0) {
  console.error('ERRO: nenhum grupo de sidebar extraído do config.mts — o formato mudou?')
  process.exit(1)
}

const lines = []
lines.push('# DayZ Modding Wiki')
lines.push('')
lines.push('> Community documentation for DayZ modding: the Enforce Script language, mod structure, GUI system, file formats, engine API, patterns, step-by-step tutorials, and server administration. Grounded in the vanilla DayZ scripts and official Bohemia Interactive samples; all code examples are original and self-contained. English is the canonical language (11 translations available via the site language switcher).')
lines.push('')
lines.push('Key facts for language models writing Enforce Script: it is NOT C/C++. There is no ternary operator, no `auto`, no `try/catch`, no `do...while`, no `#include`, and multi-line call expressions break the parser. See the "What Does NOT Exist" page below before generating code.')
lines.push('')

for (const group of groups) {
  lines.push('## ' + group.title)
  lines.push('')
  for (const item of group.items) {
    lines.push(`- [${item.text}](${SITE}/en/${item.link})`)
  }
  lines.push('')
}

const out = lines.join('\n')
fs.mkdirSync(path.join(ROOT, 'public'), { recursive: true })
fs.writeFileSync(path.join(ROOT, 'public', 'llms.txt'), out)
console.log(`gen-llms: ${groups.length} seções, ${groups.reduce((s, x) => s + x.items.length, 0)} links -> public/llms.txt (${out.length} bytes)`)
