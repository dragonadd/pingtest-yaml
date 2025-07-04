# 代理节点测试工具

一个用于测试代理节点连接性和延迟的Python脚本，支持从GitHub Gist下载订阅内容，自动去重，并将节点按连接状态分类保存。

## 功能特点

- ✅ 支持GitHub Gist链接的订阅内容下载
- ✅ 自动解析YAML格式的代理配置
- ✅ 智能去重，避免重复节点
- ✅ 多线程并发测试，提高效率
- ✅ 实时显示测试进度
- ✅ 自动分类保存正常和超时节点
- ✅ 详细的日志记录

## 环境要求

- Python 3.6+
- 必需的Python库：
  - `requests`
  - `PyYAML`

## 安装依赖

```bash
pip install requests PyYAML
```

或者使用requirements.txt（如果提供）：

```bash
pip install -r requirements.txt
```

## 使用方法

### 1. 运行脚本

```bash
python proxytest.py
```

### 2. 输入GitHub Gist链接

脚本启动后，会提示输入GitHub Gist原始内容链接：

```
请输入GitHub Gist原始内容链接:
```

输入类似以下格式的链接：
```
https://gist.githubusercontent.com/username/gist_id/raw/file_name.yaml
```

### 3. 等待测试完成

脚本会自动：
- 下载订阅内容
- 解析YAML配置
- 去除重复节点
- 并发测试所有节点的连接性
- 显示实时进度

### 4. 查看结果

测试完成后，会生成两个文件：
- `normal_links.txt` - 连接正常的节点
- `timeout_links.txt` - 连接超时的节点

## 配置说明

脚本中的主要配置参数：

```python
TIMEOUT = 5  # 连接超时时间（秒）
MAX_WORKERS = 20  # 并发测试的最大线程数
```

可以根据需要修改这些参数：
- `TIMEOUT`: 增加超时时间可以给网络较慢的节点更多时间
- `MAX_WORKERS`: 增加并发数可以加快测试速度，但会增加系统负载

## 输入格式要求

脚本期望的YAML格式示例：

```yaml
proxies:
  - name: "节点1"
    server: "example.com"
    port: 443
    type: "ss"
    cipher: "aes-256-gcm"
    password: "password123"
  - name: "节点2"
    server: "example2.com"
    port: 80
    type: "http"
```

## 输出文件格式

生成的文件格式为：

```
proxies:
  - {name: "节点1", server: "example.com", port: 443, type: "ss", cipher: "aes-256-gcm", password: "password123"}
  - {name: "节点2", server: "example2.com", port: 80, type: "http"}
```

## 注意事项

1. **仅支持GitHub Gist链接**：出于安全考虑，脚本只接受GitHub Gist的URL
2. **需要网络连接**：脚本需要能够访问GitHub和测试的代理服务器
3. **防火墙设置**：确保防火墙允许脚本进行网络连接测试
4. **大量节点测试**：当节点数量较多时，测试可能需要较长时间

## 故障排除

### 常见问题

**Q: 提示"仅支持GitHub Gist的URL"**
A: 请确保输入的是GitHub Gist的原始内容链接，格式如：`https://gist.githubusercontent.com/...`

**Q: 解析YAML时出错**
A: 检查Gist中的内容是否为有效的YAML格式，确保缩进和语法正确

**Q: 所有节点都显示超时**
A: 可能是网络问题或防火墙阻止了连接，尝试增加`TIMEOUT`值或检查网络设置

**Q: 脚本运行缓慢**
A: 可以适当增加`MAX_WORKERS`值以提高并发数，但注意不要设置过高

### 日志信息

脚本会输出详细的日志信息，包括：
- 下载和解析进度
- 去重统计
- 测试进度
- 错误信息

## 许可证

请根据实际情况添加适当的许可证信息。

## 贡献

欢迎提交Issue和Pull Request来改进这个工具。

## 免责声明

本工具仅用于测试网络连接性，请遵守相关法律法规和服务条款。
