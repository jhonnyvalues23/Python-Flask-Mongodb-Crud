from flask import Flask, jsonify, request
import pymongo
from bson.json_util import dumps
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash

from flask_jwt_extended import create_access_token
from flask_jwt_extended import jwt_required
from flask_jwt_extended import JWTManager


connection_url = 'mongodb+srv://database:database@cluster0.sk6ftrt.mongodb.net/?retryWrites=true&w=majority'

app = Flask(__name__)
app.config["JWT_SECRET_KEY"] = "super-secret"
client = pymongo.MongoClient(connection_url)
jwt = JWTManager(app)
Database = client.get_database('Example')
SampleTable = Database.SampleTable
Templates = Database.Templates


@app.route('/register/', methods=['POST'])
def register():
    _json = request.json
    _fname = _json['first_name']
    _lname = _json['last_name']
    _email = _json['email']
    _password = _json['password']

    if _fname and _lname and _email and _password and request.method == 'POST':
        _hashed_password = generate_password_hash(_password)
        id = SampleTable.insert_one({'first_name': _fname, 'last_name': _lname, 'email': _email, 'password': _hashed_password})
        resp = jsonify('User added successfully!')
        resp.status_code = 200
        return resp
    
    else:
        return not_found()


@app.route('/login/', methods=['POST'])
def login():
    _json = request.json
    _email = _json['email']
    _password = _json['password']

    if _email and _password and request.method == 'POST':

        user = SampleTable.find_one({'email': _email})
        if user:
            if check_password_hash(user['password'], _password):
                # token = jwt.encode({'email': user['email'], 'exp' : datetime.datetime.utcnow() + datetime.timedelta(minutes=30)}, app.config['SECRET_KEY'])
                # return jsonify({'token' : token})
                access_token = create_access_token(identity=_email)
                return jsonify(access_token=access_token)
            else:
                resp = jsonify('Wrong password!')
                resp.status_code = 200
                return resp
        else:
            resp = jsonify('User not found!')
            resp.status_code = 200
            return resp

    else:
        return not_found()

@app.route('/template/', methods=['GET','POST'])
@jwt_required()
def template():
    if request.method == 'GET':
        templates = Templates.find()
        resp = dumps(templates)
        return resp
    _json = request.json
    _template_name = _json['template_name']
    _subject = _json['subject']
    _body = _json['body']

    if _template_name and _subject and _body and request.method == 'POST':
        id = Templates.insert_one({'template_name': _template_name, 'subject': _subject, 'body': _body})
        resp = jsonify('Template added successfully!')
        resp.status_code = 200
        return resp
    
    else:
        return not_found()

@app.route('/template/<template_id>/', methods=['GET','PUT','DELETE'])
@jwt_required()
def template_id(template_id):
    if request.method == 'GET':
        template = Templates.find_one({'_id': ObjectId(template_id)})
        resp = dumps(template)
        return resp

    elif request.method == 'PUT':
        _json = request.json
        _template_name = _json['template_name']
        _subject = _json['subject']
        _body = _json['body']

        if _template_name and _subject and _body and request.method == 'PUT':
            Templates.update_one({'_id': ObjectId(template_id)}, {'$set': {'template_name': _template_name, 'subject': _subject, 'body': _body}})
            resp = jsonify('Template updated successfully!')
            resp.status_code = 200
            return resp

    elif request.method == 'DELETE':
        Templates.delete_one({'_id': ObjectId(template_id)})
        resp = jsonify('Template deleted successfully!')
        resp.status_code = 200
        return resp

    else:
        return not_found()


@app.errorhandler(404)
def not_found(error=None):
    message = {
        'status': 404,
        'message': 'Not Found' + request.url
    }
    resp = jsonify(message)
    resp.status_code = 404

    return resp



if __name__ == '__main__':
    app.run(debug=True)