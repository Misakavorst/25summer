#!/usr/bin/env python3
"""
yfinance助手工具使用示例
解决 "Too Many Requests. Rate limited" 问题
"""

from yfinance_helper import YFinanceHelper
from yfinance_config import get_recommended_config, print_api_info
from datetime import datetime, timedelta
import time

def example_basic_usage():
    """基础使用示例"""
    print("=== 基础使用示例 ===")
    
    # 创建助手实例（使用保守的延迟设置）
    helper = YFinanceHelper(delay_min=1.0, delay_max=3.0)
    
    # 获取单个股票数据
    print("获取AAPL股票数据...")
    data = helper.get_stock_data("AAPL", "2024-01-01", "2024-01-31")
    
    if data is not None:
        print(f"✅ 成功获取 {len(data)} 条AAPL数据")
        print(f"价格范围: ${data['Close'].min():.2f} - ${data['Close'].max():.2f}")
    else:
        print("❌ 获取数据失败")

def example_batch_processing():
    """批量处理示例 - 使用yf.download()批量功能"""
    print("\n=== 批量处理示例 (yf.download) ===")
    
    # 使用推荐的批量处理配置
    config = get_recommended_config("normal")  # 使用normal配置，因为yf.download更高效
    helper = YFinanceHelper(
        delay_min=config["delay_min"],
        delay_max=config["delay_max"]
    )
    
    # 要分析的股票列表
    tickers = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA"]
    
    print(f"批量获取 {len(tickers)} 只股票的数据（使用yf.download批量功能）...")
    start_time = time.time()
    
    batch_data = helper.batch_get_stock_data(
        tickers,
        "2024-01-01",
        "2024-01-31",
        batch_size=10,  # yf.download可以处理更大的批次
        delay_between_batches=3.0,
        use_bulk_download=True  # 使用yf.download的批量下载功能
    )
    
    elapsed = time.time() - start_time
    print(f"批量处理完成，耗时: {elapsed:.1f} 秒")
    
    # 显示结果
    for ticker in tickers:
        if ticker in batch_data:
            data = batch_data[ticker]
            avg_price = data['Close'].mean()
            print(f"✅ {ticker}: {len(data)} 条数据, 平均价格: ${avg_price:.2f}")
        else:
            print(f"❌ {ticker}: 获取失败")
    
    # 对比传统方法
    print(f"\n🔄 对比传统逐个下载方法...")
    start_time = time.time()
    
    individual_data = helper.batch_get_stock_data(
        tickers[:3],  # 只测试前3个避免太久
        "2024-01-01",
        "2024-01-31",
        batch_size=3,
        use_bulk_download=False  # 使用传统逐个下载
    )
    
    elapsed_individual = time.time() - start_time
    print(f"传统方法耗时: {elapsed_individual:.1f} 秒")
    
    if elapsed_individual > 0:
        speedup = elapsed_individual / elapsed * len(tickers) / 3
        print(f"🚀 批量下载预计快 {speedup:.1f} 倍")

def example_price_analysis():
    """价格分析示例"""
    print("\n=== 价格分析示例 ===")
    
    helper = YFinanceHelper()
    
    # 分析NVIDIA在特定日期的价格
    ticker = "NVDA"
    analysis_dates = [
        datetime(2024, 1, 15),
        datetime(2024, 2, 15),
        datetime(2024, 3, 15),
    ]
    
    print(f"分析 {ticker} 在不同日期的价格:")
    prices = []
    
    for date in analysis_dates:
        price = helper.get_stock_price_on_date(ticker, date)
        if price is not None:
            prices.append(price)
            print(f"  {date.strftime('%Y-%m-%d')}: ${price:.2f}")
        else:
            print(f"  {date.strftime('%Y-%m-%d')}: 数据获取失败")
    
    if len(prices) >= 2:
        change = (prices[-1] - prices[0]) / prices[0] * 100
        print(f"\n📈 {ticker} 期间涨跌幅: {change:+.2f}%")

def example_with_error_handling():
    """带错误处理的示例"""
    print("\n=== 错误处理示例 ===")
    
    helper = YFinanceHelper()
    
    # 测试各种可能的错误情况
    test_cases = [
        ("AAPL", "2024-01-01", "2024-01-31", "正常股票"),
        ("INVALID", "2024-01-01", "2024-01-31", "无效股票代码"),
        ("AAPL", "2025-01-01", "2025-01-31", "未来日期"),
        ("AAPL", "1900-01-01", "1900-01-31", "过早日期"),
    ]
    
    for ticker, start, end, description in test_cases:
        print(f"\n测试: {description} ({ticker})")
        data = helper.get_stock_data(ticker, start, end, max_retries=2)
        
        if data is not None:
            print(f"✅ 成功: {len(data)} 条数据")
        else:
            print(f"❌ 失败: 无法获取数据")

def example_cache_demo():
    """缓存功能演示"""
    print("\n=== 缓存功能演示 ===")
    
    helper = YFinanceHelper()
    
    ticker = "MSFT"
    start_date = "2024-01-01"
    end_date = "2024-01-15"
    
    # 第一次请求（从API获取）
    print("第一次请求（从API获取）...")
    start_time = time.time()
    data1 = helper.get_stock_data(ticker, start_date, end_date)
    time1 = time.time() - start_time
    
    if data1 is not None:
        print(f"✅ 第一次请求成功，耗时: {time1:.2f} 秒")
        
        # 第二次请求（从缓存获取）
        print("第二次请求（从缓存获取）...")
        start_time = time.time()
        data2 = helper.get_stock_data(ticker, start_date, end_date)
        time2 = time.time() - start_time
        
        if data2 is not None:
            print(f"✅ 第二次请求成功，耗时: {time2:.2f} 秒")
            print(f"🚀 缓存加速比: {time1/time2:.1f}x")
        else:
            print("❌ 缓存请求失败")
    else:
        print("❌ 第一次请求失败")

def main():
    """运行所有示例"""
    print("🔧 yfinance助手工具使用示例")
    print("解决 'Too Many Requests. Rate limited' 问题")
    print("=" * 60)
    
    # 显示API限制信息
    print("\n📋 API限制和解决方案:")
    print("- 使用延迟减少请求频率")
    print("- 实现缓存避免重复请求") 
    print("- 批量处理提高效率")
    print("- 错误重试增强稳定性")
    
    # 运行示例
    examples = [
        example_basic_usage,
        example_batch_processing, 
        example_price_analysis,
        example_cache_demo,
        example_with_error_handling,
    ]
    
    for example_func in examples:
        try:
            example_func()
        except KeyboardInterrupt:
            print("\n⏹️  用户中断执行")
            break
        except Exception as e:
            print(f"\n❌ 示例执行出错: {e}")
    
    print("\n" + "=" * 60)
    print("💡 使用建议:")
    print("1. 根据使用频率调整延迟时间")
    print("2. 利用缓存减少API请求")
    print("3. 批量处理大量股票数据")
    print("4. 在非交易时间进行大量数据收集")
    print("5. 监控API使用情况，避免触发限制")

if __name__ == "__main__":
    main()
