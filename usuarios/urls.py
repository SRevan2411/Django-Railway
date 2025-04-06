from django.urls import path
#from .views import UserHistoryView,RegisterView,LoginView,GetUserProfileView,CourseCreateView,CourseDetails,CourseAllListView,CourseListView, ResourceCreateView, VideoListView, ResourceUpdateView, ResourceDeleteView, UserProfileDetailView, LikeToggleView, VideoLikesCountView, CourseLikesCountView
from .views import *
urlpatterns = [
    #Cosas del usuario
    path('register/',RegisterView.as_view(),name='register'),
    path('login/',LoginView.as_view(),name='login'),
    path('profile/',GetUserProfileView.as_view(),name='profile'),
    path('user/profile/view/', UserProfileDetailView.as_view(), name='user-profile-detail'),
    #Cosas de los cursos
    path('courses/create/', CourseCreateView.as_view(), name='course-create'),  # Crear curso
    path('courses/list/', CourseListView.as_view(), name='course-list'),
    path('courses/user/list', CourseUserListView.as_view(), name='user-course-list'),
    path('courses/<int:course_id>/videos/upload/', ResourceCreateView.as_view(), name='create_resource'),
    path('courses/<int:course_id>/videos/', VideoListView.as_view(), name='list_videos_by_course'),
    path('courses/<int:course_id>/admin/', VideoAdminView.as_view(), name='list_videos_by_course'),
    path('courses/list/all/',CourseAllListView.as_view(),name='course-list-all'),
    path('courses/<int:course_id>/',CourseDetails.as_view(),name='courseDetails'),
    path('courses/<int:course_id>/delete',CourseDeleteView.as_view(),name='CourseDelete'),
    path('courses/<int:course_id>/count',CourseVideoCountView.as_view(),name="CourseVideoCount"),

    path('courses/<int:course_id>/videos/<int:id>/update/', ResourceUpdateView.as_view(), name='update_resource'),
    path('courses/<int:course_id>/videos/<int:id>/delete/', ResourceDeleteView.as_view(), name='delete_resource'),
    
    #Cosas de los videos
    path('videos/<int:video_id>/like/', LikeToggleView.as_view(), name='like-toggle'),
    path('videos/<int:video_id>/likes/count/', VideoLikesCountView.as_view(), name='video-likes-count'),
    path('courses/<int:course_id>/likes/count/', CourseLikesCountView.as_view(), name='course-likes-count'),
    

    #URLS de Historial
    path('history/',UserHistoryGetView.as_view(),name='userHistory'),
    path('add_to_history/', UserHistoryView.as_view(), name='add_to_history'),


    #URLS de Comentarios
    path('videos/<int:video_id>/comments/',CommentListView.as_view(),name='getComments'),
    path('videos/<int:video_id>/comments/create',CommentCreateView.as_view(),name='createComment'),

    #URLS de las solicitudes
    path('topic/request/create',TopicRequestCreateView.as_view(),name='createTopicRequest'),
    path('topic/request/list/all',TopicRequestListView.as_view(),name='getTopicRequests'),
    path('topic/request/<int:topic_id>/delete',TopicRequestDeleteView.as_view(),name='deleteTopicRequest'),
    
]
