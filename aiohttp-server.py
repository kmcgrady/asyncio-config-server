from aiohttp import web
from bson.json_util import dumps
from motor.motor_asyncio import AsyncIOMotorClient

async def init_db(app):
  mongo_uri = 'mongodb://test:test@ds147668.mlab.com:47668/us_config_test'
  collection = AsyncIOMotorClient(mongo_uri, io_loop=app.loop).us_config_test.configs
  app['collection'] = collection

async def health_check(request):
  return web.Response(text='OK')

async def add_config(request):
  body = await request.json()

  await request.app['collection'].update_one({
    'tenant': body['tenant'],
    'integration_type': body['integration_type']
  }, {'$set': body}, upsert=True)

  return web.json_response(body)

async def get_config(request):
  result = await request.app['collection'].find_one({
    'tenant': request.query.get('tenant'),
    'integration_type': request.query.get('integration_type')
  }, {'_id': False})

  if not result:
    return web.Response(status=404, text='The configuration you requested could not be found.')

  return web.json_response(result)



app = web.Application()
app.on_startup.append(init_db)
app.router.add_get('/', health_check)
app.router.add_get('/config', get_config)
app.router.add_post('/config', add_config)

web.run_app(app, port=8000)