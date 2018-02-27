from os import environ

from bson.json_util import dumps
from dotenv import load_dotenv, find_dotenv
from jsonschema import validate, ValidationError
from motor.motor_asyncio import AsyncIOMotorClient
from pydash import pick
from sanic import Sanic
from sanic.exceptions import NotFound, InvalidUsage
from sanic.response import text, json

from config_schema import configuration_get_schema, configuration_post_schema

load_dotenv(find_dotenv())
app = Sanic()

@app.listener('before_server_start')
def init(application, loop):
  client = AsyncIOMotorClient(environ.get('DATABASE_URI'), io_loop=loop)
  database_name = environ.get('DATABASE')
  collection_name = environ.get('COLLECTION')
  application.collection = client[database_name][collection_name]

@app.route('/config', methods=['POST'])
async def add_config(request):
  body = request.json
  try:
    validate(body, configuration_post_schema)
  except ValidationError as ex:
    raise InvalidUsage(ex.message)

  application = request.app
  query = pick(body, 'tenant', 'integration_type')

  await application.collection.update_one(query, {'$set': body}, upsert=True)

  return json(body)

@app.route('/config', methods=['GET'])
async def get_config(request):
  application = request.app

  try:
    validate(request.raw_args, configuration_get_schema)
  except ValidationError as ex:
    raise InvalidUsage(ex.message)

  query = pick(request.raw_args, 'tenant', 'integration_type')

  result = await application.collection.find_one(query, {'_id': False})

  if not result:
    raise NotFound('The configuration you requested could not be found.')

  return text(dumps(result), headers={'Content-Type': 'application/json'})

@app.route('/')
async def health_check(_request):
  return text('OK')

if __name__ == '__main__':
  app.run(host='0.0.0.0', port=8000)
