// Reparador de âncoras mortas. NÃO é executado por ninguém automaticamente e
// NÃO altera nada por padrão: sem --apply ele só imprime o que faria.
//
// Contexto: as tabelas de conteúdo deste wiki foram escritas com slugs no dialeto
// do GitHub; o VitePress usa outro algoritmo, então uma parte das âncoras internas
// não resolve no site publicado. Ver scripts/check-links.mjs --anchors.
//
// Este script reusa exatamente a mesma extração de check-links.mjs (mesmos links,
// mesma máscara de código, mesmos IDs lidos do renderer VitePress instalado) e
// propõe, para cada âncora morta, o heading de destino.
//
// REGRA DE SEGURANÇA: só reescreve mapeamentos INEQUÍVOCOS.
//   1. slug-GitHub: exatamente UM heading do arquivo-alvo cujo slug no dialeto do
//      GitHub (calculado a partir do markdown-fonte do heading) é igual à âncora
//      morta. Esse é o dialeto em que as ToCs foram escritas, então é a evidência
//      mais forte de qual heading o autor quis referenciar.
//   2. sem-pontuação: exatamente UM heading cujo id real, reduzido a [a-z0-9],
//      é igual à âncora morta reduzida a [a-z0-9].
// Se as duas regras discordam, ou se qualquer uma delas devolve 0 ou 2+ candidatos,
// a entrada NÃO é reescrita: vai para a lista MANUAL, para decisão humana.
//
// Uso:
//   node scripts/repair-anchors.mjs                       # dry-run, escopo en/
//   node scripts/repair-anchors.mjs --json=out.json       # dry-run + plano em JSON
//   node scripts/repair-anchors.mjs pt                    # dry-run, escopo pt/
//   node scripts/repair-anchors.mjs --apply               # ESCREVE (exige intenção explícita)
//
// Não rode --apply enquanto auditores de conteúdo estiverem editando os mesmos
// arquivos: a reescrita é por linha/coluna e assume o arquivo no estado em que foi
// lido nesta execução.
import fs from 'node:fs'
import path from 'node:path'
import {
  ROOT, ANCHOR_DEFAULT_SCOPE, collect, harvest, makeIdReader, findDeadAnchors, rel,
} from './check-links.mjs'

const argv = process.argv.slice(2)
const flags = argv.filter(a => a.startsWith('--'))
const scopes = argv.filter(a => !a.startsWith('--'))
const apply = flags.includes('--apply')
const jsonOut = (flags.find(a => a.startsWith('--json=')) || '').slice('--json='.length)

// Slug no dialeto do GitHub: minúsculas, remove tudo que não é palavra/espaço/hífen,
// espaços viram hífen. É o dialeto em que as ToCs deste repositório foram escritas.
const ghSlug = s => s
  .normalize('NFKD').replace(/[̀-ͯ]/g, '')
  .toLowerCase().replace(/[^\w\s-]/g, '').trim().replace(/\s+/g, '-')

const bare = s => s.toLowerCase().replace(/[^a-z0-9]/g, '')

const scope = scopes.length ? scopes : ANCHOR_DEFAULT_SCOPE
const files = collect(scope)
const readIds = await makeIdReader()
const { checked, entries } = findDeadAnchors(files, readIds)

// ------------------------------------------------------------------ resolução

const resolved = []
const manual = []

for (const e of entries) {
  const info = readIds(path.resolve(ROOT, e.target))
  const heads = info ? info.headings : []

  // Regra 1: slug-GitHub, calculado do markdown-fonte do heading (fallback: texto).
  // Desambiguação de duplicatas no GitHub: dup, dup-1, dup-2 — mesma convenção.
  const ghSeen = new Map()
  const ghCandidates = []
  for (const h of heads) {
    const base = ghSlug(h.rawSource ?? h.text ?? '')
    const n = ghSeen.get(base) || 0
    ghSeen.set(base, n + 1)
    const slug = n === 0 ? base : `${base}-${n}`
    if (slug && slug === e.anchor) ghCandidates.push(h)
  }

  // Regra 2: comparação sem pontuação contra o id REAL.
  const bareCandidates = heads.filter(h => bare(h.id) === bare(e.anchor))

  const uniq = arr => [...new Set(arr.map(h => h.id))]
  const gh = uniq(ghCandidates)
  const bc = uniq(bareCandidates)

  let pick = null
  let rule = null
  if (gh.length === 1 && (bc.length === 0 || (bc.length === 1 && bc[0] === gh[0]))) { pick = gh[0]; rule = 'github-slug' }
  else if (gh.length === 0 && bc.length === 1) { pick = bc[0]; rule = 'punctuation-insensitive' }

  if (pick) {
    const h = heads.find(x => x.id === pick)
    resolved.push({ ...e, new_anchor: pick, rule, heading: h ? (h.rawSource ?? h.text) : null })
  } else {
    manual.push({
      ...e,
      reason: gh.length > 1 || bc.length > 1 ? 'ambiguous: multiple candidate headings'
        : gh.length === 0 && bc.length === 0 ? 'no candidate heading matches this anchor'
          : 'rules disagree on the target heading',
      github_slug_candidates: gh,
      punctuation_insensitive_candidates: bc,
    })
  }
}

// ------------------------------------------------------------------ relatório

const byFile = {}
for (const r of resolved) (byFile[r.file] ||= []).push(r)

console.log(`repair-anchors [${scope.join(', ')}] ${apply ? '*** APPLY ***' : '(dry-run — nada será escrito)'}`)
console.log(`  ${files.length} arquivos | ${checked} âncoras verificadas | ${entries.length} mortas`)
console.log(`  ${resolved.length} reescritas inequívocas em ${Object.keys(byFile).length} arquivos | ${manual.length} exigem decisão manual\n`)

for (const [f, list] of Object.entries(byFile).sort()) {
  console.log(`  ${f}`)
  for (const r of list) console.log(`    :${r.line}  ${r.anchor}  ->  ${r.new_anchor}   [${r.rule}]`)
}

if (manual.length) {
  console.log('\nMANUAL (não serão tocadas):')
  for (const m of manual) console.log(`  ${m.file}:${m.line}  #${m.anchor}  (alvo: ${m.target})  — ${m.reason}`)
}

// ------------------------------------------------------------------ escrita

let written = 0
if (apply && resolved.length) {
  const grouped = {}
  for (const r of resolved) (grouped[r.file] ||= []).push(r)
  for (const [f, list] of Object.entries(grouped)) {
    const abs = path.resolve(ROOT, f)
    const lines = fs.readFileSync(abs, 'utf8').split('\n')
    // Reescreve por linha/coluna exata, do fim para o começo, para não invalidar colunas.
    const ordered = [...list].sort((a, b) => b.line - a.line || b.col - a.col)
    for (const r of ordered) {
      const i = r.line - 1
      const line = lines[i]
      if (line === undefined) { console.error(`  (aviso) ${f}:${r.line} não existe mais — pulando`); continue }
      const start = r.col - 1
      const seg = line.slice(start)
      const oldHref = r.href
      if (!seg.startsWith(oldHref)) { console.error(`  (aviso) ${f}:${r.line}:${r.col} não bate com "${oldHref}" — pulando`); continue }
      const newHref = oldHref.slice(0, oldHref.indexOf('#') + 1) + r.new_anchor
      lines[i] = line.slice(0, start) + newHref + line.slice(start + oldHref.length)
      written++
    }
    fs.writeFileSync(abs, lines.join('\n'))
  }
  console.log(`\nescritas aplicadas: ${written}`)
} else if (apply) {
  console.log('\nnada a aplicar.')
}

if (jsonOut) {
  const out = {
    generated: new Date().toISOString(),
    tool: 'scripts/repair-anchors.mjs',
    mode: apply ? 'apply' : 'dry-run',
    id_source: 'vitepress createMarkdownRenderer (versão instalada em node_modules)',
    scope,
    files_scanned: files.length,
    anchors_checked: checked,
    dead: entries.length,
    unambiguous: resolved.length,
    manual: manual.length,
    written,
    rewrites: resolved,
    manual_entries: manual,
  }
  fs.writeFileSync(path.resolve(ROOT, jsonOut), JSON.stringify(out, null, 2) + '\n')
  console.log(`\nplano JSON: ${jsonOut}`)
}
