from flask_wtf import FlaskForm
from wtforms import StringField, DateField, FloatField, IntegerField, TextAreaField, SelectField, SubmitField
from wtforms.validators import DataRequired, Length, NumberRange, Optional

class TradeForm(FlaskForm):
    """Form for adding or editing a trade"""
    symbol = StringField('Stock Symbol', validators=[
        DataRequired(), 
        Length(min=1, max=10, message='Symbol must be between 1 and 10 characters')
    ])
    
    entry_date = DateField('Entry Date', validators=[DataRequired()])
    exit_date = DateField('Exit Date', validators=[DataRequired()])
    
    entry_price = FloatField('Entry Price', validators=[
        DataRequired(),
        NumberRange(min=0.01, message='Entry price must be greater than 0')
    ])
    
    exit_price = FloatField('Exit Price', validators=[
        DataRequired(),
        NumberRange(min=0.01, message='Exit price must be greater than 0')
    ])
    
    position_size = IntegerField('Position Size (Shares)', validators=[
        DataRequired(),
        NumberRange(min=1, message='Position size must be at least 1')
    ])
    
    trade_type = SelectField('Trade Type', choices=[
        ('LONG', 'Long (Buy)'), 
        ('SHORT', 'Short (Sell)')
    ], validators=[DataRequired()])
    
    notes = TextAreaField('Notes', validators=[Optional()])
    
    submit = SubmitField('Save Trade')

class FilterForm(FlaskForm):
    """Form for filtering trades"""
    symbol = StringField('Stock Symbol', validators=[Optional()])
    
    start_date = DateField('Start Date', validators=[Optional()])
    end_date = DateField('End Date', validators=[Optional()])
    
    trade_type = SelectField('Trade Type', choices=[
        ('', 'All'),
        ('LONG', 'Long (Buy)'), 
        ('SHORT', 'Short (Sell)')
    ], validators=[Optional()])
    
    result = SelectField('Result', choices=[
        ('', 'All'),
        ('profit', 'Profit'), 
        ('loss', 'Loss')
    ], validators=[Optional()])
    
    submit = SubmitField('Apply Filter')
