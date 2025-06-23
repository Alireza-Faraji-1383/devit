from rest_framework import status
from rest_framework.response import Response
from .utils.responses import StandardResponse  # کلاس پاسخ استاندارد 
from rest_framework.exceptions import ValidationError

class StandardResponseMixin:

    def finalize_response(self, request, response, *args, **kwargs):

        if isinstance(response.data, dict) and ('data' in response.data or 'errors' in response.data):
             return super().finalize_response(request, response, *args, **kwargs)

        if not status.is_success(response.status_code):
            return super().finalize_response(request, response, *args, **kwargs)


        if response.status_code == status.HTTP_204_NO_CONTENT:
            response.status_code = status.HTTP_200_OK
            response.data = {
                "message": "آیتم با موفقیت حذف شد.",
                "data": None
            }
        else:
            response.data = {
                "message": "عملیات با موفقیت انجام شد.",
                "data": response.data
            }
            
        return super().finalize_response(request, response, *args, **kwargs)

    def handle_exception(self, exc):

        if isinstance(exc, ValidationError):
            return StandardResponse.error(
                message='خطای اعتبارسنجی.',
                errors=exc.detail,
                status=status.HTTP_400_BAD_REQUEST
            )

        return super().handle_exception(exc)