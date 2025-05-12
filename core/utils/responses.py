from rest_framework.response import Response
from rest_framework import status

class StandardResponse:
    @staticmethod
    def success(message="", data=None, status_code=status.HTTP_200_OK):
        return Response({
            "message": message,
            "data": data
        }, status=status_code)

    @staticmethod
    def error(message="", errors=None, status_code=status.HTTP_400_BAD_REQUEST):
        return Response({
            "message": message,
            "errors": errors
        }, status=status_code)