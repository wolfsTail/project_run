from rest_framework import serializers
from .models import Challenge, Position, Run, AthleteInfo, CollectibleItem
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


class CollectibleItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CollectibleItem
        fields = ["id", "name", "uid", "latitude", "longitude", "picture", "value"]
        read_only_fields = ["id"]

    def validate_latitude(self, v):
        if v is None or not (-90 <= float(v) <= 90):
            raise serializers.ValidationError("Latitude must be between -90 and 90.")
        return v

    def validate_longitude(self, v):
        if v is None or not (-180 <= float(v) <= 180):
            raise serializers.ValidationError("Longitude must be between -180 and 180.")
        return v


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


class UserDetailSerializer(serializers.ModelSerializer):
    type = serializers.SerializerMethodField()
    runs_finished = serializers.SerializerMethodField()
    items = CollectibleItemSerializer(many=True, read_only=True)
    
    class Meta:
        model = User
        fields = ('id', 'date_joined', 'username', 'last_name', 'first_name', 'type', 'runs_finished', 'items')

    def get_type(self, obj):
        return "coach" if obj.is_staff else "athlete"
    
    def get_runs_finished(self, obj):
        annotated = getattr(obj, "runs_finished", None)
        if annotated is not None:
            return annotated
        return obj.runs.filter(status="finished").count()


class AthleteInfoSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(read_only=True)
    weight = serializers.IntegerField(allow_null=True, required=False)

    class Meta:
        model = AthleteInfo
        fields = ("goals", "weight", "user_id")

    def validate_weight(self, value):
        if value is None:
            return value
        if value <= 0 or value >= 900:
            raise serializers.ValidationError("weight must be in (0, 900).")
        return value


class ChallengeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Challenge
        fields = ("id", "full_name", "athlete", "created_at")
        read_only_fields = fields


class PositionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Position
        fields = ("id", "run", "latitude", "longitude", "created_at")
        read_only_fields = ("id", "created_at")

    def validate_latitude(self, v):
        if v is None or v < -90 or v > 90:
            raise serializers.ValidationError("latitude must be in [-90.0, 90.0]")
        return v

    def validate_longitude(self, v):
        if v is None or v < -180 or v > 180:
            raise serializers.ValidationError("longitude must be in [-180.0, 180.0]")
        return v

    def validate(self, attrs):
        run = attrs.get("run") or getattr(self.instance, "run", None)
        if not isinstance(run, Run):
            raise serializers.ValidationError({"run": "Invalid run"})
        if run.status != "in_progress":
            raise serializers.ValidationError({"run": "Run must be in status 'in_progress'"})
        return attrs
