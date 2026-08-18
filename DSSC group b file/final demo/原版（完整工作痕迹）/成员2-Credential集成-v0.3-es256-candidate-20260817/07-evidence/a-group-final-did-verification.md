# A组最终Provider DID与Demo密钥验证报告

## 1. 验证对象

- A组仓库：`https://github.com/ShenYouSOTA/dssc-toolbox`
- A组仓库Commit：`89d40ccf0bd43af22f2129f81d0ba0214f5c327c`
- Provider DID：`did:web:shenyousota.github.io:dssc-toolbox`
- kid：`did:web:shenyousota.github.io:dssc-toolbox#key-1`
- 算法：`ES256`
- 密钥类型：`EC P-256`
- 公网DID Document：`https://shenyousota.github.io/dssc-toolbox/did.json`

## 2. 验证方法

在A组仓库中运行：

`just did-verify`

如果本机没有just，则直接运行A组的：

`demo/did_identity.py verify`

该工具读取A组本地Demo私钥对应的公钥，并与公网did.json中的publicKeyJwk进行比较。

## 3. 验证结果

- 公网did.json访问：PASS
- DID Document ID匹配：PASS
- verificationMethod ID匹配：PASS
- 公钥类型EC：PASS
- 曲线P-256：PASS
- 公网公钥与A组Demo私钥匹配：PASS

## 4. 结论

A组最终Provider DID已经能够从公网正常解析。

公网did.json中的EC P-256公钥与A组仓库中的教学Demo私钥匹配，可以开始准备ES256候选Credential签名。

该密钥仅用于虚构主体Energy Data Provider Ltd.的教学Demo，不得用于生产环境。
