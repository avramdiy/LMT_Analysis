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
        <a href="/volume-monthly">View Average Monthly Volume (11/2016 - 11/2017)</a>
        {}
    </body>
    </html>
    """.format(html_table)
    return template

@app.route('/volume-monthly')
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

if __name__ == '__main__':
    app.run(debug=True)
