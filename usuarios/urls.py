from django.urls import path
from .views import RegisterView,LoginView,GetUserProfileView,CourseCreateView,CourseListView

urlpatterns = [
    path('register/',RegisterView.as_view(),name='register'),
    path('login/',LoginView.as_view(),name='login'),
    path('profile/',GetUserProfileView.as_view(),name='profile'),
    path('courses/create/', CourseCreateView.as_view(), name='course-create'),  # Crear curso
    path('courses/list/', CourseListView.as_view(), name='course-list')


]
