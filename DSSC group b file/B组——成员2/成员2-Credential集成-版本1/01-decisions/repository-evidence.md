# GitHub仓库证据记录

## 仓库信息

- Repository: https://github.com/MaxVer11111/DSSC-project
- Branch: main
- Reviewed Commit: f1992e3
- Review Date: 2026-08-15

## 已确认的Compliance API参数

- Environment: development
- Method: POST
- Endpoint:
  https://compliance.lab.gaia-x.eu/development/api/credential-offers/standard-compliance
- Query Parameter: vcid
- Request Content-Type: application/vp+jwt
- Request Body: raw VP-JWT
- Expected HTTP Status: 201
- Response Content-Type: application/vc+jwt

## 仓库成功VP组成

1. LegalPerson VC-JWT
2. Issuer / Terms and Conditions VC-JWT
3. LegalRegistrationNumber VC-JWT

## 使用限制

仓库成功凭证属于官方Gaia-X样例主体，不属于
Energy Data Provider Ltd.

仓库中的官方DID、kid、注册号码和签名身份
只能用于研究结构和验证API流程，不能直接作为
本项目主体的签名材料。