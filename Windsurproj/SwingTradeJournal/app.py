from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, send_file
from models import db, Trade
from forms import TradeForm, FilterForm
from datetime import datetime
import os
import json
import pandas as pd
import io
import tempfile
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-key-for-testing')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///trades.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Fix for PostgreSQL on Render.com (if DATABASE_URL starts with postgres://)
if app.config['SQLALCHEMY_DATABASE_URI'].startswith('postgres://'):
    app.config['SQLALCHEMY_DATABASE_URI'] = app.config['SQLALCHEMY_DATABASE_URI'].replace('postgres://', 'postgresql://', 1)

db.init_app(app)

@app.route('/')
def index():
    """Main dashboard page"""
    # Get summary statistics
    total_trades = Trade.query.count()
    total_profit_loss = Trade.get_total_profit_loss() if total_trades > 0 else 0
    win_rate = Trade.get_win_rate() if total_trades > 0 else 0
    avg_holding_period = Trade.get_average_holding_period() if total_trades > 0 else 0
    
    # Get recent trades
    recent_trades = Trade.query.order_by(Trade.exit_date.desc()).limit(5).all()
    
    return render_template('index.html', 
                          total_trades=total_trades,
                          total_profit_loss=total_profit_loss,
                          win_rate=win_rate,
                          avg_holding_period=avg_holding_period,
                          recent_trades=recent_trades)

@app.route('/trades')
def trades():
    """View all trades with optional filtering"""
    filter_form = FilterForm(request.args)
    
    # Base query
    query = Trade.query
    
    # Apply filters if provided
    if filter_form.symbol.data:
        query = query.filter(Trade.symbol.ilike(f'%{filter_form.symbol.data}%'))
    
    if filter_form.start_date.data:
        query = query.filter(Trade.entry_date >= filter_form.start_date.data)
    
    if filter_form.end_date.data:
        query = query.filter(Trade.exit_date <= filter_form.end_date.data)
    
    if filter_form.trade_type.data:
        query = query.filter(Trade.trade_type == filter_form.trade_type.data)
    
    if filter_form.result.data == 'profit':
        # This is a simplification, actual implementation would be more complex
        # as we'd need to calculate profit/loss on the fly
        trades = [trade for trade in query.all() if trade.profit_loss > 0]
    elif filter_form.result.data == 'loss':
        trades = [trade for trade in query.all() if trade.profit_loss <= 0]
    else:
        trades = query.order_by(Trade.exit_date.desc()).all()
    
    return render_template('trades.html', trades=trades, filter_form=filter_form)

@app.route('/trade/new', methods=['GET', 'POST'])
def add_trade():
    """Add a new trade"""
    form = TradeForm()
    
    if form.validate_on_submit():
        trade = Trade(
            symbol=form.symbol.data.upper(),
            entry_date=form.entry_date.data,
            exit_date=form.exit_date.data,
            entry_price=form.entry_price.data,
            exit_price=form.exit_price.data,
            position_size=form.position_size.data,
            trade_type=form.trade_type.data,
            notes=form.notes.data
        )
        
        db.session.add(trade)
        db.session.commit()
        
        flash('Trade added successfully!', 'success')
        return redirect(url_for('trades'))
    
    return render_template('trade_form.html', form=form, title='Add Trade')

@app.route('/trade/<int:trade_id>/edit', methods=['GET', 'POST'])
def edit_trade(trade_id):
    """Edit an existing trade"""
    trade = Trade.query.get_or_404(trade_id)
    form = TradeForm(obj=trade)
    
    if form.validate_on_submit():
        trade.symbol = form.symbol.data.upper()
        trade.entry_date = form.entry_date.data
        trade.exit_date = form.exit_date.data
        trade.entry_price = form.entry_price.data
        trade.exit_price = form.exit_price.data
        trade.position_size = form.position_size.data
        trade.trade_type = form.trade_type.data
        trade.notes = form.notes.data
        
        db.session.commit()
        
        flash('Trade updated successfully!', 'success')
        return redirect(url_for('trades'))
    
    return render_template('trade_form.html', form=form, title='Edit Trade')

@app.route('/trade/<int:trade_id>/delete', methods=['POST'])
def delete_trade(trade_id):
    """Delete a trade"""
    trade = Trade.query.get_or_404(trade_id)
    
    db.session.delete(trade)
    db.session.commit()
    
    flash('Trade deleted successfully!', 'success')
    return redirect(url_for('trades'))

@app.route('/api/trades')
def api_trades():
    """API endpoint to get all trades as JSON"""
    trades = Trade.query.all()
    return jsonify([trade.to_dict() for trade in trades])

@app.route('/api/stats')
def api_stats():
    """API endpoint to get trading statistics as JSON"""
    total_trades = Trade.query.count()
    
    # Get risk-free rate from query parameter, default to 0
    risk_free_rate = float(request.args.get('risk_free_rate', 0.0))
    
    if total_trades == 0:
        return jsonify({
            'total_trades': 0,
            'total_profit_loss': 0,
            'win_rate': 0,
            'avg_holding_period': 0,
            'sharpe_ratio': 0,
            'monthly_performance': []
        })
    
    # Calculate stats
    total_profit_loss = Trade.get_total_profit_loss()
    win_rate = Trade.get_win_rate()
    avg_holding_period = Trade.get_average_holding_period()
    sharpe_ratio = Trade.get_sharpe_ratio(risk_free_rate)
    
    # Get monthly performance data
    trades = Trade.query.all()
    monthly_performance = []
    
    # Group trades by month
    months = {}
    for trade in trades:
        month_key = trade.exit_date.strftime('%Y-%m')
        if month_key not in months:
            months[month_key] = 0
        months[month_key] += trade.profit_loss
    
    # Convert to list format
    for month, profit_loss in months.items():
        monthly_performance.append({
            'month': month,
            'profit_loss': profit_loss
        })
    
    return jsonify({
        'total_trades': total_trades,
        'total_profit_loss': total_profit_loss,
        'win_rate': win_rate,
        'avg_holding_period': avg_holding_period,
        'sharpe_ratio': sharpe_ratio,
        'monthly_performance': monthly_performance
    })

@app.route('/analytics')
def analytics():
    """Analytics page with charts and visualizations"""
    return render_template('analytics.html')

@app.route('/import-export')
def import_export():
    """Import/Export page for trades data"""
    return render_template('import_export.html')

@app.route('/export/excel')
def export_excel():
    """Export trades to Excel file"""
    trades = Trade.query.all()
    
    if not trades:
        flash('No trades to export', 'warning')
        return redirect(url_for('import_export'))
    
    # Convert trades to DataFrame
    trades_data = []
    for trade in trades:
        trades_data.append({
            'id': trade.id,
            'symbol': trade.symbol,
            'entry_date': trade.entry_date.strftime('%Y-%m-%d'),
            'exit_date': trade.exit_date.strftime('%Y-%m-%d'),
            'entry_price': trade.entry_price,
            'exit_price': trade.exit_price,
            'position_size': trade.position_size,
            'trade_type': trade.trade_type,
            'profit_loss': trade.profit_loss,
            'profit_loss_percentage': trade.profit_loss_percentage,
            'holding_period': trade.holding_period,
            'notes': trade.notes
        })
    
    df = pd.DataFrame(trades_data)
    
    # Create a BytesIO object to store the Excel file
    output = io.BytesIO()
    
    # Use ExcelWriter to write the DataFrame to the BytesIO object
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='Trades', index=False)
    
    # Seek to the beginning of the BytesIO object
    output.seek(0)
    
    # Return the Excel file as a response
    return send_file(
        output,
        download_name=f'swing_trades_{datetime.now().strftime("%Y%m%d")}.xlsx',
        as_attachment=True,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )

@app.route('/export/csv')
def export_csv():
    """Export trades to CSV file"""
    trades = Trade.query.all()
    
    if not trades:
        flash('No trades to export', 'warning')
        return redirect(url_for('import_export'))
    
    # Convert trades to DataFrame
    trades_data = []
    for trade in trades:
        trades_data.append({
            'id': trade.id,
            'symbol': trade.symbol,
            'entry_date': trade.entry_date.strftime('%Y-%m-%d'),
            'exit_date': trade.exit_date.strftime('%Y-%m-%d'),
            'entry_price': trade.entry_price,
            'exit_price': trade.exit_price,
            'position_size': trade.position_size,
            'trade_type': trade.trade_type,
            'profit_loss': trade.profit_loss,
            'profit_loss_percentage': trade.profit_loss_percentage,
            'holding_period': trade.holding_period,
            'notes': trade.notes
        })
    
    df = pd.DataFrame(trades_data)
    
    # Create a BytesIO object to store the CSV file
    output = io.BytesIO()
    
    # Write the DataFrame to the BytesIO object as CSV
    df.to_csv(output, index=False)
    
    # Seek to the beginning of the BytesIO object
    output.seek(0)
    
    # Return the CSV file as a response
    return send_file(
        output,
        download_name=f'swing_trades_{datetime.now().strftime("%Y%m%d")}.csv',
        as_attachment=True,
        mimetype='text/csv'
    )

@app.route('/import/excel', methods=['POST'])
def import_excel():
    """Import trades from Excel file"""
    if 'file' not in request.files:
        flash('No file part', 'danger')
        return redirect(url_for('import_export'))
    
    file = request.files['file']
    
    if file.filename == '':
        flash('No selected file', 'danger')
        return redirect(url_for('import_export'))
    
    if not file.filename.endswith(('.xlsx', '.xls')):
        flash('File must be an Excel file (.xlsx or .xls)', 'danger')
        return redirect(url_for('import_export'))
    
    try:
        # Read the Excel file
        df = pd.read_excel(file)
        
        # Validate required columns
        required_columns = ['symbol', 'entry_date', 'exit_date', 'entry_price', 'exit_price', 'position_size', 'trade_type']
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            flash(f'Missing required columns: {", ".join(missing_columns)}', 'danger')
            return redirect(url_for('import_export'))
        
        # Import trades
        import_count = 0
        error_count = 0
        
        for _, row in df.iterrows():
            try:
                # Convert dates from string to datetime if needed
                entry_date = row['entry_date']
                exit_date = row['exit_date']
                
                if isinstance(entry_date, str):
                    entry_date = datetime.strptime(entry_date, '%Y-%m-%d')
                
                if isinstance(exit_date, str):
                    exit_date = datetime.strptime(exit_date, '%Y-%m-%d')
                
                # Create new trade
                trade = Trade(
                    symbol=str(row['symbol']).upper(),
                    entry_date=entry_date,
                    exit_date=exit_date,
                    entry_price=float(row['entry_price']),
                    exit_price=float(row['exit_price']),
                    position_size=int(row['position_size']),
                    trade_type=str(row['trade_type']).upper(),
                    notes=str(row.get('notes', '')) if not pd.isna(row.get('notes', '')) else ''
                )
                
                db.session.add(trade)
                import_count += 1
            except Exception as e:
                error_count += 1
                print(f"Error importing row: {e}")
        
        db.session.commit()
        
        if error_count > 0:
            flash(f'Imported {import_count} trades with {error_count} errors', 'warning')
        else:
            flash(f'Successfully imported {import_count} trades', 'success')
        
        return redirect(url_for('trades'))
    
    except Exception as e:
        flash(f'Error importing file: {str(e)}', 'danger')
        return redirect(url_for('import_export'))

@app.route('/import/csv', methods=['POST'])
def import_csv():
    """Import trades from CSV file"""
    if 'file' not in request.files:
        flash('No file part', 'danger')
        return redirect(url_for('import_export'))
    
    file = request.files['file']
    
    if file.filename == '':
        flash('No selected file', 'danger')
        return redirect(url_for('import_export'))
    
    if not file.filename.endswith('.csv'):
        flash('File must be a CSV file (.csv)', 'danger')
        return redirect(url_for('import_export'))
    
    try:
        # Read the CSV file
        df = pd.read_csv(file)
        
        # Validate required columns
        required_columns = ['symbol', 'entry_date', 'exit_date', 'entry_price', 'exit_price', 'position_size', 'trade_type']
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            flash(f'Missing required columns: {", ".join(missing_columns)}', 'danger')
            return redirect(url_for('import_export'))
        
        # Import trades
        import_count = 0
        error_count = 0
        
        for _, row in df.iterrows():
            try:
                # Convert dates from string to datetime if needed
                entry_date = row['entry_date']
                exit_date = row['exit_date']
                
                if isinstance(entry_date, str):
                    entry_date = datetime.strptime(entry_date, '%Y-%m-%d')
                
                if isinstance(exit_date, str):
                    exit_date = datetime.strptime(exit_date, '%Y-%m-%d')
                
                # Create new trade
                trade = Trade(
                    symbol=str(row['symbol']).upper(),
                    entry_date=entry_date,
                    exit_date=exit_date,
                    entry_price=float(row['entry_price']),
                    exit_price=float(row['exit_price']),
                    position_size=int(row['position_size']),
                    trade_type=str(row['trade_type']).upper(),
                    notes=str(row.get('notes', '')) if not pd.isna(row.get('notes', '')) else ''
                )
                
                db.session.add(trade)
                import_count += 1
            except Exception as e:
                error_count += 1
                print(f"Error importing row: {e}")
        
        db.session.commit()
        
        if error_count > 0:
            flash(f'Imported {import_count} trades with {error_count} errors', 'warning')
        else:
            flash(f'Successfully imported {import_count} trades', 'success')
        
        return redirect(url_for('trades'))
    
    except Exception as e:
        flash(f'Error importing file: {str(e)}', 'danger')
        return redirect(url_for('import_export'))

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def server_error(e):
    return render_template('500.html'), 500

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
