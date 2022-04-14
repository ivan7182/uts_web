######################################################
# Muhamad Shuro Fadhillah   - 19090072 - 6D          #
# Ramadhani Fauzi Azhar     - 19090118 - 6D          #
# Ikhlasul Amal A           - 19090007 - 6B          #
# Muhammad ivan satria      - 19090082 - 6D          #
######################################################


from flask import Flask, request, make_response, jsonify
from flask_restful import Resource, Api
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from functools import wraps
from sqlalchemy import Column, Integer, DateTime, func
from datetime import datetime
from flask_jwt_extended import create_access_token
from flask_jwt_extended import JWTManager
import os


app = Flask(__name__)
jwt = JWTManager(app)
api = Api(app)
db = SQLAlchemy(app)
CORS(app)

filename = os.path.dirname(os.path.abspath(__file__))
database = 'sqlite:///' + os.path.join(filename, 'uts.db')
app.config['SQLALCHEMY_DATABASE_URI'] = database
app.config['SECRET_KEY'] = "Poltek"

# Membuat Model
class users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20))
    password = db.Column(db.String(20))
    created_at= db.Column(db.DateTime(timezone=True),default=func.now())
    token = db.Column(db.String(100))

class event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    event_creator= db.Column(db.String(20))
    event_name= db.Column(db.String(20))
    event_start_time= db.Column(db.String(30)) 
    event_end_time= db.Column(db.String(30))
    event_start_lat= db.Column(db.String(20))
    event_finish_lat= db.Column(db.String(20))
    event_finish_lng= db.Column(db.String(20)) 
    created_at = db.Column(db.DateTime(timezone=True),default=func.now())

class logss(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username= db.Column(db.String(20))
    event_name= db.Column(db.String(20))
    log_lat= db.Column(db.String(20))
    log_lng= db.Column(db.String(20))
    created_at = db.Column(db.DateTime(timezone=True),default=func.now())

db.create_all()

class create(Resource):
    def post(self):
        dataUsername = request.json.get('username', None)
        dataPassword = request.json.get('password', None)

        if dataUsername and dataPassword:

            access_token = create_access_token(identity=dataUsername)
            dataModel = users(username=dataUsername, password=dataPassword, token = access_token)
            db.session.add(dataModel)
            db.session.commit()
            return make_response(jsonify({"msg" : "Registrasi Sukses"}), 200)
        return jsonify({"success" : False,"msg":"Username dan Password harus diisi"})

class Login(Resource):
    def post(self):
        dataUsername = request.json.get('username')
        dataPassword = request.json.get('password')

        queryUsername = [data.username for data in users.query.all()]
        queryPassword = [data.password for data in users.query.all()]
        if dataUsername in queryUsername and dataPassword in queryPassword:
            access_token = create_access_token(identity=dataUsername)
            DB_user = users.query.filter_by(username=dataUsername).first()
            DB_user.token = access_token
            db.session.commit()
            return make_response(jsonify({"msg" : "Login Sukses", "token" : access_token}), 200)
        return jsonify({"success" : False})

class events(Resource):
    def post(self):
        dataToken = request.json.get('token')
        data_event_name = request.json.get('event_name')
        data_event_start_time = str(request.json.get('event_start_time'))
        data_event_end_time = str(request.json.get('event_end_time'))
        data_event_start_lat = request.json.get('event_start_lat')
        data_event_finish_lat = request.json.get('event_finish_lat')
        data_event_finish_lng = request.json.get('event_finish_lng')

        data_event_start_time= datetime.strptime(data_event_start_time, '%Y-%m-%d %H:%M')
        data_event_end_time= datetime.strptime(data_event_end_time, '%Y-%m-%d %H:%M')
        
        queryToken = [data.token for data in users.query.all()]
        if dataToken in queryToken:
            DB_user = users.query.filter_by(token=dataToken).first()
        if data_event_name and data_event_start_time and data_event_end_time and data_event_start_lat and data_event_finish_lat and data_event_finish_lng:
            
            dataModel = event(event_creator=DB_user.username,event_name=data_event_name, event_start_time=data_event_start_time,
            event_end_time=data_event_end_time, event_start_lat=data_event_start_lat, event_finish_lat=data_event_finish_lat,
            event_finish_lng=data_event_finish_lng )
            db.session.add(dataModel)
            db.session.commit()
            return make_response(jsonify({"msg" : "membuat event sukses"}), 200)
        return jsonify({"success" : False,"msg":"Data Tidak Lengkap"})

class log(Resource):
    def post(self):
        dataToken = request.json.get('token')
        data_event_name = request.json.get('event_name')
        data_log_lat = request.json.get('log_lat')
        data_log_lng = request.json.get('log_lng')

        queryToken = [data.token for data in users.query.all()]
        if dataToken in queryToken:
            DB_user = users.query.filter_by(token=dataToken).first()
        if data_event_name and data_log_lat and data_log_lng :
            
            dataModel = logss(username=DB_user.username,event_name=data_event_name,log_lat=data_log_lat,log_lng=data_log_lng )
            db.session.add(dataModel)
            db.session.commit()
            return make_response(jsonify({"msg" : "sukses mencatat posisi terbaru"}), 200)
        return jsonify({"success" : False,"msg":"Data tidak dilengkap"})

class logs(Resource):
    def get(self):
        data_event_name = request.json.get('event_name')

        if data_event_name  :
            query = "SELECT * FROM logss WHERE event_name ='" + data_event_name + "' order by created_at"
            logs = db.engine.execute(query)    

            
            return make_response(jsonify({"hasil":[dict(row) for row in logs]}), 200)
        return jsonify({"success" : False,"msg":"Data tidak dilengkap"})

# Membuat Routes
api.add_resource(create, "/api/v1/users/create", methods=["POST"])
api.add_resource(Login, "/api/v1/users/login", methods=["POST"])
api.add_resource(events, "/api/v1/events/create", methods=["POST"])
api.add_resource(log, "/api/v1/events/logs", methods=["POST"])
api.add_resource(logs, "/api/v1/events/log")


if __name__ == "__main__":
    app.run(host='127.0.0.1', debug=True , port=4000)
