from django.db import models
from django.contrib.auth.models import User


class SearchHistoryRecord(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
    )
    word = models.CharField(
        max_length=30,
        blank=False,
        null=False,
    )
    count = models.IntegerField(
        default=1,
    )
    last_date = models.DateTimeField(
        auto_now=True,
    )
