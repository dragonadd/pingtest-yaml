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

## 使用方法

1. 运行脚本

   ```bash
   python pingtest.py
   ```

2. 输入GitHub Gist链接

   脚本启动后，会提示输入GitHub Gist原始内容链接：

   ```
   请输入GitHub Gist原始内容链接:
   ```

   输入类似以下格式的链接：

   ```
   https://gist.githubusercontent.com/username/gist_id/raw/file_name.yaml
   ```

3. 等待测试完成

   脚本会自动：
   - 下载订阅内容
   - 解析YAML配置
   - 去除重复节点
   - 并发测试所有节点的连接性
   - 显示实时进度

4. 查看结果

   测试完成后，会生成两个文件：
   - `normal_links.txt` - 连接正常的节点
   - `timeout_links.txt` - 连接超时的节点

## 配置说明

脚本中的主要配置参数：

```python
TIMEOUT = 5  # 连接超时时间（秒）
MAX_WORKERS = 5  # 并发测试的最大线程数
TEST_URL = "https://cp.cloudflare.com/generate_204"  # 测试URL
```

可以根据需要修改这些参数：
- **TIMEOUT**: 增加超时时间可以给网络较慢的节点更多时间
- **MAX_WORKERS**: 增加并发数可以加快测试速度，但会增加系统负载
- **TEST_URL**: 修改测试URL可以测试不同的目标地址

## 输入格式要求

脚本期望的YAML格式示例：

```yaml
proxies:
  -
    name: '🇹🇼 [IPLC-移动优化-家宽-台湾1] ✨ 2x'
    type: vmess
    server: 69-in-1.226969.xyz
    port: 30002
    uuid: aa20dc42-e6e5-3c65-88fb-3e41989ca89f
    alterId: 0
    cipher: auto
    udp: true
  -
    name: '🇭🇰 [IPLC-移动优化-香港1] ✨ 2x'
    type: ss
    server: 69-in-1.226969.xyz
    port: 10010
    cipher: aes-256-gcm
    password: q50KdJEMfQWAwOTo
    udp: true
```

另一种：

```yaml
proxies:
  - {name: "[Trojan] 🇭🇰 香港", server: bgp-xdd.blue-bgp.xyz, port: 44011, client-fingerprint: chrome, type: trojan, password: 40ffbaaf-ac3f-4fdc-a440-ca3933e751b0, sni: aliyun.com, skip-cert-verify: true, udp: true}
  - {name: "[Trojan] 🇭🇰 香港 2", server: bgp-xdd.blue-bgp.xyz, port: 44012, client-fingerprint: chrome, type: trojan, password: 4d86bc6b-0ed7-41b7-94d4-f80b6a16a8bb, sni: aliyun.com, skip-cert-verify: true, udp: true}
  - {name: "[Trojan] 🇭🇰 香港 3", server: bgp-xdd.blue-bgp.xyz, port: 44013, client-fingerprint: chrome, type: trojan, password: a050b1e4-c1c4-468c-a3c6-d960fc3fd0fc, sni: aliyun.com, skip-cert-verify: true, udp: true}
```

## 输出文件格式

生成的文件格式为：

```yaml
proxies:
    - { name: '🇭🇰 香港 01', type: ss, server: glienhglian.yangliq.com, port: 31001, cipher: aes-128-gcm, password: 33f1891d-5632-4d68-9f9a-f0f000242fde, udp: true }
    - { name: '🇭🇰 香港 02', type: ss, server: glienhglian.yangliq.com, port: 31002, cipher: aes-128-gcm, password: 33f1891d-5632-4d68-9f9a-f0f000242fde, udp: true }
```

其中，`delay` 字段表示延迟时间（毫秒），仅出现在正常节点中。

## 注意事项

- 仅支持GitHub Gist的原始内容URL，普通Gist页面URL会被拒绝
- 测试节点延迟时，每个节点默认超时时间为5秒（可在代码中修改`TIMEOUT`常量）
- 脚本使用并发测试，默认最多同时测试5个节点（可在代码中修改`MAX_WORKERS`常量）
- 测试方法仅检测TCP连接是否成功，不进行实际代理功能测试
- 对于大量节点（如超过100个），测试过程可能需要较长时间（脚本会显示进度信息）
- 确保网络连接正常，否则测试结果可能不准确
- 脚本会自动去除重复节点，去重依据是节点的关键字段（排除name、remarks等非关键字段）
- 如果订阅内容不是有效的YAML格式，脚本会报错并显示部分内容以帮助排查问题

## 故障排除

### 常见问题

**Q: 提示"仅支持GitHub Gist的URL"**  
A: 请确保输入的是GitHub Gist的原始内容链接，格式如：https://gist.githubusercontent.com/...

**Q: 解析YAML时出错**  
A: 检查Gist中的内容是否为有效的YAML格式，确保缩进和语法正确

**Q: 所有节点都显示超时**  
A: 可能是网络问题或防火墙阻止了连接，尝试增加`TIMEOUT`值或检查网络设置

**Q: 脚本运行缓慢**  
A: 可以适当增加`MAX_WORKERS`值以提高并发数，但注意不要设置过高

## 日志信息

脚本会输出详细的日志信息，包括：

- 下载和解析进度
- 去重统计
- 测试进度
- 错误信息

## 许可证

本项目采用MIT许可证。

## 贡献

欢迎提交Issue和Pull Request来改进这个工具。

## 免责声明

本项目仅供学习和技术交流使用，不保证任何可用性或稳定性。使用本工具所产生的任何法律责任及后果与作者无关。用户应自行承担使用本工具可能带来的所有风险。请遵守当地法律法规，禁止用于任何非法用途。使用本工具即表示您已理解并接受以上声明。

