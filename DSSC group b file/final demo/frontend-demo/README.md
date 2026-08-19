# DSSC Compliance Validation Demo

本机单页演示，使用浏览器直接调用 Gaia-X Compliance API。主实时请求最多等待 32 秒；仅对 8 秒内发生的瞬时浏览器/网络失败追加一次 15 秒重试。网络、CORS 或超时异常时，才回退到 2026-08-18 保存的原始响应。

## 运行

```powershell
npm install
npm run dev
```

生产构建：

```powershell
npm run build
npm run verify
npm run preview
```

`predev` 与 `prebuild` 会从相邻交付目录复制六份历史 `.txt` 和六份预签名 VP-JWT 到静态资产目录。脚本采用显式允许列表，不复制任何私钥 JWK。
