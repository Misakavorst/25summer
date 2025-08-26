import numpy as np
from typing import List, Dict, Any
from dataclasses import dataclass
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

Base = declarative_base()

class KOLPerformanceMetricsTable(Base):
    __tablename__ = 'kol_performance_metrics'
    id = Column(Integer, primary_key=True)
    kol_name = Column(String(100), nullable=False)
    direction_correctness_rate = Column(Float, nullable=False)
    mean_return_1d = Column(Float, nullable=False)
    mean_return_3d = Column(Float, nullable=False)
    mean_return_10d = Column(Float, nullable=False)
    volatility_1d = Column(Float, nullable=False)
    volatility_3d = Column(Float, nullable=False)
    volatility_10d = Column(Float, nullable=False)
    sharpe_ratio_1d = Column(Float, nullable=False)
    sharpe_ratio_3d = Column(Float, nullable=False)
    sharpe_ratio_10d = Column(Float, nullable=False)
    information_ratio_1d = Column(Float, nullable=False)
    information_ratio_3d = Column(Float, nullable=False)
    information_ratio_10d = Column(Float, nullable=False)
    total_predictions = Column(Integer, nullable=False)
    grade = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.now)
    __table_args__ = (
        Index('idx_kol_name', 'kol_name'),
    )

@dataclass
class KOLPerformanceMetrics:
    """Data class to store KOL performance metrics"""
    kol_name: str
    direction_correctness_rate: float
    mean_return_1d: float
    mean_return_3d: float
    mean_return_10d: float
    volatility_1d: float
    volatility_3d: float
    volatility_10d: float
    sharpe_ratio_1d: float
    sharpe_ratio_3d: float
    sharpe_ratio_10d: float
    information_ratio_1d: float
    information_ratio_3d: float
    information_ratio_10d: float
    total_predictions: int

def calculate_kol_performance_metrics(records) -> Dict[str, KOLPerformanceMetrics]:
    """
    Calculate comprehensive performance metrics for each KOL
    
    Args:
        records: List of KOLSentiment records with return data
    
    Returns:
        Dict mapping KOL names to their performance metrics
    """
    kol_metrics = {}
    
    for record in records:
        if record.return_1d is None:
            continue
            
        if record.kol_name not in kol_metrics:
            kol_metrics[record.kol_name] = {
                'returns_1d': [],
                'returns_3d': [],
                'returns_10d': [],
                'correct_predictions': 0,
                'total_predictions': 0
            }
        
        kol_metrics[record.kol_name]['total_predictions'] += 1
        
        # Store returns for each time period
        if record.return_1d is not None:
            kol_metrics[record.kol_name]['returns_1d'].append(record.return_1d)
        if record.return_3d is not None:
            kol_metrics[record.kol_name]['returns_3d'].append(record.return_3d)
        if record.return_10d is not None:
            kol_metrics[record.kol_name]['returns_10d'].append(record.return_10d)
        
        # Count correct predictions
        if record.return_1d is not None and is_direction_correct(record.sentiment, record.return_1d):
            kol_metrics[record.kol_name]['correct_predictions'] += 1
    
    # Calculate metrics for each KOL
    performance_results = {}
    
    for kol_name, data in kol_metrics.items():
        if data['total_predictions'] == 0:
            continue
            
        # Direction correctness rate
        direction_correctness_rate = data['correct_predictions'] / data['total_predictions']
        
        # Calculate metrics for each time period
        metrics_1d = calculate_period_metrics(data['returns_1d'])
        metrics_3d = calculate_period_metrics(data['returns_3d'])
        metrics_10d = calculate_period_metrics(data['returns_10d'])
        
        performance_results[kol_name] = KOLPerformanceMetrics(
            kol_name=kol_name,
            direction_correctness_rate=direction_correctness_rate,
            mean_return_1d=metrics_1d['mean_return'],
            mean_return_3d=metrics_3d['mean_return'],
            mean_return_10d=metrics_10d['mean_return'],
            volatility_1d=metrics_1d['volatility'],
            volatility_3d=metrics_3d['volatility'],
            volatility_10d=metrics_10d['volatility'],
            sharpe_ratio_1d=metrics_1d['sharpe_ratio'],
            sharpe_ratio_3d=metrics_3d['sharpe_ratio'],
            sharpe_ratio_10d=metrics_10d['sharpe_ratio'],
            information_ratio_1d=metrics_1d['information_ratio'],
            information_ratio_3d=metrics_3d['information_ratio'],
            information_ratio_10d=metrics_10d['information_ratio'],
            total_predictions=data['total_predictions']
        )
    
    return performance_results

def calculate_period_metrics(returns: List[float]) -> Dict[str, float]:
    """
    Calculate performance metrics for a specific time period
    
    Args:
        returns: List of returns for the time period
    
    Returns:
        Dictionary containing mean return, volatility, Sharpe ratio, and Information ratio
    """
    if not returns:
        return {
            'mean_return': 0.0,
            'volatility': 0.0,
            'sharpe_ratio': 0.0,
            'information_ratio': 0.0
        }
    
    returns_array = np.array(returns)
    mean_return = float(np.mean(returns_array))
    risk_free_rate = 0.001
    volatility = float(np.std(returns_array, ddof=1))  # Sample standard deviation
    
    # Sharpe ratio (assuming risk-free rate of 0 for simplicity)
    sharpe_ratio = float((mean_return - risk_free_rate) / volatility if volatility > 0 else 0.0)
    
    # Information ratio (excess return relative to benchmark)
    benchmark_return = 0.01
    tracking_error = volatility
    information_ratio = float((mean_return - benchmark_return) / tracking_error if tracking_error > 0 else 0.0)
    
    return {
        'mean_return': mean_return,
        'volatility': volatility,
        'sharpe_ratio': sharpe_ratio,
        'information_ratio': information_ratio
    }

def is_direction_correct(sentiment: str, ret: float) -> int:
    """
    Check if the KOL sentiment prediction direction is correct
    
    Args:
        sentiment: KOL sentiment prediction
        ret: Actual return value
    
    Returns:
        1 if prediction is correct, 0 if incorrect
    """
    if sentiment.lower() == "positive" and ret > 0:
        return 1
    elif sentiment.lower() == "negative" and ret < 0:
        return 1
    elif sentiment.lower() == "neutral" and abs(ret) < 0.01:
        return 1
    else:
        return 0

def print_performance_summary(performance_metrics: Dict[str, KOLPerformanceMetrics]):
    """
    Print a formatted summary of KOL performance metrics
    
    Args:
        performance_metrics: Dictionary of KOL performance metrics
    """
    print("KOL Performance Metrics Summary")
    print("=" * 80)
    
    for kol_name, metrics in performance_metrics.items():
        print(f"\nKOL: {kol_name}")
        print(f"Total Predictions: {metrics.total_predictions}")
        print(f"Direction Correctness Rate: {metrics.direction_correctness_rate:.2%}")
        
        print("\n1-Day Metrics:")
        print(f"  Mean Return: {metrics.mean_return_1d:.4f}")
        print(f"  Volatility: {metrics.volatility_1d:.4f}")
        print(f"  Sharpe Ratio: {metrics.sharpe_ratio_1d:.4f}")
        print(f"  Information Ratio: {metrics.information_ratio_1d:.4f}")
        
        print("\n3-Day Metrics:")
        print(f"  Mean Return: {metrics.mean_return_3d:.4f}")
        print(f"  Volatility: {metrics.volatility_3d:.4f}")
        print(f"  Sharpe Ratio: {metrics.sharpe_ratio_3d:.4f}")
        print(f"  Information Ratio: {metrics.information_ratio_3d:.4f}")
        
        print("\n10-Day Metrics:")
        print(f"  Mean Return: {metrics.mean_return_10d:.4f}")
        print(f"  Volatility: {metrics.volatility_10d:.4f}")
        print(f"  Sharpe Ratio: {metrics.sharpe_ratio_10d:.4f}")
        print(f"  Information Ratio: {metrics.information_ratio_10d:.4f}")
        print("-" * 40)

def get_top_performers(performance_metrics: Dict[str, KOLPerformanceMetrics], 
                       metric: str = 'direction_correctness_rate', 
                       top_n: int = 5) -> List[tuple]:
    """
    Get top performing KOLs based on a specific metric
    
    Args:
        performance_metrics: Dictionary of KOL performance metrics
        metric: Metric to sort by (e.g., 'direction_correctness_rate', 'sharpe_ratio_1d')
        top_n: Number of top performers to return
    
    Returns:
        List of tuples (kol_name, metric_value) sorted by metric
    """
    valid_metrics = [
        'direction_correctness_rate', 'mean_return_1d', 'mean_return_3d', 'mean_return_10d',
        'sharpe_ratio_1d', 'sharpe_ratio_3d', 'sharpe_ratio_10d',
        'information_ratio_1d', 'information_ratio_3d', 'information_ratio_10d'
    ]
    
    if metric not in valid_metrics:
        raise ValueError(f"Invalid metric. Must be one of: {valid_metrics}")
    
    performers = []
    for kol_name, metrics in performance_metrics.items():
        metric_value = getattr(metrics, metric)
        performers.append((kol_name, metric_value))
    
    # Sort by metric value (descending)
    performers.sort(key=lambda x: x[1], reverse=True)
    
    return performers[:top_n]

def save_performance_metrics_to_db(performance_metrics: dict, db_path: str = "kol_performance_metrics.db"):
    """
    Save calculated KOL performance metrics to the database table.
    """
    engine = create_engine(f'sqlite:///{db_path}')
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    try:
        for kol_name, metrics in performance_metrics.items():
            record = KOLPerformanceMetricsTable(
                kol_name=kol_name,
                direction_correctness_rate=metrics.direction_correctness_rate,
                mean_return_1d=metrics.mean_return_1d,
                mean_return_3d=metrics.mean_return_3d,
                mean_return_10d=metrics.mean_return_10d,
                volatility_1d=metrics.volatility_1d,
                volatility_3d=metrics.volatility_3d,
                volatility_10d=metrics.volatility_10d,
                sharpe_ratio_1d=metrics.sharpe_ratio_1d,
                sharpe_ratio_3d=metrics.sharpe_ratio_3d,
                sharpe_ratio_10d=metrics.sharpe_ratio_10d,
                information_ratio_1d=metrics.information_ratio_1d,
                information_ratio_3d=metrics.information_ratio_3d,
                information_ratio_10d=metrics.information_ratio_10d,
                total_predictions=metrics.total_predictions,
                grade=getattr(metrics, 'grade', None)
            )
            session.add(record)
        session.commit()
    finally:
        session.close()

# Example usage
if __name__ == "__main__":
    # This would be used with actual database records
    # from KOLSentiment import KOLSentimentDB
    # db = KOLSentimentDB()
    # records = db.get_records_with_returns()
    # performance_metrics = calculate_kol_performance_metrics(records)
    
    print("KOL Performance Metrics Calculator")
    print("Import this module and use calculate_kol_performance_metrics() with your database records") 