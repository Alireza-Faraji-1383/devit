from django.core.mail import send_mail
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from .models import PasswordResetCode
import random

def send_activation_email(user, base_url="http://localhost:5173"):
    
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)
    activation_link = f"{base_url}/verified/{uid}/{token}/"

    send_mail(
        subject="فعال‌سازی حساب کاربری",
        message=f"برای فعال‌سازی حساب روی لینک کلیک کنید:\n{activation_link}",
        from_email="no-reply@example.com",
        recipient_list=[user.email],
        fail_silently=False,
    )


def send_reset_code(user):
    code = str(random.randint(100000, 999999))
    PasswordResetCode.objects.create(user=user, code=code)

    send_mail(
        subject="کد بازیابی رمز عبور",
        message=f"کد شما برای تغییر رمز: {code}",
        from_email="no-reply@example.com",
        recipient_list=[user.email],
    )