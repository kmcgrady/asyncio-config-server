from os import environ
from bson.json_util import dumps
from dotenv import load_dotenv, find_dotenv
from motor.motor_asyncio import AsyncIOMotorClient
from sanic import Sanic
from sanic.exceptions import NotFound
from sanic.response import text, json

load_dotenv(find_dotenv())
app = Sanic()

@app.listener('before_server_start')
def init(application, loop):
  client = AsyncIOMotorClient(environ.get('DATABASE_URI'), io_loop=loop)
  application.collection = client[environ.get('DATABASE')][environ.get('COLLECTION')]

@app.route('/config', methods=['POST'])
async def add_config(request):
  body = request.json
  application = request.app

  await application.collection.update_one({
    'tenant': body['tenant'],
    'integration_type': body['integration_type']
  }, {'$set': body}, upsert=True)

  return json(body)

@app.route('/config', methods=['GET'])
async def get_config(request):
  application = request.app

  result = await application.collection.find_one({
    'tenant': request.raw_args.get('tenant'),
    'integration_type': request.raw_args.get('integration_type')
  }, {'_id': False})

  if not result:
    raise NotFound('The configuration you requested could not be found.')

  return text(dumps(result), headers={'Content-Type': 'application/json'})

@app.route('/')
async def health_check(_request):
  return text('OK')

if __name__ == '__main__':
  app.run(host='0.0.0.0', port=8000)
