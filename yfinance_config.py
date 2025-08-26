"""
yfinance API 配置和最佳实践设置
"""

# 速率限制配置
RATE_LIMIT_CONFIG = {
    # 请求间延迟（秒）
    "delay_min": 1.0,      # 最小延迟
    "delay_max": 3.0,      # 最大延迟
    "batch_delay": 5.0,    # 批次间延迟
    
    # 重试配置
    "max_retries": 3,      # 最大重试次数
    "backoff_factor": 2,   # 退避因子
    "retry_statuses": [429, 500, 502, 503, 504],  # 需要重试的HTTP状态码
    
    # 批处理配置
    "batch_size": 5,       # 每批处理的股票数量
    "cache_ttl_hours": 24, # 缓存有效期（小时）
}

# 用户代理配置（避免被识别为爬虫）
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:89.0) Gecko/20100101 Firefox/89.0',
]

# API限制说明和解决方案
API_LIMITS_INFO = """
yfinance API 限制和解决方案:

1. 速率限制 (Rate Limiting):
   - 问题: "Too Many Requests. Rate limited. Try after a while."
   - 原因: 请求频率过高
   - 解决方案:
     * 增加请求间延迟 (1-3秒)
     * 使用指数退避重试
     * 批量处理减少总请求数

2. IP封禁:
   - 问题: 长时间无法访问
   - 原因: 同一IP请求过多
   - 解决方案:
     * 使用代理轮换
     * 分散请求时间
     * 使用不同User-Agent

3. 数据缺失:
   - 问题: "possibly delisted" 或空数据
   - 原因: 股票代码无效或市场休市
   - 解决方案:
     * 验证股票代码有效性
     * 处理市场假期
     * 使用备用数据源

4. 网络超时:
   - 问题: 连接超时或响应慢
   - 原因: 网络不稳定或服务器负载高
   - 解决方案:
     * 增加超时时间
     * 使用连接池
     * 实现重试机制
"""

# 最佳实践建议
BEST_PRACTICES = """
yfinance 使用最佳实践:

1. API方法选择:
   - 优先使用 yf.download() 而不是 yf.Ticker()
   - yf.download() 对速率限制更友好
   - 批量下载时使用 yf.download() 的多股票功能
   - 设置 progress=False, show_errors=False 减少输出

2. 缓存策略:
   - 本地缓存历史数据避免重复请求
   - 设置合理的缓存过期时间（推荐24小时）
   - 检查缓存有效性，避免使用过期数据

3. 请求优化:
   - 批量获取数据而非单个请求
   - 使用适当的延迟时间（1-3秒）
   - 批量处理时增大batch_size（5-10个股票）
   - 避免在交易时间高峰期大量请求

4. 错误处理和重试:
   - 实现指数退避重试机制
   - 处理429（速率限制）状态码
   - 提供降级方案（单个请求）
   - 记录失败请求用于分析

5. 会话管理:
   - 复用HTTP会话减少连接开销
   - 设置合适的User-Agent避免被识别为爬虫
   - 使用连接池提高效率

6. 监控和日志:
   - 监控API使用情况和成功率
   - 记录响应时间和错误类型
   - 及时发现和处理速率限制问题

7. 合规使用:
   - 遵守API使用条款
   - 不要进行恶意或过度频繁的请求
   - 考虑使用付费API获得更好服务
"""

def print_api_info():
    """打印API限制信息和最佳实践"""
    print(API_LIMITS_INFO)
    print(BEST_PRACTICES)

def check_yfinance_version():
    """检查yfinance版本兼容性"""
    try:
        import yfinance as yf
        import inspect
        
        print(f"yfinance版本: {getattr(yf, '__version__', '未知')}")
        
        # 检查关键参数支持
        download_signature = inspect.signature(yf.download)
        params = download_signature.parameters
        
        critical_params = {
            'show_errors': 'show_errors' in params,
            'session': 'session' in params,
            'threads': 'threads' in params,
            'progress': 'progress' in params,
            'group_by': 'group_by' in params,
        }
        
        print("参数支持情况:")
        for param, supported in critical_params.items():
            status = "✅" if supported else "❌"
            print(f"  {param}: {status}")
        
        return critical_params
        
    except Exception as e:
        print(f"版本检查失败: {e}")
        return {}

def get_recommended_config(usage_type="normal"):
    """
    根据使用场景获取推荐配置
    
    Args:
        usage_type: 使用类型 ("light", "normal", "heavy", "batch")
    
    Returns:
        配置字典
    """
    configs = {
        "light": {  # 轻度使用：偶尔查询几个股票
            "delay_min": 0.5,
            "delay_max": 1.5,
            "batch_size": 3,
            "max_retries": 2,
        },
        "normal": {  # 正常使用：日常分析和回测
            "delay_min": 1.0,
            "delay_max": 3.0,
            "batch_size": 5,
            "max_retries": 3,
        },
        "heavy": {   # 重度使用：大量数据分析
            "delay_min": 2.0,
            "delay_max": 5.0,
            "batch_size": 3,
            "max_retries": 5,
        },
        "batch": {   # 批量处理：数据收集和研究
            "delay_min": 3.0,
            "delay_max": 8.0,
            "batch_size": 2,
            "max_retries": 5,
        }
    }
    
    return configs.get(usage_type, configs["normal"])

if __name__ == "__main__":
    print_api_info()
    
    print("\n推荐配置示例:")
    for usage_type in ["light", "normal", "heavy", "batch"]:
        config = get_recommended_config(usage_type)
        print(f"\n{usage_type.upper()} 使用场景:")
        for key, value in config.items():
            print(f"  {key}: {value}")
