from rest_framework import serializers, status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .models import User
from .models import Course, Video
from firebase_admin import storage
from datetime import timedelta

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only = True) #Evitamos que se retorne este campo al crear el usuario

    #Definir que modelo se va a serializar y que campos se necesitan
    class Meta:
        model = User
        fields = ['email','name','nickname','password','Picture']

    #Metodo que se llama cuando el serializer recibe los datos
    def create(self,validated_data):
        user = User.objects.create_user(
            email = validated_data['email'],
            name = validated_data['name'],
            nickname = validated_data['nickname'],
            password = validated_data['password'],
            Picture = validated_data.get('Picture','')
        )
        return user
    

class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ['id', 'title', 'subject', 'description', 'user']
        read_only_fields = ['user']

class ResourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Video
        fields = ['id', 'title', 'video_url', 'course', 'uploaded_at', 'description']
        read_only_fields = ['course', 'uploaded_at']

    def get_fields(self):
        fields = super().get_fields()
        if self.context['request'].method in ['PUT', 'PATCH']:
            # Hacer `video_url` de solo lectura para las solicitudes de edición
            fields['video_url'].read_only = True
        return fields