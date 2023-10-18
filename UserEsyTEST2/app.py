from flask import Flask, render_template, request,  redirect, jsonify
from flask_sqlalchemy import SQLAlchemy
import os
from flask import send_from_directory

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'static/store_image'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}

db = SQLAlchemy(app)

# Define the database model
class Record(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    status = db.Column(db.String(20))
    name_image1 = db.Column(db.String(100))
    name_image2 = db.Column(db.String(100))

    def __init__(self, id, status, name_image1, name_image2):
        self.id = id
        self.status = status
        self.name_image1 = name_image1
        self.name_image2 = name_image2

@app.route('/')
def index():
    return render_template('index.html')

# Function to check if the file extension is allowed
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

# Home page route
@app.route('/add')
def home():
    return render_template('upload_page.html')

# Database route
@app.route('/database', methods=['POST'])
def database():
    # Get data from the request
    id = request.form['id']
    status = request.form['status']
    image1 = request.files['image1']
    image2 = request.files['image2']

    print(status)

    # Save the images to the store_image folder
    if image1 and allowed_file(image1.filename):
        filename1 = '{}_face.{}'.format(id, image1.filename.rsplit('.', 1)[1].lower())
        image1.save(os.path.join(app.config['UPLOAD_FOLDER'], filename1))
    if image2 and allowed_file(image2.filename):
        filename2 = '{}_card.{}'.format(id, image2.filename.rsplit('.', 1)[1].lower())
        image2.save(os.path.join(app.config['UPLOAD_FOLDER'], filename2))
    print(filename1, filename2)
    # Save the data to the database
    record = Record(id=id, status=status, name_image1=filename1, name_image2=filename2)
    db.session.add(record)
    db.session.commit()

    return 'Data saved successfully.'

@app.route('/static/store_image/<path:filename>')
def serve_image(filename):
    return send_from_directory(app.static_folder, f'store_image/{filename}')

@app.route('/log')
def show():
    entries = Record.query.all()
    return render_template('show.html', entries=entries)

@app.route('/delete_all', methods=['POST'])
def delete_all():
    # Delete all records from the database
    db.session.query(Record).delete()
    db.session.commit()
    
    # Delete all images from the store_image folder
    filelist = os.listdir(app.config['UPLOAD_FOLDER'])
    for filename in filelist:
        os.remove(os.path.join(app.config['UPLOAD_FOLDER'], filename))

    return redirect('/log')

@app.route('/data', methods=['GET'])
def get_data():
    entries = Record.query.all()
    data = []
    for entry in entries:
        data.append({
            'id': entry.id,
            'status': entry.status,
            'name_image1': entry.name_image1,
            'name_image2': entry.name_image2
        })
    return jsonify(data)


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run()