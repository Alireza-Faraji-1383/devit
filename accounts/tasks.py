from celery import shared_task
from .models import User
from .utils import send_activation_email, send_reset_code 

@shared_task
def send_activation_email_task(user_id):
    try:
        user = User.objects.get(pk=user_id)
        send_activation_email(user)
        return f"Activation email for user {user_id} sent."
    except User.DoesNotExist:
        return f"User with id {user_id} not found."

@shared_task
def send_reset_code_task(user_id):
    try:
        user = User.objects.get(pk=user_id)
        send_reset_code(user)
        return f"Reset code for user {user_id} sent."
    except User.DoesNotExist:
        return f"User with id {user_id} not found."