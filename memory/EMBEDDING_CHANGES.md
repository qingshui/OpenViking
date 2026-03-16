# OpenViking 开发记录

## 2026-03-12: 添加 openai_compatible embedding provider

### 背景
用户需要使用自定义的 embedding API 地址（非 OpenAI 官方 API），调用本地部署的 embedding 模型。

### 修改的文件

| 文件 | 修改内容 |
|------|----------|
| `openviking_cli/utils/config/embedding_config.py` | 1. 在 provider 选项中添加 `openai_compatible`<br>2. 添加 `openai_compatible` 的验证逻辑（要求 api_key 和 api_base 必填）<br>3. 工厂方法使用 `OpenAICompatibleDenseEmbedder` |
| `openviking/models/embedder/openai_embedders.py` | 新增 `OpenAICompatibleDenseEmbedder` 类，支持非标准 OpenAI 响应格式 |
| `openviking/models/embedder/__init__.py` | 导出新的 `OpenAICompatibleDenseEmbedder` 类 |
| `tests/misc/test_config_validation.py` | 添加 `test_openai_compatible_provider()` 测试函数 |

### 新增类: OpenAICompatibleDenseEmbedder

位于 `openviking/models/embedder/openai_embedders.py`

**特性：**
- 使用 httpx 直接调用 API，而非 OpenAI SDK
- 支持多种响应格式：
  - 标准 OpenAI: `{"data": [{"embedding": [...]}]}`
  - 简单列表: `[{"embedding": [...]}]`
  - 嵌套列表: `[{"embedding": [[...]]}]`
  - 直接 embedding: `{"embedding": [...]}`

### 配置示例

```json
{
  "embedding": {
    "dense": {
      "provider": "openai_compatible",
      "api_base": "http://10.67.184.13:8001",
      "api_key": "your-api-key",
      "model": "qwen3-embedding",
      "dimension": 1024
    }
  }
}
```

### 测试验证

使用 `http://10.67.184.13:8001/embeddings` 端点和 `qwen3-embedding` 模型测试通过：
- 单个 embedding: 向量维度 1024 ✓
- 批量 embedding: 正确返回多个向量 ✓
