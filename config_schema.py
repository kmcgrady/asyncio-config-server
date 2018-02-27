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
