# ES256候选JWT本地验签报告

## 结论

- 公网DID Document解析：**PASS**
- 公网EC P-256公钥与教学Demo私钥匹配：**PASS**
- 有效VC/VP与无效测试JWT的预期签名状态：**PASS**
- 总体本地密码学验证：**PASS**

## 签名参数

- DID：`did:web:shenyousota.github.io:dssc-toolbox`
- kid：`did:web:shenyousota.github.io:dssc-toolbox#key-1`
- 算法：`ES256`
- DID Document：`https://shenyousota.github.io/dssc-toolbox/did.json`

## 逐文件结果

| 文件 | 分段 | alg | typ | kid匹配 | 实际签名有效 | 结果 |
|---|---:|---|---|---|---|---|
| `05-signed/es256-candidate/legal-person.es256-candidate.vc.jwt` | 3 | `ES256` | `vc+jwt` | True | True | PASS |
| `05-signed/es256-candidate/service-offering.es256-candidate.vc.jwt` | 3 | `ES256` | `vc+jwt` | True | True | PASS |
| `05-signed/es256-candidate/presentation.es256-candidate.vp.jwt` | 3 | `ES256` | `vp+jwt` | True | True | PASS |
| `06-invalid-tests/signed-es256-candidate/presentation.inv-01.es256-candidate.vp.jwt` | 3 | `ES256` | `vp+jwt` | True | True | PASS |
| `06-invalid-tests/signed-es256-candidate/legal-person.missing-name.es256-candidate.vc.jwt` | 3 | `ES256` | `vc+jwt` | True | True | PASS |
| `06-invalid-tests/signed-es256-candidate/presentation.inv-02.es256-candidate.vp.jwt` | 3 | `ES256` | `vp+jwt` | True | True | PASS |
| `06-invalid-tests/signed-es256-candidate/legal-person.expired.es256-candidate.vc.jwt` | 3 | `ES256` | `vc+jwt` | True | True | PASS |
| `06-invalid-tests/signed-es256-candidate/presentation.inv-03.es256-candidate.vp.jwt` | 3 | `ES256` | `vp+jwt` | True | True | PASS |
| `06-invalid-tests/signed-es256-candidate/service-offering.provider-mismatch.es256-candidate.vc.jwt` | 3 | `ES256` | `vc+jwt` | True | True | PASS |
| `06-invalid-tests/signed-es256-candidate/presentation.inv-04.es256-candidate.vp.jwt` | 3 | `ES256` | `vp+jwt` | True | True | PASS |
| `06-invalid-tests/signed-es256-candidate/service-offering.dataset-mismatch.es256-candidate.vc.jwt` | 3 | `ES256` | `vc+jwt` | True | True | PASS |
| `06-invalid-tests/signed-es256-candidate/presentation.inv-07.tampered-signature.es256-candidate.vp.jwt` | 3 | `ES256` | `vp+jwt` | True | False | PASS |

## 边界

本报告证明本地JWT结构、ES256签名、公网DID公钥匹配以及源文件封装正确。
它不等于Gaia-X Compliance API已经接受这些候选凭证；API测试由成员3执行。
教学Demo私钥为公开演示材料，不得用于生产环境。
