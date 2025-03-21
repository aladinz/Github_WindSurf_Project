from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy import func

db = SQLAlchemy()

class Trade(db.Model):
    __tablename__ = 'trades'
    
    id = db.Column(db.Integer, primary_key=True)
    symbol = db.Column(db.String(10), nullable=False)
    entry_date = db.Column(db.DateTime, nullable=False)
    exit_date = db.Column(db.DateTime, nullable=False)
    entry_price = db.Column(db.Float, nullable=False)
    exit_price = db.Column(db.Float, nullable=False)
    position_size = db.Column(db.Integer, nullable=False)  # Number of shares
    trade_type = db.Column(db.String(10), nullable=False)  # 'LONG' or 'SHORT'
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    @property
    def profit_loss(self):
        """Calculate profit or loss for the trade"""
        if self.trade_type == 'LONG':
            return (self.exit_price - self.entry_price) * self.position_size
        else:  # SHORT
            return (self.entry_price - self.exit_price) * self.position_size
    
    @property
    def profit_loss_percentage(self):
        """Calculate profit or loss percentage for the trade"""
        if self.trade_type == 'LONG':
            return ((self.exit_price - self.entry_price) / self.entry_price) * 100
        else:  # SHORT
            return ((self.entry_price - self.exit_price) / self.entry_price) * 100
    
    @property
    def holding_period(self):
        """Calculate holding period in days"""
        return (self.exit_date - self.entry_date).days
    
    @classmethod
    def get_total_profit_loss(cls):
        """Get total profit/loss across all trades"""
        trades = cls.query.all()
        return sum(trade.profit_loss for trade in trades)
    
    @classmethod
    def get_win_rate(cls):
        """Calculate win rate percentage"""
        trades = cls.query.all()
        if not trades:
            return 0
        winning_trades = sum(1 for trade in trades if trade.profit_loss > 0)
        return (winning_trades / len(trades)) * 100
    
    @classmethod
    def get_average_holding_period(cls):
        """Calculate average holding period in days"""
        result = db.session.query(func.avg(func.julianday(cls.exit_date) - 
                                         func.julianday(cls.entry_date))).scalar()
        return result if result else 0
    
    @classmethod
    def get_best_trade(cls):
        """Get the most profitable trade"""
        trades = cls.query.all()
        if not trades:
            return None
        return max(trades, key=lambda trade: trade.profit_loss)
    
    @classmethod
    def get_worst_trade(cls):
        """Get the least profitable trade"""
        trades = cls.query.all()
        if not trades:
            return None
        return min(trades, key=lambda trade: trade.profit_loss)
    
    @classmethod
    def get_sharpe_ratio(cls, risk_free_rate=0.0):
        """
        Calculate the Sharpe Ratio for all trades
        
        The Sharpe ratio measures the performance of an investment compared to a risk-free asset,
        after adjusting for its risk. It's calculated as:
        (Average Return - Risk-Free Rate) / Standard Deviation of Returns
        
        Args:
            risk_free_rate (float): The risk-free rate of return (default: 0.0)
            
        Returns:
            float: The Sharpe ratio, or 0 if there are insufficient trades
        """
        trades = cls.query.all()
        if len(trades) < 2:  # Need at least 2 trades to calculate standard deviation
            return 0
            
        # Calculate daily returns
        # Sort trades by exit date
        sorted_trades = sorted(trades, key=lambda t: t.exit_date)
        
        # Extract profit/loss percentages
        returns = [trade.profit_loss_percentage for trade in sorted_trades]
        
        # Calculate average return and standard deviation
        avg_return = sum(returns) / len(returns)
        
        # Calculate variance
        variance = sum((r - avg_return) ** 2 for r in returns) / len(returns)
        
        # Calculate standard deviation
        std_dev = variance ** 0.5
        
        # Avoid division by zero
        if std_dev == 0:
            return 0
            
        # Calculate Sharpe ratio
        sharpe_ratio = (avg_return - risk_free_rate) / std_dev
        
        return sharpe_ratio
    
    def to_dict(self):
        """Convert trade to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'symbol': self.symbol,
            'entry_date': self.entry_date.strftime('%Y-%m-%d'),
            'exit_date': self.exit_date.strftime('%Y-%m-%d'),
            'entry_price': self.entry_price,
            'exit_price': self.exit_price,
            'position_size': self.position_size,
            'trade_type': self.trade_type,
            'profit_loss': self.profit_loss,
            'profit_loss_percentage': self.profit_loss_percentage,
            'holding_period': self.holding_period,
            'notes': self.notes,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S')
        }
