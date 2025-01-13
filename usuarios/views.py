from django.shortcuts import render
from rest_framework import status
from django.http import Http404
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import UserSerializer, CourseSerializer, ResourceSerializer
from .models import Course, Video, User
from rest_framework.authtoken.models import Token
from rest_framework.authentication import TokenAuthentication
from django.contrib.auth import authenticate
from rest_framework.permissions import IsAuthenticated
from rest_framework import generics
from rest_framework.generics import ListAPIView
from firebase_admin import storage
from datetime import timedelta

# Usuarios --------------------------------------------------------------------------------------

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
    
class UserProfileDetailView(generics.RetrieveAPIView):
    serializer_class = UserSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_object(self):
        # Devuelve directamente el usuario autenticado
        return self.request.user
# Cursos -------------------------------------------------------------------------------------        

class CourseCreateView(generics.CreateAPIView):
    serializer_class = CourseSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class CourseListView(generics.ListAPIView):
    serializer_class = CourseSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Lista los cursos solo del usuario autenticado
        return Course.objects.filter(user=self.request.user)
    
#Listado de todos los cursos sin iniciar sesión
class CourseAllListView(ListAPIView):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = []

#Videos / Recursos ---------------------------------------------------------------------------

class ResourceCreateView(generics.CreateAPIView):
    serializer_class = ResourceSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        course_id = self.kwargs['course_id']  # Obtenemos el curso de la URL
        course = Course.objects.get(id=course_id)  # Asegúrate de tener el curso
        serializer.save(course=course)

class VideoListView(generics.ListAPIView):
    serializer_class = ResourceSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        course_id = self.kwargs['course_id']  # Obtiene el `course_id` de la URL
        return Video.objects.filter(course_id=course_id)
    
class ResourceUpdateView(generics.UpdateAPIView):
    serializer_class = ResourceSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    lookup_field = 'id'

    def get_queryset(self):
        course_id = self.kwargs['course_id']
        return Video.objects.filter(course__id=course_id, course__user=self.request.user)

    def perform_update(self, serializer):
        serializer.save()


class ResourceDeleteView(generics.DestroyAPIView):
    serializer_class = ResourceSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    lookup_field = 'id'

    def get_queryset(self):
        course_id = self.kwargs['course_id']
        return Video.objects.filter(course__id=course_id, course__user=self.request.user)

    def perform_destroy(self, instance):
        instance.delete()