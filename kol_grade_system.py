def calculate_kol_grade(
    accuracy: float,
    sharpe: float,
    sample_num: int,
    w_acc: float = 0.5,
    w_sharpe: float = 0.3,
    w_sample: float = 0.2,
    sample_norm: int = 50
) -> float:
    """
    Calculate a composite grade for a KOL.
    
    Args:
        accuracy (float): Direction correctness rate (0~1)
        sharpe (float): Sharpe ratio
        sample_num (int): Number of samples/messages
        w_acc, w_sharpe, w_sample (float): Weights for each factor
        sample_norm (int): Normalization base for sample number
    
    Returns:
        float: Grade (0~100)
    """
    # Normalize sample number (capped at 1)
    sample_score = min(sample_num / sample_norm, 1.0)
    # Normalize sharpe (adjust based on actual distribution)
    sharpe_score = min(max(sharpe / 2, 0), 1.0)  # Assuming Sharpe 2 is full score
    # Calculate total score
    grade = 100 * (w_acc * accuracy + w_sharpe * sharpe_score + w_sample * sample_score)
    return round(grade, 2)

def add_grade_to_performance(performance_metrics: dict) -> dict:
    """
    Add grade to each KOL's performance metrics dict.
    """
    for kol_name, metrics in performance_metrics.items():
        # Here we use 1d Sharpe as an example, you can change it to average or maximum Sharpe
        grade = calculate_kol_grade(
            accuracy=metrics.direction_correctness_rate,
            sharpe=metrics.sharpe_ratio_1d,
            sample_num=metrics.total_predictions
        )
        setattr(metrics, 'grade', grade)
    return performance_metrics

# Example usage
if __name__ == "__main__":
    # Assuming we have performance_metrics
    # from kol_performance_metrics import calculate_kol_performance_metrics
    # performance_metrics = calculate_kol_performance_metrics(records)
    # performance_metrics = add_grade_to_performance(performance_metrics)
    print("Grade system ready. Use add_grade_to_performance() to enrich your KOL metrics.") 