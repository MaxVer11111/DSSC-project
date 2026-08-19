import { useMemo, useState } from 'react'

const ENDPOINT = 'https://compliance.lab.gaia-x.eu/development/api/credential-offers/standard-compliance'
// Historical deep-validation requests completed roughly 20–22 seconds apart.
// Leave enough room for browser preflight, TLS, DID and X.509 network work.
const PRIMARY_TIMEOUT_MS = 32_000
const FAST_RETRY_TIMEOUT_MS = 15_000
const FAST_FAILURE_THRESHOLD_MS = 8_000

type CaseId = 'BASE' | 'INV-01' | 'INV-02' | 'INV-03' | 'INV-04' | 'INV-07'
type RunState = 'idle' | 'running' | 'complete'
type Source = 'LIVE' | 'RECORDED'
type JsonRecord = Record<string, unknown>

type DemoCase = {
  id: CaseId
  name: string
  shortName: string
  vcid: string
  jwtFile: string
  responseFile: string
  evidence: string[]
  defaultTone: 'blue' | 'green' | 'orange'
  defaultLabel: string
  pipelineTarget: 'deep' | 'signature'
}

type Result = {
  source: Source
  httpStatus: number
  durationMs: number
  capturedAt?: string
  fallbackReason?: string
  body: JsonRecord
  rawBody: string
}

type CaseRun = {
  state: RunState
  result?: Result
  attempt?: number
  timeoutMs?: number
}

const CASES: DemoCase[] = [
  {
    id: 'BASE',
    name: 'Trust-chain penetration',
    shortName: 'Baseline reaches deep validation',
    vcid: 'https://gaia-x.eu/.well-known/dssc-test-valid-r3.jwt',
    jwtFile: 'base.vp.jwt',
    responseFile: 'valid_dev.txt',
    evidence: ['No registration number issuers found in VP', 'missing a gx:Issuer entity with terms and conditions'],
    defaultTone: 'blue',
    defaultLabel: '穿透达成',
    pipelineTarget: 'deep',
  },
  {
    id: 'INV-01',
    name: 'Missing legalName',
    shortName: 'Required property omitted',
    vcid: 'https://gaia-x.eu/.well-known/dssc-test-inv-01-r3.jwt',
    jwtFile: 'inv-01.vp.jwt',
    responseFile: 'inv-01_dev.txt',
    evidence: ['legalName'],
    defaultTone: 'orange',
    defaultLabel: 'API 已拒绝，预期命中证据不足',
    pipelineTarget: 'deep',
  },
  {
    id: 'INV-02',
    name: 'Expired credential',
    shortName: 'Past validUntil timestamp',
    vcid: 'https://gaia-x.eu/.well-known/dssc-test-inv-02-r3.jwt',
    jwtFile: 'inv-02.vp.jwt',
    responseFile: 'inv-02_dev.txt',
    evidence: ['is in the past'],
    defaultTone: 'green',
    defaultLabel: '按预期拒绝',
    pipelineTarget: 'deep',
  },
  {
    id: 'INV-03',
    name: 'Provider DID mismatch',
    shortName: 'Issuer / provider mismatch',
    vcid: 'https://gaia-x.eu/.well-known/dssc-test-inv-03-r3.jwt',
    jwtFile: 'inv-03.vp.jwt',
    responseFile: 'inv-03_dev.txt',
    evidence: ['issuer and provider issuer do not match'],
    defaultTone: 'green',
    defaultLabel: '按预期拒绝',
    pipelineTarget: 'deep',
  },
  {
    id: 'INV-04',
    name: 'Dataset URI mismatch',
    shortName: 'Wrong aggregation target',
    vcid: 'https://gaia-x.eu/.well-known/dssc-test-inv-04-r3.jwt',
    jwtFile: 'inv-04.vp.jwt',
    responseFile: 'inv-04_dev.txt',
    evidence: ['wrong-dataset'],
    defaultTone: 'orange',
    defaultLabel: 'API 已拒绝，预期命中证据不足',
    pipelineTarget: 'deep',
  },
  {
    id: 'INV-07',
    name: 'Tampered signature',
    shortName: 'Modified VP signature',
    vcid: 'https://gaia-x.eu/.well-known/dssc-test-inv-07-r3.jwt',
    jwtFile: 'inv-07.vp.jwt',
    responseFile: 'inv-07_dev.txt',
    evidence: ['signature verification failed'],
    defaultTone: 'green',
    defaultLabel: '按预期拒绝',
    pipelineTarget: 'signature',
  },
]

const EMPTY_RUNS = Object.fromEntries(CASES.map((item) => [item.id, { state: 'idle' as const }])) as Record<CaseId, CaseRun>

function assetUrl(path: string) {
  return `${import.meta.env.BASE_URL}data/${path}`
}

function safeObject(value: unknown): JsonRecord {
  return value !== null && typeof value === 'object' && !Array.isArray(value) ? value as JsonRecord : { response: value }
}

function parseBody(rawBody: string): JsonRecord {
  try {
    return safeObject(JSON.parse(rawBody))
  } catch {
    return { response: rawBody }
  }
}

function parseRecorded(text: string, durationMs: number, reason: string): Result {
  const marker = '--- Response Body ---'
  const markerIndex = text.indexOf(marker)
  if (markerIndex < 0) throw new Error('Recorded response has no Response Body section')

  const rawBody = text.slice(markerIndex + marker.length).trim()
  const timestamp = text.match(/^Timestamp:\s*(.+)$/m)?.[1]?.trim()
  const status = Number(text.match(/^HTTP Status:\s*(\d+)$/m)?.[1])
  if (!Number.isFinite(status)) throw new Error('Recorded response has no HTTP status')

  return {
    source: 'RECORDED',
    httpStatus: status,
    durationMs,
    capturedAt: timestamp,
    fallbackReason: reason,
    body: parseBody(rawBody),
    rawBody,
  }
}

function getErrors(body: JsonRecord): string[] {
  return Array.isArray(body.errors) ? body.errors.filter((item): item is string => typeof item === 'string') : []
}

function priorityErrors(item: DemoCase, body: JsonRecord): string[] {
  const errors = getErrors(body)
  if (!errors.length) return []
  const matches = errors.filter((error) => item.evidence.some((needle) => error.toLowerCase().includes(needle.toLowerCase())))
  if (item.id === 'BASE') return matches.slice(0, 3)
  const unique = [...matches, ...errors.filter((error) => !matches.includes(error))]
  return unique.slice(0, 3)
}

function resultTone(item: DemoCase, result?: Result) {
  if (!result) return 'neutral'
  if (result.httpStatus < 400) return 'orange'
  return item.defaultTone
}

function formatDuration(durationMs: number) {
  return durationMs >= 1000 ? `${(durationMs / 1000).toFixed(2)}s` : `${Math.round(durationMs)}ms`
}

function displayField(value: unknown) {
  if (typeof value === 'string') return value
  if (value === undefined) return '—'
  return JSON.stringify(value)
}

function App() {
  const [selectedId, setSelectedId] = useState<CaseId>('BASE')
  const [runs, setRuns] = useState<Record<CaseId, CaseRun>>(EMPTY_RUNS)
  const [expanded, setExpanded] = useState(false)
  const [runAllActive, setRunAllActive] = useState(false)
  const [progress, setProgress] = useState(0)
  const [copyState, setCopyState] = useState<'idle' | 'copied' | 'failed'>('idle')

  const selectedCase = CASES.find((item) => item.id === selectedId)!
  const selectedRun = runs[selectedId]
  const selectedResult = selectedRun.result
  const selectedErrors = useMemo(
    () => selectedResult ? priorityErrors(selectedCase, selectedResult.body) : [],
    [selectedCase, selectedResult],
  )
  const completedCount = CASES.filter((item) => runs[item.id].state === 'complete').length
  const anyRunning = CASES.some((item) => runs[item.id].state === 'running')

  async function loadRecorded(item: DemoCase, durationMs: number, reason: string) {
    const response = await fetch(assetUrl(`responses/${item.responseFile}`))
    if (!response.ok) throw new Error(`Recorded response unavailable (${response.status})`)
    return parseRecorded(await response.text(), durationMs, reason)
  }

  async function execute(item: DemoCase, onAttempt: (attempt: number, timeoutMs: number) => void): Promise<Result> {
    const startedAt = performance.now()
    try {
      const jwtResponse = await fetch(assetUrl(`jwts/${item.jwtFile}`))
      if (!jwtResponse.ok) throw new Error(`VP-JWT unavailable (${jwtResponse.status})`)
      const jwt = (await jwtResponse.text()).trim()

      const timeouts = [PRIMARY_TIMEOUT_MS, FAST_RETRY_TIMEOUT_MS]
      let lastReason = 'browser request error'
      let attemptsMade = 0

      for (let index = 0; index < timeouts.length; index += 1) {
        const attemptStartedAt = performance.now()
        const controller = new AbortController()
        const timeoutMs = timeouts[index]
        const timer = window.setTimeout(() => controller.abort('timeout'), timeoutMs)
        attemptsMade = index + 1
        onAttempt(attemptsMade, timeoutMs)

        try {
          const response = await fetch(`${ENDPOINT}?vcid=${encodeURIComponent(item.vcid)}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/vp+jwt' },
            body: jwt,
            signal: controller.signal,
          })
          const rawBody = await response.text()
          return {
            source: 'LIVE',
            httpStatus: response.status,
            durationMs: performance.now() - startedAt,
            body: parseBody(rawBody),
            rawBody,
          }
        } catch (error) {
          const attemptDuration = performance.now() - attemptStartedAt
          lastReason = controller.signal.aborted
            ? `timeout after ${Math.round(timeoutMs / 1000)}s`
            : error instanceof Error ? error.message : 'browser request error'

          // A full timeout indicates a slow/unavailable service; duplicating the heavy
          // validation immediately would add load without improving the demo.
          if (controller.signal.aborted || attemptDuration >= FAST_FAILURE_THRESHOLD_MS) break
        } finally {
          window.clearTimeout(timer)
        }
      }

      return loadRecorded(
        item,
        performance.now() - startedAt,
        `${lastReason} (${attemptsMade} live attempt${attemptsMade === 1 ? '' : 's'})`,
      )
    } catch (error) {
      const durationMs = performance.now() - startedAt
      const reason = error instanceof Error ? error.message : 'browser request error'
      return loadRecorded(item, durationMs, reason)
    }
  }

  async function runCase(item: DemoCase) {
    setSelectedId(item.id)
    setExpanded(false)
    setCopyState('idle')
    setRuns((current) => ({ ...current, [item.id]: { ...current[item.id], state: 'running' } }))
    try {
      const result = await execute(item, (attempt, timeoutMs) => {
        setRuns((current) => ({ ...current, [item.id]: { ...current[item.id], state: 'running', attempt, timeoutMs } }))
      })
      setRuns((current) => ({ ...current, [item.id]: { state: 'complete', result } }))
      return result
    } catch (error) {
      setRuns((current) => ({ ...current, [item.id]: { state: 'idle' } }))
      throw error
    }
  }

  async function runAll() {
    if (anyRunning) return
    setRunAllActive(true)
    setProgress(0)
    for (let index = 0; index < CASES.length; index += 1) {
      setProgress(index + 1)
      try {
        await runCase(CASES[index])
      } catch {
        // A missing local fallback is surfaced by leaving this case idle; continue the sequence.
      }
    }
    setRunAllActive(false)
  }

  async function copyResponse() {
    if (!selectedResult) return
    try {
      await navigator.clipboard.writeText(JSON.stringify(selectedResult.body, null, 2))
      setCopyState('copied')
      window.setTimeout(() => setCopyState('idle'), 1800)
    } catch {
      setCopyState('failed')
    }
  }

  const apiMode = anyRunning ? 'REQUESTING' : selectedResult?.source ?? 'LIVE'

  return (
    <div className="app-shell">
      <header className="topbar">
        <div className="brand-block">
          <div className="eyebrow"><span className="eyebrow-line" />DSSC · TRUST &amp; COMPLIANCE</div>
          <h1>DSSC Compliance Validation Demo</h1>
          <p>Real-time Credential Validation via Gaia-X Compliance API</p>
        </div>
        <div className="top-actions">
          <div className="api-state" aria-live="polite">
            <span>API STATUS</span>
            <strong className={`mode mode-${apiMode.toLowerCase()}`}><i />{apiMode}</strong>
          </div>
          <button className="run-all" type="button" onClick={runAll} disabled={anyRunning}>
            {runAllActive ? <><span className="spinner" />{progress} / 6</> : <><span aria-hidden="true">▶</span> Run All</>}
          </button>
        </div>
      </header>

      <main className="workspace">
        <aside className="case-panel panel">
          <div className="panel-heading">
            <div>
              <span className="section-index">01</span>
              <h2>Validation cases</h2>
            </div>
            <span className="count">{completedCount} / 6</span>
          </div>

          <div className="case-list" role="listbox" aria-label="Validation cases">
            {CASES.map((item) => {
              const run = runs[item.id]
              const tone = resultTone(item, run.result)
              return (
                <button
                  type="button"
                  role="option"
                  aria-selected={selectedId === item.id}
                  className={`case-row ${selectedId === item.id ? 'selected' : ''}`}
                  key={item.id}
                  onClick={() => { setSelectedId(item.id); setExpanded(false); setCopyState('idle') }}
                >
                  <span className={`case-marker tone-${tone}`}>
                    {run.state === 'running' ? <span className="spinner dark" /> : run.state === 'complete' ? '✓' : ''}
                  </span>
                  <span className="case-copy">
                    <span className="case-id">{item.id}</span>
                    <strong>{item.name}</strong>
                    <small>{item.shortName}</small>
                  </span>
                  <span className="chevron">›</span>
                </button>
              )
            })}
          </div>

          <button className="run-selected" type="button" onClick={() => runCase(selectedCase)} disabled={anyRunning}>
            {selectedRun.state === 'running' ? <><span className="spinner" />Running request</> : <><span aria-hidden="true">▶</span> Run Selected</>}
          </button>
          <p className="endpoint-note"><span />Development endpoint · 32s live window</p>
        </aside>

        <section className="pipeline-panel panel">
          <div className="panel-heading">
            <div>
              <span className="section-index">02</span>
              <h2>Validation pipeline</h2>
            </div>
            <span className={`semantic-badge tone-${selectedCase.defaultTone}`}>{selectedCase.defaultLabel}</span>
          </div>

          <div className="pipeline-context">
            <span className="mono-id">{selectedCase.id}</span>
            <div>
              <strong>{selectedCase.name}</strong>
              <small>{selectedCase.pipelineTarget === 'signature' ? 'Signature gate' : 'Deep validation reached'}</small>
            </div>
          </div>

          <div className={`pipeline ${selectedCase.pipelineTarget === 'signature' ? 'signature-stop' : 'deep-reached'} ${selectedRun.state}`}>
            <div className="linear-track">
              {[
                ['01', 'JWT Parsing', 'JWT 解析'],
                ['02', 'VP Signature', 'VP 签名'],
                ['03', 'DID Resolution', 'DID 解析'],
                ['04', 'X.509 Confirmation', 'X.509 证书确认'],
              ].map(([number, label, zh], index) => (
                <div className={`pipe-step step-${index + 1}`} key={number} title={`${label} · ${zh}`}>
                  <span className="node">{selectedRun.state === 'running' && index === 0 ? <span className="spinner dark" /> : number}</span>
                  <strong>{label}</strong>
                  <small>{zh}</small>
                </div>
              ))}
            </div>

            <div className="branch-zone">
              <div className="branch-source"><span>04</span><strong>X.509</strong></div>
              <div className="branch-lines" aria-hidden="true"><i /><i /><i /></div>
              <div className="branch-targets">
                <div className="branch-card" title="SHACL / Content · SHACL / 内容校验"><span>05</span><div><strong>SHACL / Content</strong><small>内容约束</small></div></div>
                <div className="branch-card" title="Labelling Criteria · 标签准则"><span>06</span><div><strong>Labelling Criteria</strong><small>标签准则</small></div></div>
                <div className="branch-card" title="Missing Credentials · 缺失凭证"><span>07</span><div><strong>Missing Credentials</strong><small>LRN / Issuer T&amp;C</small></div></div>
              </div>
            </div>
          </div>

          <div className="pipeline-legend">
            <span><i className="legend-dot passed" />Trust-chain penetrated</span>
            <span><i className="legend-dot rejected" />Validation rejected</span>
            <span><i className="legend-dot pending" />Not reached</span>
          </div>

          {completedCount > 0 && (
            <div className="summary-matrix">
              <div className="matrix-title"><span>RUN SUMMARY</span><strong>{completedCount} of 6 captured</strong></div>
              <div className="matrix-grid">
                {CASES.map((item) => {
                  const result = runs[item.id].result
                  return (
                    <button type="button" key={item.id} onClick={() => setSelectedId(item.id)} className={selectedId === item.id ? 'active' : ''}>
                      <span>{item.id}</span>
                      <strong>{result ? `HTTP ${result.httpStatus}` : '—'}</strong>
                      <small>{result ? `${formatDuration(result.durationMs)} · ${result.source}` : 'Not run'}</small>
                    </button>
                  )
                })}
              </div>
            </div>
          )}
        </section>

        <section className="response-panel panel">
          <div className="panel-heading response-heading">
            <div>
              <span className="section-index">03</span>
              <h2>API response</h2>
            </div>
            {selectedResult && <span className={`source-badge source-${selectedResult.source.toLowerCase()}`}><i />{selectedResult.source}</span>}
          </div>

          {!selectedResult && selectedRun.state !== 'running' && (
            <div className="empty-state">
              <div className="empty-glyph">{'{ }'}</div>
              <strong>No response captured</strong>
              <p>Select a case and run a validation request.</p>
            </div>
          )}

          {selectedRun.state === 'running' && (
            <div className="loading-state" aria-live="polite">
              <span className="loader-ring" />
              <strong>Calling Compliance API</strong>
              <p>Live attempt {selectedRun.attempt ?? 1} · waiting up to {Math.round((selectedRun.timeoutMs ?? PRIMARY_TIMEOUT_MS) / 1000)} seconds</p>
              <div className="loading-bar"><span /></div>
            </div>
          )}

          {selectedResult && selectedRun.state !== 'running' && (
            <div className="response-content">
              <div className="response-metrics">
                <div><span>HTTP STATUS</span><strong className="http-code">{selectedResult.httpStatus}</strong></div>
                <div><span>REQUEST TIME</span><strong>{formatDuration(selectedResult.durationMs)}</strong></div>
                <div><span>ERRORS</span><strong>{getErrors(selectedResult.body).length}</strong></div>
              </div>

              {selectedResult.source === 'RECORDED' && (
                <div className="recorded-note">
                  <strong>RECORDED FALLBACK</strong>
                  <span>Captured: {selectedResult.capturedAt ?? 'unknown'}</span>
                  <span>Live request failed: {selectedResult.fallbackReason}</span>
                </div>
              )}

              <dl className="response-fields">
                <div><dt>message</dt><dd>{displayField(selectedResult.body.message)}</dd></div>
                <div><dt>error</dt><dd>{displayField(selectedResult.body.error)}</dd></div>
              </dl>

              <div className="raw-errors">
                <div className="subheading"><span>PRIORITY RAW ERRORS</span><em>{selectedErrors.length} shown</em></div>
                {selectedErrors.length ? selectedErrors.map((error, index) => (
                  <div className="error-line" key={`${index}-${error.slice(0, 30)}`}>
                    <span>{String(index + 1).padStart(2, '0')}</span>
                    <code>{error}</code>
                  </div>
                )) : <p className="no-errors">No string entries in <code>errors[]</code>.</p>}
              </div>

              <button className="expand-button" type="button" onClick={() => setExpanded((value) => !value)} aria-expanded={expanded}>
                <span>{expanded ? '−' : '+'}</span>{expanded ? 'Hide full response' : 'Expand full response'}<i>{expanded ? '↑' : '↓'}</i>
              </button>

              {expanded && (
                <div className="json-view">
                  <div className="json-toolbar">
                    <span>RAW JSON</span>
                    <button type="button" onClick={copyResponse}>{copyState === 'copied' ? 'Copied' : copyState === 'failed' ? 'Copy failed' : 'Copy response'}</button>
                  </div>
                  <pre>{JSON.stringify(selectedResult.body, null, 2)}</pre>
                </div>
              )}
            </div>
          )}
        </section>
      </main>

      <footer>
        <span>Project demonstration interface — not an official Gaia-X product.</span>
        <span className="footer-endpoint">DEVELOPMENT · {ENDPOINT.replace('https://', '')}</span>
      </footer>
    </div>
  )
}

export default App
