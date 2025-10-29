from rest_framework import serializers
from .models import Run


class RunSerializer(serializers.ModelSerializer):
    class Meta:
        mode = Run
        fields = '__all__'
