from gettext import translation
from django import forms 
from re import U
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, UsernameField
from django.contrib.auth.models import User
from django.forms import ModelForm
from django.forms.widgets import PasswordInput, TextInput
from django.db import transaction

from django.utils.translation import gettext_lazy as _

from .models import *

DUMMY_CHOICES =(
	("1", "Placeholder"),
	("2", "Placeholder"),
)

class CustomAuthForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super(CustomAuthForm, self).__init__(*args, **kwargs)
		
    username = UsernameField(widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'Nombre de Usuario', 'id': 'username'}))
    password = forms.CharField(widget=forms.PasswordInput(
        attrs={
            'class': 'form-control',
            'placeholder': 'Contraseña',
            'id': 'password',
        }
	))

class EstSignupForm(UserCreationForm):
	
	class Meta(UserCreationForm):
		model = User
		fields = ['username', "first_name", "last_name", "email", "password1", "password2"]

	def save(self):
		user = super().save(commit=False)
		user.es_estudiante = True
		user.save()
		estudiante = Estudiante.objects.create(user_estudiante=user)
		return user

class FormInscribirGrupo(forms.Form):
	#Form el cual se usa para poder capturar un código de matería/clase dado por el profesor
	codigo = forms.CharField(label='Ingresa el código de la clase', max_length = 10)


class PreguntaInicial(forms.Form):
	#Form que captura la pregunta inicial de paso 1.1 del Modelo Gavilán
	contenido = forms.CharField(label='', max_length = 500, widget=forms.Textarea(attrs={'rows':2, 'placeholder': 'Ingresa tu pregunta inicial'}))


class RetroalimentacionPI(forms.Form):
	#Form que captura la pregunta inicial de paso 1.1 del Modelo Gavilán
	contenido = forms.CharField(label='', max_length = 500, widget=forms.Textarea(attrs={'rows':2, 'placeholder': 'Ingresa tu comentario'}))

# FORMS PROFESOR

class ProfSignupForm(UserCreationForm):
	class Meta(UserCreationForm.Meta):
		model = User
		fields = ['username', "first_name", "last_name", "email", "password1", "password2"]
	
	def save(self, commit=True):
		user = super().save(commit=False)
		user.es_profesor = True
		user.save()
		profesor = Profesor.objects.create(user_profesor=user)

class FormGrupo(ModelForm):
	class Meta:
		model = Grupo
		fields = ['nombre_grupo', 'materia', 'institucion']
		labels = {
            'nombre_grupo': _('Nombre del grupo')
        }

class FormTema(ModelForm):
	class Meta:
		model = Tema
		fields = ['nombre_tema']
		labels = {
            'nombre_tema': _('Nombre del tema')
        }


class FormCrearEquipo(forms.Form):
	nombre_equipo = forms.CharField(label='Nombre del equipo',max_length=100)
	integrantes = forms.MultipleChoiceField(choices=DUMMY_CHOICES,widget=forms.SelectMultiple)
	def __init__(self,*args,**kwargs):
		id_grupo = ''
		if 'id_grupo' in kwargs.keys():
			id_grupo = kwargs.pop('id_grupo')
		super().__init__(*args, **kwargs)
		if id_grupo != '':
			estudiantes = Estudiante.objects.filter(grupos_inscritos__id_grupo=id_grupo)
			choices_estudiantes = []
			for e in estudiantes:
				choices_estudiantes.append((e.user_estudiante.id,str(e)))
			self.fields['integrantes'].choices = choices_estudiantes

class AsignarTemaGrupo(forms.Form):
	tema = forms.ChoiceField(label='Tema',choices=DUMMY_CHOICES)
	equipos = forms.MultipleChoiceField(choices=DUMMY_CHOICES,widget=forms.SelectMultiple)
	def __init__(self,*args,**kwargs):
		id_grupo = ''
		if 'id_grupo' in kwargs.keys():
			id_grupo = kwargs.pop('id_grupo')
		super().__init__(*args, **kwargs)
		if id_grupo != '':
			user_id = Grupo.objects.get(id_grupo=id_grupo).profesor_grupo
			temas = Tema.objects.filter(profesor_tema=user_id).values_list('id_tema','nombre_tema')
			equipos = Equipo.objects.filter(grupo_equipo=id_grupo).values_list('id_equipo', 'nombre_equipo')
			self.fields['tema'].choices = temas
			self.fields['equipos'].choices = equipos

'''
#Heredo del userCreationForm que viene en django
class CustomUserCreationForm(UserCreationForm):
	
	#Forms el cual se usa para la creación de un usuario nuevo, su uso se ve refejado en la base de
	#datos del modelo User que tiene django por defecto
	
	class Meta:
		#Se define que es el modelo User el cual se le agregaran los datos capturados
		model = User
		fields = ['username', "first_name", "last_name", "email", "password1", "password2"]

class FormInscribirGrupo(forms.Form):
	
	#Form el cual se usa para poder capturar un código de matería/clase dado por el profesor
	
	codigo = forms.CharField(label='Ingresa el código de la clase', max_length = 10)

class FormActividadPI(forms.Form):
	
	#Form que captura la pregunta inicial de paso 1.1 del Modelo Gavilán
	
	contenido = forms.CharField(label='', max_length = 500, widget=forms.Textarea(attrs={'rows':2, 'placeholder': 'Ingresa tu pregunta inicial'}))

#FORM EN ETAPA DE PRUEBA
class PostPreguntaInicial(forms.ModelForm):
	#Aqui se obtiene el campo de contenido de nuestro modelo Forms para Post
	content = forms.CharField(label='', widget=forms.Textarea(attrs={'rows':2, 'placeholder': 'Ingresa tu pregunta inicial'}))

	class Meta:
		model = Post
		fields = ['content']
'''