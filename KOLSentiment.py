from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta
import yfinance as yf
import pandas as pd
from yfinance_helper import YFinanceHelper

Base = declarative_base()

class KOLSentiment(Base):
    __tablename__ = 'kol_sentiment'
    
    id = Column(Integer, primary_key=True)
    prediction_time = Column(DateTime, nullable=False, default=datetime.now)  # Prediction time for each record
    kol_name = Column(String(100), nullable=False)
    ticker = Column(String(20), nullable=False)
    sector = Column(String(50), nullable=False)
    sentiment = Column(String(20), nullable=False)
    confidence = Column(Float, nullable=False)
    
    # Initial stock price at the time of KOL message
    initial_price = Column(Float, nullable=True)
    
    # Returns for 1, 3, and 10 days
    return_1d = Column(Float, nullable=True)
    return_3d = Column(Float, nullable=True)
    return_10d = Column(Float, nullable=True)
    
    created_at = Column(DateTime, default=datetime.now)
    
    __table_args__ = (
        Index('idx_prediction_time', 'prediction_time'),
        Index('idx_kol_name', 'kol_name'),
        Index('idx_ticker', 'ticker'),
        Index('idx_sector', 'sector'),
    )

class KOLSentimentDB:
    def __init__(self, db_path="kol_sentiment.db"):
        self.db_path = db_path
        self.engine = create_engine(f'sqlite:///{db_path}')
        self.Session = sessionmaker(bind=self.engine)
        self.init_database()
        
        # 初始化yfinance助手工具
        self.yf_helper = YFinanceHelper(
            cache_dir="yfinance_cache",
            delay_min=1.0,  # 最小延迟1秒
            delay_max=3.0   # 最大延迟3秒
        )
    
    def init_database(self):
        """Initialize the database and create tables"""
        Base.metadata.create_all(self.engine)
    
    def get_stock_price(self, ticker, date):
        """Get stock price for a specific date using YFinanceHelper"""
        try:
            price = self.yf_helper.get_stock_price_on_date(ticker, date)
            if price is not None:
                return price
            else:
                print(f"${ticker}: 无法获取 {date} 的价格数据")
                return None
        except Exception as e:
            print(f"Error getting price for {ticker} on {date}: {e}")
            return None
    
    def calculate_returns(self, ticker, initial_date, initial_price):
        """Calculate returns for 1, 3, and 10 days using YFinanceHelper"""
        try:
            # 获取足够的历史数据
            start_date = initial_date.strftime('%Y-%m-%d')
            end_date = (initial_date + timedelta(days=20)).strftime('%Y-%m-%d')
            
            hist = self.yf_helper.get_stock_data(ticker, start_date, end_date)
            if hist is None or hist.empty:
                print(f"${ticker}: 无法获取历史数据 ({start_date} 到 {end_date})")
                return None, None, None
            
            returns = {}
            
            # Calculate 1-day return
            if len(hist) > 1:
                price_1d = hist['Close'].iloc[1]
                returns['1d'] = (price_1d - initial_price) / initial_price
                print(f"Return 1d: {returns['1d']}, Return 3d: {returns.get('3d', 'N/A')}, Return 10d: {returns.get('10d', 'N/A')}")
            
            # Calculate 3-day return
            if len(hist) > 3:
                price_3d = hist['Close'].iloc[3]
                returns['3d'] = (price_3d - initial_price) / initial_price
            
            # Calculate 10-day return
            if len(hist) > 10:
                price_10d = hist['Close'].iloc[10]
                returns['10d'] = (price_10d - initial_price) / initial_price
            
            return returns.get('1d'), returns.get('3d'), returns.get('10d')
            
        except Exception as e:
            print(f"Error calculating returns for {ticker}: {e}")
            return None, None, None
    
    def insert_record_with_returns(self, kol_name, ticker, sector, sentiment, confidence, prediction_time=None):
        """Insert a new record with price and return calculations"""
        if prediction_time is None:
            prediction_time = datetime.now()
        session = self.Session()
        try:
            # Get initial price
            initial_price = self.get_stock_price(ticker, prediction_time)
            # Create record
            record = KOLSentiment(
                prediction_time=prediction_time,
                kol_name=kol_name,
                ticker=ticker,
                sector=sector,
                sentiment=sentiment,
                confidence=confidence,
                initial_price=initial_price
            )
            # Calculate returns if we have initial price
            if initial_price is not None:
                return_1d, return_3d, return_10d = self.calculate_returns(ticker, prediction_time, initial_price)
                print(f"Return 1d: {return_1d}, Return 3d: {return_3d}, Return 10d: {return_10d}")
                record.return_1d = return_1d
                record.return_3d = return_3d
                record.return_10d = return_10d
                session.add(record)
                session.commit()
            return record.id
        finally:
            session.close()
    
    def update_returns_for_existing_records(self):
        """Update returns for records that don't have return data yet"""
        session = self.Session()
        try:
            records = session.query(KOLSentiment).filter(
                KOLSentiment.return_1d.isnot(None)
            ).all()
            for record in records:
                if record.initial_price is not None:
                    return_1d, return_3d, return_10d = self.calculate_returns(
                        record.ticker, record.prediction_time, record.initial_price
                    )
                    record.return_1d = return_1d
                    record.return_3d = return_3d
                    record.return_10d = return_10d
            session.commit()
        finally:
            session.close()
    
    def get_records_with_returns(self):
        """Get all records with return data"""
        session = self.Session()
        try:
            return session.query(KOLSentiment).filter(
                KOLSentiment.return_1d.isnot(None)
            ).order_by(KOLSentiment.prediction_time.desc()).all()
        finally:
            session.close()
    
    def get_records_by_kol(self, kol_name):
        """Get records by KOL name"""
        session = self.Session()
        try:
            return session.query(KOLSentiment).filter(
                KOLSentiment.kol_name == kol_name
            ).order_by(KOLSentiment.prediction_time.desc()).all()
        finally:
            session.close()
    
    def get_records_by_ticker(self, ticker):
        """Get records by ticker"""
        session = self.Session()
        try:
            return session.query(KOLSentiment).filter(
                KOLSentiment.ticker == ticker
            ).order_by(KOLSentiment.prediction_time.desc()).all()
        finally:
            session.close()
    
    def get_records_by_sector(self, sector):
        """Get records by sector"""
        session = self.Session()
        try:
            return session.query(KOLSentiment).filter(
                KOLSentiment.sector == sector
            ).order_by(KOLSentiment.prediction_time.desc()).all()
        finally:
            session.close()
    
    def get_records_by_date_range(self, start_date, end_date):
        """Get records by date range"""
        session = self.Session()
        try:
            return session.query(KOLSentiment).filter(
                KOLSentiment.prediction_time.between(start_date, end_date)
            ).order_by(KOLSentiment.prediction_time.desc()).all()
        finally:
            session.close()
    
    def update_record(self, record_id, **kwargs):
        """Update a record by ID"""
        session = self.Session()
        try:
            record = session.query(KOLSentiment).filter(KOLSentiment.id == record_id).first()
            if record:
                for key, value in kwargs.items():
                    if hasattr(record, key):
                        setattr(record, key, value)
                session.commit()
                return True
            return False
        finally:
            session.close()
    
    def delete_record(self, record_id):
        """Delete a record by ID"""
        session = self.Session()
        try:
            record = session.query(KOLSentiment).filter(KOLSentiment.id == record_id).first()
            if record:
                session.delete(record)
                session.commit()
                return True
            return False
        finally:
            session.close()

# Example usage
if __name__ == "__main__":
    # Create database instance
    db = KOLSentimentDB()
    
    # Insert sample data with returns calculation
    sample_data = [
        ("KOL1", "AAPL", "Technology", "Positive", 0.85),
        ("KOL2", "TSLA", "Automotive", "Negative", 0.72),
        ("KOL3", "MSFT", "Technology", "Neutral", 0.65),
    ]
    
    for kol_name, ticker, sector, sentiment, confidence in sample_data:
        record_id = db.insert_record_with_returns(kol_name, ticker, sector, sentiment, confidence)
        print(f"Inserted record ID: {record_id}")
    
    # Query records with returns
    print("\nRecords with returns:")
    records = db.get_records_with_returns()
    for record in records:
        print(f"ID: {record.id}, KOL: {record.kol_name}, Ticker: {record.ticker}, "
              f"Initial Price: ${record.initial_price:.2f}, "
              f"1D Return: {record.return_1d:.2%}, "
              f"3D Return: {record.return_3d:.2%}, "
              f"10D Return: {record.return_10d:.2%}") 