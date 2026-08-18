# A组公开教学Demo签名密钥说明

本目录中的`provider-key.private.jwk.json`由A组公开提供，
仅用于本课程DSSC教学Demo。

- Provider DID：`did:web:shenyousota.github.io:dssc-toolbox`
- kid：`did:web:shenyousota.github.io:dssc-toolbox#key-1`
- 算法：`ES256`
- 密钥类型：`EC P-256`
- 来源：`https://github.com/ShenYouSOTA/dssc-toolbox`
- 公网DID Document：`https://shenyousota.github.io/dssc-toolbox/did.json`

该文件只用于虚构主体`Energy Data Provider Ltd.`的教学演示，
不得用于生产环境、真实身份、真实服务或其他项目。

本项目保存该文件，是为了让其他成员只下载成员2仓库，
即可重新生成和验证ES256候选Credential。