from ast import For
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from ..forms import *
from django.contrib.auth import authenticate, login
from django.template import RequestContext
from django.contrib.auth.models import User
from django.views.generic import CreateView
from ..models import *
from ..decorators import teacher_required
from django.urls import reverse
import random
import string


class ProfSignup(CreateView):
	model = User
	form_class = ProfSignupForm
	template_name = 'registration/signup_form.html'
	
	def get_context_data(self, **kwargs):
		kwargs['user_type'] = 'Profesor'
		return super().get_context_data(**kwargs)

	def form_valid(self, form):
		user = form.save()
		login(self.request, user)
		return redirect('AMCE:ProfMisGrupos')
		
@teacher_required
def vistaProfesor(request):
	return render(request,"profesor/vistaProfesor.html")

@teacher_required
@login_required
def ProfMisGrupos(request):
	"""
		Función para la vista MisGrupos
		Se muestran los grupos asociados al profesor actual
	"""
	user = get_object_or_404(User, pk=request.user.pk)
	grupos = Grupo.objects.filter(profesor_grupo=user.pk)
	grupos = grupos[::-1]
	return render(request,"profesor/MisGrupos.html", {'grupos':grupos})

@teacher_required
@login_required
def ProfCrearGrupo(request):
	"""
		Función para la vista CrearGrupo
		Se crea el grupo cuando se submite el formulario
	"""
	user = get_object_or_404(User, pk=request.user.pk)
	profesor = Profesor.objects.get(user_profesor=user.pk)
	if request.method == 'POST':
		form = FormGrupo(request.POST)
		# Mientras exista un grupo que tenga el id que generamos, generamos otro
		if form.is_valid():
			while True:
				id_grupo = random_string(7)
				ya_existe = Grupo.objects.filter(id_grupo=id_grupo)
				if not ya_existe.exists():
					break
			
			nuevo_grupo = Grupo(id_grupo=id_grupo,
								nombre_grupo=form.cleaned_data['nombre_grupo'], 
								materia=form.cleaned_data['materia'], 
								institucion=form.cleaned_data['institucion'], 
								profesor_grupo=profesor)

			messages.add_message(request, messages.INFO, 'Grupo creado exitosamente', extra_tags='alert-success')
			nuevo_grupo.save()
			form = FormGrupo()
			return redirect(reverse('AMCE:ProfPaginaGrupo',  args=[id_grupo]))
	else:
		form = FormGrupo()
	return render(request, 'profesor/CrearGrupo.html', {'form': form})

@teacher_required
@login_required
def ProfPaginaGrupo(request, id_grupo):
	user = get_object_or_404(User, pk=request.user.pk)
	grupo = Grupo.objects.get(id_grupo=id_grupo)
	equipos = Equipo.objects.filter(grupo_equipo=id_grupo)
	temas = []
	# Obtenemos todos los temas asignados a los equipos del grupo
	for e in equipos:
		for t in e.temas_asignados.all():
			if not t in temas:
				temas.append(t)
	return render(request, 'profesor/PaginaGrupo.html', {'id_grupo':id_grupo, 'grupo':grupo, 'equipos':equipos, "temas":temas})

@teacher_required
@login_required
def ProfCrearEquipo(request, id_grupo):
	user = get_object_or_404(User, pk=request.user.pk)
	grupo = Grupo.objects.get(id_grupo=id_grupo)
	if request.method == 'POST':
		form = FormCrearEquipo(request.POST)
		if form.is_valid():
			nuevo_equipo = Equipo(nombre_equipo=form.cleaned_data['nombre_equipo'],
								   grupo_equipo=grupo)
			nuevo_equipo.save()
			for integrante in form.cleaned_data['integrantes']:
				estudiante = Estudiante.objects.get(user_estudiante=integrante)
				nuevo_equipo.estudiantes.add(estudiante)
			messages.add_message(request, messages.SUCCESS, 'Equipo creado exitosamente', extra_tags='alert-success')
			form = FormCrearEquipo(id_grupo=id_grupo)
			return redirect(reverse('AMCE:ProfPaginaGrupo',  args=[id_grupo]))
	else:
		form = FormCrearEquipo(id_grupo=id_grupo)
	return render(request, 'profesor/CrearEquipo.html', {'id_grupo':id_grupo,'form': form})

@teacher_required
@login_required
def ProfPaginaEquipo(request, id_grupo, id_equipo):
	user = get_object_or_404(User, pk=request.user.pk)
	equipo = Equipo.objects.get(id_equipo=id_equipo)
	print(equipo)
	estudiantes = equipo.estudiantes.all()
	print(estudiantes)
	estudiantes_nombres = []
	for e in estudiantes:
		estudiantes_nombres.append(str(e))
	return render(request, 'profesor/PaginaEquipo.html', {'equipo_nombre':equipo.nombre_equipo, 'estudiantes_nombres':estudiantes_nombres})

@teacher_required
@login_required
def ProfAsignarTemaGrupo(request, id_grupo):
	user = get_object_or_404(User, pk=request.user.pk)
	grupo = Grupo.objects.get(id_grupo=id_grupo)
	if request.method == 'POST':
		form = AsignarTemaGrupo(request.POST)
		if form.is_valid():
			id_tema = form.cleaned_data['tema']
			tema = Tema.objects.get(id_tema=id_tema)
			for id_equipo in form.cleaned_data['equipos']:
				equipo = Equipo.objects.get(id_equipo=id_equipo)
				equipo.temas_asignados.add(tema)
			messages.add_message(request, messages.SUCCESS, 'Tema asignado exitosamente', extra_tags='alert-success')
			form = FormCrearEquipo(id_grupo=id_grupo)
			return redirect(reverse('AMCE:ProfPaginaGrupo', args=[id_grupo]))
	else:
		form = AsignarTemaGrupo(id_grupo=id_grupo)
	return render(request, 'profesor/AsignarTemaGrupo.html', {'id_grupo':id_grupo,'form': form})

@teacher_required
@login_required
def ProfTemaAsignado(request, id_grupo, id_tema):
	current_user = get_object_or_404(User, pk=request.user.pk)
	tema = Tema.objects.filter(id_tema=id_tema)
	grupo = Grupo.objects.filter(id_grupo=id_grupo)
	equipos = Equipo.objects.filter(grupo_equipo=id_grupo,temas_asignados__id_tema=id_tema)
	return render(request, 'profesor/TemaAsignado.html', {'grupo':grupo[0], 'tema':tema[0], 'equipos':equipos})

@teacher_required
@login_required
def ProfMisTemas(request):
	#Se muestran los Temas asignados al ID del usuario actual
	user = get_object_or_404(User, pk=request.user.pk)
	temas = Tema.objects.filter(profesor_tema=user.pk)
	temas = temas[::-1]
	return render(request,"profesor/MisTemas.html", {'temas':temas})

@teacher_required
@login_required
def ProfCrearTema(request):
	user = get_object_or_404(User, pk=request.user.pk)
	profesor = Profesor.objects.get(user_profesor=user.pk)
	temas = Tema.objects.filter(profesor_tema=request.user.pk)
	if request.method == 'POST':
		form = FormTema(request.POST)
		if form.is_valid():
			nuevo_tema = Tema(nombre_tema=form.cleaned_data['nombre_tema'],
								profesor_tema=profesor)
			nuevo_tema.save()
			messages.add_message(request, messages.SUCCESS, 'Tema creado', extra_tags='alert-success')
			form = FormTema()
			return redirect(reverse('AMCE:ProfMisTemas'))
	else:
		form = FormTema()
	return render(request, 'profesor/CrearTema.html', {'form': form})

@teacher_required
@login_required
def ProfProgresoEquipo(request, id_grupo, id_tema, id_equipo):
	user = get_object_or_404(User, pk=request.user.pk)
	profesor = Profesor.objects.get(user_profesor=user.pk)
	definirProb = DefinirProblema.objects.filter(equipo_definirProb=id_equipo)
	id_definirProb = definirProb.id_definirProb
	preguntas_iniciales = Pregunta.objects.filter(definirProb_pregunta=id_definirProb,tipo_pregunta=1)
	
	return render(request, 'profesor/CrearTema.html', {'form': form})

#Función para generar el id de un Grupo cuando se crea
def random_string(char_num): 
	letter_count = random.randint(1, char_num-2)
	digit_count = char_num - letter_count
	str1 = ''.join((random.choice(string.ascii_lowercase) for x in range(letter_count)))  
	str1 += ''.join((random.choice(string.digits) for x in range(digit_count)))  

	sam_list = list(str1) # it converts the string to list.  
	random.shuffle(sam_list) # It uses a random.shuffle() function to shuffle the string.  
	final_string = ''.join(sam_list)  
	return final_string
	