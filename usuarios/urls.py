from django.urls import path
<<<<<<< Updated upstream
from .views import RegisterView,LoginView,GetUserProfileView,CourseCreateView,CourseListView
=======
from .views import RegisterView,LoginView,GetUserProfileView,CourseCreateView,CourseListView, ResourceCreateView, VideoListView, ResourceUpdateView, ResourceDeleteView, UserProfileDetailView
>>>>>>> Stashed changes

urlpatterns = [
    path('register/',RegisterView.as_view(),name='register'),
    path('login/',LoginView.as_view(),name='login'),
    path('profile/',GetUserProfileView.as_view(),name='profile'),
    path('courses/create/', CourseCreateView.as_view(), name='course-create'),  # Crear curso
<<<<<<< Updated upstream
    path('courses/list/', CourseListView.as_view(), name='course-list')
=======
    path('courses/list/', CourseListView.as_view(), name='course-list'),
    
    path('courses/<int:course_id>/videos/upload/', ResourceCreateView.as_view(), name='create_resource'),
    path('courses/<int:course_id>/videos/', VideoListView.as_view(), name='list_videos_by_course'),
>>>>>>> Stashed changes

    path('courses/<int:course_id>/videos/<int:id>/update/', ResourceUpdateView.as_view(), name='update_resource'),
    path('courses/<int:course_id>/videos/<int:id>/delete/', ResourceDeleteView.as_view(), name='delete_resource'),
    path('user/profile/view/', UserProfileDetailView.as_view(), name='user-profile-detail'),

]
