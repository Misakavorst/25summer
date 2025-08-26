#!/usr/bin/env python3
"""
测试yfinance版本兼容性修复
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from yfinance_helper import YFinanceHelper
import yfinance as yf
import time

def test_yfinance_version():
    """检查yfinance版本"""
    print("=== yfinance版本信息 ===")
    
    try:
        print(f"yfinance版本: {yf.__version__}")
    except:
        print("无法获取yfinance版本信息")
    
    # 检查关键参数支持
    import inspect
    download_signature = inspect.signature(yf.download)
    params = list(download_signature.parameters.keys())
    
    print(f"yf.download()支持的参数:")
    for param in params:
        print(f"  - {param}")
    
    # 检查特定参数
    critical_params = ['show_errors', 'session', 'threads', 'progress', 'group_by']
    print(f"\n关键参数支持情况:")
    for param in critical_params:
        supported = param in params
        status = "✅ 支持" if supported else "❌ 不支持"
        print(f"  - {param}: {status}")

def test_basic_download():
    """测试基础下载功能"""
    print("\n=== 测试基础下载功能 ===")
    
    try:
        # 使用最基础的参数
        print("测试最基础的yf.download()调用...")
        data = yf.download("AAPL", start="2024-01-01", end="2024-01-15")
        
        if not data.empty:
            print(f"✅ 基础下载成功: {len(data)} 条记录")
            return True
        else:
            print("❌ 基础下载失败: 数据为空")
            return False
            
    except Exception as e:
        print(f"❌ 基础下载失败: {e}")
        return False

def test_helper_compatibility():
    """测试YFinanceHelper兼容性"""
    print("\n=== 测试YFinanceHelper兼容性 ===")
    
    try:
        print("初始化YFinanceHelper...")
        helper = YFinanceHelper(delay_min=0.5, delay_max=1.0)
        
        print("\n测试单个股票下载...")
        data = helper.get_stock_data("MSFT", "2024-01-01", "2024-01-15")
        
        if data is not None:
            print(f"✅ 单个股票下载成功: {len(data)} 条记录")
            
            # 测试批量下载
            print("\n测试批量下载...")
            batch_data = helper.batch_get_stock_data(
                ["GOOGL", "AMZN"], 
                "2024-01-01", 
                "2024-01-15",
                use_bulk_download=True
            )
            
            success_count = len(batch_data)
            print(f"✅ 批量下载成功: {success_count}/2 个股票")
            
            return True
        else:
            print("❌ 单个股票下载失败")
            return False
            
    except Exception as e:
        print(f"❌ YFinanceHelper测试失败: {e}")
        return False

def test_parameter_fallback():
    """测试参数降级功能"""
    print("\n=== 测试参数降级功能 ===")
    
    try:
        helper = YFinanceHelper()
        
        # 显示兼容性检查结果
        print(f"show_errors支持: {helper.supports_show_errors}")
        print(f"session支持: {helper.supports_session}")
        
        # 测试参数生成
        base_kwargs = {
            'start': '2024-01-01',
            'end': '2024-01-15',
            'progress': False,
            'threads': False
        }
        
        final_kwargs = helper._get_download_kwargs(base_kwargs)
        print(f"\n生成的下载参数:")
        for key, value in final_kwargs.items():
            print(f"  - {key}: {value}")
        
        return True
        
    except Exception as e:
        print(f"❌ 参数降级测试失败: {e}")
        return False

def main():
    """运行兼容性测试"""
    print("🔧 yfinance兼容性测试")
    print("解决 'show_errors' 参数不兼容问题")
    print("=" * 50)
    
    tests = [
        ("yfinance版本检查", test_yfinance_version),
        ("基础下载功能", test_basic_download),
        ("参数降级功能", test_parameter_fallback),
        ("YFinanceHelper兼容性", test_helper_compatibility),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n🧪 {test_name}")
        print("-" * 30)
        
        try:
            success = test_func()
            results.append((test_name, success))
            
            if success is True:
                print(f"✅ {test_name}: 通过")
            elif success is False:
                print(f"❌ {test_name}: 失败")
            else:
                print(f"ℹ️  {test_name}: 信息查看")
                
        except Exception as e:
            print(f"❌ {test_name}: 测试出错 - {e}")
            results.append((test_name, False))
        
        time.sleep(0.5)  # 短暂延迟
    
    # 显示总结
    print("\n" + "=" * 50)
    print("📊 兼容性测试总结:")
    
    passed = 0
    for test_name, result in results:
        if result is True:
            status = "✅ 通过"
            passed += 1
        elif result is False:
            status = "❌ 失败"
        else:
            status = "ℹ️  信息"
            passed += 0.5
    
        print(f"  {test_name}: {status}")
    
    # 计算数值类型的结果数量
    numeric_results = [r for _, r in results if isinstance(r, bool)]
    if numeric_results:
        success_rate = sum(numeric_results) / len(numeric_results) * 100
        print(f"\n🎯 成功率: {success_rate:.1f}%")
        
        if success_rate >= 80:
            print("🎉 兼容性修复成功！可以正常使用。")
        elif success_rate >= 60:
            print("⚠️  基本兼容，但可能存在小问题。")
        else:
            print("🚨 兼容性问题较多，需要进一步调试。")
    
    print("\n💡 建议:")
    print("1. 如果遇到参数错误，脚本会自动降级")
    print("2. 保持yfinance版本更新以获得最佳体验")
    print("3. 如果问题持续，可以尝试重新安装yfinance")
    print("4. 使用 pip install yfinance --upgrade 升级版本")

if __name__ == "__main__":
    main()
