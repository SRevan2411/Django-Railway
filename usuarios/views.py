from django.shortcuts import render
from rest_framework import status
from django.http import Http404
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import UserSerializer, CourseSerializer, ResourceSerializer, LikeSerializer, HistorySerializer
from .filters import CourseFilter
from .models import Course, Video, User, Like, History
from rest_framework.authtoken.models import Token
from rest_framework.authentication import TokenAuthentication
from django.contrib.auth import authenticate
from rest_framework.permissions import IsAuthenticated
from rest_framework import generics
from rest_framework.generics import ListAPIView
from firebase_admin import storage
from datetime import timedelta
from django_filters.rest_framework import DjangoFilterBackend

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

    def get(self, request):
        courses = Course.objects.all()

        data = [
            {
                "id": course.id,
                "title": course.title,
                "description": course.description,
                "total_likes": Like.objects.filter(video__course=course).count(),
            }
            for course in courses
        ]

        return Response(data, status=200)
    
#Listado de todos los cursos sin iniciar sesión
class CourseAllListView(ListAPIView):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = CourseFilter
    permission_classes = []

#Retorna la información del curso por ID, junto a sus videos
class CourseDetails(ListAPIView):
    def get(self,request,course_id):
        try:
            #si el id hace match obtenemos el objeto
            course = Course.objects.get(id = course_id)
        except Course.DoesNotExist:
            #si no, devolvemos un error
            return Response(
                {"error": "Course not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        #serializamos el objeto (convierte el object a formato JSON)
        course_serializer = CourseSerializer(course)
        #Obtenemos los recursos
        resources = Video.objects.filter(course = course)
        #Serializamos los recursos
        resources_serializer = ResourceSerializer(resources, many=True, context={"request": request})
        #Encapsulamos los datos
        data = {
            "course": course_serializer.data,
            "resource": resources_serializer.data
        }
        #retornamos los datos
        return Response(data, status=status.HTTP_200_OK)

        

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

    def get(self, request, course_id):
        videos = Video.objects.filter(course_id=course_id)
        user = request.user

        # Construimos la respuesta con el estado 'liked' para cada video
        data = [
            {
                "id": video.id,
                "title": video.title,
                "description": video.description,
                "liked": Like.objects.filter(video=video, user=user).exists(),
                "uploaded_at": video.uploaded_at,
                "video_url": video.video_url,
            }
            for video in videos
        ]
        return Response(data, status=200)
    
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

#SISTEMA DE LIKES
class LikeToggleView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, video_id):
        try:
            # Buscar o crear el like para el usuario y el video especificado
            video = Video.objects.get(id=video_id)
            like, created = Like.objects.get_or_create(video=video, user=request.user)

            if not created:  # Si el like ya existía, lo eliminamos
                like.delete()
                return Response({"message": "Like removed", "liked": False}, status=status.HTTP_200_OK)

            # Si se creó un nuevo like, devolvemos una respuesta
            return Response({"message": "Like added", "liked": True}, status=status.HTTP_201_CREATED)

        except Video.DoesNotExist:
            return Response({"error": "Video no encontrado"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    def delete(self, request, video_id):
        try:
            # Verificar si el like existe
            like = Like.objects.get(video_id=video_id, user=request.user)
            like.delete()  # Eliminar el like

            return Response({"message": "Like removed"}, status=200)

        except Like.DoesNotExist:
            return Response({"error": "Like not found"}, status=404)
        except Exception as e:
            return Response({"error": str(e)}, status=500)

class VideoLikesCountView(APIView):
    def get(self, request, video_id):
        try:
            # Verifica si el video existe
            video = Video.objects.get(id=video_id)
            
            # Cuenta los likes relacionados con el video
            total_likes = Like.objects.filter(video=video).count()
            
            return Response({"video_id": video.id, "total_likes": total_likes}, status=status.HTTP_200_OK)

        except Video.DoesNotExist:
            return Response({"error": "Video not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CourseLikesCountView(APIView):
    def get(self, request, course_id):
        try:
            # Verifica si el curso existe
            course = Course.objects.get(id=course_id)
            
            # Filtra los likes de los videos asociados al curso
            total_likes = Like.objects.filter(video__course=course).count()
            
            return Response({"course_id": course.id, "total_likes": total_likes}, status=status.HTTP_200_OK)

        except Course.DoesNotExist:
            return Response({"error": "Course not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class UserVideoLikesView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Obtener los IDs de videos desde el query params
        video_ids = request.query_params.getlist('video_ids')

        # Obtener los likes del usuario autenticado
        user_likes = Like.objects.filter(user=request.user, video_id__in=video_ids).values_list('video_id', flat=True)

        # Formatear la respuesta indicando si hay like o no
        response_data = {video_id: video_id in user_likes for video_id in map(int, video_ids)}
        
        return Response(response_data, status=200)
    

#SISTEMA DE HISTORIAL
class UserHistoryView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        #serializamos los datos
        serializer = HistorySerializer(data=request.data)
        
        if serializer.is_valid():
            video_id = serializer.validated_data['video']
            try:
                # Checar si el video existe
                video = Video.objects.get(id=video_id.id)

                # usar get or create para ver si ya existe la entrada al historial
                history_entry, created = History.objects.get_or_create(video=video,user=request.user)

                if created:
                    # Serializar el objeto creado para devolverlo como respuesta
                    response_serializer = HistorySerializer(history_entry)
                    return Response(response_serializer.data, status=status.HTTP_201_CREATED)
                else:
                    return Response(
                        {"message": "Video already in history"}, status=status.HTTP_200_OK
                    )
            except Video.DoesNotExist:
                return Response({"error": "Video not found"}, status=status.HTTP_404_NOT_FOUND)
        else:
            return Response({"error":"bad request"},status=status.HTTP_400_BAD_REQUEST)
        
