# 无效测试源文件

这些文件是特意构造的无效测试输入。

它们仍然是语法正确的 JSON-LD 文件。每个文件只修改一个目标条件，以便判断测试失败发生在哪一个验证层级。

| 编号     | 文件                                          | 故意修改的内容                 | 预期失败层级     |
| ------ | ------------------------------------------- | ----------------------- | ---------- |
| INV-01 | `legal-person.missing-name.jsonld`          | 删除 `gx:legalName`       | 凭证内容验证     |
| INV-02 | `legal-person.expired.jsonld`               | 将 `validUntil` 设置为过去的日期 | 时间有效性验证    |
| INV-03 | `service-offering.provider-mismatch.jsonld` | 使用另一个 Provider DID      | 跨文件一致性检查   |
| INV-04 | `service-offering.dataset-mismatch.jsonld`  | 引用另一个 Dataset URI       | 跨文件一致性检查   |
| INV-05 | `dataset.wrong-format.jsonld`               | 将格式设置为 `text/csv`       | SHACL/语义验证 |
| INV-06 | `dataset.reversed-dates.jsonld`             | 将开始日期设置为晚于结束日期          | 时间语义规则验证   |

这些文件都是未签名的源文件。只有在最终签名身份和验证规则确定之后，才会生成最终的无效 JWT 测试用例。
