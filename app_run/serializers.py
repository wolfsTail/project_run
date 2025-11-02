from rest_framework import serializers
from .models import Run
from django.contrib.auth.models import User



class UserSerializerInner(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'last_name', 'first_name')


class RunSerializer(serializers.ModelSerializer):
    athlete_data = UserSerializerInner(source='athlete', read_only=True)
    class Meta:
        model = Run
        fields = '__all__'


class UserSerializer(serializers.ModelSerializer):
    type = serializers.SerializerMethodField()
    runs_finished = serializers.SerializerMethodField()
    class Meta:
        model = User
        fields = ('id', 'date_joined', 'username', 'last_name', 'first_name', 'type', 'runs_finished')

    def get_type(self, obj):
        return "coach" if obj.is_staff else "athlete"
    
    def get_runs_finished(self, obj):
        annotated = getattr(obj, "runs_finished", None)
        if annotated is not None:
            return annotated
        return obj.runs.filter(status="finished").count()
