import fs from 'node:fs'
import v8 from 'node:v8'
import vm from 'node:vm'

// `vitepress build` runs two complete Rollup builds -- client, then SSR -- in a
// single Node process (vitepress 1.6.4, `bundle()` in dist/node/chunk-*.js). At
// this site's size (1260 pages / 12 locales / ~211 MB of transformed module
// code) the client build leaves well over a gigabyte of garbage that V8 has not
// reclaimed by the time the SSR build begins allocating its own module graph,
// so the two peaks stack. On this site, that stacking was observed to kill
// the process with "Ineffective mark-compacts near heap limit" on Node
// 24.14.0 at buildConcurrency 64 with no GC plugin (an 8 GiB and, separately,
// a 16 GiB old-space allowance); no run without this plugin has been
// attempted on Node 22.23.2, so the same death on this runtime is unverified,
// not proven.
//
// Measured on this site (Node 22.23.2, --max-old-space-size=16384):
//
//   forced collection at SSR buildStart   heapUsed 3718 MB -> 2342 MB
//   forced collection at client closeBundle        3731 MB -> 3717 MB
//   forced collection at SSR closeBundle          15224 MB -> 15221 MB
//
// Only the first one does anything, so it is the only one kept. The two
// closeBundle points reclaim nothing because Vite still holds the Rollup bundle
// when that hook fires, and because VitePress deliberately retains
// `clientResult` -- it feeds the page-rendering pass afterwards. This plugin
// therefore does not, and cannot, "free the client bundle"; it only collects
// the garbage that is already unreachable at the one moment that was measured
// to matter.
//
// This plugin releases a measured 1382 MB immediately at SSR `buildStart`
// (verified run: 3720 MB -> 2338 MB; an earlier instrumented run measured
// 3718 MB -> 2342 MB, see above). It does not make the build cheap, and it
// does not establish a lower whole-run peak: no build on Node 22.23.2 has
// been run without this collection to compare peaks against. The verified
// run still needed a 16 GiB old-space allowance. See
// .audit/en-2026-09-11/build-REPORT.md.

/**
 * Prefer a real `--expose-gc` (NODE_OPTIONS or CLI). Fall back to exposing gc()
 * at runtime so a plain `npm run build` still benefits. Node documents that
 * v8.setFlagsFromString after startup may not take effect, so a failure here is
 * reported and treated as "no forced GC", never as a build error.
 */
function acquireGc(): (() => void) | null {
  const exposed = (globalThis as any).gc
  if (typeof exposed === 'function') return exposed as () => void
  try {
    v8.setFlagsFromString('--expose-gc')
    const gc = vm.runInNewContext('gc')
    return typeof gc === 'function' ? (gc as () => void) : null
  } catch {
    return null
  } finally {
    try {
      v8.setFlagsFromString('--no-expose-gc')
    } catch {
      /* best effort */
    }
  }
}

// Opt-in phase/memory timeline:  VP_BUILD_MEM_LOG=<writable path> npm run build
// Diagnostics only -- never allowed to fail a build.
const LOG = process.env.VP_BUILD_MEM_LOG
const t0 = Date.now()

function note(tag: string, msg: string) {
  if (!LOG) return
  try {
    const m = process.memoryUsage()
    fs.appendFileSync(
      LOG,
      [
        ((Date.now() - t0) / 1000).toFixed(1) + 's',
        tag,
        'rss=' + Math.round(m.rss / 1e6) + 'MB',
        'heap=' + Math.round(m.heapUsed / 1e6) + 'MB',
        'ext=' + Math.round(m.external / 1e6) + 'MB',
        msg
      ].join('\t') + '\n'
    )
  } catch {
    /* diagnostics must never break the build */
  }
}

export function buildMemoryPlugin(): any {
  let tag = 'client'
  let isBuild = false
  let nTransform = 0
  let transformChars = 0

  return {
    name: 'vitepress-build-memory',
    enforce: 'post',

    configResolved(config: any) {
      isBuild = config.command === 'build'
      tag = config.build?.ssr ? 'ssr' : 'client'
      note(tag, 'configResolved')
    },

    buildStart() {
      if (!isBuild) return
      note(tag, 'buildStart')
      // Only the SSR bundle's start was measured to release anything.
      if (tag !== 'ssr') return
      const gc = acquireGc()
      if (!gc) {
        console.warn(
          '[vitepress-build-memory] no gc() available; the SSR bundle will start ' +
            'with the client build\'s garbage still resident. Re-run with ' +
            'NODE_OPTIONS="--expose-gc --max-old-space-size=16384".'
        )
        return
      }
      note(tag, 'gc:before ssr bundle')
      gc()
      note(tag, 'gc:after ssr bundle')
    },

    transform(code: string, _id: string) {
      if (!LOG) return null
      nTransform++
      transformChars += code.length
      if (nTransform % 250 === 0) {
        note(tag, 'transform#' + nTransform + ' chars=' + Math.round(transformChars / 1e6) + 'M')
      }
      return null
    },

    // buildEnd/generateBundle also fire on failed builds; these are progress
    // markers for the timeline, not success markers.
    buildEnd() {
      if (isBuild) note(tag, 'buildEnd')
    },

    generateBundle(_options: any, bundle: Record<string, any>) {
      if (!LOG) return
      const names = Object.keys(bundle)
      let chars = 0
      for (const name of names) {
        const item = bundle[name]
        if (item.type === 'chunk') chars += item.code.length
        else if (typeof item.source === 'string') chars += item.source.length
      }
      note(tag, 'generateBundle outputs=' + names.length + ' chars=' + Math.round(chars / 1e6) + 'M')
    },

    closeBundle() {
      if (isBuild) note(tag, 'closeBundle')
    }
  }
}
