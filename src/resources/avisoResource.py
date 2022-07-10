import json
from bson import ObjectId
from flask import request
from database.model import Aviso
from flask_restful import Resource
from paho.mqtt import client as mqtt_client
from .validators import AvisoValidator, AvisoFiltroValidator

client_mqtt = None

class AvisoSave(Resource):
    @AvisoValidator
    def post(self):
        try:
            body = request.get_json()
            if 'id' in body.keys():
                objects = Aviso.objects(id=ObjectId(body['id']))
                if len(objects) == 0:
                    return {'message': 'Aviso não encontrado.', 'id':str(body['id'])}, 400
                id = body['id'] 
                del body['id']
                body = Aviso.findRegiao(body)
                objects.update_one(**body)
                self.mqqt_client.publish('avisos', payload=json.dumps(body))
                return {'message': 'Aviso editado com sucesso.', 'id':str(id)}, 200
            else:
                aviso = Aviso(**Aviso.ws2document(body)).save()
                id = aviso.id
                self.mqqt_client.publish('avisos', payload=json.dumps(aviso))
                return {'message': 'Aviso salvo com sucesso.', 'id':str(id)}, 200
        except Exception as e:
            return {'message': 'Erro ao salvar aviso - ' + str(e)}, 500

class AvisoList(Resource):
    @AvisoFiltroValidator
    def post(self):
        try:
            body = request.get_json()
            return {"resultado": Aviso.list(body)}, 200
        except Exception as e:
            return {'message': 'Erro ao listar avisos - ' + str(e)}, 500
        

def connect_mqtt(client_id, username, password, broker, port):
    global client_mqtt
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!")
        else:
            print("Failed to connect, return code %d\n", rc)
    # Set Connecting Client ID
    client = mqtt_client.Client(client_id)
    client.username_pw_set(username, password)
    client.on_connect = on_connect
    client.connect(broker, port)
    client_mqtt = client