from rest_framework import serializers
from .models import User, Blog, BlogView

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'country']

class BlogSerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(source='author.username', read_only=True)
    
    class Meta:
        model = Blog
        fields = ['id', 'title', 'author', 'author_name', 'created_at']

class BlogViewSerializer(serializers.ModelSerializer):
    blog_title = serializers.CharField(source='blog.title', read_only=True)
    
    class Meta:
        model = BlogView
        fields = ['id', 'blog', 'blog_title', 'viewed_at', 'count']

class BlogViewsAnalyticsSerializer(serializers.Serializer):
    object_type = serializers.ChoiceField(choices=['country', 'user'])
    range = serializers.ChoiceField(choices=['week', 'month', 'year'])

class TopAnalyticsSerializer(serializers.Serializer):
    top = serializers.ChoiceField(choices=['user', 'country', 'blog'])
    time_range = serializers.CharField(required=False)

class PerformanceAnalyticsSerializer(serializers.Serializer):
    compare = serializers.ChoiceField(choices=['day', 'week', 'month', 'year'])
    user_id = serializers.IntegerField(required=False)