from rest_framework import serializers


class WhiteBitSerializer(serializers.Serializer):
    method = serializers.CharField()
    id = serializers.CharField()
    params = serializers.JSONField()
