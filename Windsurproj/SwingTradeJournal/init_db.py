from app import app, db
from models import Trade
from datetime import datetime, timedelta
import random

def create_sample_data():
    """Create sample trade data for demonstration purposes"""
    # Clear existing data
    db.session.query(Trade).delete()
    
    # Sample stock symbols
    symbols = ['AAPL', 'MSFT', 'AMZN', 'GOOGL', 'TSLA', 'FB', 'NFLX', 'NVDA', 'AMD', 'INTC']
    
    # Create sample trades over the past 6 months
    end_date = datetime.now()
    start_date = end_date - timedelta(days=180)
    
    sample_trades = []
    
    for i in range(30):
        # Random dates within the past 6 months
        exit_date = start_date + timedelta(days=random.randint(0, 180))
        entry_date = exit_date - timedelta(days=random.randint(1, 14))  # Hold 1-14 days
        
        # Random trade details
        symbol = random.choice(symbols)
        trade_type = random.choice(['LONG', 'SHORT'])
        
        if trade_type == 'LONG':
            entry_price = round(random.uniform(50, 500), 2)
            # 70% chance of profitable trade
            if random.random() < 0.7:
                exit_price = round(entry_price * random.uniform(1.01, 1.15), 2)  # 1-15% gain
            else:
                exit_price = round(entry_price * random.uniform(0.85, 0.99), 2)  # 1-15% loss
        else:  # SHORT
            entry_price = round(random.uniform(50, 500), 2)
            # 60% chance of profitable trade
            if random.random() < 0.6:
                exit_price = round(entry_price * random.uniform(0.85, 0.99), 2)  # 1-15% gain for short
            else:
                exit_price = round(entry_price * random.uniform(1.01, 1.15), 2)  # 1-15% loss for short
        
        position_size = random.randint(10, 1000)
        
        trade = Trade(
            symbol=symbol,
            entry_date=entry_date,
            exit_date=exit_date,
            entry_price=entry_price,
            exit_price=exit_price,
            position_size=position_size,
            trade_type=trade_type,
            notes=f"Sample {trade_type.lower()} trade for {symbol}"
        )
        
        sample_trades.append(trade)
    
    db.session.add_all(sample_trades)
    db.session.commit()
    
    print(f"Created {len(sample_trades)} sample trades")

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        create_sample_data()
        print("Database initialized with sample data!")
