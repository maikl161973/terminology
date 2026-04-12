from rest_framework import serializers
from .models import RefBook, Version, Element


class RefBookSerializer(serializers.ModelSerializer):
    class Meta:
        model = RefBook
        fields = ('id', 'code', 'name')


class ElementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Element
        fields = ('code', 'value')


class VersionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Version
        fields = ('version', 'start_date')