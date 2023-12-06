import random

from flask import abort
from jsonschema import ValidationError, validate
from textbooks.core.utils import logger


class AlmaServerGateway:
  def __init__(self, config) -> None:
    # Probably a yaml file
     self.config = config


  def queryServer(self, requestData):
      responseData = {}
      for item in requestData:
          responseData[item] = { "count":  random.randrange(0, 10) }
      return responseData


class TopTextbooksProcessor:
  TEXTBOOKS_SCHEMA = {
      "type" : "array",
      "items": {
            "type": "string"
            }
  }

  def __init__(self, data, server):
    self.data = data
    self.server = server

  def process(self):
      # Validate JSON received from Drupal
      try:
        validate(self.data, self.TEXTBOOKS_SCHEMA)
      except ValidationError as e:
        logger.error(str(e))
        abort(400, "JSON received is not valid.")

      # Process data

      # Send request
      return self.server.queryServer(self.data)
