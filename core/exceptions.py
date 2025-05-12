from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status

def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is not None:
        detail = response.data.get("detail")
        if detail:
            response.data = {
                "errors": {
                    "detail": detail
                }
            }
        else:
            response.data = {
                "errors": response.data
            }

    return response
