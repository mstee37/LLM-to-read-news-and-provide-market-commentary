import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
from pandas.tseries.offsets import BusinessDay
from send_email import send_email_v2
from scrape_eco_calendar import scrape_and_process_calendar

def calculate_changes(ticker, name, start_date, end_date):
    data = yf.download(ticker, start=start_date, end=end_date, auto_adjust=False)
    data.columns = data.columns.get_level_values(0)
    # print(data.columns)
    # Ensure data is sorted by date
    data = data.sort_index()
    # print(data.index[-1])
    # Calculate changes
    last_close = data['Adj Close'].iloc[-1]

    # print(data.index[-1])
    day_ago_date = data.index[-1] - BusinessDay(1)
    # [print(day_ago_date)]
    week_ago_date = data.index[-1] - BusinessDay(5)
    # print(week_ago_date)
    month_ago_date = data.index[-1] - BusinessDay(20)
    # print(month_ago_date)

    day_ago = data.loc[day_ago_date, 'Adj Close'] if day_ago_date in data.index else last_close
    week_ago = data.loc[week_ago_date, 'Adj Close'] if week_ago_date in data.index else last_close
    month_ago = data.loc[month_ago_date, 'Adj Close'] if month_ago_date in data.index else last_close

    day_over_day_abs = last_close - day_ago
    week_over_week_abs = last_close - week_ago
    month_over_month_abs = last_close - month_ago

    day_over_day_pct = (day_over_day_abs / day_ago) * 100 if day_ago != 0 else 0
    week_over_week_pct = (week_over_week_abs / week_ago) * 100 if week_ago != 0 else 0
    month_over_month_pct = (month_over_month_abs / month_ago) * 100 if month_ago != 0 else 0

    return {
        "Ticker" : name,
        'Last Close': last_close,
        f'DoD %': day_over_day_pct,
        f'WoW %': week_over_week_pct,
        f'MoM %': month_over_month_pct,
        f'DoD Abs': day_over_day_abs,
        f'WoW Abs': week_over_week_abs,
        f'MoM Abs': month_over_month_abs,
    }

def get_tickers_changes(tickers, names, start_date, end_date):
    results = []
    for ticker, name in zip(tickers, names):
        try:
            changes = calculate_changes(ticker, name, start_date, end_date)
            # changes['Ticker'] = ticker
            results.append(changes)
        except Exception as e:
            print(f"Error retrieving data for {ticker}: {e}")

    return pd.DataFrame(results)

def combine_html_tables(html_1, html_2):
    
    # Combine the HTML tables with a line break in between
    combined_html_table = f"{html_1}<br><br>{html_2}"
    
    return combined_html_table

if __name__ == "__main__":
    # tickers = ["BTC-USD"]  # Add your list of tickers here
    tickers = pd.read_csv("C:\\Users\\tee_m\\Desktop\\TIC3901 Indus Project\\scripts\\input_ticker_prices.csv")["Ticker"].tolist()
    # print(tickers.columns)
    names = pd.read_csv("C:\\Users\\tee_m\\Desktop\\TIC3901 Indus Project\\scripts\\input_ticker_prices.csv")["Name"].tolist()

    
    end_date = datetime.today().date()
    start_date = end_date - timedelta(29) - BusinessDay(1)  # Retrieve data for the past month
    # print(start_date)
    
    results_df = get_tickers_changes(tickers, names, start_date, end_date)
    
    # Display the results
    print(results_df.sort_values(by="DoD %").round(5).to_string())
    
    html_df = combine_html_tables(results_df.sort_values(by="DoD %").round(5).to_html(index=False, justify="center", border=1), scrape_and_process_calendar())
    
    send_email_v2(subject=f"{end_date} Daily Snapshot & ECO Calendar", query="No LLM used in this process", html_body=html_df)

    # Save to a CSV file
    results_df.to_csv("C:\\Users\\tee_m\\Desktop\\TIC3901 Indus Project\\scripts\\output_ticker_prices.csv", index=False)