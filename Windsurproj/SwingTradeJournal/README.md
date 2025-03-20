# Swing Trading Journal

A comprehensive web application for tracking and analyzing swing trades. This application allows traders to log their trades, visualize performance metrics, and gain insights into their trading patterns.

## Features

- **Trade Logging**: Record detailed information about each trade including stock symbol, entry/exit prices, dates, position size, and profit/loss.
- **Data Visualization**: View performance charts showing profit/loss over time, win rate, and other key metrics.
- **Filtering**: Filter trades by date range, stock symbol, or performance.
- **Dashboard**: Get a quick overview of trading performance with key statistics.
- **Responsive Design**: Works on desktop and mobile devices.

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
- Data Visualization: Plotly, Dash
- Database: SQLite (default, can be configured for other databases)
