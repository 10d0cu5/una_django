from django.db import models

# Create your models here.
from rest_framework import serializers


class User(models.Model):
    user_id = models.TextField(primary_key=True)


class UserSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()


class LogEntry(models.Model):
    log_id = models.AutoField(primary_key=True)
    device = models.TextField(max_length=50,blank=False,null=False)
    device_serial_number = models.TextField(max_length=36,blank=False, null=False)
    device_timestamp = models.DateTimeField(blank=False, null=False)
    device_record_type = models.IntegerField(blank=False, null=False)
    glucose_value = models.IntegerField(blank=False, null=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    # Left out the other values as they didn't add any more value to the entry log
    # Also did not model out other tables like device or glucose values in more detail

    class Meta:
        unique_together = ('device_timestamp', 'user',)


class LogEntrySerializer(serializers.Serializer):
    log_id = serializers.IntegerField()
    device = serializers.CharField()
    device_serial_number = serializers.CharField()
    device_timestamp = serializers.DateTimeField()
    device_record_type = serializers.IntegerField()
    glucose_value = serializers.IntegerField()
    user = serializers.SerializerMethodField('get_user_id')

    def get_user_id(self, obj):
        return obj.user.user_id