from flask import Flask, render_template_string
import pandas as pd
import os

app = Flask(__name__)

# Path to your file
FILE_PATH = r"C:\Users\avram\OneDrive\Desktop\TRG Week 25\enph.us.txt"

@app.route('/')
def display_table():
    # Verify if the file exists
    if not os.path.exists(FILE_PATH):
        return "File not found. Please check the file path.", 404
    
    try:
        # Load the file, setting the header row to the second row (index 1)
        df = pd.read_csv(FILE_PATH, delimiter=",", header=0)
        
        # Clean column names to handle potential issues like extra spaces
        df.columns = df.columns.str.strip()
        
        # Drop the 'OpenInt' column if it exists
        if 'OpenInt' in df.columns:
            df = df.drop(columns=['OpenInt'])
        else:
            print("Column 'OpenInt' not found. Skipping.")
    except Exception as e:
        return f"Error reading the file: {str(e)}", 500
    
    # Convert the DataFrame to HTML with attributes aligned
    html_table = df.to_html(
        classes='table table-bordered table-hover text-center', 
        index=False, 
        border=0
    )
    
    # HTML template to render
    template = f"""
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
        </style>
        <title>Aligned Data Table</title>
    </head>
    <body>
        <h1>Data Table</h1>
        {html_table}
    </body>
    </html>
    """
    return render_template_string(template)

if __name__ == '__main__':
    app.run(debug=True)
