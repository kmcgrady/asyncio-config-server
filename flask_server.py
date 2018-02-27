from os import environ
from dotenv import load_dotenv, find_dotenv
from flask import Flask, jsonify, abort, request
from jsonschema import validate, ValidationError
from pydash import pick
from pymongo import MongoClient

from config_schema import configuration_get_schema, configuration_post_schema

load_dotenv(find_dotenv())
app = Flask(__name__)
client = MongoClient(environ.get('DATABASE_URI'))
collection = client[environ.get('DATABASE')][environ.get('COLLECTION')]

@app.route('/config', methods=['POST'])
def add_config():
  body = request.json

  try:
    validate(body, configuration_post_schema)
  except ValidationError as ex:
    return abort(400, ex.message)

  query = pick(body, 'tenant', 'integration_type')

  collection.update_one(query, {'$set': body}, upsert=True)

  return jsonify(body)

@app.route('/config', methods=['GET'])
def get_config():
  try:
    validate(request.args, configuration_get_schema)
  except ValidationError as ex:
    return abort(400, ex.message)

  query = pick(request.args, 'tenant', 'integration_type')
  result = collection.find_one(query, {'_id': False})

  if not result:
    return abort(404, 'The configuration you requested could not be found.')

  return jsonify(result)

@app.route('/')
def health_check():
  return 'OK'

if __name__ == '__main__':
  app.run(host='0.0.0.0', port=8000)
