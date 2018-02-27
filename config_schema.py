configuration_post_schema = {
  'type': 'object',
  'properties': {
    'tenant': {'type': 'string'},
    'integration_type': {'type': 'string'},
    'configuration': {'type': 'object'}
  },
  'required': ['tenant', 'integration_type', 'configuration']
}

configuration_get_schema = {
  'type': 'object',
  'properties': {
    'tenant': {'type': 'string'},
    'integration_type': {'type': 'string'}
  },
  'required': ['tenant', 'integration_type']
}

sample_config = {
  "tenant": "acme",
  "integration_type": "flight-information-system",
  "configuration": {
    "username": "acme_user",
    "password": "acme54321",
    "wsdl_urls": {
      "session_url": "https://session.manager.svc",
      "booking_url": "https://booking.manager.svc"
    }
  }
}
