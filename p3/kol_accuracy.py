def is_direction_correct(sentiment, ret):
    """
    Check if the KOL sentiment prediction direction is correct based on actual returns
    
    Args:
        sentiment (str): KOL sentiment prediction ("positive", "negative", "neutral")
        ret (float): Actual return value
    
    Returns:
        int: 1 if prediction is correct, 0 if incorrect
    """
    if sentiment.lower() == "positive" and ret > 0:
        return 1
    elif sentiment.lower() == "negative" and ret < 0:
        return 1
    elif sentiment.lower() == "neutral" and abs(ret) < 0.01:  # Consider neutral if return is very small
        return 1
    else:
        return 0

def calculate_accuracy_score(sentiment, ret_1d, ret_3d, ret_10d):
    """
    Calculate accuracy scores for different time periods
    
    Args:
        sentiment (str): KOL sentiment prediction
        ret_1d (float): 1-day return
        ret_3d (float): 3-day return
        ret_10d (float): 10-day return
    
    Returns:
        dict: Dictionary containing accuracy scores for each time period
    """
    accuracy_scores = {
        'accuracy_1d': is_direction_correct(sentiment, ret_1d) if ret_1d is not None else None,
        'accuracy_3d': is_direction_correct(sentiment, ret_3d) if ret_3d is not None else None,
        'accuracy_10d': is_direction_correct(sentiment, ret_10d) if ret_10d is not None else None
    }
    
    return accuracy_scores

def get_kol_performance_stats(records):
    """
    Calculate performance statistics for KOL predictions
    
    Args:
        records (list): List of KOLSentiment records with return data
    
    Returns:
        dict: Performance statistics for each KOL
    """
    kol_stats = {}
    
    for record in records:
        if record.return_1d is None:
            continue
            
        if record.kol_name not in kol_stats:
            kol_stats[record.kol_name] = {
                'total_predictions': 0,
                'correct_1d': 0,
                'correct_3d': 0,
                'correct_10d': 0,
                'accuracy_1d': 0.0,
                'accuracy_3d': 0.0,
                'accuracy_10d': 0.0
            }
        
        kol_stats[record.kol_name]['total_predictions'] += 1
        
        # Calculate accuracy for each time period
        if record.return_1d is not None:
            if is_direction_correct(record.sentiment, record.return_1d):
                kol_stats[record.kol_name]['correct_1d'] += 1
        
        if record.return_3d is not None:
            if is_direction_correct(record.sentiment, record.return_3d):
                kol_stats[record.kol_name]['correct_3d'] += 1
        
        if record.return_10d is not None:
            if is_direction_correct(record.sentiment, record.return_10d):
                kol_stats[record.kol_name]['correct_10d'] += 1
    
    # Calculate accuracy percentages
    for kol_name, stats in kol_stats.items():
        if stats['total_predictions'] > 0:
            stats['accuracy_1d'] = stats['correct_1d'] / stats['total_predictions']
            stats['accuracy_3d'] = stats['correct_3d'] / stats['total_predictions']
            stats['accuracy_10d'] = stats['correct_10d'] / stats['total_predictions']
    
    return kol_stats

def analyze_sentiment_accuracy(records):
    """
    Analyze accuracy by sentiment type
    
    Args:
        records (list): List of KOLSentiment records with return data
    
    Returns:
        dict: Accuracy statistics by sentiment type
    """
    sentiment_stats = {
        'positive': {'total': 0, 'correct_1d': 0, 'correct_3d': 0, 'correct_10d': 0, 'accuracy_1d': 0.0, 'accuracy_3d': 0.0, 'accuracy_10d': 0.0},
        'negative': {'total': 0, 'correct_1d': 0, 'correct_3d': 0, 'correct_10d': 0, 'accuracy_1d': 0.0, 'accuracy_3d': 0.0, 'accuracy_10d': 0.0},
        'neutral': {'total': 0, 'correct_1d': 0, 'correct_3d': 0, 'correct_10d': 0, 'accuracy_1d': 0.0, 'accuracy_3d': 0.0, 'accuracy_10d': 0.0}
    }
    
    for record in records:
        if record.return_1d is None:
            continue
            
        sentiment = record.sentiment.lower()
        if sentiment in sentiment_stats:
            sentiment_stats[sentiment]['total'] += 1
            
            if record.return_1d is not None:
                if is_direction_correct(record.sentiment, record.return_1d):
                    sentiment_stats[sentiment]['correct_1d'] += 1
            
            if record.return_3d is not None:
                if is_direction_correct(record.sentiment, record.return_3d):
                    sentiment_stats[sentiment]['correct_3d'] += 1
            
            if record.return_10d is not None:
                if is_direction_correct(record.sentiment, record.return_10d):
                    sentiment_stats[sentiment]['correct_10d'] += 1
    
    # Calculate accuracy percentages
    for sentiment, stats in sentiment_stats.items():
        if stats['total'] > 0:
            stats['accuracy_1d'] = stats['correct_1d'] / stats['total']
            stats['accuracy_3d'] = stats['correct_3d'] / stats['total']
            stats['accuracy_10d'] = stats['correct_10d'] / stats['total']
    
    return sentiment_stats

# Example usage
if __name__ == "__main__":
    # Example usage with sample data
    sample_sentiment = "positive"
    sample_return = 0.05  # 5% positive return
    
    is_correct = is_direction_correct(sample_sentiment, sample_return)
    print(f"Sentiment: {sample_sentiment}, Return: {sample_return:.2%}, Correct: {is_correct}")
    
    # Test with different scenarios
    test_cases = [
        ("positive", 0.03, "Should be correct"),
        ("positive", -0.02, "Should be incorrect"),
        ("negative", -0.05, "Should be correct"),
        ("negative", 0.01, "Should be incorrect"),
        ("neutral", 0.005, "Should be correct (small return)"),
        ("neutral", 0.05, "Should be incorrect (large return)")
    ]
    
    print("\nTesting direction correctness:")
    for sentiment, ret, description in test_cases:
        result = is_direction_correct(sentiment, ret)
        print(f"{description}: Sentiment={sentiment}, Return={ret:.2%}, Correct={result}") 