// Valida links internos de ARQUIVO markdown ([txt](rel.md)) sem depender do build
// do VitePress, que estoura memória neste site de 12 locales. Espelha a parte
// confiável da checagem de dead-link do VitePress: todo link .md relativo deve
// resolver para um arquivo existente.
//
// Nota: NÃO valida âncoras (#secção). O algoritmo de slug do plugin de âncoras do
// VitePress não é o `slugify` exportado do pacote, e reproduzi-lo fora do build gera
// falso-positivo (o próprio build só reporta links de arquivo mortos, não âncoras).
// Para uma checagem de âncora autoritativa, rode `npm run build` até o fim.
//
// Uso: node scripts/check-links.mjs [scope...]   (default: todos os locales + raiz)
import fs from 'node:fs'
import path from 'node:path'
import { fileURLToPath } from 'node:url'

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..')
const scopes = process.argv.slice(2)
const LOCALES = ['en', 'pt', 'de', 'ru', 'es', 'fr', 'ja', 'zh-hans', 'cs', 'pl', 'hu', 'it']
const targets = scopes.length ? scopes : [...LOCALES, '.']

function walk(dir) {
  const out = []
  for (const e of fs.readdirSync(dir, { withFileTypes: true })) {
    if (['node_modules', '.vitepress', '.git', 'scripts', 'public'].includes(e.name)) continue
    const p = path.join(dir, e.name)
    if (e.isDirectory()) out.push(...walk(p))
    else if (e.name.endsWith('.md')) out.push(p)
  }
  return out
}

const files = []
for (const t of targets) {
  if (t === '.') {
    for (const e of fs.readdirSync(ROOT)) if (e.endsWith('.md')) files.push(path.join(ROOT, e))
  } else {
    const dir = path.join(ROOT, t)
    if (fs.existsSync(dir)) files.push(...walk(dir))
  }
}

const linkRe = /\[[^\]]*\]\(([^)]+)\)/g
const dead = []
for (const f of files) {
  const txt = fs.readFileSync(f, 'utf8')
  let m
  while ((m = linkRe.exec(txt))) {
    let href = m[1].trim()
    if (/^(https?:|mailto:|#|\/)/.test(href)) continue
    const pathPart = href.split('#')[0]
    if (!pathPart || !pathPart.endsWith('.md')) continue
    const target = path.resolve(path.dirname(f), pathPart)
    if (!fs.existsSync(target)) {
      dead.push(path.relative(ROOT, f).replace(/\\/g, '/') + '  ->  ' + href)
    }
  }
}

console.log('check-links: ' + files.length + ' arquivos verificados | ' + dead.length + ' links de arquivo mortos')
if (dead.length) { console.log('\nLINKS MORTOS:'); dead.forEach(d => console.log('  ' + d)) }
process.exit(dead.length > 0 ? 1 : 0)
