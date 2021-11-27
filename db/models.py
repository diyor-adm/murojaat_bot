import sys

try:
    from django.db import models
except Exception:
    print('Exception: Django Not Found, please install it with "pip install django".')
    sys.exit()


class Appeal(models.Model):
    first_name = models.CharField(max_length=256)
    last_name = models.CharField(max_length=256)
    region = models.CharField(max_length=256)
    address = models.CharField(max_length=256)
    phone_number = models.CharField(max_length=64)
    appeal = models.TextField()
    user_id = models.PositiveIntegerField()
