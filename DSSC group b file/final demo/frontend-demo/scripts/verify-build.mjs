import { readFile, readdir } from 'node:fs/promises'
import { join } from 'node:path'
import { fileURLToPath } from 'node:url'

const distUrl = new URL('../dist/', import.meta.url)
const dist = fileURLToPath(distUrl)
const required = [
  'data/responses/valid_dev.txt',
  'data/responses/inv-01_dev.txt',
  'data/responses/inv-02_dev.txt',
  'data/responses/inv-03_dev.txt',
  'data/responses/inv-04_dev.txt',
  'data/responses/inv-07_dev.txt',
  'data/jwts/base.vp.jwt',
  'data/jwts/inv-01.vp.jwt',
  'data/jwts/inv-02.vp.jwt',
  'data/jwts/inv-03.vp.jwt',
  'data/jwts/inv-04.vp.jwt',
  'data/jwts/inv-07.vp.jwt',
]

await Promise.all(required.map((path) => readFile(new URL(path, distUrl))))

async function walk(directory) {
  const entries = await readdir(directory, { withFileTypes: true })
  return (await Promise.all(entries.map(async (entry) => {
    const path = join(directory, entry.name)
    return entry.isDirectory() ? walk(path) : [path]
  }))).flat()
}

const files = await walk(dist)
if (files.some((path) => /private|\.jwk(?:\.|$)/i.test(path))) {
  throw new Error('Private key material found in dist.')
}

const contents = await Promise.all(files.map(async (path) => {
  try { return await readFile(path, 'utf8') } catch { return '' }
}))
if (contents.some((content) => /"d"\s*:\s*"[A-Za-z0-9_-]{20,}"/.test(content))) {
  throw new Error('Possible private JWK parameter found in dist.')
}

// Guard the live window against regressing below the observed deep-validation
// cadence in the recorded sequential run (BASE through INV-04).
const appSource = await readFile(new URL('../src/App.tsx', import.meta.url), 'utf8')
const primaryLiteral = appSource.match(/const PRIMARY_TIMEOUT_MS = ([\d_]+)/)?.[1]
const primaryTimeoutMs = Number(primaryLiteral?.replaceAll('_', ''))
if (!Number.isFinite(primaryTimeoutMs)) throw new Error('Could not read PRIMARY_TIMEOUT_MS.')

const historicalOrder = ['valid_dev.txt', 'inv-01_dev.txt', 'inv-02_dev.txt', 'inv-03_dev.txt', 'inv-04_dev.txt']
const timestamps = await Promise.all(historicalOrder.map(async (name) => {
  const text = await readFile(new URL(`data/responses/${name}`, distUrl), 'utf8')
  const value = text.match(/^Timestamp:\s*(.+)$/m)?.[1]?.trim()
  const timestamp = Date.parse(value ?? '')
  if (!Number.isFinite(timestamp)) throw new Error(`Missing recorded timestamp in ${name}.`)
  return timestamp
}))
const observedGaps = timestamps.slice(1).map((timestamp, index) => timestamp - timestamps[index])
const largestObservedGap = Math.max(...observedGaps)
if (primaryTimeoutMs < largestObservedGap + 5_000) {
  throw new Error(`Primary live window ${primaryTimeoutMs}ms is too close to observed ${largestObservedGap}ms cadence.`)
}

console.log(`Verified ${required.length} expected assets, ${primaryTimeoutMs}ms live window, and no private JWK material.`)
