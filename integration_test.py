from copy import deepcopy
from json import dumps
from os import environ

from dotenv import load_dotenv, find_dotenv
import pytest
from pydash import pick
from pymongo import MongoClient

from config_schema import sample_config

load_dotenv(find_dotenv())
environ['DATABASE_URI'] = environ.get('TEST_DATABASE_URI')
environ['DATABASE'] = environ.get('TEST_DATABASE')

from sanic_server import app  # pylint: disable=wrong-import-position

client = MongoClient(environ.get('TEST_DATABASE_URI'))
collection = client[environ.get('TEST_DATABASE')][environ.get('COLLECTION')]

@pytest.yield_fixture(autouse=True)
def run_around_tests():
  query = pick(sample_config, 'tenant', 'integration_type')
  collection.delete_one(query)

  yield # Run the test

  collection.delete_one(query)

def test_health_check_returns_200():
  _, response = app.test_client.get('/')
  assert response.status == 200
  assert response.body.decode("utf-8") == 'OK'

def test_post_config():
  query = pick(sample_config, 'tenant', 'integration_type')
  result = collection.find_one(query, {'_id': False})

  assert result is None

  _, response = app.test_client.post('/config', data=dumps(sample_config))
  assert response.status == 200
  print(response)
  assert response.json == sample_config
  result = collection.find_one(query, {'_id': False})

  assert result == sample_config

def test_post_config_bad_request():
  config_copy = deepcopy(sample_config)
  del config_copy['tenant']

  _, response = app.test_client.post('/config', data=dumps(config_copy))
  assert response.status == 400

  config_copy = deepcopy(sample_config)
  del config_copy['integration_type']

  _, response = app.test_client.post('/config', data=dumps(config_copy))
  assert response.status == 400

  config_copy = deepcopy(sample_config)
  del config_copy['configuration']

  _, response = app.test_client.post('/config', data=dumps(config_copy))
  assert response.status == 400

def test_post_config_upsert():
  query = pick(sample_config, 'tenant', 'integration_type')
  collection.update_one(query, {'$set': sample_config}, upsert=True)

  # Update a field that already exists.
  config_copy = deepcopy(sample_config)
  config_copy['configuration']['username'] = 'test_change_user'

  _, response = app.test_client.post('/config', data=dumps(config_copy))

  assert response.status == 200
  assert response.json != sample_config
  assert response.json == config_copy

  result = collection.find_one(query, {'_id': False})

  assert result == config_copy

def test_post_config_upsert_merge():
  query = pick(sample_config, 'tenant', 'integration_type')
  collection.update_one(query, {'$set': sample_config}, upsert=True)
  # Keep original stuff
  config_copy = deepcopy(sample_config)
  config_copy['configuration'] = {
    'notes': 'needs attention'
  }

  _, response = app.test_client.post('/config', data=dumps(config_copy))

  assert response.status == 200
  assert response.json != sample_config
  assert response.json != config_copy

  actual_config = deepcopy(sample_config)
  actual_config['configuration']['notes'] = 'needs attention'

  assert response.json == actual_config

  result = collection.find_one(query, {'_id': False})

  assert result == actual_config

def test_get_config():
  query = pick(sample_config, 'tenant', 'integration_type')
  collection.update_one(query, {'$set': sample_config}, upsert=True)

  uri = '/config?tenant=acme&integration_type=flight-information-system'
  _, response = app.test_client.get(uri)
  assert response.status == 200
  assert response.json == sample_config

def test_get_config_bad_request():
  # invalid tenant parameter name
  uri = '/config?tenan=acme&integration_type=flight-information-system'
  _, response = app.test_client.get(uri)
  assert response.status == 400

  # invalid integration type parameter name
  uri = '/config?tenant=acme&intgration_type=flight-information-system'
  _, response = app.test_client.get(uri)
  assert response.status == 400

  # missing tenant
  uri = '/config?integration_type=flight-information-system'
  _, response = app.test_client.get(uri)
  assert response.status == 400

  # missing integration type
  uri = '/config?tenant=acme'
  _, response = app.test_client.get(uri)
  assert response.status == 400

def test_get_config_not_found():
  # no tenant name
  uri = '/config?tenant=ken&integration_type=flight-information-system'
  _, response = app.test_client.get(uri)
  assert response.status == 404

  # no integration type
  uri = '/config?tenant=acme&integration_type=anvil-system'
  _, response = app.test_client.get(uri)
  assert response.status == 404
