# 成员2 Credential 集成

本目录用于统一 A/C/D 组数据，维护未签名 LegalPerson、ServiceOffering，
准备开发阶段 VC-JWT / VP-JWT，并记录正式签名前的所有阻塞项。

## 当前结论

- 未签名跨文件一致性：`PASS`；
- Compliance API 参数：已从组长仓库成功 Demo 确认；
- 官方 VP 本地结构验证：`PASS`；
- 项目 DID `did:web:mp-operations.org`：DNS 解析失败；
- 正式合规签名：`BLOCKED_DO_NOT_SIGN`；
- 本地开发签名流水线：允许使用临时 RSA 密钥测试。

## 开发签名与正式签名的区别

`05-signed/provisional/` 中的文件只用于证明以下技术步骤可以运行：

1. 读取 JSON-LD；
2. 生成 RS256 VC-JWT；
3. 将 VC 组装为 VP；
4. 生成 RS256 VP-JWT；
5. 使用公开 JWK 在本地验证签名。

这些文件使用不可解析的占位 DID，不是 Compliance API 意义上的有效凭证，
不得放入 `valid/`，也不得宣称已经通过 Gaia-X 合规验证。

## 本地开发签名步骤

在项目根目录运行：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass `
  -File ".\scripts\generate-development-keypair.ps1"
```

临时私钥默认保存在仓库外：

```text
%LOCALAPPDATA%\DSSC-Credential-Dev\dev-rsa-private.jwk
```

不要上传、提交或发送该文件。

然后生成开发 JWT：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass `
  -File ".\scripts\build-provisional-jwts.ps1"
```

最后验证 JWT 三段结构、Header、`kid` 和 RS256 签名：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass `
  -File ".\scripts\verify-provisional-jwts.ps1"
```

预期结果：

```text
Overall local cryptographic verification: PASS
```

## 正式材料到位后的替换项

收到 A 组或组长的正式材料后，必须替换：

- Issuer DID；
- Holder DID；
- DID Document；
- `kid`；
- 私钥及算法；
- Legal Registration Number Credential；
- Terms and Conditions Credential。

替换后必须重新生成所有 VC-JWT 和 VP-JWT；不能只修改已经签名的 JWT。
