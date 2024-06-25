# from flask import Flask
# from flask_sqlalchemy import SQLAlchemy
# from app import ResourceSecondaryInfo, app, db, Resource # Make sure this import is correct and ResourceSecondaryInfo is part of the same SQLAlchemy instance

# # Initialize Flask app
# # app = Flask(__name__)

# # Database configuration
# # app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:root@localhost:5433/ResourseManagementTool_db'
# # app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# # Initialize SQLAlchemy
# # db = SQLAlchemy()
# # db.init_app(app)

# # Define the Employee model

# # Function to check the query
# def check_managers():
#     with app.app_context():
#         # managers = Employee.query.filter_by(position='Account Manager').all()
#         # secondary_info = ResourceSecondaryInfo.query.filter_by(id=34899).first()
#         # print(secondary_info)
#         # if managers:
#         #     print(f"Found {len(managers)} managers with the position 'Account Manager':")
#         #     for manager in managers:
#         #         print(f"ID: {manager.id}, Name: {manager.name}")
#         # else:
#         #     print("No managers with the position 'Account Manager' found.")
#         # resources = Resource.query.filter_by(hiring_manager_id=4).all()
#         # print((resources))
#         # secondary_infos ={}
#         # for i in resources:
#         #     res_info =  ResourceSecondaryInfo.query.filter_by(id = id).first()
#         #     print(res_info)
#         #     secondary_infos = {i.emp_id: ResourceSecondaryInfo.query.filter_by(id=i.emp_id).first()}
#         # print(dict(secondary_infos))
#         resources = Resource.query.filter_by(hiring_manager_id=4).all()
#         secondary_infos = {r.emp_id: ResourceSecondaryInfo.query.filter_by(id=r.emp_id).first() for r in resources}
#         print(resources)
#         print(secondary_infos)
#         for i in secondary_infos:
#             print(i["experience_level"])
# if __name__ == "__main__":
#     with app.app_context():
#         check_managers()
from flask import Flask, render_template, request, redirect, url_for, send_from_directory,jsonify
from werkzeug.utils import secure_filename
import os

from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///your_database.db'  # Replace with your database URI
db = SQLAlchemy(app)


# Define the upload folder
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = 'C:\Users\VahedAb\Desktop\resumeattachement\uploads'

# Function to check if the file extension is allowed
def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Function to create the upload folder if it doesn't exist
def create_upload_folder():
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])

@app.route('/')
def index():
    # Get list of uploaded resumes
    resumes = os.listdir(app.config['UPLOAD_FOLDER'])
    return render_template('index.html', resumes=resumes)

class Upload(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    # Add more fields as needed

    def __repr__(self):
        return f'<Upload {self.id}>'
@app.route('/upload', methods=['POST'])
def upload_resume():
    if request.method == 'POST':
        # Create the upload folder if it doesn't exist
        create_upload_folder()
        
        # Check if the post request has the file part
        if 'file' not in request.files:
            return redirect(request.url)
        
        file = request.files['file']
        
        # If the user does not select a file, the browser should also submit an empty part without filename
        if file.filename == '':
            return redirect(request.url)
        new_upload = Upload(filename=file, filepath=os.path.join(app.config['UPLOAD_FOLDER'], file))
        db.session.add(new_upload)
        db.session.commit()
        
        # If file is allowed and properly uploaded, save it to the upload folder
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return redirect(url_for('index'))
    
    return render_template('index.html', error='Invalid file format or upload failed.')

@app.route('/uploads/<filename>')
def download_resume(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

USER_ROLES = {
    'admin': ['edit', 'view'],
    'user': ['view']
}

resources = {
    1: {'name': 'Resource 1', 'description': 'Description for Resource 1'},
    2: {'name': 'Resource 2', 'description': 'Description for Resource 2'},
    3: {'name': 'Resource 3', 'description': 'Description for Resource 3'},
    4: {'name': 'Resource 4', 'description': 'Description for Resource 4'},
    5: {'name': 'Resource 5', 'description': 'Description for Resource 5'},
    6: {'name': 'Resource 6', 'description': 'Description for Resource 6'},
    7: {'name': 'Resource 7', 'description': 'Description for Resource 7'},
    8: {'name': 'Resource 8', 'description': 'Description for Resource 8'},
    
    # Add more resources as needed
}

def get_resource_from_database(resource_id):
    return resources.get(resource_id)

def update_resource_in_database(resource_id, name, description):
    if resource_id in resources:
        resources[resource_id]['name'] = name
        resources[resource_id]['description'] = description

@app.route('/edit_resource/<int:resource_id>', methods=['GET', 'POST'])
def edit_resource(resource_id):
    # Mock user role (replace this with your actual authentication mechanism)
    user_role = 'admin'  # Example role
    
    # Check if user has permission to edit resources
    if 'edit' not in USER_ROLES.get(user_role, []):
        return "You are not authorized to edit resources."
    
    # Handle form submission
    if request.method == 'POST':
        # Process form data and update resource in the database
        name = request.form['name']
        description = request.form['description']
        update_resource_in_database(resource_id, name, description)
        
        #return redirect(url_for('index'))  # Redirect to the homepage or any other page
        return jsonify(resources)
    #return render_template('index.html', error='Invalid file format or upload failed.')
    
    # Render the edit form
    resource = get_resource_from_database(resource_id)
    if resource:
        resource['id'] = resource_id  # Add the 'id' attribute to the resource dictionary
        return render_template('edit_resource.html', resource_id=resource_id,resource=resource)
    else:
        return "Resource not found."

if __name__ == '__main__':
    app.run(debug=True)
