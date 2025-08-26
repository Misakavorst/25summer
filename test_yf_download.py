#!/usr/bin/env python3
"""
测试yf.download()方法的效果和性能
对比yf.Ticker()和yf.download()的差异
"""

import yfinance as yf
import time
import pandas as pd
from datetime import datetime, timedelta
import sys
import os

# 添加当前目录到路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from yfinance_helper import YFinanceHelper

def test_yf_download_single():
    """测试yf.download()单个股票"""
    print("=== 测试 yf.download() 单个股票 ===")
    
    ticker = "AAPL"
    start_date = "2024-01-01"
    end_date = "2024-01-31"
    
    print(f"获取 {ticker} 数据 ({start_date} 到 {end_date})")
    
    try:
        start_time = time.time()
        # 根据yfinance版本动态设置参数
        download_kwargs = {
            'start': start_date,
            'end': end_date,
            'progress': False,
            'threads': False
        }
        
        # 检查show_errors参数是否支持
        import inspect
        download_signature = inspect.signature(yf.download)
        if 'show_errors' in download_signature.parameters:
            download_kwargs['show_errors'] = False
        
        data = yf.download(ticker, **download_kwargs)
        elapsed = time.time() - start_time
        
        if not data.empty:
            print(f"✅ 成功获取 {len(data)} 条记录，耗时: {elapsed:.2f} 秒")
            print(f"价格范围: ${data['Close'].min():.2f} - ${data['Close'].max():.2f}")
            return True
        else:
            print("❌ 数据为空")
            return False
            
    except Exception as e:
        print(f"❌ 错误: {e}")
        return False

def test_yf_download_multiple():
    """测试yf.download()多个股票"""
    print("\n=== 测试 yf.download() 多个股票 ===")
    
    tickers = ["AAPL", "MSFT", "GOOGL"]
    start_date = "2024-01-01"
    end_date = "2024-01-31"
    
    print(f"批量获取 {tickers} 数据")
    
    try:
        start_time = time.time()
        # 根据yfinance版本动态设置参数
        download_kwargs = {
            'start': start_date,
            'end': end_date,
            'progress': False,
            'threads': True,
            'group_by': 'ticker'
        }
        
        # 检查show_errors参数是否支持
        import inspect
        download_signature = inspect.signature(yf.download)
        if 'show_errors' in download_signature.parameters:
            download_kwargs['show_errors'] = False
        
        data = yf.download(tickers, **download_kwargs)
        elapsed = time.time() - start_time
        
        if not data.empty:
            print(f"✅ 批量下载成功，耗时: {elapsed:.2f} 秒")
            
            # 分析每个股票的数据
            for ticker in tickers:
                try:
                    if ticker in data.columns.levels[0]:
                        ticker_data = data[ticker]
                        if not ticker_data.empty:
                            avg_price = ticker_data['Close'].mean()
                            print(f"  {ticker}: {len(ticker_data)} 条记录, 平均价格: ${avg_price:.2f}")
                        else:
                            print(f"  {ticker}: 数据为空")
                    else:
                        print(f"  {ticker}: 未找到")
                except Exception as e:
                    print(f"  {ticker}: 处理出错 - {e}")
            
            return True
        else:
            print("❌ 批量数据为空")
            return False
            
    except Exception as e:
        print(f"❌ 批量下载错误: {e}")
        return False

def test_yf_ticker_vs_download():
    """对比yf.Ticker()和yf.download()的性能"""
    print("\n=== 对比 yf.Ticker() vs yf.download() ===")
    
    ticker = "NVDA"
    start_date = "2024-01-01"
    end_date = "2024-01-31"
    
    # 测试yf.Ticker()
    print(f"测试 yf.Ticker() 获取 {ticker} 数据...")
    try:
        start_time = time.time()
        stock = yf.Ticker(ticker)
        data1 = stock.history(start=start_date, end=end_date)
        time1 = time.time() - start_time
        
        if not data1.empty:
            print(f"✅ yf.Ticker(): {len(data1)} 条记录，耗时: {time1:.2f} 秒")
        else:
            print("❌ yf.Ticker(): 数据为空")
            time1 = float('inf')
    except Exception as e:
        print(f"❌ yf.Ticker() 错误: {e}")
        time1 = float('inf')
    
    # 等待一下避免速率限制
    time.sleep(2)
    
    # 测试yf.download()
    print(f"测试 yf.download() 获取 {ticker} 数据...")
    try:
        start_time = time.time()
        # 根据yfinance版本动态设置参数
        download_kwargs = {
            'start': start_date,
            'end': end_date,
            'progress': False
        }
        
        # 检查show_errors参数是否支持
        import inspect
        download_signature = inspect.signature(yf.download)
        if 'show_errors' in download_signature.parameters:
            download_kwargs['show_errors'] = False
        
        data2 = yf.download(ticker, **download_kwargs)
        time2 = time.time() - start_time
        
        if not data2.empty:
            print(f"✅ yf.download(): {len(data2)} 条记录，耗时: {time2:.2f} 秒")
        else:
            print("❌ yf.download(): 数据为空")
            time2 = float('inf')
    except Exception as e:
        print(f"❌ yf.download() 错误: {e}")
        time2 = float('inf')
    
    # 比较结果
    if time1 != float('inf') and time2 != float('inf'):
        if time2 < time1:
            speedup = time1 / time2
            print(f"🚀 yf.download() 比 yf.Ticker() 快 {speedup:.1f} 倍")
        else:
            slowdown = time2 / time1
            print(f"⚠️  yf.download() 比 yf.Ticker() 慢 {slowdown:.1f} 倍")
    
    return time2 < time1 if time1 != float('inf') and time2 != float('inf') else None

def test_yfinance_helper_with_download():
    """测试更新后的YFinanceHelper"""
    print("\n=== 测试更新后的 YFinanceHelper ===")
    
    helper = YFinanceHelper(delay_min=0.5, delay_max=1.5)
    
    # 单个股票测试
    print("测试单个股票获取...")
    data = helper.get_stock_data("TSLA", "2024-01-01", "2024-01-31")
    
    if data is not None:
        print(f"✅ 单个股票: {len(data)} 条记录")
        
        # 批量测试
        print("\n测试批量获取（使用yf.download批量功能）...")
        tickers = ["AMZN", "META", "NFLX"]
        
        start_time = time.time()
        batch_data = helper.batch_get_stock_data(
            tickers,
            "2024-01-01",
            "2024-01-31",
            batch_size=5,
            use_bulk_download=True  # 使用批量下载
        )
        elapsed = time.time() - start_time
        
        print(f"批量下载完成，耗时: {elapsed:.1f} 秒")
        success_count = len(batch_data)
        print(f"成功率: {success_count}/{len(tickers)} ({success_count/len(tickers)*100:.1f}%)")
        
        return success_count > 0
    else:
        print("❌ 单个股票获取失败")
        return False

def test_rate_limiting_resilience():
    """测试速率限制抵抗能力"""
    print("\n=== 测试速率限制抵抗能力 ===")
    
    helper = YFinanceHelper(delay_min=0.1, delay_max=0.3)  # 故意设置较短延迟
    
    # 连续请求多个股票来测试速率限制处理
    tickers = ["IBM", "INTC", "AMD", "QCOM", "AVGO"]
    print(f"快速连续获取 {len(tickers)} 只股票数据...")
    
    success_count = 0
    start_time = time.time()
    
    for i, ticker in enumerate(tickers):
        print(f"获取 {ticker} ({i+1}/{len(tickers)})...")
        data = helper.get_stock_data(ticker, "2024-01-15", "2024-01-31")
        
        if data is not None:
            success_count += 1
            print(f"  ✅ 成功: {len(data)} 条记录")
        else:
            print(f"  ❌ 失败")
    
    elapsed = time.time() - start_time
    print(f"\n总耗时: {elapsed:.1f} 秒")
    print(f"成功率: {success_count}/{len(tickers)} ({success_count/len(tickers)*100:.1f}%)")
    
    return success_count >= len(tickers) * 0.8  # 80%成功率算通过

def main():
    """运行所有测试"""
    print("🧪 yf.download() 方法测试")
    print("=" * 50)
    
    tests = [
        ("yf.download() 单个股票", test_yf_download_single),
        ("yf.download() 多个股票", test_yf_download_multiple),
        ("yf.Ticker() vs yf.download()", test_yf_ticker_vs_download),
        ("更新后的 YFinanceHelper", test_yfinance_helper_with_download),
        ("速率限制抵抗能力", test_rate_limiting_resilience),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n🔬 {test_name}")
        print("-" * 40)
        
        try:
            result = test_func()
            results.append((test_name, result))
            
            if result is True:
                status = "✅ 通过"
            elif result is False:
                status = "❌ 失败"
            else:
                status = "⚠️  部分成功"
                
            print(f"结果: {status}")
            
        except Exception as e:
            print(f"❌ 测试出错: {e}")
            results.append((test_name, False))
        
        # 测试间延迟
        time.sleep(1)
    
    # 显示总结
    print("\n" + "=" * 50)
    print("📊 测试结果总结:")
    
    passed = 0
    for test_name, result in results:
        if result is True:
            status = "✅ 通过"
            passed += 1
        elif result is False:
            status = "❌ 失败"
        else:
            status = "⚠️  部分"
            passed += 0.5
    
        print(f"  {test_name}: {status}")
    
    total_score = passed / len(results) * 100
    print(f"\n🎯 总体评分: {total_score:.1f}%")
    
    if total_score >= 80:
        print("🎉 yf.download() 方法工作良好！推荐使用。")
    elif total_score >= 60:
        print("⚠️  yf.download() 基本可用，但可能存在一些问题。")
    else:
        print("🚨 yf.download() 存在较多问题，需要进一步调试。")
    
    print("\n💡 建议:")
    print("1. yf.download() 通常比 yf.Ticker() 更稳定")
    print("2. 批量下载可以显著提高效率")
    print("3. 适当的延迟和重试机制依然必要")
    print("4. 缓存可以大幅减少API调用次数")

if __name__ == "__main__":
    main()
