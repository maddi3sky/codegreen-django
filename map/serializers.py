from rest_framework import serializers
from .models import DataPoint, Comment, UserMark


class DataPointSerializer(serializers.ModelSerializer):
    class Meta:
        model = DataPoint
        fields = ['lat', 'lng', 'ndvi']


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['id', 'author', 'text', 'created_at', 'year', 'site_id']
        read_only_fields = ['id', 'created_at']

    def create(self, validated_data):
        request = self.context['request']
        if request.user.is_authenticated:
            validated_data['user'] = request.user
            validated_data['author'] = request.user.get_full_name() or request.user.email
        return super().create(validated_data)


class UserMarkSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserMark
        fields = ['id', 'lat', 'lng', 'label', 'site_id', 'created_at']
        read_only_fields = ['id', 'created_at']
