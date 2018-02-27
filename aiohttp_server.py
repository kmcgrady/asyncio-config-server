from os import environ

from aiohttp import web
from dotenv import load_dotenv, find_dotenv
from jsonschema import validate, ValidationError
from motor.motor_asyncio import AsyncIOMotorClient
from pydash import pick

from config_schema import configuration_get_schema, configuration_post_schema

load_dotenv(find_dotenv())

async def init_db(application):
  loop = application.loop
  client = AsyncIOMotorClient(environ.get('DATABASE_URI'), io_loop=loop)
  database_name = environ.get('DATABASE')
  collection_name = environ.get('COLLECTION')
  application['collection'] = client[database_name][collection_name]

async def health_check(_request):
  return web.Response(text='OK')

async def add_config(request):
  body = await request.json()

  try:
    validate(body, configuration_post_schema)
  except ValidationError as ex:
    return web.Response(status=400, text=ex.message)

  query = pick(body, 'tenant', 'integration_type')
  collection = request.app['collection']
  await collection.update_one(query, {'$set': body}, upsert=True)

  return web.json_response(body)

async def get_config(request):
  try:
    validate(request.query, configuration_get_schema)
  except ValidationError as ex:
    return web.Response(status=400, text=ex.message)

  query = pick(request.query, 'tenant', 'integration_type')
  result = await request.app['collection'].find_one(query, {'_id': False})

  if not result:
    message = 'The configuration you requested could not be found.'
    return web.Response(status=404, text=message)

  return web.json_response(result)

app = web.Application()
app.on_startup.append(init_db)
app.router.add_get('/', health_check)
app.router.add_get('/config', get_config)
app.router.add_post('/config', add_config)

web.run_app(app, port=8000)
