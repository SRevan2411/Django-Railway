from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db import models

# Create your models here.

#Clase user manager (contiene metodos utiles como cifrado de password)
class UserManager(BaseUserManager):
    #password=None, usamos esto en caso de que el usuario pase a inactivo
    def create_user(self,name,nickname,email,password = None):
        if not email:
            raise ValueError("User must have an email")
        if not name:
            raise ValueError("User must have a name")
        user = self.model(
            email = self.normalize_email(email), #Normalizar = ExaMple@mail.com -> example@mail.com
            name = name,
            nickname = nickname
           
        )
        #usamos un metodo para que se cifre el password
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    #Clase para super usuarios
    def create_superuser(self,name,nickname,email,password=None):
        user = self.create_user(name,nickname,email,password)
        user.is_admin = True
        user.save(using = self._db)
        return user
    
#Definicion del modelo, heredamos de la clase usuario por defecto de django
class User(AbstractBaseUser):
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=100)
    nickname = models.CharField(max_length=100,unique=True)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']

    def __str__(self):
        return self.email
    

