#!/usr/bin/env python3
"""
测试yfinance助手工具的功能
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from yfinance_helper import YFinanceHelper
from datetime import datetime, timedelta
import time

def test_single_stock():
    """测试单个股票数据获取"""
    print("=== 测试单个股票数据获取 ===")
    
    helper = YFinanceHelper(delay_min=0.5, delay_max=2.0)
    
    # 测试获取AAPL数据
    print("获取AAPL股票数据...")
    data = helper.get_stock_data("AAPL", "2024-01-01", "2024-01-31")
    
    if data is not None:
        print(f"✅ 成功获取AAPL数据，共 {len(data)} 条记录")
        print(f"数据范围: {data.index[0]} 到 {data.index[-1]}")
        print(f"收盘价范围: ${data['Close'].min():.2f} - ${data['Close'].max():.2f}")
    else:
        print("❌ 获取AAPL数据失败")
    
    return data is not None

def test_specific_date_price():
    """测试获取特定日期的股票价格"""
    print("\n=== 测试获取特定日期价格 ===")
    
    helper = YFinanceHelper()
    
    # 测试获取特定日期的价格
    target_date = datetime(2024, 1, 15)
    print(f"获取AAPL在 {target_date.strftime('%Y-%m-%d')} 的价格...")
    
    price = helper.get_stock_price_on_date("AAPL", target_date)
    
    if price is not None:
        print(f"✅ AAPL 2024-01-15 收盘价: ${price:.2f}")
        return True
    else:
        print("❌ 获取特定日期价格失败")
        return False

def test_batch_processing():
    """测试批量处理股票数据"""
    print("\n=== 测试批量处理 ===")
    
    helper = YFinanceHelper(delay_min=0.3, delay_max=1.0)
    
    # 测试批量获取多个股票数据
    tickers = ["AAPL", "MSFT", "GOOGL", "TSLA", "NVDA"]
    print(f"批量获取股票数据: {tickers}")
    
    start_time = time.time()
    batch_data = helper.batch_get_stock_data(
        tickers, 
        "2024-01-01", 
        "2024-01-31", 
        batch_size=2,  # 每批2个
        delay_between_batches=2.0
    )
    end_time = time.time()
    
    print(f"批量处理完成，耗时: {end_time - start_time:.1f} 秒")
    
    success_count = 0
    for ticker in tickers:
        if ticker in batch_data:
            data = batch_data[ticker]
            print(f"✅ {ticker}: {len(data)} 条记录")
            success_count += 1
        else:
            print(f"❌ {ticker}: 获取失败")
    
    print(f"成功率: {success_count}/{len(tickers)} ({success_count/len(tickers)*100:.1f}%)")
    return success_count > 0

def test_cache_functionality():
    """测试缓存功能"""
    print("\n=== 测试缓存功能 ===")
    
    helper = YFinanceHelper()
    
    # 第一次获取（应该从API获取）
    print("第一次获取MSFT数据（从API）...")
    start_time = time.time()
    data1 = helper.get_stock_data("MSFT", "2024-01-01", "2024-01-15")
    time1 = time.time() - start_time
    
    # 第二次获取（应该从缓存获取）
    print("第二次获取MSFT数据（从缓存）...")
    start_time = time.time()
    data2 = helper.get_stock_data("MSFT", "2024-01-01", "2024-01-15")
    time2 = time.time() - start_time
    
    if data1 is not None and data2 is not None:
        print(f"✅ 缓存功能正常")
        print(f"第一次耗时: {time1:.2f}s, 第二次耗时: {time2:.2f}s")
        print(f"缓存加速比: {time1/time2:.1f}x")
        return True
    else:
        print("❌ 缓存功能测试失败")
        return False

def test_error_handling():
    """测试错误处理"""
    print("\n=== 测试错误处理 ===")
    
    helper = YFinanceHelper()
    
    # 测试无效的股票代码
    print("测试无效股票代码...")
    data = helper.get_stock_data("INVALID_TICKER", "2024-01-01", "2024-01-31")
    
    if data is None:
        print("✅ 无效股票代码处理正确")
        return True
    else:
        print("❌ 无效股票代码处理异常")
        return False

def test_integration_with_kolsentiment():
    """测试与KOLSentiment的集成"""
    print("\n=== 测试与KOLSentiment集成 ===")
    
    try:
        from KOLSentiment import KOLSentimentDB
        
        # 创建测试数据库
        db = KOLSentimentDB("test_yfinance_helper.db")
        
        # 测试获取股票价格
        test_date = datetime(2024, 1, 15)
        price = db.get_stock_price("AAPL", test_date)
        
        if price is not None:
            print(f"✅ KOLSentiment集成正常，AAPL价格: ${price:.2f}")
            
            # 测试计算收益率
            returns = db.calculate_returns("AAPL", test_date, price)
            if any(r is not None for r in returns):
                print(f"✅ 收益率计算正常: 1d={returns[0]:.4f}, 3d={returns[1]:.4f}, 10d={returns[2]:.4f}")
                return True
            else:
                print("❌ 收益率计算失败")
                return False
        else:
            print("❌ KOLSentiment集成失败")
            return False
            
    except Exception as e:
        print(f"❌ 集成测试出错: {e}")
        return False

def main():
    """运行所有测试"""
    print("YFinanceHelper 工具测试")
    print("=" * 50)
    
    tests = [
        ("单个股票数据获取", test_single_stock),
        ("特定日期价格获取", test_specific_date_price),
        ("批量处理", test_batch_processing),
        ("缓存功能", test_cache_functionality),
        ("错误处理", test_error_handling),
        ("KOLSentiment集成", test_integration_with_kolsentiment),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n🧪 {test_name}")
        print("-" * 30)
        
        try:
            success = test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"❌ 测试出错: {e}")
            results.append((test_name, False))
    
    # 显示测试结果总结
    print("\n" + "=" * 50)
    print("测试结果总结:")
    
    passed = 0
    for test_name, success in results:
        status = "✅ 通过" if success else "❌ 失败"
        print(f"  {test_name}: {status}")
        if success:
            passed += 1
    
    print(f"\n总结: {passed}/{len(results)} 测试通过 ({passed/len(results)*100:.1f}%)")
    
    if passed == len(results):
        print("🎉 所有测试通过！yfinance助手工具可以正常使用。")
    elif passed > len(results) / 2:
        print("⚠️  大部分测试通过，工具基本可用，但可能存在一些问题。")
    else:
        print("🚨 多个测试失败，请检查网络连接和API配置。")

if __name__ == "__main__":
    main()
