import django_filters
from .models import Course

class CourseFilter(django_filters.FilterSet):
    title = django_filters.CharFilter(lookup_expr='icontains')

    class Meta:
        model = Course
        #Aqui se definen los campos de busqueda
        fields = ['title']