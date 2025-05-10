from flask import Flask, render_template, request, redirect, url_for, send_from_directory, flash
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'popson_secret_key'

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'zip', 'rar', 'csv', 'tif', 'shp', 'nc'}
ADMIN_PASSWORD = 'admin123'

CATEGORIES = ['remote_sensing', 'gis', 'atmospheric']
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

for category in CATEGORIES:
    os.makedirs(os.path.join(UPLOAD_FOLDER, category), exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/datasets')
def datasets():
    query = request.args.get('q', '').lower()
    data_files = {}
    for category in CATEGORIES:
        folder = os.path.join(app.config['UPLOAD_FOLDER'], category)
        files = os.listdir(folder)
        if query:
            files = [f for f in files if query in f.lower()]
        data_files[category] = files
    return render_template('datasets.html', data_files=data_files, query=query)

@app.route('/download/<category>/<filename>')
def download_file(category, filename):
    return send_from_directory(os.path.join(app.config['UPLOAD_FOLDER'], category), filename, as_attachment=True)

@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        password = request.form.get('password')
        category = request.form.get('category')
        file = request.files.get('file')

        if password != ADMIN_PASSWORD:
            flash('Incorrect password!', 'danger')
            return redirect(url_for('upload_file'))

        if file and allowed_file(file.filename) and category in CATEGORIES:
            filename = secure_filename(file.filename)
            save_path = os.path.join(app.config['UPLOAD_FOLDER'], category, filename)
            file.save(save_path)
            flash('File uploaded successfully!', 'success')
            return redirect(url_for('datasets'))
        else:
            flash('Invalid file or category!', 'warning')
    return render_template('upload.html', categories=CATEGORIES)

@app.route('/contact')
def contact():
    return render_template('contact.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
