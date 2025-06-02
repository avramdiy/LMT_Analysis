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
    
    # Read the file into a Pandas DataFrame
    try:
        # Adjust the delimiter to match your file structure (e.g., '\t' for tab-separated data)
        df = pd.read_csv(FILE_PATH, delimiter="\t")
    except Exception as e:
        return f"Error reading the file: {str(e)}", 500
    
    # Convert the DataFrame to HTML with attributes aligned
    # This includes adding classes for styling and ensuring the table is structured clearly
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
