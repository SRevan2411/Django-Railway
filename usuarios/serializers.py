from rest_framework import serializers, status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .models import User
from .models import Course, Video, Like, History, Comment, TopicRequest
from firebase_admin import storage
from datetime import timedelta
from django.db.models import Count

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only = True) #Evitamos que se retorne este campo al crear el usuario

    #Definir que modelo se va a serializar y que campos se necesitan
    class Meta:
        model = User
        fields = ['id','email','name','nickname','password','Picture','XP','lvl']

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
    nickname = serializers.SerializerMethodField()
    total_likes = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = ['id', 'title', 'subject', 'description','tag', 'user', 'total_likes','nickname']
        read_only_fields = ['user']
    
    def get_total_likes(self, obj):
        # Calcular la suma de likes de todos los videos relacionados con este curso
        return obj.resources.aggregate(total_likes=Count('likes'))['total_likes'] or 0
    def get_nickname(self, obj):
        return obj.user.nickname

class RankingSerializer(serializers.ModelSerializer):
    courses_count = serializers.IntegerField() #como ese campo no es parte del serializador users, se usa esa función para decirle que se espera agregar con un annotate
    class Meta:
        model= User
        fields = ['id','nickname','lvl','XP','courses_count']

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

class LikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Like
        fields = ['id', 'video', 'user', 'created_at']
        read_only_fields = ['user', 'created_at']

class HistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = History
        fields = ['id', 'video', 'user', 'visited_at']
        read_only_fields = ['user', 'visited_at']

#Serializador para comentarios
class CommentSerializer(serializers.ModelSerializer):
    nickname = serializers.SerializerMethodField()
    class Meta:
        model = Comment
        fields = ['id','user','nickname','video','created_at','content']
    def get_nickname(self,obj):
        return obj.user.nickname

#Serializador para las solicitudes de curso o material
class TopicRequestSerializer(serializers.ModelSerializer):
    nickname = serializers.SerializerMethodField()
    class Meta:
        model = TopicRequest
        fields = ['id','user','nickname','created_at','content','subject']

    def get_nickname(self,obj):
        return obj.user.nickname

