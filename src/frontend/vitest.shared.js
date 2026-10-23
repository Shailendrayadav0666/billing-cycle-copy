import path from 'node:path'
import { fileURLToPath } from 'node:url'

// The tests and step definitions live in the repo-root tests/ tree (AIRE five-roots rule), outside
// this package. Node-style resolution walks up from the importing file and never reaches this
// package's node_modules, so bare imports from those files are resolved as if imported from here.
export const packageRoot = fileURLToPath(new URL('.', import.meta.url))
export const repoRoot = path.resolve(packageRoot, '../..')

export function resolveFromPackage() {
  const anchor = path.join(packageRoot, 'package.json')
  return {
    name: 'aire-resolve-from-package',
    enforce: 'pre',
    async resolveId(source, importer, options) {
      const bare = !source.startsWith('.') && !source.startsWith('/') && !source.startsWith('\0') && !/^[A-Za-z]:/.test(source)
      if (!bare || !importer || path.resolve(importer).startsWith(packageRoot)) return null
      return this.resolve(source, anchor, { ...options, skipSelf: true })
    },
  }
}
