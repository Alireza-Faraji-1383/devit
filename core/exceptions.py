from django.http import Http404
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status

def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if isinstance(exc, Http404):
        return Response({'errors': 'موردی با این مشخصات یافت نشد.'}, status=status.HTTP_404_NOT_FOUND)

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
