// Valida que todo link do sidebar em .vitepress/config.mts resolve para um arquivo .md
// existente em TODOS os locales. O VitePress NÃO faz dead-link check de sidebar — entradas
// apontando para arquivos inexistentes buildam limpo e viram 404 em produção.
// Uso: node scripts/check-sidebar.mjs   (exit 1 se houver link quebrado)
import fs from 'node:fs'
import path from 'node:path'
import { fileURLToPath } from 'node:url'

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..')
const LOCALES = ['en', 'pt', 'de', 'ru', 'es', 'fr', 'ja', 'zh-hans', 'cs', 'pl', 'hu', 'it']

const config = fs.readFileSync(path.join(ROOT, '.vitepress', 'config.mts'), 'utf8')
const links = [...config.matchAll(/link:\s*`\$\{l\}\/([^`]+)`/g)].map(m => m[1])

if (links.length === 0) {
  console.error('ERRO: nenhum link `${l}/...` encontrado no config.mts — o formato mudou?')
  process.exit(1)
}

let broken = 0
for (const locale of LOCALES) {
  for (const link of links) {
    const file = path.join(ROOT, locale, link + '.md')
    if (!fs.existsSync(file)) {
      console.error(`QUEBRADO: sidebar -> /${locale}/${link} (falta ${locale}/${link}.md)`)
      broken++
    }
  }
}

console.log(`check-sidebar: ${links.length} links x ${LOCALES.length} locales = ${links.length * LOCALES.length} checagens, ${broken} quebrados`)
process.exit(broken > 0 ? 1 : 0)
