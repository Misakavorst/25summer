import yfinance as yf
import time
import random
import pandas as pd
from datetime import datetime, timedelta
import pickle
import os
import inspect
from typing import Dict, List, Optional, Tuple
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

class YFinanceHelper:
    """
    yfinance API 速率限制解决方案工具类
    """
    
    def __init__(self, cache_dir="yfinance_cache", delay_min=0.5, delay_max=2.0):
        """
        初始化
        
        Args:
            cache_dir: 缓存目录
            delay_min: 最小延迟时间（秒）
            delay_max: 最大延迟时间（秒）
        """
        self.cache_dir = cache_dir
        self.delay_min = delay_min
        self.delay_max = delay_max
        self.session = None
        
        # 创建缓存目录
        if not os.path.exists(cache_dir):
            os.makedirs(cache_dir)
        
        # 设置重试会话
        self._setup_session()
        
        # 检查yfinance版本兼容性
        self._check_yfinance_compatibility()
    
    def _setup_session(self):
        """设置带重试机制的会话"""
        self.session = requests.Session()
        
        # 设置重试策略
        retry_strategy = Retry(
            total=3,  # 总重试次数
            backoff_factor=2,  # 退避因子
            status_forcelist=[429, 500, 502, 503, 504],  # 需要重试的状态码
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        
        # 设置User-Agent避免被识别为爬虫
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def _check_yfinance_compatibility(self):
        """检查yfinance版本兼容性"""
        try:
            download_signature = inspect.signature(yf.download)
            self.supports_show_errors = 'show_errors' in download_signature.parameters
            self.supports_session = 'session' in download_signature.parameters
            
            print(f"yfinance兼容性检查:")
            print(f"  - show_errors参数: {'✅ 支持' if self.supports_show_errors else '❌ 不支持'}")
            print(f"  - session参数: {'✅ 支持' if self.supports_session else '❌ 不支持'}")
        except Exception as e:
            print(f"⚠️  yfinance兼容性检查失败: {e}")
            self.supports_show_errors = False
            self.supports_session = False
    
    def _get_download_kwargs(self, base_kwargs: dict) -> dict:
        """根据yfinance版本获取兼容的下载参数"""
        kwargs = base_kwargs.copy()
        
        # 添加可选参数
        if self.supports_show_errors:
            kwargs['show_errors'] = False
        
        if self.supports_session and self.session:
            kwargs['session'] = self.session
        
        return kwargs
    
    def _get_cache_path(self, ticker: str, start_date: str, end_date: str) -> str:
        """获取缓存文件路径"""
        cache_filename = f"{ticker}_{start_date}_{end_date}.pkl"
        return os.path.join(self.cache_dir, cache_filename)
    
    def _load_from_cache(self, ticker: str, start_date: str, end_date: str) -> Optional[pd.DataFrame]:
        """从缓存加载数据"""
        cache_path = self._get_cache_path(ticker, start_date, end_date)
        
        if os.path.exists(cache_path):
            try:
                # 检查缓存文件是否过期（1天）
                cache_time = os.path.getmtime(cache_path)
                if time.time() - cache_time < 24 * 3600:  # 24小时内的缓存有效
                    with open(cache_path, 'rb') as f:
                        data = pickle.load(f)
                    print(f"从缓存加载 {ticker} 数据")
                    return data
            except Exception as e:
                print(f"缓存加载失败: {e}")
        
        return None
    
    def _save_to_cache(self, ticker: str, start_date: str, end_date: str, data: pd.DataFrame):
        """保存数据到缓存"""
        cache_path = self._get_cache_path(ticker, start_date, end_date)
        
        try:
            with open(cache_path, 'wb') as f:
                pickle.dump(data, f)
            print(f"缓存保存 {ticker} 数据")
        except Exception as e:
            print(f"缓存保存失败: {e}")
    
    def _random_delay(self):
        """随机延迟"""
        delay = random.uniform(self.delay_min, self.delay_max)
        time.sleep(delay)
    
    def get_stock_data(self, ticker: str, start_date: str, end_date: str, 
                       max_retries: int = 3) -> Optional[pd.DataFrame]:
        """
        获取股票数据（带缓存和重试机制）- 使用yf.download()
        
        Args:
            ticker: 股票代码
            start_date: 开始日期 (YYYY-MM-DD)
            end_date: 结束日期 (YYYY-MM-DD)
            max_retries: 最大重试次数
            
        Returns:
            股票数据DataFrame，失败返回None
        """
        # 先尝试从缓存加载
        cached_data = self._load_from_cache(ticker, start_date, end_date)
        if cached_data is not None:
            return cached_data
        
        # 从API获取数据
        for attempt in range(max_retries):
            try:
                print(f"获取 {ticker} 数据 (尝试 {attempt + 1}/{max_retries})...")
                
                # 随机延迟
                if attempt > 0:
                    self._random_delay()
                
                # 使用yf.download获取数据
                base_kwargs = {
                    'start': start_date,
                    'end': end_date,
                    'progress': False,  # 禁用进度条
                    'threads': False,   # 禁用多线程
                }
                
                download_kwargs = self._get_download_kwargs(base_kwargs)
                data = yf.download(ticker, **download_kwargs)
                
                if not data.empty:
                    # 保存到缓存
                    self._save_to_cache(ticker, start_date, end_date, data)
                    print(f"成功获取 {ticker} 数据 ({len(data)} 条记录)")
                    return data
                else:
                    print(f"警告: {ticker} 数据为空")
                    
            except Exception as e:
                error_msg = str(e)
                if "Too Many Requests" in error_msg or "Rate limited" in error_msg or "429" in error_msg:
                    wait_time = (2 ** attempt) + random.uniform(1, 3)
                    print(f"速率限制: {ticker} - 等待 {wait_time:.1f} 秒后重试...")
                    time.sleep(wait_time)  # 指数退避 + 随机抖动
                else:
                    print(f"错误获取 {ticker} 数据: {e}")
                    if attempt < max_retries - 1:
                        time.sleep(1)  # 短暂等待后重试
                    else:
                        break
        
        print(f"失败: 无法获取 {ticker} 数据")
        return None
    
    def get_stock_price_on_date(self, ticker: str, target_date: datetime, 
                               days_buffer: int = 5) -> Optional[float]:
        """
        获取指定日期的股票价格
        
        Args:
            ticker: 股票代码
            target_date: 目标日期
            days_buffer: 日期缓冲区间（天）
            
        Returns:
            股票价格，失败返回None
        """
        # 计算日期范围
        start_date = (target_date - timedelta(days=days_buffer)).strftime('%Y-%m-%d')
        end_date = (target_date + timedelta(days=days_buffer)).strftime('%Y-%m-%d')
        
        # 获取数据
        data = self.get_stock_data(ticker, start_date, end_date)
        
        if data is not None and not data.empty:
            # 查找最接近目标日期的价格
            target_date_str = target_date.strftime('%Y-%m-%d')
            
            # 尝试精确匹配
            if target_date_str in data.index.strftime('%Y-%m-%d'):
                return data.loc[data.index.strftime('%Y-%m-%d') == target_date_str, 'Close'].iloc[0]
            
            # 找最接近的日期
            data['date_diff'] = abs((data.index - target_date).days)
            closest_idx = data['date_diff'].idxmin()
            return data.loc[closest_idx, 'Close']
        
        return None
    
    def batch_get_stock_data(self, tickers: List[str], start_date: str, end_date: str, 
                            batch_size: int = 10, delay_between_batches: float = 3.0,
                            use_bulk_download: bool = True) -> Dict[str, pd.DataFrame]:
        """
        批量获取股票数据
        
        Args:
            tickers: 股票代码列表
            start_date: 开始日期
            end_date: 结束日期
            batch_size: 批处理大小
            delay_between_batches: 批次间延迟时间
            use_bulk_download: 是否使用yf.download的批量下载功能
            
        Returns:
            股票代码到数据的字典
        """
        results = {}
        
        if use_bulk_download:
            # 使用yf.download的批量下载功能
            return self._batch_download_bulk(tickers, start_date, end_date, batch_size, delay_between_batches)
        else:
            # 逐个下载
            return self._batch_download_individual(tickers, start_date, end_date, batch_size, delay_between_batches)
    
    def _batch_download_bulk(self, tickers: List[str], start_date: str, end_date: str,
                            batch_size: int, delay_between_batches: float) -> Dict[str, pd.DataFrame]:
        """使用yf.download批量下载"""
        results = {}
        
        # 分批处理
        for i in range(0, len(tickers), batch_size):
            batch = tickers[i:i + batch_size]
            print(f"\n批量下载批次 {i//batch_size + 1}: {batch}")
            
            try:
                # 先检查缓存
                cached_tickers = []
                uncached_tickers = []
                
                for ticker in batch:
                    cached_data = self._load_from_cache(ticker, start_date, end_date)
                    if cached_data is not None:
                        results[ticker] = cached_data
                        cached_tickers.append(ticker)
                    else:
                        uncached_tickers.append(ticker)
                
                if cached_tickers:
                    print(f"从缓存加载: {cached_tickers}")
                
                # 批量下载未缓存的数据
                if uncached_tickers:
                    print(f"批量下载: {uncached_tickers}")
                    
                    # 使用yf.download批量下载
                    base_kwargs = {
                        'start': start_date,
                        'end': end_date,
                        'progress': False,
                        'threads': True,  # 批量下载时可以使用多线程
                        'group_by': 'ticker'  # 按股票代码分组
                    }
                    
                    bulk_kwargs = self._get_download_kwargs(base_kwargs)
                    bulk_data = yf.download(uncached_tickers, **bulk_kwargs)
                    
                    if not bulk_data.empty:
                        # 处理批量下载的数据
                        if len(uncached_tickers) == 1:
                            # 单个股票的情况
                            ticker = uncached_tickers[0]
                            results[ticker] = bulk_data
                            self._save_to_cache(ticker, start_date, end_date, bulk_data)
                            print(f"✅ {ticker}: {len(bulk_data)} 条记录")
                        else:
                            # 多个股票的情况
                            for ticker in uncached_tickers:
                                try:
                                    if ticker in bulk_data.columns.levels[0]:
                                        ticker_data = bulk_data[ticker]
                                        if not ticker_data.empty:
                                            results[ticker] = ticker_data
                                            self._save_to_cache(ticker, start_date, end_date, ticker_data)
                                            print(f"✅ {ticker}: {len(ticker_data)} 条记录")
                                        else:
                                            print(f"❌ {ticker}: 数据为空")
                                    else:
                                        print(f"❌ {ticker}: 未找到数据")
                                except Exception as e:
                                    print(f"❌ {ticker}: 处理数据时出错 - {e}")
                    else:
                        print(f"❌ 批量下载失败: 数据为空")
                        
            except Exception as e:
                print(f"❌ 批量下载出错: {e}")
                # 降级到逐个下载
                print("降级到逐个下载...")
                for ticker in uncached_tickers:
                    data = self.get_stock_data(ticker, start_date, end_date)
                    if data is not None:
                        results[ticker] = data
                    self._random_delay()
            
            # 批次间延迟
            if i + batch_size < len(tickers):
                print(f"批次完成，等待 {delay_between_batches} 秒...")
                time.sleep(delay_between_batches)
        
        return results
    
    def _batch_download_individual(self, tickers: List[str], start_date: str, end_date: str,
                                  batch_size: int, delay_between_batches: float) -> Dict[str, pd.DataFrame]:
        """逐个下载（原有方法）"""
        results = {}
        
        # 分批处理
        for i in range(0, len(tickers), batch_size):
            batch = tickers[i:i + batch_size]
            print(f"\n处理批次 {i//batch_size + 1}: {batch}")
            
            for ticker in batch:
                data = self.get_stock_data(ticker, start_date, end_date)
                if data is not None:
                    results[ticker] = data
                
                # 批次内延迟
                self._random_delay()
            
            # 批次间延迟
            if i + batch_size < len(tickers):
                print(f"批次完成，等待 {delay_between_batches} 秒...")
                time.sleep(delay_between_batches)
        
        return results
    
    def clear_cache(self, older_than_days: int = 7):
        """
        清理缓存文件
        
        Args:
            older_than_days: 清理多少天前的缓存
        """
        if not os.path.exists(self.cache_dir):
            return
        
        cutoff_time = time.time() - older_than_days * 24 * 3600
        removed_count = 0
        
        for filename in os.listdir(self.cache_dir):
            if filename.endswith('.pkl'):
                file_path = os.path.join(self.cache_dir, filename)
                if os.path.getmtime(file_path) < cutoff_time:
                    os.remove(file_path)
                    removed_count += 1
        
        print(f"清理了 {removed_count} 个过期缓存文件")

def demo_usage():
    """演示用法"""
    helper = YFinanceHelper(delay_min=1.0, delay_max=3.0)
    
    # 单个股票数据获取
    print("=== 获取单个股票数据 ===")
    data = helper.get_stock_data("AAPL", "2024-01-01", "2024-01-31")
    if data is not None:
        print(f"AAPL 数据形状: {data.shape}")
        print(data.head())
    
    # 批量获取
    print("\n=== 批量获取股票数据 ===")
    tickers = ["MSFT", "GOOGL", "TSLA"]
    batch_data = helper.batch_get_stock_data(tickers, "2024-01-01", "2024-01-31", batch_size=2)
    
    for ticker, data in batch_data.items():
        print(f"{ticker}: {data.shape[0]} 条记录")
    
    # 获取特定日期价格
    print("\n=== 获取特定日期价格 ===")
    from datetime import datetime
    price = helper.get_stock_price_on_date("AAPL", datetime(2024, 1, 15))
    print(f"AAPL 2024-01-15 价格: {price}")

if __name__ == "__main__":
    demo_usage()
