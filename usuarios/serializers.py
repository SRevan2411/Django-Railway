from rest_framework import serializers
from .models import User
from .models import Course

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only = True) #Evitamos que se retorne este campo al crear el usuario

    #Definir que modelo se va a serializar y que campos se necesitan
    class Meta:
        model = User
        fields = ['email','name','nickname','password']

    #Metodo que se llama cuando el serializer recibe los datos
    def create(self,validated_data):
        user = User.objects.create_user(
            email = validated_data['email'],
            name = validated_data['name'],
            nickname = validated_data['nickname'],
            password = validated_data['password']
        )
        return user
    

class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ['id', 'title', 'subject', 'description', 'user']
        read_only_fields = ['user']