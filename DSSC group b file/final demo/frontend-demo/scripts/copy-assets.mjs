import { copyFile, mkdir } from 'node:fs/promises'
import { dirname, join } from 'node:path'
import { fileURLToPath } from 'node:url'

const projectRoot = join(dirname(fileURLToPath(import.meta.url)), '..')
const demoRoot = join(projectRoot, '..')
const deliveryRoot = join(
  demoRoot,
  '最终版（最终干净交付物）',
  '成员2-Credential集成-v0.3-es256-candidate-FINAL-20260817',
)
const responsesRoot = join(demoRoot, 'api-responses')
const signedRoot = join(deliveryRoot, '06-invalid-tests', 'signed-es256-candidate')
const baselineRoot = join(deliveryRoot, '05-signed', 'es256-candidate')

const responseTarget = join(projectRoot, 'public', 'data', 'responses')
const jwtTarget = join(projectRoot, 'public', 'data', 'jwts')
await Promise.all([mkdir(responseTarget, { recursive: true }), mkdir(jwtTarget, { recursive: true })])

const assets = [
  ...['valid', 'inv-01', 'inv-02', 'inv-03', 'inv-04', 'inv-07'].map((id) => ({
    from: join(responsesRoot, `${id}_dev.txt`),
    to: join(responseTarget, `${id}_dev.txt`),
  })),
  {
    from: join(baselineRoot, 'presentation.es256-candidate.vp.jwt'),
    to: join(jwtTarget, 'base.vp.jwt'),
  },
  ...['01', '02', '03', '04'].map((id) => ({
    from: join(signedRoot, `presentation.inv-${id}.es256-candidate.vp.jwt`),
    to: join(jwtTarget, `inv-${id}.vp.jwt`),
  })),
  {
    from: join(signedRoot, 'presentation.inv-07.tampered-signature.es256-candidate.vp.jwt'),
    to: join(jwtTarget, 'inv-07.vp.jwt'),
  },
]

await Promise.all(assets.map(({ from, to }) => copyFile(from, to)))
console.log(`Copied ${assets.length} public demo assets (6 responses, 6 pre-signed VP-JWTs).`)
