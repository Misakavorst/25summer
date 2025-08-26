import pandas as pd
import json
import os
from datetime import datetime

# Read the CSV file
input_file = '../opinion_mining/output_data/youtube_subtitles_Invest_with_Henry(By Gemini).csv'
output_file = 'extracted_video_data.csv'
company_knowledge_file = '../opinion_mining/knowledge_library/company_knowledge.json'
processed_output_file = 'processed_video_data_with_tickers.csv'

try:
    # Load the CSV file
    df = pd.read_csv(input_file)
    
    # Check if the required columns exist
    required_columns = ['video_id', 'channel_name', 'publishedAt', 'title', 'company', 'confidence', 'sentiment']
    missing_columns = [col for col in required_columns if col not in df.columns]
    
    if missing_columns:
        print(f"Warning: The following columns do not exist in the original file: {missing_columns}")
        print(f"Available columns: {list(df.columns)}")
    
    # Extract the existing columns
    available_columns = [col for col in required_columns if col in df.columns]
    extracted_df = df[available_columns].copy()
    
    # Save to a new CSV file
    extracted_df.to_csv(output_file, index=False, encoding='utf-8')
    
    print(f"Successfully extracted data!")
    print(f"Original data rows: {len(df)}")
    print(f"Extracted columns: {available_columns}")
    print(f"Output file: {output_file}")
    print(f"Extracted data rows: {len(extracted_df)}")
    
    # Display the first few rows of data preview
    print("\nData preview:")
    print(extracted_df.head())
    
    # Load company knowledge base
    print(f"\nLoading company knowledge base from {company_knowledge_file}...")
    with open(company_knowledge_file, 'r', encoding='utf-8') as f:
        company_knowledge = json.load(f)
    
    print(f"Loaded {len(company_knowledge)} companies from knowledge base")
    
    # Process the data to add ticker information
    print("\nProcessing data to match companies with tickers...")
    
    # Add ticker column
    extracted_df['ticker'] = None
    extracted_df['sector'] = None
    
    matched_companies = 0
    unmatched_companies = set()
    
    for index, row in extracted_df.iterrows():
        company_name = row['company']
        if company_name in company_knowledge:
            ticker = company_knowledge[company_name]['ticker']
            sector = company_knowledge[company_name]['sector']
            extracted_df.at[index, 'ticker'] = ticker
            extracted_df.at[index, 'sector'] = sector
            matched_companies += 1
        else:
            unmatched_companies.add(company_name)
    
    # Filter out rows where no ticker was found (跳过找不到的公司)
    processed_df = extracted_df.dropna(subset=['ticker']).copy()
    
    # Save the processed data
    processed_df.to_csv(processed_output_file, index=False, encoding='utf-8')
    
    print(f"\nProcessing summary:")
    print(f"Total companies processed: {len(extracted_df)}")
    print(f"Companies matched with tickers: {matched_companies}")
    print(f"Companies skipped (no ticker found): {len(extracted_df) - matched_companies}")
    print(f"Final processed rows: {len(processed_df)}")
    print(f"Processed data saved to: {processed_output_file}")
    
    if unmatched_companies:
        try:
            # Convert all to strings before sorting to avoid comparison errors
            unmatched_list = [str(company) for company in unmatched_companies if company is not None]
            print(f"\nUnmatched companies: {sorted(unmatched_list)}")
        except Exception as e:
            print(f"\nUnmatched companies (unsorted): {list(unmatched_companies)}")
            print(f"Sorting error: {e}")
    
    # Display processed data preview
    print("\nProcessed data preview:")
    print(processed_df[['company', 'ticker', 'sector', 'sentiment', 'confidence']].head())
    
    # Create sample data format similar to main.py
    print("\nCreating sample data format (similar to main.py)...")
    sample_data = []
    
    for index, row in processed_df.iterrows():
        try:
            # Convert publishedAt to datetime
            published_date = datetime.fromisoformat(row['publishedAt'].replace('Z', '+00:00'))
            
            # Map sentiment value to positive/negative (assuming sentiment > 0 is positive)
            try:
                sentiment_value = float(row['sentiment'])
                sentiment_label = "positive" if sentiment_value > 0 else "negative"
            except (ValueError, TypeError):
                sentiment_label = "neutral"  # Default for non-numeric values
            
            sample_data.append({
                'kol_name': row['channel_name'],
                'ticker': row['ticker'],
                'sector': row['sector'],
                'sentiment': sentiment_label,
                'confidence': float(row['confidence']),
                'prediction_time': published_date,
                'video_id': row['video_id'],
                'title': row['title'],
                'company': row['company'],
                'sentiment_score': float(row['sentiment'])
            })
        except Exception as e:
            print(f"Error processing row {index}: {e}")
            continue
    
    # Convert to DataFrame and save as CSV
    sample_df = pd.DataFrame(sample_data)
    sample_output_file = 'kol_sample_data.csv'
    sample_df.to_csv(sample_output_file, index=False, encoding='utf-8')
    
    print(f"Sample data saved to: {sample_output_file}")
    print(f"Total sample records: {len(sample_df)}")
    
    # Display first few rows
    print("\nSample data preview:")
    print(sample_df[['kol_name', 'ticker', 'sector', 'sentiment', 'confidence']].head(10))
    
    # Also show the tuple format for reference
    print(f"\nFirst 5 records in tuple format (similar to main.py):")
    for i, data in enumerate(sample_data[:5]):
        print(f"(\"{data['kol_name']}\", \"{data['ticker']}\", \"{data['sector']}\", \"{data['sentiment']}\", {data['confidence']}, {data['prediction_time']})")
    
except FileNotFoundError:
    print(f"Error: File not found {input_file}")
except Exception as e:
    print(f"Error processing file: {e}")
