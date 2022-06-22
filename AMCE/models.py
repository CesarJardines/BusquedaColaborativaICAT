from django.db import models
#se importan el modelo Usuario que viene por defecto en Django
from django.contrib.auth.models import User
from django.contrib.auth.models import AbstractUser
#se importa la zona horaria 
from django.utils import timezone 

class User(AbstractUser):
	es_estudiante = models.BooleanField(default=False)
	es_profesor = models.BooleanField(default=False)

	def __str__(self):
		return '{} {}'.format(self.last_name, self.first_name)

class Profesor(models.Model):
	user_profesor = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)

class Grupo(models.Model):
	id_grupo = models.CharField(max_length=10, primary_key=True)
	nombre_grupo = models.CharField(max_length=100)
	materia = models.CharField(max_length=100, null=True, blank=True)
	institucion = models.CharField(max_length=100, null=True, blank=True)

	profesor_grupo = models.ForeignKey(Profesor, on_delete=models.CASCADE)

	def __str__(self):
		return f'Nombre: {self.nombre_grupo} Código:{self.id_grupo}'

class Estudiante(models.Model):
	user_estudiante = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
	grupos_inscritos = models.ManyToManyField(Grupo, blank=True)

	def __str__(self):
		user = User.objects.get(id=self.user_estudiante.id)
		return '{} {}'.format(user.last_name, user.first_name)

class Tema(models.Model):
	id_tema = models.AutoField(primary_key=True)
	nombre_tema = models.CharField(max_length=100)
	#Borrar preguntas_secundarias ya que se define en definirProblema
	preguntas_secundarias = models.IntegerField(default=1)

	profesor_tema = models.ForeignKey(Profesor, on_delete=models.CASCADE)

class Equipo(models.Model):
	id_equipo = models.AutoField(primary_key=True)
	nombre_equipo = models.CharField(max_length=100)

	grupo_equipo = models.ForeignKey(Grupo, on_delete=models.CASCADE)
	estudiantes = models.ManyToManyField(Estudiante, blank=True)
	temas_asignados = models.ManyToManyField(Tema, blank=True)

class DefinirProblema(models.Model):
	id_definirProb = models.AutoField(primary_key=True)
	preguntas_secundarias = models.IntegerField(default=1)
	fuentes = models.IntegerField(default=1)

	equipo_definirProb = models.ForeignKey(Equipo, on_delete=models.CASCADE)
	tema_definirProb = models.ForeignKey(Tema, on_delete=models.CASCADE)


class ParticipacionEst(models.Model):
	id_actividad = models.AutoField(primary_key=True)
	fecha = models.DateTimeField(default = timezone.now)
	#Se agrega contenido para guardar la participación del estudiante 
	contentido = models.TextField(null=True)
	
	estudiante_part = models.ForeignKey(Estudiante, on_delete=models.CASCADE, related_name='post')

class Pregunta(models.Model):
	id_pregunta = models.OneToOneField(ParticipacionEst, on_delete=models.CASCADE, primary_key=True)
	INICIAL = 1
	SECUNDARIA = 2
	OTRO = 10
	TIPOS_PREGUNTA = (
		(INICIAL, 'inicial'),
		(SECUNDARIA, 'secundaria'),
		(OTRO, 'otro')
	)
	tipo_pregunta = models.PositiveSmallIntegerField(choices=TIPOS_PREGUNTA, default=10)
	votos = models.IntegerField(default=0)
	ganadora = models.BooleanField(default=False)
	
	definirProb_pregunta = models.ForeignKey(DefinirProblema, on_delete=models.CASCADE)

class ComentariosPreguntaInicial(models.Model):
	participacionEst = models.ForeignKey(ParticipacionEst, on_delete=models.CASCADE)
	pregunta = models.ForeignKey(Pregunta, on_delete=models.CASCADE)


class EvaPreguntaSecundarias(models.Model):
	estudiante = models.ForeignKey(User,  on_delete=models.CASCADE)
	id_definirProb_pregunta = models.ForeignKey(DefinirProblema, on_delete=models.CASCADE)