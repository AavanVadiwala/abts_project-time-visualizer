from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS  # Import Flask-CORS
import pandas as pd
import os
import math  # Add this at the top of your file

app = Flask(__name__, static_folder='static')
CORS(app)  # Enable CORS for all routes

# Directory to save uploaded files (optional, for debugging)
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/')
def serve_frontend():
    # Serve the main HTML file
    return send_from_directory(app.static_folder, 'index_frontend.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'myfile' not in request.files:
        print("No file uploaded")
        return jsonify({'error': 'No file uploaded'}), 400

    file = request.files['myfile']

    if file.filename == '':
        print("No file selected")
        return jsonify({'error': 'No file selected'}), 400

    try:
        # Save the file temporarily (optional)
        file_path = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(file_path)
        print(f"File saved at {file_path}")

        # Read the CSV file using pandas
        df = pd.read_csv(file_path)
        print("CSV file read successfully")

        # Ensure required columns exist
        if 'Labels' not in df.columns or 'Time Spent' not in df.columns:
            print("Missing required columns in CSV")
            return jsonify({'error': 'CSV must contain "Labels" and "Time Spent" columns'}), 400

        # Group by 'Labels' and calculate total time spent
        grouped_data = df.groupby('Labels')['Time Spent'].sum().reset_index()
        print("Data grouped successfully")

        # Convert time spent from seconds to hours and round up to the nearest hour
        grouped_data['Time Spent'] = (grouped_data['Time Spent'] / 3600).apply(math.ceil)
        print("Time converted to Hours (rounded up to the nearest hour)")

        # Prepare data for the bar graph
        data = {
            'labels': grouped_data['Labels'].tolist(),
            'values': grouped_data['Time Spent'].tolist()
        }
        print("Data prepared for graph:", data)

        # Return the processed data as JSON
        return jsonify({'message': 'File processed successfully', 'data': data})

    except Exception as e:
        print("Error occurred:", str(e))
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))  # Use PORT from environment, default to 5000
    app.run(host='0.0.0.0', port=port)