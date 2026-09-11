// Valida links internos de ARQUIVO markdown ([txt](rel.md)) sem depender do build
// do VitePress, que estoura memória neste site de 12 locales. Espelha a parte
// confiável da checagem de dead-link do VitePress: todo link .md relativo deve
// resolver para um arquivo existente.
//
// ÂNCORAS (--anchors): o VitePress NÃO valida âncoras — o build só reporta links
// de arquivo mortos, nunca fragmentos `#secção`. Por isso a checagem mora aqui.
//
// Correção de um comentário anterior deste arquivo, que afirmava que o slug do
// plugin de âncoras do VitePress "não é o `slugify` exportado do pacote" e não
// poderia ser reproduzido fora do build. A primeira metade estava errada: o plugin
// faz `token.attrGet("id") ?? slugify(title)` usando o `slugify` definido logo
// abaixo, no mesmo bundle (node_modules/vitepress/dist/node/chunk-*.js). A segunda
// metade estava certa, e é exatamente por isso que esta checagem é necessária.
//
// Ainda assim este script NÃO reimplementa o slug: ele renderiza cada arquivo com o
// renderer VitePress REALMENTE INSTALADO (`createMarkdownRenderer`) e lê os
// atributos `id=` do HTML gerado. Isso cobre de graça:
//   - headings duplicados        (Dup / Dup-1 / Dup-2)
//   - markup inline no heading   (`code`, **bold**, [link](x))
//   - IDs explícitos             (## Título {#meu-id})
//   - o prefixo `_` que o VitePress adiciona a slugs iniciados por dígito
//     (## 1. Mod Won't Load  ->  #_1-mod-won-t-load)
//   - o em-dash literal preservado no id
//     (## Class.CastTo — Safe Downcasting  ->  #class-castto-—-safe-downcasting)
//
// Links dentro de blocos cercados (``` / ~~~), de código inline (`...`) e de
// comentários HTML são ignorados: são exemplos, não navegação.
//
// Uso:
//   node scripts/check-links.mjs [scope...]          # links de arquivo, todos os locales (default)
//   node scripts/check-links.mjs --anchors           # + âncoras, escopo en/ (opt-in)
//   node scripts/check-links.mjs --anchors pt        # + âncoras, escopo pt/
//   node scripts/check-links.mjs --anchors --json=out.json
//   node scripts/check-links.mjs --anchors --strict  # exit 1 se houver problema
//   node scripts/check-links.mjs --external           # + HTTP dos links externos (opt-in)
//
// LINKS EXTERNOS (--external): estritamente opt-in. Sem essa flag o script NAO faz
// nenhuma requisicao de rede — o modo padrao continua 100% offline e deterministico,
// utilizavel sem internet e em CI sem acesso externo.
// Motivacao: dois links de repositorio no README.md da raiz responderam 404 por
// meses (Da0ne/VPP-AdminTools e DrkDevil/DayZ-Colorful-UI) e nenhuma checagem
// existente os cobria. O escopo padrao e apenas README.md e index.md da raiz, que
// e onde ficam os creditos do ecossistema; nao varremos os 12 locales.
//
// Sem --strict o exit code continua sempre 0, como sempre foi — não quebra
// invocações existentes.
//
// Este módulo também EXPORTA suas partes (collect/harvest/makeIdReader/...) para
// que scripts/repair-anchors.mjs use exatamente a mesma extração. Só executa a CLI
// quando chamado diretamente.
import fs from 'node:fs'
import path from 'node:path'
import { fileURLToPath, pathToFileURL } from 'node:url'

export const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..')
export const LOCALES = ['en', 'pt', 'de', 'ru', 'es', 'fr', 'ja', 'zh-hans', 'cs', 'pl', 'hu', 'it']
export const ANCHOR_DEFAULT_SCOPE = ['en']
export const SITE_BASE = '/DayZ-Modding-Wiki/'

export const rel = f => path.relative(ROOT, f).replace(/\\/g, '/')

// ---------------------------------------------------------------- coleta de arquivos

export function walk(dir) {
  const out = []
  for (const e of fs.readdirSync(dir, { withFileTypes: true })) {
    if (['node_modules', '.vitepress', '.git', 'scripts', 'public'].includes(e.name)) continue
    const p = path.join(dir, e.name)
    if (e.isDirectory()) out.push(...walk(p))
    else if (e.name.endsWith('.md')) out.push(p)
  }
  return out
}

export function collect(targets) {
  const files = []
  for (const t of targets) {
    if (t === '.') {
      for (const e of fs.readdirSync(ROOT)) if (e.endsWith('.md')) files.push(path.join(ROOT, e))
    } else {
      const dir = path.join(ROOT, t)
      if (fs.existsSync(dir)) files.push(...walk(dir))
    }
  }
  return files.sort()
}

// ------------------------------------------------- extração de links fora de código

// Remove blocos cercados, código inline e comentários HTML, preservando a contagem
// de linhas E as colunas, para que linha/coluna reportadas continuem corretas.
export function maskNonProse(src) {
  const lines = src.split('\n')
  let fence = null
  for (let i = 0; i < lines.length; i++) {
    const open = lines[i].match(/^\s*(`{3,}|~{3,})/)
    if (fence) {
      const closing = lines[i].match(/^\s*(`{3,}|~{3,})\s*$/)
      lines[i] = ' '.repeat(lines[i].length)
      if (closing && closing[1][0] === fence[0] && closing[1].length >= fence.length) fence = null
      continue
    }
    if (open) { fence = open[1]; lines[i] = ' '.repeat(lines[i].length); continue }
  }
  let out = lines.join('\n')
  const blank = s => s.replace(/[^\n]/g, ' ')
  out = out.replace(/<!--[\s\S]*?-->/g, blank)
  out = out.replace(/(`+)(?:(?!\1)[\s\S])*?\1/g, blank)
  return out
}

// flag `d` para ter o offset exato do href (grupo 1), e não o do `[` do link:
// repair-anchors.mjs reescreve por coluna e precisa apontar para o href.
const LINK_RE = /\[[^\]]*\]\(\s*([^)\s]+?)(?:\s+["'][^)]*)?\s*\)/dg

// Retorna { href, line, col } de cada link markdown fora de código.
export function harvest(file) {
  const masked = maskNonProse(fs.readFileSync(file, 'utf8'))
  const found = []
  masked.split('\n').forEach((line, i) => {
    LINK_RE.lastIndex = 0
    let m
    while ((m = LINK_RE.exec(line))) found.push({ href: m[1].trim(), line: i + 1, col: m.indices[1][0] + 1 })
  })
  return found
}

// --------------------------------------------- IDs reais, via o renderer instalado

const ENTITIES = { '&quot;': '"', '&#39;': "'", '&amp;': '&', '&lt;': '<', '&gt;': '>', '&ZeroWidthSpace;': '' }
const decode = s => s.replace(/&quot;|&#39;|&amp;|&lt;|&gt;|&ZeroWidthSpace;/g, e => ENTITIES[e])

// makeIdReader() -> async (file) => { ids: Set<string>, headings: [{id, rawSource, text}] } | null
// null = arquivo não pôde ser renderizado; nesse caso NÃO afirmamos nada sobre ele.
export async function makeIdReader() {
  const { createMarkdownRenderer } = await import('vitepress')
  const md = await createMarkdownRenderer(ROOT, {}, SITE_BASE)
  const cache = new Map()
  return function read(file) {
    const key = path.resolve(file)
    if (cache.has(key)) return cache.get(key)
    let result = null
    try {
      // frontmatter é removido pelo VitePress antes do render; fazemos o mesmo.
      const src = fs.readFileSync(key, 'utf8').replace(/^---\r?\n[\s\S]*?\r?\n---\r?\n/, '')
      const html = md.render(src)
      const headings = []
      const ids = new Set()
      const re = /<h([1-6])\b[^>]*\bid="([^"]*)"[^>]*>([\s\S]*?)<\/h\1>/g
      let m
      while ((m = re.exec(html))) {
        const id = m[2]
        const inner = m[3]
        const aria = inner.match(/aria-label="Permalink to &quot;([\s\S]*?)&quot;"/)
        const rawSource = aria ? decode(aria[1]) : null
        const text = decode(inner.replace(/<a class="header-anchor"[\s\S]*?<\/a>/g, '').replace(/<[^>]+>/g, '')).trim()
        ids.add(id)
        headings.push({ id, level: Number(m[1]), rawSource, text })
      }
      result = { ids, headings }
    } catch (err) {
      console.error(`  (aviso) falha ao renderizar ${rel(key)}: ${err.message}`)
      result = null
    }
    cache.set(key, result)
    return result
  }
}

// Percorre `files` e devolve toda âncora interna que não existe no alvo.
// readIds vem de makeIdReader().
export function findDeadAnchors(files, readIds) {
  const entries = []
  let checked = 0
  for (const f of files) {
    for (const { href, line, col } of harvest(f)) {
      if (/^(https?:|mailto:)/.test(href)) continue
      const hash = href.indexOf('#')
      if (hash < 0) continue
      const pathPart = href.slice(0, hash)
      const anchor = decodeURIComponent(href.slice(hash + 1))
      if (!anchor) continue
      let target = f
      if (pathPart) {
        if (pathPart.startsWith('/')) continue          // link absoluto de site: fora do escopo
        if (!pathPart.endsWith('.md')) continue
        target = path.resolve(path.dirname(f), decodeURIComponent(pathPart))
        if (!fs.existsSync(target)) continue            // já reportado como link de arquivo morto
      }
      const info = readIds(target)
      if (!info) continue
      checked++
      if (!info.ids.has(anchor)) {
        entries.push({ file: rel(f), line, col, href, anchor, target: rel(target) })
      }
    }
  }
  return { checked, entries }
}

export function findDeadFileLinks(files) {
  const dead = []
  for (const f of files) {
    for (const { href, line } of harvest(f)) {
      if (/^(https?:|mailto:|#|\/)/.test(href)) continue
      const pathPart = href.split('#')[0]
      if (!pathPart || !pathPart.endsWith('.md')) continue
      const target = path.resolve(path.dirname(f), decodeURIComponent(pathPart))
      if (!fs.existsSync(target)) dead.push({ file: rel(f), line, href })
    }
  }
  return dead
}

// ------------------------------------------------- links externos (opt-in, rede)

export const EXTERNAL_DEFAULT_FILES = ['README.md', 'index.md']

// Coleta URLs http(s) de prosa (fora de codigo) dos arquivos indicados.
export function harvestExternal(files) {
  const seen = new Map()
  for (const f of files) {
    if (!fs.existsSync(f)) continue
    const masked = maskNonProse(fs.readFileSync(f, 'utf8'))
    masked.split('\n').forEach((line, i) => {
      // links markdown e href/src de HTML inline (o README da raiz usa ambos)
      for (const m of line.matchAll(/https?:\/\/[^\s)"'<>\]]+/g)) {
        const url = m[0].replace(/[.,;]+$/, '')
        if (!seen.has(url)) seen.set(url, [])
        seen.get(url).push(`${rel(f)}:${i + 1}`)
      }
    })
  }
  return seen
}

// HEAD e, se o servidor nao responder bem a HEAD, GET. Erros de rede viram status 0.
async function probe(url, timeoutMs) {
  for (const method of ['HEAD', 'GET']) {
    const ac = new AbortController()
    const t = setTimeout(() => ac.abort(), timeoutMs)
    try {
      const res = await fetch(url, { method, redirect: 'follow', signal: ac.signal })
      clearTimeout(t)
      if (method === 'HEAD' && (res.status === 405 || res.status === 403 || res.status === 501)) continue
      return { status: res.status, finalUrl: res.url || url, method }
    } catch (err) {
      clearTimeout(t)
      if (method === 'GET') return { status: 0, finalUrl: url, method, error: String(err.message || err) }
    }
  }
  return { status: 0, finalUrl: url, method: 'GET', error: 'unreachable' }
}

// Sub-paths do GitHub que exigem autenticacao: respondem 404 a requisicoes anonimas
// MESMO quando o repositorio existe e tem estrelas. Verificado em 2026-09-11 com
// torvalds/linux/stargazers e vuejs/vitepress/stargazers, ambos 404 sem login.
// Tratar esses 404 como link morto e um FALSO POSITIVO: foi exatamente o erro que
// esta checagem cometeu na sua primeira execucao.
const AUTH_GATED = /^https?:\/\/github\.com\/[^/]+\/[^/]+\/(stargazers|watchers|network|forks)(\/|$|\?)/i

// Devolve [{url, where[], status, finalUrl, redirected}] — status 0 = falha de rede,
// que NAO deve ser tratada como link morto sem uma segunda verificacao manual.
export async function checkExternal(files, { timeoutMs = 15000, concurrency = 4 } = {}) {
  const seen = harvestExternal(files)
  const urls = [...seen.keys()].sort()
  const out = []
  let i = 0
  async function worker() {
    while (i < urls.length) {
      const url = urls[i++]
      const r = await probe(url, timeoutMs)
      const authGated = AUTH_GATED.test(url) && r.status === 404
      out.push({ url, where: seen.get(url), status: r.status, finalUrl: r.finalUrl, redirected: r.finalUrl !== url, error: r.error, authGated })
    }
  }
  await Promise.all(Array.from({ length: Math.min(concurrency, urls.length) }, worker))
  out.sort((a, b) => a.url.localeCompare(b.url))
  return out
}

// ------------------------------------------------------------------------- CLI

const isMain = process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href

if (isMain) {
  const argv = process.argv.slice(2)
  const flags = argv.filter(a => a.startsWith('--'))
  const scopes = argv.filter(a => !a.startsWith('--'))
  const wantAnchors = flags.includes('--anchors')
  const wantExternal = flags.includes('--external')
  const strict = flags.includes('--strict')
  const jsonOut = (flags.find(a => a.startsWith('--json=')) || '').slice('--json='.length)

  const fileFiles = collect(scopes.length ? scopes : [...LOCALES, '.'])
  const dead = findDeadFileLinks(fileFiles)

  console.log(`check-links: ${fileFiles.length} arquivos verificados | ${dead.length} links de arquivo mortos`)
  if (dead.length) {
    console.log('\nLINKS MORTOS:')
    dead.forEach(d => console.log(`  ${d.file}:${d.line}  ->  ${d.href}`))
  }

  let anchorReport = null
  if (wantAnchors) {
    const anchorScope = scopes.length ? scopes : ANCHOR_DEFAULT_SCOPE
    const anchorFiles = collect(anchorScope)
    const readIds = await makeIdReader()
    const { checked, entries } = findDeadAnchors(anchorFiles, readIds)
    const pages = new Set(entries.map(e => e.file))

    console.log(`\ncheck-anchors [${anchorScope.join(', ')}]: ${anchorFiles.length} arquivos | ${checked} âncoras verificadas | ${entries.length} mortas em ${pages.size} páginas`)
    if (entries.length) {
      console.log('\nÂNCORAS MORTAS (id real lido do renderer VitePress instalado):')
      for (const e of entries) console.log(`  ${e.file}:${e.line}  ->  ${e.href}   (alvo: ${e.target})`)
    }

    anchorReport = {
      generated: new Date().toISOString(),
      tool: 'scripts/check-links.mjs --anchors',
      id_source: 'vitepress createMarkdownRenderer (versão instalada em node_modules); IDs lidos do HTML renderizado, não reimplementados',
      scope: anchorScope,
      files_scanned: anchorFiles.length,
      anchors_checked: checked,
      dead: entries.length,
      pages_affected: pages.size,
      entries,
    }
    if (jsonOut) {
      fs.writeFileSync(path.resolve(ROOT, jsonOut), JSON.stringify(anchorReport, null, 2) + '\n')
      console.log(`\nrelatório JSON: ${jsonOut}`)
    }
  }

  let externalReport = null
  if (wantExternal) {
    const extFiles = (scopes.length ? scopes : EXTERNAL_DEFAULT_FILES)
      .map(f => path.resolve(ROOT, f))
      .filter(f => f.endsWith('.md') && fs.existsSync(f))
    const results = await checkExternal(extFiles)
    const broken = results.filter(r => r.status >= 400 && !r.authGated)
    const gated = results.filter(r => r.authGated)
    const unreachable = results.filter(r => r.status === 0)
    const redirected = results.filter(r => r.status > 0 && r.status < 400 && r.redirected)

    console.log(`\ncheck-external [${extFiles.map(f => rel(f)).join(', ')}]: ${results.length} URLs | ${broken.length} >=400 | ${gated.length} auth-gated (not checkable) | ${unreachable.length} unreachable | ${redirected.length} redirected`)
    for (const r of gated) console.log(`  AUTH-GATED  ${r.url}   (${r.where.join(', ')})  <- GitHub answers 404 anonymously even when the repo exists; NOT a dead link`)
    for (const r of broken) console.log(`  BROKEN  ${r.status}  ${r.url}   (${r.where.join(', ')})`)
    for (const r of unreachable) console.log(`  UNREACHABLE  ${r.url}   (${r.where.join(', ')})  ${r.error || ''}  <- network failure, verify by hand before treating as dead`)
    for (const r of redirected) console.log(`  REDIRECT ${r.status}  ${r.url}  ->  ${r.finalUrl}   (${r.where.join(', ')})`)

    externalReport = {
      generated: new Date().toISOString(),
      tool: 'scripts/check-links.mjs --external',
      note: 'Opt-in only. The default run makes no network requests. status 0 means the request failed locally and is not evidence the link is dead.',
      files: extFiles.map(f => rel(f)),
      urls_checked: results.length,
      broken: broken.length,
      auth_gated: gated.length,
      unreachable: unreachable.length,
      redirected: redirected.length,
      results,
    }
    if (jsonOut) {
      const target = path.resolve(ROOT, jsonOut.replace(/\.json$/, '') + '-external.json')
      fs.writeFileSync(target, JSON.stringify(externalReport, null, 2) + '\n')
      console.log(`\nrelatorio JSON externo: ${rel(target)}`)
    }
  }

  const problems = dead.length + (anchorReport ? anchorReport.dead : 0) + (externalReport ? externalReport.broken : 0)
  if (strict && problems > 0) process.exit(1)
}
