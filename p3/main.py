from KOLSentiment import KOLSentimentDB
from kol_performance_metrics import calculate_kol_performance_metrics, print_performance_summary, save_performance_metrics_to_db
from kol_grade_system import add_grade_to_performance
import datetime
import pandas as pd
from datetime import datetime as dt

def load_kol_data_from_csv(csv_file="kol_sample_data.csv"):
    """
    从CSV文件加载KOL数据并转换为sample_data格式
    """
    print(f"Loading KOL data from {csv_file}...")
    
    try:
        # 读取CSV文件
        df = pd.read_csv(csv_file)
        print(f"Loaded {len(df)} records from CSV")
        
        # 转换数据格式
        sample_data = []
        for index, row in df.iterrows():
            try:
                # 解析时间字符串
                if isinstance(row['prediction_time'], str):
                    # 处理带时区的时间格式
                    time_str = row['prediction_time'].replace('+00:00', '')
                    prediction_time = dt.fromisoformat(time_str)
                else:
                    prediction_time = row['prediction_time']
                
                # 构建tuple格式的数据
                sample_data.append((
                    row['kol_name'],      # kol_name
                    row['ticker'],        # ticker
                    row['sector'],        # sector
                    row['sentiment'],     # sentiment
                    float(row['confidence']),  # confidence
                    prediction_time       # prediction_time
                ))
            except Exception as e:
                print(f"Error processing row {index}: {e}")
                continue
        
        print(f"Successfully converted {len(sample_data)} records")
        return sample_data
        
    except FileNotFoundError:
        print(f"CSV file {csv_file} not found, using default sample data")
        return get_default_sample_data()
    except Exception as e:
        print(f"Error loading CSV: {e}, using default sample data")
        return get_default_sample_data()

def get_default_sample_data():
    """
    返回默认的示例数据
    """
    return [
        ("elonmusk", "TSLA", "Tech", "positive", 0.85, datetime.datetime(2025, 6, 2, 0, 0, 0)),
        ("elonmusk", "TSLA", "Tech", "negative", 0.80, datetime.datetime(2025, 6, 9, 0, 0, 0)),
        ("warrenbuffett", "AAPL", "Tech", "positive", 0.90, datetime.datetime(2025, 6, 2, 0, 0, 0)),
        ("warrenbuffett", "AAPL", "Tech", "negative", 0.70, datetime.datetime(2025, 6, 9, 0, 0, 0)),
        ("cathiewood", "ARKK", "Tech", "positive", 0.75, datetime.datetime(2025, 6, 2, 0, 0, 0)),
        ("cathiewood", "ARKK", "Tech", "negative", 0.60, datetime.datetime(2025, 6, 9, 0, 0, 0)),
        ("elonmusk", "TSLA", "Tech", "positive", 0.85, datetime.datetime(2025, 6, 16, 0, 0, 0)),
        ("elonmusk", "TSLA", "Tech", "negative", 0.80, datetime.datetime(2025, 6, 23, 0, 0, 0)),
        ("warrenbuffett", "AAPL", "Tech", "positive", 0.90, datetime.datetime(2025, 6, 16, 0, 0, 0)),
        ("warrenbuffett", "AAPL", "Tech", "negative", 0.70, datetime.datetime(2025, 6, 23, 0, 0, 0)),
        ("cathiewood", "ARKK", "Tech", "positive", 0.75, datetime.datetime(2025, 6, 16, 0, 0, 0)),
        ("cathiewood", "ARKK", "Tech", "negative", 0.60, datetime.datetime(2025, 6, 23, 0, 0, 0)),
        ("elonmusk", "TSLA", "Tech", "positive", 0.85, datetime.datetime(2025, 6, 30, 0, 0, 0)),
        ("warrenbuffett", "AAPL", "Tech", "positive", 0.90, datetime.datetime(2025, 6, 30, 0, 0, 0)),
        ("cathiewood", "ARKK", "Tech", "positive", 0.75, datetime.datetime(2025, 6, 30, 0, 0, 0)),
    ]

def run_integration_test():
    # 1. Initialize database
    db = KOLSentimentDB("test_kol_sentiment.db")
    
    # 2. Load data from CSV file (or use default sample data if CSV not found)
    sample_data = load_kol_data_from_csv("kol_sample_data.csv")
    for kol_name, ticker, sector, sentiment, confidence, prediction_time in sample_data:
        db.insert_record_with_returns(kol_name, ticker, sector, sentiment, confidence, prediction_time)
    
    # 3. Query all records with returns
    records = db.get_records_with_returns()
    print(f"Total records with returns: {len(records)}")
    
    # 4. Calculate KOL performance metrics
    performance_metrics = calculate_kol_performance_metrics(records)
    print_performance_summary(performance_metrics)
    
    # 5. Calculate grades
    performance_metrics = add_grade_to_performance(performance_metrics)
    
    # 6. Print final table
    print("\nFinal KOL Table:")
    print("{:<15} {:<8} {:<8} {:<8} {:<12} {:<8}".format(
        "KOL", "Grade", "Accuracy", "Sharpe", "MeanRet", "Samples"
    ))
    for kol, metrics in performance_metrics.items():
        print("{:<15} {:<8} {:<8.2f} {:<8.2f} {:<12.2%} {:<8}".format(
            kol,
            getattr(metrics, "grade", 0),
            metrics.direction_correctness_rate,
            metrics.sharpe_ratio_1d,
            metrics.mean_return_1d,
            metrics.total_predictions
        ))
    save_performance_metrics_to_db(performance_metrics)

def run_csv_analysis():
    """
    使用CSV数据运行KOL性能分析
    """
    print("="*60)
    print("KOL Performance Analysis using CSV data")
    print("="*60)
    
    # 1. Initialize database
    db = KOLSentimentDB("kol_sentiment_csv.db")
    
    # 2. Load data from CSV file
    sample_data = load_kol_data_from_csv("kol_sample_data.csv")
    
    if not sample_data:
        print("No data loaded, exiting...")
        return
    
    # 3. Insert data into database
    print(f"\nInserting {len(sample_data)} records into database...")
    for kol_name, ticker, sector, sentiment, confidence, prediction_time in sample_data:
        db.insert_record_with_returns(kol_name, ticker, sector, sentiment, confidence, prediction_time)
    
    # 4. Query all records with returns
    records = db.get_records_with_returns()
    print(f"Total records with returns: {len(records)}")
    
    # 5. Calculate KOL performance metrics
    performance_metrics = calculate_kol_performance_metrics(records)
    print_performance_summary(performance_metrics)
    
    # 6. Calculate grades
    performance_metrics = add_grade_to_performance(performance_metrics)
    
    # 7. Print final table
    print("\nFinal KOL Performance Table:")
    print("{:<20} {:<8} {:<8} {:<8} {:<12} {:<8}".format(
        "KOL", "Grade", "Accuracy", "Sharpe", "MeanRet", "Samples"
    ))
    print("-" * 70)
    for kol, metrics in performance_metrics.items():
        print("{:<20} {:<8} {:<8.2f} {:<8.2f} {:<12.2%} {:<8}".format(
            kol,
            getattr(metrics, "grade", 0),
            metrics.direction_correctness_rate,
            metrics.sharpe_ratio_1d,
            metrics.mean_return_1d,
            metrics.total_predictions
        ))
    
    # 8. Save performance metrics to database
    save_performance_metrics_to_db(performance_metrics)
    
    print(f"\nAnalysis complete! Results saved to kol_sentiment_csv.db")

def test_csv_loading():
    """
    测试CSV数据加载功能
    """
    print("Testing CSV data loading...")
    sample_data = load_kol_data_from_csv("kol_sample_data.csv")
    
    if sample_data:
        print(f"Successfully loaded {len(sample_data)} records")
        print("\nFirst 5 records:")
        for i, record in enumerate(sample_data[:5]):
            print(f"  {i+1}. {record}")
        
        # 统计数据
        kol_names = set()
        tickers = set()
        sectors = set()
        sentiments = {"positive": 0, "negative": 0, "neutral": 0}
        
        for kol_name, ticker, sector, sentiment, confidence, prediction_time in sample_data:
            kol_names.add(kol_name)
            tickers.add(ticker)
            sectors.add(sector)
            if sentiment in sentiments:
                sentiments[sentiment] += 1
        
        print(f"\nData Statistics:")
        print(f"  KOL Names: {list(kol_names)}")
        print(f"  Number of unique tickers: {len(tickers)}")
        print(f"  Tickers: {sorted(list(tickers))}")
        print(f"  Sectors: {sorted(list(sectors))}")
        print(f"  Sentiment distribution: {sentiments}")
    else:
        print("Failed to load data from CSV")

if __name__ == "__main__":
    # 可以选择运行哪个测试
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "csv":
        run_csv_analysis()
    elif len(sys.argv) > 1 and sys.argv[1] == "test":
        test_csv_loading()
    else:
        print("Running integration test with sample data...")
        run_integration_test()
        print("\nAvailable options:")
        print("  python main.py csv   - Run analysis with CSV data")
        print("  python main.py test  - Test CSV loading only")
