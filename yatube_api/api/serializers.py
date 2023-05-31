import base64

from django.core.files.base import ContentFile
from rest_framework import serializers

import posts.models as models


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
        return super().to_internal_value(data)


class PostSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(slug_field='username',
                                          read_only=True)
    image = Base64ImageField(required=False, allow_null=True)

    class Meta:
        model = models.Post
        fields = '__all__'


class GroupSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Group
        fields = '__all__'


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        read_only=True, slug_field='username'
    )

    class Meta:
        model = models.Comment
        fields = '__all__'
        read_only_fields = ('post', 'author',)


class FollowSerializer(serializers.ModelSerializer):
    user = serializers.SlugRelatedField(
        slug_field='username', default=serializers.CurrentUserDefault(),
        read_only=True)
    following = serializers.SlugRelatedField(
        slug_field='username', queryset=models.User.objects.all(),)

    class Meta:
        model = models.Follow
        validators = [
            serializers.UniqueTogetherValidator(
                queryset=models.Follow.objects.all(),
                fields=('user', 'following'),
                message='Вы уже подписаны.'
            )
        ]
        fields = '__all__'

    def validate_following(self, value):
        if self.context['request'].user == value:
            raise serializers.ValidationError('Нельзя подписаться на себя.')
        return value
