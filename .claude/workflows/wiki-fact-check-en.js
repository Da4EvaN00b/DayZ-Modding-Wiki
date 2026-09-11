export const meta = {
  name: 'wiki-fact-check-en',
  description: 'Fact-check English DayZ wiki chapters against vanilla scripts + reference docs (+web) and auto-fix confirmed technical errors',
  phases: [
    { title: 'Verify', detail: 'Extract and verify falsifiable technical claims per chapter against authoritative sources' },
    { title: 'Fix', detail: 'Adversarially re-confirm WRONG claims and apply only proven corrections to the chapter file' },
  ],
}

const DEFAULT_CHAPTERS = [
  'D:/DayZProjects/docs/wiki/en/06-engine-api/01-entity-system.md',
  'D:/DayZProjects/docs/wiki/en/01-enforce-script/12-gotchas.md',
  'D:/DayZProjects/docs/wiki/en/07-patterns/03-rpc-patterns.md',
]

const CLAIMS_SCHEMA = {
  type: 'object',
  additionalProperties: false,
  properties: {
    chapter: { type: 'string' },
    claims: {
      type: 'array',
      items: {
        type: 'object',
        additionalProperties: false,
        properties: {
          claim_text: { type: 'string' },
          quote: { type: 'string' },
          category: { type: 'string', enum: ['api_signature', 'class_name', 'enum_value', 'config_syntax', 'file_path', 'behavior', 'other'] },
          verdict: { type: 'string', enum: ['CORRECT', 'WRONG', 'UNVERIFIABLE'] },
          source: { type: 'string', enum: ['vanilla_script', 'reference_doc', 'stardz_mod', 'web', 'none'] },
          evidence: { type: 'string' },
          proposed_correction: { type: 'string' },
          confidence: { type: 'number' },
        },
        required: ['claim_text', 'quote', 'category', 'verdict', 'source', 'evidence', 'proposed_correction', 'confidence'],
      },
    },
  },
  required: ['chapter', 'claims'],
}

const FIX_SCHEMA = {
  type: 'object',
  additionalProperties: false,
  properties: {
    chapter: { type: 'string' },
    file_edited: { type: 'boolean' },
    applied: {
      type: 'array',
      items: {
        type: 'object',
        additionalProperties: false,
        properties: {
          original: { type: 'string' },
          corrected: { type: 'string' },
          reason: { type: 'string' },
          evidence: { type: 'string' },
          confidence: { type: 'number' },
        },
        required: ['original', 'corrected', 'reason', 'evidence', 'confidence'],
      },
    },
    skipped: {
      type: 'array',
      items: {
        type: 'object',
        additionalProperties: false,
        properties: {
          claim: { type: 'string' },
          reason: { type: 'string' },
        },
        required: ['claim', 'reason'],
      },
    },
  },
  required: ['chapter', 'file_edited', 'applied', 'skipped'],
}

function shortName(p) { return p.split(/[\\/]/).slice(-2).join('/') }

function verifyPrompt(path) {
  return [
    'You are a meticulous DayZ Enforce Script fact-checker. Check ONE wiki chapter for technical accuracy against authoritative local sources (web only as a last resort).',
    '',
    'CHAPTER TO CHECK (read the whole file first): ' + path,
    '',
    'AUTHORITATIVE SOURCES, in priority order:',
    '1. Vanilla DayZ script dump at D:/DayZProjects/scripts/ — ~2,805 .c files, the DEFINITIVE source for class names, inheritance, method signatures, parameter lists, return types, and enum/constant values. Use Grep to find a symbol across that folder, then Read the .c file around the match to confirm the exact signature.',
    '2. Curated reference docs at D:/DayZProjects/docs/ — especially DAYZ_ENFORCE_SCRIPT_REFERENCE.md, DAYZ_GUI_REFERENCE.md, DAYZ_VANILLA_SCRIPTS_REFERENCE.md, DAYZ_MOD_ARCHITECTURE_PATTERNS.md.',
    '3. First-party working mods at D:/DayZProjects/StarDZ_Core/ — real Enforce Script patterns.',
    '4. Web (ONLY when 1-3 cannot resolve a claim): the official Bohemia Interactive DayZ community wiki. Use WebSearch/WebFetch sparingly and never over local evidence.',
    '',
    'EXTRACT only FALSIFIABLE technical claims, e.g.:',
    '- API/method/function signatures: exact name, parameters, return type, owning class.',
    '- Class names and inheritance (e.g. ItemBase extends InventoryItem).',
    '- Enum and constant names and their values.',
    '- config.cpp / mod.cpp keys and syntax, types.xml fields.',
    '- File paths, extensions, and folder-layout claims.',
    '- Concrete documented runtime behavior or call order.',
    'DO NOT extract opinions, tutorial narration, design advice, or anything not checkable against the engine.',
    '',
    'For EACH claim set verdict:',
    '- CORRECT: confirmed by a source (cite it in evidence).',
    '- WRONG: contradicted by a source (method does not exist in the dump, wrong return type, misspelled class, wrong enum value, etc.). Give a precise proposed_correction grounded in the source and cite the evidence (file path + what you found).',
    '- UNVERIFIABLE: no source confirms or refutes it. Do NOT guess WRONG.',
    'Always Grep the vanilla dump for the exact symbol before judging it WRONG. Prefer vanilla scripts over reference docs over web.',
    'Put a verbatim snippet from the chapter into quote so a later editor can locate the exact text.',
    '',
    'Return ONLY the structured object. confidence is 0-1.',
  ].join('\n')
}

function fixPrompt(path, wrong) {
  return [
    'You are a careful DayZ wiki editor. Apply ONLY confirmed factual corrections to ONE chapter file. The burden of proof is on CHANGING text — when in doubt, leave it alone.',
    '',
    'FILE TO EDIT: ' + path,
    '',
    'CANDIDATE CORRECTIONS flagged WRONG by a prior checker (treat every one as UNPROVEN until you verify it yourself):',
    JSON.stringify(wrong, null, 2),
    '',
    'PROCEDURE for each candidate:',
    '1. Independently verify against the authoritative sources YOURSELF — do not trust the prior checker evidence string:',
    '   - Vanilla scripts D:/DayZProjects/scripts/ (Grep the symbol, Read the .c) = definitive.',
    '   - Reference docs D:/DayZProjects/docs/*.md. First-party D:/DayZProjects/StarDZ_Core/. Web only as last resort.',
    '2. Apply the correction ONLY if you can reproduce evidence that the original is wrong AND that your correction is right. Otherwise SKIP it and record why in skipped.',
    '3. Read the file, then Edit with the exact verbatim original text from it. Change ONLY the incorrect technical token(s). Do NOT rewrite prose, reflow text, or alter style.',
    '4. Follow wiki conventions: inline class/method/path names stay in backticks; Enforce Script fences stay as c; NEVER translate or alter code identifiers. Keep the chapter voice.',
    '5. If a flagged claim is actually correct, SKIP it — never introduce an error.',
    '',
    'After editing, return the structured changelog: every correction actually applied (original, corrected, reason, evidence, confidence) and everything skipped (claim, reason). Set file_edited true only if you made at least one Edit.',
  ].join('\n')
}

let CHAPTERS = args
if (typeof CHAPTERS === 'string') {
  try { CHAPTERS = JSON.parse(CHAPTERS) } catch (e) { CHAPTERS = CHAPTERS.split(/\r?\n/).map(s => s.trim()).filter(Boolean) }
}
if (!Array.isArray(CHAPTERS) || CHAPTERS.length === 0) {
  CHAPTERS = DEFAULT_CHAPTERS
}
log('args diagnostic: typeof=' + (typeof args) + ' isArray=' + Array.isArray(args) + ' -> running ' + CHAPTERS.length + ' chapter(s)')

phase('Verify')
const results = await pipeline(
  CHAPTERS,
  (path) => agent(verifyPrompt(path), { schema: CLAIMS_SCHEMA, phase: 'Verify', label: 'verify:' + shortName(path), agentType: 'general-purpose' }),
  (verify, path) => {
    if (!verify || !Array.isArray(verify.claims)) {
      return { chapter: path, file_edited: false, applied: [], skipped: [], wrong_count: 0, note: 'verify-failed' }
    }
    const wrong = verify.claims.filter(c => c.verdict === 'WRONG')
    const claims_total = verify.claims.length
    if (wrong.length === 0) {
      return { chapter: path, file_edited: false, applied: [], skipped: [], wrong_count: 0, claims_total }
    }
    return agent(fixPrompt(path, wrong), { schema: FIX_SCHEMA, phase: 'Fix', label: 'fix:' + shortName(path), agentType: 'general-purpose' })
      .then(fix => fix
        ? Object.assign({}, fix, { wrong_count: wrong.length, claims_total })
        : { chapter: path, file_edited: false, applied: [], skipped: [], wrong_count: wrong.length, claims_total, note: 'fix-failed' })
  }
)

const clean = results.filter(Boolean)
const edited = clean.filter(r => r.file_edited)
const totalApplied = clean.reduce((s, r) => s + ((r.applied && r.applied.length) || 0), 0)
const totalWrong = clean.reduce((s, r) => s + (r.wrong_count || 0), 0)
const totalClaims = clean.reduce((s, r) => s + (r.claims_total || 0), 0)
log('Fact-check done: ' + edited.length + ' chapters edited, ' + totalApplied + ' corrections applied, ' + totalWrong + ' flagged WRONG out of ' + totalClaims + ' claims')

return {
  chapters_checked: clean.length,
  chapters_edited: edited.length,
  claims_total: totalClaims,
  flagged_wrong: totalWrong,
  corrections_applied: totalApplied,
  details: clean,
}