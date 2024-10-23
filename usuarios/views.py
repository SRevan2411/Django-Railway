from django.shortcuts import render
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import UserSerializer
from .serializers import CourseSerializer
from .models import Course
from rest_framework.authtoken.models import Token
from rest_framework.authentication import TokenAuthentication
from django.contrib.auth import authenticate
from rest_framework.permissions import IsAuthenticated
from rest_framework import generics

# Create your views here.

class RegisterView(APIView):
    def post(self,request):
        #Le pasamos los datos del request al serializer
        serializer = UserSerializer(data=request.data)

        #Crear el usuario si los datos son validos
        if serializer.is_valid():
            serializer.save()
            return Response({'message':'Usuario creado exitosamente'}, status = status.HTTP_201_CREATED)
        else:
            #si no son validos devolvemos el error
            return Response({'message':'Creacion de usuario fallida'},status = status.HTTP_400_BAD_REQUEST)
        
class LoginView(APIView):
    def post(self,request):
        email = request.data.get('email')
        password = request.data.get('password')

        #autenticar usuario
        user = authenticate(email=email,password=password)

        if user is not None:
            #Crear el token si se pudo autenticar
            token,created = Token.objects.get_or_create(user=user)
            return Response({'token':token.key,"nickname":user.nickname},status=status.HTTP_200_OK)
        else:
            return Response({'error':'datos invalidos'},status=status.HTTP_400_BAD_REQUEST)
        

class GetUserProfileView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self,request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)
    

class CourseCreateView(generics.CreateAPIView):
    serializer_class = CourseSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)