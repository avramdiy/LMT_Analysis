from flask import Flask, render_template_string
import pandas as pd
import os
import plotly.graph_objs as go
import plotly.offline as pyo

app = Flask(__name__)

FILE_PATH = r"C:\Users\avram\OneDrive\Desktop\TRG Week 25\enph.us.txt"

def load_and_prepare_data():
    if not os.path.exists(FILE_PATH):
        return None, "File not found."

    try:
        df = pd.read_csv(FILE_PATH, delimiter=",", header=0)
        df.columns = df.columns.str.strip()
        if 'OpenInt' in df.columns:
            df = df.drop(columns=['OpenInt'])
        if 'Date' not in df.columns:
            return None, "Date column not found."
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
        df = df.dropna(subset=['Date'])
        return df, None
    except Exception as e:
        return None, str(e)

@app.route('/')
def display_table():
    df, err = load_and_prepare_data()
    if err:
        return err, 404

    start_date = pd.Timestamp('2012-11-01')
    end_date = pd.Timestamp('2017-11-30')
    df = df[(df['Date'] >= start_date) & (df['Date'] <= end_date)]

    if df.empty:
        return "No data available for the specified date range.", 404

    html_table = df.to_html(
        classes='table table-bordered table-hover text-center',
        index=False,
        border=0
    )

    template = """
    <!DOCTYPE html>
    <html>
    <head>
        <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css">
        <style>
            .table {{
                margin: auto;
                width: 90%;
            }}
            h1 {{
                text-align: center;
                margin-top: 20px;
            }}
            a {{
                display: block;
                text-align: center;
                margin: 15px auto;
            }}
        </style>
        <title>Data Table</title>
    </head>
    <body>
        <h1>Data Table</h1>
        <a href="/monthlyvolume">View Average Monthly Volume (11/2016 - 11/2017)</a>
        <a href="/monthlyopen">View Average Monthly Open (11/2016 - 11/2017)</a>
        <a href="/monthlyclose">View Average Monthly Close (11/2016 - 11/2017)</a>
        {}
    </body>
    </html>
    """.format(html_table)
    return template

@app.route('/monthlyvolume')
def plot_monthly_volume():
    df, err = load_and_prepare_data()
    if err:
        return err, 404

    start_date = pd.Timestamp('2016-11-01')
    end_date = pd.Timestamp('2017-11-30')
    df = df[(df['Date'] >= start_date) & (df['Date'] <= end_date)]

    if df.empty:
        return "No data available for the specified date range.", 404

    if 'Volume' not in df.columns:
        return "Volume column not found.", 404

    df['Volume'] = pd.to_numeric(df['Volume'], errors='coerce')
    df = df.dropna(subset=['Volume'])
    df['YearMonth'] = df['Date'].dt.to_period('M')
    monthly_avg = df.groupby('YearMonth')['Volume'].mean().reset_index()
    monthly_avg['YearMonth'] = monthly_avg['YearMonth'].dt.to_timestamp()

    trace = go.Scatter(
        x=monthly_avg['YearMonth'],
        y=monthly_avg['Volume'],
        mode='lines+markers',
        name='Average Volume'
    )
    layout = go.Layout(
        title='Average Monthly Trading Volume (Nov 2016 - Nov 2017)',
        xaxis=dict(title='Month'),
        yaxis=dict(title='Average Volume'),
        margin=dict(l=40, r=40, t=50, b=40)
    )
    fig = go.Figure(data=[trace], layout=layout)
    graph_html = pyo.plot(fig, output_type='div', include_plotlyjs=True)

    template = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Average Monthly Volume</title>
        <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css">
        <style>
            body {{
                max-width: 900px;
                margin: 30px auto;
                font-family: Arial, sans-serif;
            }}
            a {{
                display: block;
                margin-bottom: 20px;
                text-align: center;
            }}
        </style>
    </head>
    <body>
        <a href="/">← Back to Data Table</a>
        <h1>Average Monthly Trading Volume</h1>
        {}
    </body>
    </html>
    """.format(graph_html)
    return template

@app.route('/monthlyopen')
def plot_monthly_open():
    df, err = load_and_prepare_data()
    if err:
        return err, 404

    # Filter date range
    start_date = pd.Timestamp('2016-11-01')
    end_date = pd.Timestamp('2017-11-30')
    df = df[(df['Date'] >= start_date) & (df['Date'] <= end_date)]

    if df.empty:
        return "No data available for the specified date range.", 404

    if 'Open' not in df.columns:
        return "Column 'Open' not found.", 404

    df['Open'] = pd.to_numeric(df['Open'], errors='coerce')
    df = df.dropna(subset=['Open'])

    monthly_open = df.groupby(pd.Grouper(key='Date', freq='M'))['Open'].mean().reset_index()
    monthly_open = monthly_open.sort_values('Date')

    trace = go.Scatter(
        x=monthly_open['Date'],
        y=monthly_open['Open'],
        mode='lines+markers',
        name='Average Open Price',
        line=dict(color='firebrick')
    )

    layout = go.Layout(
        title='Average Monthly Open Price (Nov 2016 - Nov 2017)',
        xaxis=dict(title='Month'),
        yaxis=dict(title='Average Open Price'),
        margin=dict(l=40, r=40, t=50, b=40)
    )

    fig = go.Figure(data=[trace], layout=layout)
    graph_html = pyo.plot(fig, output_type='div', include_plotlyjs=False)

    template = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Monthly Average Open Price</title>
        <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
        <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css">
        <style>
            body {{
                max-width: 900px;
                margin: 30px auto;
                font-family: Arial, sans-serif;
            }}
            a {{
                display: block;
                margin-bottom: 20px;
                text-align: center;
            }}
        </style>
    </head>
    <body>
        <a href="/">← Back to Data Table</a>
        <h1>Average Monthly Open Price</h1>
        {graph_html}
    </body>
    </html>
    """
    return template

@app.route('/monthlyclose')
def plot_monthly_close():
    df, err = load_and_prepare_data()
    if err:
        return err, 404

    # Filter date range
    start_date = pd.Timestamp('2016-11-01')
    end_date = pd.Timestamp('2017-11-30')
    df = df[(df['Date'] >= start_date) & (df['Date'] <= end_date)]

    if df.empty:
        return "No data available for the specified date range.", 404

    if 'Close' not in df.columns:
        return "Column 'Close' not found.", 404

    df['Close'] = pd.to_numeric(df['Close'], errors='coerce')
    df = df.dropna(subset=['Close'])

    monthly_close = df.groupby(pd.Grouper(key='Date', freq='M'))['Close'].mean().reset_index()
    monthly_close = monthly_close.sort_values('Date')

    trace = go.Scatter(
        x=monthly_close['Date'],
        y=monthly_close['Close'],
        mode='lines+markers',
        name='Average Close Price',
        line=dict(color='green')
    )

    layout = go.Layout(
        title='Average Monthly Close Price (Nov 2016 - Nov 2017)',
        xaxis=dict(title='Month'),
        yaxis=dict(title='Average Close Price'),
        margin=dict(l=40, r=40, t=50, b=40)
    )

    fig = go.Figure(data=[trace], layout=layout)
    graph_html = pyo.plot(fig, output_type='div', include_plotlyjs=False)

    template = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Monthly Average Close Price</title>
        <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
        <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css">
        <style>
            body {{
                max-width: 900px;
                margin: 30px auto;
                font-family: Arial, sans-serif;
            }}
            a {{
                display: block;
                margin-bottom: 20px;
                text-align: center;
            }}
        </style>
    </head>
    <body>
        <a href="/">← Back to Data Table</a>
        <h1>Average Monthly Close Price</h1>
        {graph_html}
    </body>
    </html>
    """
    return template

if __name__ == '__main__':
    app.run(debug=True)
