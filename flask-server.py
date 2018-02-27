from flask import Flask, jsonify, abort, Response, request
from pymongo import MongoClient

app = Flask(__name__)
mongo_uri = 'mongodb://test:test@ds147668.mlab.com:47668/us_config_test'
collection = MongoClient(mongo_uri).us_config_test.configs

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
