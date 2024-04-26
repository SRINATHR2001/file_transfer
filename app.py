from flask import Flask, request, send_from_directory, render_template_string
import os
import time

app = Flask(__name__)

# Define the path to store uploaded files
UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024  # 5 MB limit

# Function to maintain the maximum file count of 2
def manage_files():
    files = os.listdir(app.config['UPLOAD_FOLDER'])
    if len(files) >= 5:
        # Sort by creation time and remove the oldest file if there are more than or exactly 2 files
        files.sort(key=lambda x: os.path.getctime(os.path.join(app.config['UPLOAD_FOLDER'], x)))
        os.remove(os.path.join(app.config['UPLOAD_FOLDER'], files[0]))

@app.route('/', methods=['GET', 'POST'])
def index():
    message = ""
    
    if request.method == 'POST':
        file = request.files['file']
        if file:
            manage_files()  # Make sure there are only 2 files
            
            # Create a unique filename and save the file
            filename = str(time.time()) + "_" + file.filename
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            message = "File uploaded successfully!"

    # Get all stored files
    files = os.listdir(app.config['UPLOAD_FOLDER'])
    # Sort files by creation time (most recent to oldest)
    files.sort(key=lambda x: os.path.getctime(os.path.join(app.config['UPLOAD_FOLDER'], x)), reverse=True)
    
    return render_template_string('''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>File Uploader</title>
        <!-- Include Bootstrap CSS -->
        <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.3.1/css/bootstrap.min.css">
    </head>
    <body>
        <div class="container mt-5">
            <h1>Upload File</h1>
            <form method="post" enctype="multipart/form-data">
                <div class="form-group">
                    <input type="file" name="file" class="form-control-file" required>
                </div>
                <button type="submit" class="btn btn-success">Upload</button>
            </form>
            <div class="mt-3">
                {{ message }}
            </div>
            <div class="mt-3">
                {% for file in files %}
                <a href="/download/{{ file }}" class="btn btn-primary">Download {{ file }}</a>
                {% endfor %}
            </div>
        </div>
    </body>
    </html>
    ''', message=message, files=files)

@app.route('/download/<filename>')
def download_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    app.run(port=5001, debug=True)