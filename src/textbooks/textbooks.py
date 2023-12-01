import random

from core.request_handler import handle_request
from flask import Blueprint, request
from jsonschema import validate


class AlmaServerGateway:


    def queryServer(self, requestData):
        responseData = {}
        for item in requestData:
            responseData[item] = { "count":  random.randrange(0, 10) }
        return responseData

class TopTextbooksProcessor:
  def __init__(self, server=AlmaServerGateway()):
    self.server = server

  textbooks_schema = {
      "type" : "array",
      "items": {
            "type": "string"
            }
  }

  def validate(self, requestJson):
    validate(requestJson, TopTextbooksProcessor.textbooks_schema)

  def process(self, requestData):

      # Using the JSON received from drupal generate get requests to alma
      # Collect the responses back into and collect the count and the
      return self.server.queryServer(requestData)


def construct_processor_endpoint(processor):
  textbooks_endpoint = Blueprint('textbooks', __name__)
  @textbooks_endpoint.route('/textbooks', methods=['GET', 'POST'])
  def textbooks():
      handle_request(request, processor)

  return textbooks_endpoint



