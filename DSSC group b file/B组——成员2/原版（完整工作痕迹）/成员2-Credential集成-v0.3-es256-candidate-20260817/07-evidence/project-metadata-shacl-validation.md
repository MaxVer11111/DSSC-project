# 项目实际Dataset Metadata的SHACL本地预检报告

## 1. 验证对象

- 被测文件：`03-normalized-metadata/dataset-metadata.jsonld`
- Dataset canonical URI：`https://example.org/dssc-energy/datasets/building-energy-hourly-v1`
- Shape文件：D组E5F权威Shape
- Shape路径：`07-evidence/d-group-handoff-20260817/D组交付-ZIP解压/shacl-rules/building-energy-shapes_D.ttl`
- Shape SHA-256：`E5F150D7DBE338FCBB7B020585CC83713DE1FDB6B1A4BE393BE1BEF47895411E`
- 验证工具：PySHACL 0.30.1
- 验证方式：Python API加载RDF图后执行SHACL验证

## 2. 验证结果

- `Conforms: True`
- PySHACL退出码：`0`
- 总体判定：**PASS**

## 3. 说明

本报告验证的是成员2当前项目实际使用的Dataset Metadata。

D组原交付包中的PDF报告验证的是D组提供的示例Metadata，因此两类证据分别保存，不能互相替代。

当前项目Metadata已经迁移到A组定稿的Dataset canonical URI，并通过D组E5F Shape本地预检。

由于Windows环境下PySHACL命令行对相对文件路径的URI解析出现兼容性问题，本次验证先通过RDFLib读取Data Graph和Shapes Graph，再调用PySHACL Python API执行验证。该调整只改变文件加载方式，不改变使用的Metadata、Shape或验证规则。

本地PySHACL结果用于签名前开发预检。最终集成阶段仍需由成员3的Compliance API或D组ITB再次执行验证。