from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db import models
from django.utils import timezone

# Create your models here.

#Clase user manager (contiene metodos utiles como cifrado de password)
class UserManager(BaseUserManager):
    #password=None, usamos esto en caso de que el usuario pase a inactivo
    def create_user(self,name,nickname,email, Picture, XP=0, lvl=0, password = None):
        if not email:
            raise ValueError("User must have an email")
        if not name:
            raise ValueError("User must have a name")
        if not Picture:
            None
        user = self.model(
            email = self.normalize_email(email), #Normalizar = ExaMple@mail.com -> example@mail.com
            name = name,
            nickname = nickname,
            XP = XP,
            lvl = lvl,
            Picture = Picture,
        )
        #usamos un metodo para que se cifre el password
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    #Clase para super usuarios
    def create_superuser(self,name,email,password=None):
        user = self.create_user(name,name,email,'Defaulturl', XP=0, lvl=1,password=password)
        user.is_admin = True
        user.is_staff = True  # Importante para acceder al panel de administración
        user.is_superuser = True  # Otorga permisos de superusuario
        user.save(using = self._db)
        return user
    
#Definicion del modelo, heredamos de la clase usuario por defecto de django
class User(AbstractBaseUser):
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=100)
    nickname = models.CharField(max_length=100,unique=True)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    XP = models.IntegerField(default = 0)
    lvl = models.IntegerField(default = 0)
    Picture=models.URLField(max_length=500, blank=True, null=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']


    def __str__(self):
        return self.email
    def has_perm(self, perm, obj=None):
        """Indica si el usuario tiene un permiso específico."""
        return True

    def has_module_perms(self, app_label):
        """Indica si el usuario tiene permisos para ver una app específica."""
        return True
    
    #Metodos relacionados con la xp y el nivel del usuario
    def update_xp(self,cantidad):
        self.XP += cantidad
        niveles_subidos = self.XP // 100
        self.XP = self.XP % 100
        self.lvl += niveles_subidos
        self.save(update_fields=['XP','lvl'])

    

    
#Modelo correspondiente para la tabla de los cursos
class Course(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Relación con el usuario
    title = models.CharField(max_length=255)
    subject = models.CharField(max_length=100) #Tema
    description = models.TextField()
    tag = models.CharField(max_length=100)

    def __str__(self):
        return self.title

#Modelo correspondiente para la tabla de los recursos (videos del curso)   
class Video(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='resources') #Relacion con el curso
    title = models.CharField(max_length=255)
    description = models.TextField()
    video_url = models.URLField()
    uploaded_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.title

#Modelo correspondiente para la tabla Likes (lIKES del curso)
class Like(models.Model):
    video = models.ForeignKey(Video, on_delete=models.CASCADE, related_name="likes")
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = ('video', 'user')  # Garantiza que un usuario no dé más de un like a un video

    def __str__(self):
        return f"Like by {self.user.email} on {self.video.title}"

#Modelo correspondiente para la tabla historial (historial del usuario)
class History(models.Model):
    video = models.ForeignKey(Video,on_delete=models.CASCADE, related_name="history")
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    visited_at = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = ('video', 'user') #solo registramos una sola vez el video al historial

    def __str__(self):
        return f"Video {self.video.title} was visited by {self.user.email}"
    
#Modelo utilizado para los comentarios

class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    video = models.ForeignKey(Video, on_delete=models.CASCADE)
    created_at = models.DateTimeField(default=timezone.now)
    content = models.TextField()

    class Meta:
        ordering = ['created_at']
    
#Modelo utilizado para las solicitudes de curso o material
class TopicRequest(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(default=timezone.now)
    subject = models.CharField(max_length=100) #Tema
    content = models.TextField()

    class Meta:
        ordering = ['created_at']