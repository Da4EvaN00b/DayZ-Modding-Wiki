export const meta = {
  name: 'wiki-propagate-translations',
  description: 'Propagate verified English wiki corrections into the 11 translated language copies (code identical, prose translated)',
  phases: [
    { title: 'Propagate', detail: 'Per (chapter x language): read the English git diff and mirror the same technical fix into the translation' },
  ],
}

const LANGS = ['pt', 'de', 'ru', 'es', 'fr', 'ja', 'zh-hans', 'cs', 'pl', 'hu', 'it']
const BASE = 'cf5347e~1'
const HEAD = 'cf5347e'

const PROP_SCHEMA = {
  type: 'object',
  additionalProperties: false,
  properties: {
    lang: { type: 'string' },
    translated_file: { type: 'string' },
    file_edited: { type: 'boolean' },
    applied_count: { type: 'number' },
    skipped: {
      type: 'array',
      items: {
        type: 'object',
        additionalProperties: false,
        properties: { what: { type: 'string' }, reason: { type: 'string' } },
        required: ['what', 'reason'],
      },
    },
    note: { type: 'string' },
  },
  required: ['lang', 'translated_file', 'file_edited', 'applied_count', 'skipped', 'note'],
}

function shortName(p) { return p.split(/[\\/]/).slice(-2).join('/') }

function propPrompt(enPath, lang) {
  const transPath = enPath.replace(/^en\//, lang + '/')
  return [
    'You are propagating ALREADY-VERIFIED English corrections into the ' + lang + ' translation of a DayZ wiki chapter. The English file was just fact-checked against the vanilla engine sources and corrected. Your job is to apply the SAME technical fixes to the translation — do NOT re-verify, re-translate the whole chapter, or invent new changes.',
    '',
    'ENGLISH FILE (source of truth for the changes): ' + enPath,
    'TRANSLATED FILE TO EDIT: ' + transPath,
    '',
    'STEP 1 — See exactly what changed in English. Run:',
    '  git -c core.autocrlf=false --no-pager diff ' + BASE + ' ' + HEAD + ' -- "' + enPath + '"',
    'Each hunk shows the old (-) English and the new (+) English. Those are the ONLY changes to mirror.',
    '',
    'STEP 2 — Read the translated file, then apply each change to it:',
    '- Code, identifiers, class/method names, signatures, parameter lists, return types, enum values, config keys, file paths, numbers, and XML/brace structure are IDENTICAL across all languages and are NEVER translated. Find them verbatim in the translated file and change exactly what the English diff changed.',
    '- Natural-language prose (table description cells, sentences, and code COMMENTS) appears in ' + lang + ' in the translated file. Keep the existing ' + lang + ' wording; change only the portion the English correction changed, and write any new/changed words in correct ' + lang + '. If the English change added or rewrote a comment or sentence, translate that new text into ' + lang + '.',
    '- If the English correction replaced an entire code block (e.g. a corrected signature list or a fixed XML/.layout example), replace the corresponding block in the translated file with the same corrected code, translating only its comments/labels into ' + lang + '.',
    '- Use exact verbatim Edits. Do NOT reflow, restyle, or re-translate untouched text. Never introduce an error.',
    '- The translated file is a translation of the OLD English, so the pre-correction text should be present (in ' + lang + ' for prose, identical for code). If a specific change genuinely cannot be located because the translation diverged, SKIP it and record what and why.',
    '',
    'Apply ALL changes from the diff, then return the structured result (set file_edited true only if you made at least one Edit; applied_count = number of distinct corrections mirrored).',
  ].join('\n')
}

let FILES = args
if (typeof FILES === 'string') {
  try { FILES = JSON.parse(FILES) } catch (e) { FILES = FILES.split(/\r?\n/).map(s => s.trim()).filter(Boolean) }
}
if (!Array.isArray(FILES) || FILES.length === 0) {
  throw new Error('args must be a non-empty array of en/ file paths; got ' + typeof args)
}

const WORK = []
for (const f of FILES) {
  for (const lang of LANGS) WORK.push({ en: f, lang: lang })
}
log('Propagating ' + FILES.length + ' chapters x ' + LANGS.length + ' languages = ' + WORK.length + ' work units')

phase('Propagate')
const results = await pipeline(
  WORK,
  (w) => agent(propPrompt(w.en, w.lang), {
    schema: PROP_SCHEMA,
    phase: 'Propagate',
    label: w.lang + ':' + shortName(w.en),
    agentType: 'general-purpose',
  }).catch(() => null)
)

const clean = results.filter(Boolean)
const edited = clean.filter(r => r.file_edited)
const totalApplied = clean.reduce((s, r) => s + (r.applied_count || 0), 0)
const totalSkipped = clean.reduce((s, r) => s + ((r.skipped && r.skipped.length) || 0), 0)
const failed = WORK.length - clean.length

const byLang = {}
for (const r of clean) {
  byLang[r.lang] = byLang[r.lang] || { edited: 0, applied: 0 }
  if (r.file_edited) byLang[r.lang].edited += 1
  byLang[r.lang].applied += (r.applied_count || 0)
}
log('Propagation done: ' + edited.length + '/' + WORK.length + ' files edited, ' + totalApplied + ' corrections mirrored, ' + totalSkipped + ' skipped, ' + failed + ' agent failures')

return {
  work_units: WORK.length,
  files_edited: edited.length,
  corrections_mirrored: totalApplied,
  skipped: totalSkipped,
  agent_failures: failed,
  by_language: byLang,
  details: clean,
}