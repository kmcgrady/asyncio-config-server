from dotenv import load_dotenv, find_dotenv
from flask import Flask, jsonify, abort, Response, request
from pymongo import MongoClient
from os import environ

load_dotenv(find_dotenv())
app = Flask(__name__)
client = MongoClient(environ.get('DATABASE_URI'))
collection = client[environ.get('DATABASE')][environ.get('COLLECTION')]

@app.route('/config', methods=['POST'])
def add_config():
  body = request.json

  collection.update_one({
    'tenant': body['tenant'],
    'integration_type': body['integration_type']
  }, {'$set': body}, upsert=True)

  return jsonify(body)

@app.route('/config', methods=['GET'])
def get_config():
  result = collection.find_one({
    'tenant': request.args.get('tenant'),
    'integration_type': request.args.get('integration_type')
  }, {'_id': False})

  if not result:
    return abort(404, 'The configuration you requested could not be found.')

  return jsonify(result)

@app.route('/')
def health_check():
  return 'OK'

if __name__ == '__main__':
  app.run(host='0.0.0.0', port=8000)
