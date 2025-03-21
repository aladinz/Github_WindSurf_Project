# Swing Trading Journal

A comprehensive web application for tracking and analyzing swing trades. This application allows traders to log their trades, visualize performance metrics, and gain insights into their trading patterns.

## Features

- **Trade Logging**: Record detailed information about each trade including stock symbol, entry/exit prices, dates, position size, and profit/loss.
- **Data Visualization**: View performance charts showing profit/loss over time, win rate, and other key metrics.
- **Filtering**: Filter trades by date range, stock symbol, or performance.
- **Dashboard**: Get a quick overview of trading performance with key statistics.
- **Responsive Design**: Works on desktop and mobile devices.
- **Sharpe Ratio**: Calculates and displays the Sharpe Ratio, a measure of risk-adjusted return.
- **Import/Export**: Export trades to Excel or CSV format and import trades from Excel or CSV files.

## Installation

1. Clone this repository
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Initialize the database:
   ```
   python init_db.py
   ```
4. Run the application:
   ```
   python app.py
   ```

## Usage

1. Navigate to `http://localhost:5000` in your web browser
2. Use the "Add Trade" button to log new trades
3. View your performance metrics on the dashboard
4. Filter and analyze your trading history

## Technology Stack

- Backend: Flask, SQLAlchemy
- Frontend: HTML, CSS, JavaScript, Bootstrap
- Data Visualization: Plotly
- Database: SQLite (default, can be configured for other databases)

## Deployment

### Deploying to Render.com

1. Create a free account on [Render.com](https://render.com)
2. Fork or clone this repository to your GitHub account
3. In Render dashboard, click "New" and select "Web Service"
4. Connect your GitHub repository
5. Configure the service:
   - Name: SwingTradeJournal (or your preferred name)
   - Environment: Python
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn app:app`
   - Select the free plan
6. Click "Create Web Service"

The application will be deployed and available at the URL provided by Render (typically `https://your-service-name.onrender.com`).

### Environment Variables

For production deployment, set the following environment variables:
- `SECRET_KEY`: A secure random string for session encryption
- `FLASK_ENV`: Set to 'production' for production deployment

## New Features

### Sharpe Ratio

The application now calculates and displays the Sharpe Ratio, a measure of risk-adjusted return. You can adjust the risk-free rate used in the calculation through the user interface.

### Import/Export

- **Export**: Export your trades to Excel or CSV format for backup or analysis in other tools
- **Import**: Import trades from Excel or CSV files, with validation to ensure data integrity
