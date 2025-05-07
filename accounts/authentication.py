from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.exceptions import AuthenticationFailed

class JWTAuthenticateCookie(JWTAuthentication):
    def authenticate(self, request):
        access_token = request.COOKIES.get("access_token")

        if access_token is None:
            return None  

        try:
            validated_token = self.get_validated_token(access_token)
            return self.get_user(validated_token), validated_token
        except Exception:
            raise AuthenticationFailed("Invalid or expired token in cookie.")
