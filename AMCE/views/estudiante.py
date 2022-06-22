from pyexpat import ParserCreate
from django.shortcuts import render, redirect, get_object_or_404, HttpResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from ..forms import *
from django.contrib.auth import authenticate, login
from django.template import RequestContext
from django.contrib.auth.models import User
from django.views.generic import CreateView
from ..models import *
from ..decorators import student_required
from django.urls import reverse
#se importa para aumentar el contador de votos en feed
from django.db.models import F
from django.conf import settings
from django.core.mail import send_mail
import datetime




class EstSignup(CreateView):
	model = User
	form_class = EstSignupForm
	template_name = 'registration/signup_form.html'
	
	def get_context_data(self, **kwargs):
		kwargs['user_type'] = 'Estudiante'
		return super().get_context_data(**kwargs)

	def form_valid(self, form):
		user = form.save()
		login(self.request, user)
		return redirect('AMCE:EstMisGrupos')
		

@student_required
def vistaAlumno(request):
	current_user = get_object_or_404(User, pk=request.user.pk)
	#Comento esta linea porque me daba error sin saber el por qué
	#grupos_inscritos = Estudiante.objects.filter(user_estudiante=current_user.id).values_list('grupos_inscritos', flat=True)

	#Se agregan estas lineas con el fin de sustituir la linea de arriba 
	estudiante = Estudiante.objects.get(user_estudiante=current_user.id)
	#Consultamos todos grupos a los cual el usuario estudiante está inscrito y los mostramos
	grupos_inscritos = estudiante.grupos_inscritos.all()

	return render(request,"estudiante/MisGrupos.html", {'grupos_inscritos':grupos_inscritos})

@student_required
@login_required
def EstInscribirGrupo(request):
	'''
	Función para que un usuario alumno pueda inscribir una matería dado un código de clase
	por parte del profesor 
	'''
	current_user = get_object_or_404(User, pk=request.user.pk)
	grupos_inscritos = Estudiante.objects.filter(user_estudiante=request.user.pk)
	
	if request.method == 'POST':
		form = FormInscribirGrupo(request.POST)
		if form.is_valid():
			repetido = Estudiante.objects.filter(user_estudiante=current_user.id, grupos_inscritos=form.cleaned_data['codigo'])
			codigo = form.cleaned_data['codigo']
			try:
				if repetido.exists():
					messages.success(request, 'Ya estás inscrito en el grupo con código ' + codigo)
					return redirect(to="AMCE:EstMisGrupos")
				else:
					grupo = Grupo.objects.get(id_grupo=codigo)
					grupo_a_inscribir= Estudiante(user_estudiante_id=current_user.id)
					grupo_a_inscribir.grupos_inscritos.add(grupo.id_grupo)
					grupo_a_inscribir.save()
					messages.success(request, 'Grupo inscrito')
					return redirect(to="AMCE:EstMisGrupos")
			except Grupo.DoesNotExist:
				messages.error(request, 'El código de grupo que ingresaste no es válido')
				return redirect(to="AMCE:EstMisGrupos")
	else:
		form = FormInscribirGrupo()

	return render(request, 'estudiante/InscribirGrupo.html', {'form': form})

@student_required
@login_required
def EstMisGrupos(request):
	'''
	Función la cual muestra al usuario alumno los grupos a los cuales está inscrito  
	'''
	current_user = get_object_or_404(User, pk=request.user.pk)
	#Obtenemos el objeto estudiante actual
	estudiante = Estudiante.objects.get(user_estudiante=current_user.id)
	#Consultamos todos grupos a los cual el usuario estudiante está inscrito y los mostramos
	grupos_inscritos = estudiante.grupos_inscritos.all()

	return render(request,"estudiante/MisGrupos.html",{'grupos_inscritos':grupos_inscritos})

@student_required
@login_required
def EstPaginaGrupo(request, id_grupo):
	'''
	Función la cual muestra los temas asignados al equipo del usuario.
	Un usuario debe de tener un equipo pero este puede ser diferente para cada tema, lo que se hace es que 
	se haga una búsqueda que llegue hasta la tabla Asignar, la cual muestra que equipos (id) tienen el tema (id)
	Args:
		id_grupo (char): código de la materia 
	'''
	#Se verifica que el usuario tenga equipo
	try:
		current_user = get_object_or_404(User, pk=request.user.pk)
		#Se obtiene el objeto Equipo de nuestro actual estudiante
		equipo = Equipo.objects.get(estudiantes=current_user.id, grupo_equipo=id_grupo)
		#Consultamos los temas asigandos que tiene el equipo del usuario y los filtramos por materia 
		temas_asignados = equipo.temas_asignados.filter()
		#Consultamos e identificamos el grupo actual para mostrar los datos de grupo y materia en el header 
		grupo = Grupo.objects.filter(id_grupo = id_grupo)
	#De no tener equipo se le notifica que aún no tiene equipo
	except Equipo.DoesNotExist:
		messages.error(request, 'Aún no tienes equipo, espera a que tu profesor te asigne uno.')
		return redirect('AMCE:EstMisGrupos')
	

	return render(request, 'estudiante/PaginaGrupo.html', {'grupo':grupo.first(),'id_grupo':id_grupo ,'temas_asignados':temas_asignados})

def envioCorreoAvisoNoContinuar(texto, email):
	correo = send_mail(
    		texto,
    		settings.EMAIL_HOST_USER,
    		[email],
    		fail_silently=False,
			)
	return correo
	

@student_required
@login_required
def AvisoNoContinuar(request, id_tema, id_grupo):
	'''
	Funcion para mostrar el aviso de que el equipo aún no acaba esta parte
	'''
	current_user = get_object_or_404(User, pk=request.user.pk)
	equipo = Equipo.objects.get(estudiantes=current_user.id, grupo_equipo=id_grupo).id_equipo
	#obtengo todos los integrantes del equipo con ese id_equipo
	integrantesEquipo = Equipo.objects.filter(id_equipo=equipo).values_list('estudiantes', flat=True)
	#Se consulta el equipo actual del usuario para pasarselo como parámetro en defProbPreguntaQuery
	equipo = Equipo.objects.get(estudiantes=current_user.id, grupo_equipo=id_grupo)
	#Se obtiene el problema asignado a un equipo, esto para poder obtener el parámetro definirProb_pregunta_id
	defProbPreguntaQuery = DefinirProblema.objects.get(equipo_definirProb_id = equipo.id_equipo, tema_definirProb_id = id_tema)
	temaNombre = Tema.objects.get(id_tema=id_tema).nombre_tema

	#Por cada integrante del equipo se va a buscar su participación de la PI
	for i in integrantesEquipo:
		#Si se encuentra la participación de un usuario no pasa nada
		try:
			obj = Pregunta.objects.get(id_pregunta__estudiante_part=i, definirProb_pregunta_id=defProbPreguntaQuery, tipo_pregunta=1)
		#Si no encuentra la participación de un usuario entonces manda correo a ese usuario quién no tiene la participación
		except Pregunta.DoesNotExist:
			#Obtenemos el id para posteriormente usar el nombre del usuario en el cuerpo del mensaje
			obj2 = User.objects.get(id=i)
			send_mail(
    		'Aviso, Faltas tu!',
    		f'Hola {obj2.first_name}, tu equipo ya realizó la actividad de formular la pregunta inicial del tema {temaNombre}, faltas tu! Entra a Búsqueda Colaborativa y continua con tu proceso de investigación.',
    		settings.EMAIL_HOST_USER,
    		[obj2.email],
    		fail_silently=False,
			)
	
	return render(request, 'estudiante/AvisoNoContinuar.html', {'id_tema':id_tema, 'id_grupo':id_grupo})

@student_required
@login_required
def postPreguntaInicial(request, id_tema ,id_grupo):
	'''
	Función la cual habilita que un usuario pueda ingresar una función principal mediante un form.

	Args:
		tema (string): El tema asignado de la pregunta inicial

		codigo (string): codigo de la materia 
	
	'''
	#Consulta para obtener el tema de la actividad asignada y mostrarla en el template, así como usarla en defProbPreguntaQuery
	temaPreguntaInicial = Tema.objects.get(id_tema=id_tema)
	current_user = get_object_or_404(User, pk=request.user.pk)
	#Se consulta el equipo actual del usuario para pasarselo como parámetro en defProbPreguntaQuery
	equipo = Equipo.objects.get(estudiantes=current_user.id, grupo_equipo=id_grupo)
	#Se obtiene el problema asignado a un equipo, esto para poder obtener el parámetro definirProb_pregunta_id
	defProbPreguntaQuery = DefinirProblema.objects.get(equipo_definirProb_id = equipo.id_equipo, tema_definirProb_id = temaPreguntaInicial.id_tema)
	#Obtenemos todas las participaciones del equipo de nuestro actual usuario (AGREGAR CÓMO PARÁMETRO 1 COMO PREGUNTA INICIAL)
	numTotalPartici = Pregunta.objects.filter(definirProb_pregunta=defProbPreguntaQuery.id_definirProb, tipo_pregunta=1)
	#Obtenemos los integrantes del  equipo
	integrantesEquipo = Equipo.objects.filter(estudiantes__grupos_inscritos=equipo.grupo_equipo_id, temas_asignados__id_tema=id_tema).values_list('estudiantes', flat=True)

	#Se obtienen los ids del usuario actual 
	idsUsuarioParticipacion = ParticipacionEst.objects.filter(estudiante_part=current_user.id).values_list('id_actividad', flat=True)
	#Se obtienen los id's de id_pregunta del numTotalPartici que asocia al equipo del actual estudiante y el del tema asignado
	idsUsuarioPregunta = numTotalPartici.values_list('id_pregunta', flat=True)

	#Se pregunta si el numero total de particiapciones con id_definirProb del equipo es igual al número de integrantes
	if numTotalPartici.count() == integrantesEquipo.count():
		#Si el numero de integrantes coincide con el número de participaciones entonces pasamos al siguente paso
		return redirect('AMCE:AnalisisPreguntaInicial',id_grupo=id_grupo, id_tema=id_tema)
		#Si no lo mandamos al modal de aviso 
	else:
		#Verificamos si hay una intersección entre los ids de participaciones del usuario con los ids de las preguntas asociadas a un id de DefinirPregunta
		if bool(set(idsUsuarioParticipacion)&set(idsUsuarioPregunta)):
			#Si hay un elemento en comun quiere decir que ya tiene su participación
			return redirect('AMCE:AvisoNoContinuar' , id_grupo=id_grupo, id_tema=id_tema)
		#Si no hay participación previa del usuario en este paso, quiere decir que no hay hecho este paso y se le permite hacerlo
		else:
			#Validación del forms de PreguntaInicial
			if request.method == 'POST':
				#Se captura la información proporcionada en el form del template
				form = PreguntaInicial(request.POST)
				if form.is_valid():
					#Creamos un elemento para nuestra tabla de actividad 
					nuevaParticipacion = ParticipacionEst(contentido = form.cleaned_data['contenido'],
												 estudiante_part_id = current_user.id)
					messages.success(request, 'Pregunta inicial guardada')
					nuevaParticipacion.save()
					#De igual menera creamos un elemento del modelo Pregunta con el id_actividad que se acabó de crear con la variable nuevaParticipacion
					nuevoCampoPregunta = Pregunta(id_pregunta_id=nuevaParticipacion.id_actividad, tipo_pregunta=1, definirProb_pregunta_id=defProbPreguntaQuery.id_definirProb)
					nuevoCampoPregunta.save()

					#Participación actual del estudiante del tema actual para verificar si es la uñtima participación que el equipo necesita para continuar con el sig paso
					par = Pregunta.objects.get(id_pregunta__estudiante_part_id = current_user.id ,definirProb_pregunta=defProbPreguntaQuery.id_definirProb, tipo_pregunta=1)
					#Entero el cual define la ultima participación del equipo
					ultimaParticipacion = integrantesEquipo.count()-1
					try:
						#Si la participación que hizo el estudiante es la ultima participación que se espera, manda el correo
						if par == numTotalPartici[ultimaParticipacion]:
							print('manda correo')
							#Se les notifica a los integrantes del equipo que todos han acabado
							for i in integrantesEquipo:
								nombreUsuario = User.objects.get(id=i)
								send_mail(
								'Tu equipo ya acabó de formular la pregunta inicial!',
								f'Hola {nombreUsuario.first_name}, el último integrante de tu equipo ha terminado de formular la pregunta inicial del tema {temaPreguntaInicial.nombre_tema}. Entra a Búsqueda Colaborativa y continua con tu proceso de investigación.',
								settings.EMAIL_HOST_USER,
								[nombreUsuario.email],
								fail_silently=False,
								)
					#Si no encuentra la participación de un usuario entonces manda correo a ese usuario quién no tiene la participación
					except IndexError:
						print('no se manda correo correo')
					#Se redirige a la pregunta inicial para que se valide si puede avanzar o no al siguente paso
					return redirect('AMCE:PreguntaInicial',id_grupo=id_grupo, id_tema=id_tema)
			else:
				form = PreguntaInicial()
	
	return render(request, 'estudiante/PreguntaInicial.html', {'id_tema':id_tema,'id_grupo':id_grupo ,'temaPreguntaInicial':temaPreguntaInicial, 'form': form})

@student_required
@login_required
def AnalisisPreguntaInicial(request, id_tema ,id_grupo):
	#corroborar si ya comentaron las preguntas iniciales
	temaPreguntaInicial = Tema.objects.get(id_tema=id_tema)
	current_user = get_object_or_404(User, pk=request.user.pk)
	equipo = Equipo.objects.get(estudiantes=current_user.id, grupo_equipo=id_grupo)
	defProbPreguntaQuery = DefinirProblema.objects.get(equipo_definirProb_id = equipo.id_equipo, tema_definirProb_id = temaPreguntaInicial.id_tema)
	numTotalPartici = Pregunta.objects.filter(definirProb_pregunta=defProbPreguntaQuery.id_definirProb)
	integrantesEquipo = Equipo.objects.filter(estudiantes__grupos_inscritos=equipo.grupo_equipo_id, temas_asignados__id_tema=id_tema)

	comentariosPregunta = ComentariosPreguntaInicial.objects.filter(pregunta__definirProb_pregunta = defProbPreguntaQuery).values_list('participacionEst_id', flat=True)
	#Se obtienen los ids del usuario actual 
	idsUsuarioParticipacion = ParticipacionEst.objects.filter(estudiante_part=current_user.id).values_list('id_actividad', flat=True)
	#Si todos los integrantes retrolimentaron la pregunta inicial se redirecciona al siguente paso
	if comentariosPregunta.count() == integrantesEquipo.count():
		#Redireccionamos al usuario a la pantalla Definición de la Pregunta inicial
		return redirect('AMCE:defPreguntaInicial', id_grupo=id_grupo, id_tema=id_tema)
	else:
		print('ir a analisis pregunta inicial')
		#Se corrobora si ya tiene participación en la actividad
		if bool(set(idsUsuarioParticipacion)&set(comentariosPregunta)):
			#Si ya tiene una retroalimentación se le redireciona a la pantalla de No continuar
			return redirect('AMCE:AvisoNoContinuarAnalisis' , id_grupo=id_grupo, id_tema=id_tema)
	return render(request,"estudiante/Actividad.html", {'id_tema':id_tema, 'id_grupo':id_grupo})

@student_required
@login_required
def feedPIHecha(request, id_tema ,id_grupo):
	'''
	Esta es una de las dos funciones semejantes que se tienen en el views de estudiante, la unica diferencia que tienen 
	es que regresan un template diferente. Las funciones cuentan los integrantes del equipo del usuario actual relacionado al tema 
	de la pregunta inicial 
		Args:
		id_tema (string): El tema asignado de la pregunta inicial

		id_grupo (string): codigo de la materia 
	'''
	temaPreguntaInicial = Tema.objects.get(id_tema=id_tema)
	current_user = get_object_or_404(User, pk=request.user.pk)
	equipo = Equipo.objects.get(estudiantes=current_user.id, grupo_equipo=id_grupo)
	defProbPreguntaQuery = DefinirProblema.objects.get(equipo_definirProb_id = equipo.id_equipo, tema_definirProb_id = temaPreguntaInicial.id_tema)
	numTotalPartici = Pregunta.objects.filter(definirProb_pregunta=defProbPreguntaQuery.id_definirProb)
	integrantesEquipo = Equipo.objects.filter(estudiantes__grupos_inscritos=equipo.grupo_equipo_id, temas_asignados__id_tema=id_tema)
	#Se hace una consulta para input text del template con atributo comentario, esto devuelve la lista con lo
	comentario = request.POST.getlist('comentario')
	#Se quitan los caracteres vacios
	respuesta = "".join(string for string in comentario if len(string) > 0)

	#Se obtienen los ids del usuario actual 
	idsUsuarioParticipacion = ParticipacionEst.objects.filter(estudiante_part=current_user.id).values_list('id_actividad', flat=True)

	#Se obtienen los id's de ComentariosPreguntaInicial asociados al tema asignado y equipo del usuario. Sacamos las participacionEst_id y aplicamos intersección para revisar si ya hay una participación previa 
	comentariosPregunta = ComentariosPreguntaInicial.objects.filter(pregunta__definirProb_pregunta = defProbPreguntaQuery).values_list('participacionEst_id', flat=True)
	#Se verifica que numero total de comentarios con los ids de participaciones estudiantes sean las mismas a los integrantes, de serlo es porque todos comentarno una PI
	if comentariosPregunta.count() == integrantesEquipo.count():
		print(comentariosPregunta)
		print(integrantesEquipo.count())
		#Redireccionamos al usuario a la pantalla Definición de la Pregunta inicial
		return redirect('AMCE:defPreguntaInicial', id_grupo=id_grupo, id_tema=id_tema)
	else:
		#----------------------
		#Si faltan integrantes por retroalimentar la pregunta inicial, se verifica si ya retroalimentó anteriormente 
		if bool(set(idsUsuarioParticipacion)&set(comentariosPregunta)):
			#Si ya tiene una retroalimentación se le redireciona a la pantalla de No continuar
			return redirect('AMCE:AvisoNoContinuarAnalisis' , id_grupo=id_grupo, id_tema=id_tema)
		else:
			#Si no hay retroalimentación previa, se le permite entrar para que haga su retroalimentación
			if request.method == 'POST':
				#se captura el nombre de usuario por el cual se está votando
				voto = request.POST.get("voto")
				#comentario = request.POST.get("comentario")
				print(respuesta)
				print(voto)
				nuevaParticipacion = ParticipacionEst(contentido = respuesta,
														estudiante_part_id = current_user.id)
				nuevaParticipacion.save()
				#print(nuevaParticipacion.id_actividad)
				id_PreguntaAsociadaAUsuario = Pregunta.objects.filter(id_pregunta__estudiante_part_id=voto, definirProb_pregunta=defProbPreguntaQuery).values_list('id_pregunta', flat=True)

				nuevoComentario = ComentariosPreguntaInicial(participacionEst_id = nuevaParticipacion.id_actividad, pregunta_id = id_PreguntaAsociadaAUsuario)
				nuevoComentario.save()

				#Se agrega voto y se agrega comentario a las respectivas celdas de la Bade de Datos
				voto_sumar = Pregunta.objects.filter(id_pregunta__estudiante_part_id=voto, definirProb_pregunta=defProbPreguntaQuery).update(votos=F('votos')+1)
				messages.success(request, 'Comentario y voto guardado correctamente')
				return redirect('AMCE:feedPIHecha', id_grupo=id_grupo, id_tema=id_tema)
	return render(request, 'estudiante/FeedPreguntaInicialHecha.html', {'temaPreguntaInicial':temaPreguntaInicial, 'numTotalPartici':numTotalPartici})

@student_required
@login_required
def AvisoNoContinuarAnalisis(request, id_tema, id_grupo):
	'''
	Esta es una de las dos funciones semejantes que se tienen en el views de estudiante, la unica diferencia que tienen 
	es que regresan un template diferente. Las funciones cuentan los integrantes del equipo del usuario actual relacionado al tema 
	de la pregunta inicial 
		Args:
		tema (string): El tema asignado de la pregunta inicial

		codigo (string): codigo de la materia 
	'''
	current_user = get_object_or_404(User, pk=request.user.pk)
	#Se consulta el equipo actual del usuario para pasarselo como parámetro en defProbPreguntaQuery
	equipo = Equipo.objects.get(estudiantes=current_user.id, grupo_equipo=id_grupo).id_equipo
	#obtengo todos los integrantes del equipo con ese id_equipo
	integrantesEquipo = Equipo.objects.filter(id_equipo=equipo).values_list('estudiantes', flat=True)
	#Se obtiene el problema asignado a un equipo, esto para poder obtener el parámetro definirProb_pregunta_id
	defProbPreguntaQuery = DefinirProblema.objects.get(equipo_definirProb_id = equipo, tema_definirProb_id = id_tema)
	temaNombre = Tema.objects.get(id_tema=id_tema).nombre_tema

	#Se obtienen los ids del usuario actual 
	idsUsuarioParticipacion = ParticipacionEst.objects.filter(estudiante_part=current_user.id).values_list('id_actividad', flat=True)
	#Se obtienen los id's de ComentariosPreguntaInicial asociados al tema asignado y equipo del usuario. Sacamos las participacionEst_id y aplicamos intersección para revisar si ya hay una participación previa 
	comentariosPregunta = ComentariosPreguntaInicial.objects.filter(pregunta__definirProb_pregunta = defProbPreguntaQuery).values_list('participacionEst_id', flat=True)
	
	#Por cada integrante del equipo se va a buscar su participación de la PI
	for i in integrantesEquipo:
		nombreUsuario = User.objects.get(id=i)
		#Si se encuentra la participación de un usuario no pasa nada
		#Se consulta integrante x integrante para ver si tiene participación 
		integranteN = ParticipacionEst.objects.filter(estudiante_part=i).values_list('id_actividad', flat=True)
		try:
			#Obtenemos los usuarios que aún les falta su participación y se les manda correo
			if not(bool(set(integranteN)&set(comentariosPregunta))):
				print('Manda correo a los que no han hecho la actividad')
				send_mail(
				'Aviso, Faltas tu!',
				f'Hola {nombreUsuario.first_name}, tu equipo ya terminó de evaluar la pregunta inicial del tema {temaNombre}, faltas tu! Entra a Búsqueda Colaborativa y continua con tu proceso de investigación.',
				settings.EMAIL_HOST_USER,
				[nombreUsuario.email],
				fail_silently=False,
				)
		#Si no encuentra la participación de un usuario entonces manda correo a ese usuario quién no tiene la participación
		except:
			#Obtenemos el id para posteriormente usar el nombre del usuario en el cuerpo del mensaje
			print('todo está bien')
	#envioCorreo = envioCorreoAvisoNoContinuar()
	return render(request, 'estudiante/AnalisisAviso.html', {'id_tema':id_tema, 'id_grupo':id_grupo})

@student_required
@login_required
def defPreguntaInicial(request,  id_tema, id_grupo):
	#http://127.0.0.1:8000/estudiante/Grupo/1/Tema/1/PreguntaInicial/DefiniciónPreguntaInicial/
	temaPreguntaInicial = Tema.objects.get(id_tema=id_tema)
	current_user = get_object_or_404(User, pk=request.user.pk)
	equipo = Equipo.objects.get(estudiantes=current_user.id, grupo_equipo=id_grupo)
	#obtenemos el equiopo y tema a los cuales se asocian 
	defProbPreguntaQuery = DefinirProblema.objects.get(equipo_definirProb_id = equipo.id_equipo, tema_definirProb_id = temaPreguntaInicial.id_tema)

	pregunta = Pregunta.objects.filter(definirProb_pregunta = defProbPreguntaQuery)

	#Obtenemos todas las participaciones del equipo de nuestro actual usuario 
	numTotalPartici = Pregunta.objects.filter(definirProb_pregunta=defProbPreguntaQuery.id_definirProb, tipo_pregunta=2)

	#Se obtienen los ids de las participaciones del usuario actual 
	idsUsuarioParticipacion = ParticipacionEst.objects.filter(estudiante_part=current_user.id).values_list('id_actividad', flat=True)
	#Se obtienen los id's de ComentariosPreguntaInicial asociados al tema asignado y equipo del usuario. Sacamos las participacionEst_id y aplicamos intersección para revisar si ya hay una participación previa 
	preguntasSecUsuario = Pregunta.objects.filter(definirProb_pregunta = defProbPreguntaQuery, tipo_pregunta=2 ).values_list('id_pregunta', flat=True)

	#Obtenemos los integrantes del  equipo (A ESTO SE LE AGREGÓ VALUE LIST)
	integrantesEquipo = Equipo.objects.filter(estudiantes__grupos_inscritos=equipo.grupo_equipo_id, temas_asignados__id_tema=id_tema).values_list('estudiantes', flat=True)
	
	#Comprobamos si tienen preguntas secundarias ya hechas
	noPreguntasSec = DefinirProblema.objects.get(tema_definirProb_id = id_tema).preguntas_secundarias
	#Se pregunta si el numero total de particiapciones con id_definirProb del equipo es igual al número de integrantes
	if numTotalPartici.count() == (integrantesEquipo.count() * noPreguntasSec):
		#Si el numero de integrantes coincide con el número de participaciones entonces pasamos al siguente paso
		return redirect('AMCE:EvaluacionPS', id_grupo=id_grupo, id_tema=id_tema)
		#Si no lo mandamos al modal de aviso 
	else:
		#Si faltan integrantes por retroalimentar la pregunta inicial, se verifica si ya retroalimentó anteriormente 
		if bool(set(idsUsuarioParticipacion)&set(preguntasSecUsuario)):
			#Si ya tiene una retroalimentación se le redireciona a la pantalla de No continuar
			return redirect('AMCE:PSAvisoNoContinuar' , id_grupo=id_grupo, id_tema=id_tema)
		else:
			#Buscamos cual es la pregunta inicial con más votos
			max = 0
			for i in pregunta:
				if i.votos >= max:
					max = i.votos
			preguntaSelactualiza = Pregunta.objects.filter(votos = max, definirProb_pregunta = defProbPreguntaQuery).update(ganadora=True)
			preguntaSel = Pregunta.objects.filter(votos = max, definirProb_pregunta = defProbPreguntaQuery)

			#CHECAR ESTE MÉTODO DE VALIDACIÓN 
			#Si hay preguntas que están empatadas en votos toma la primera por default ya que se genera un empate
			if pregunta.count() > 1:
				preguntaSel = preguntaSel[0]
			#aquí se debe de actualizar a true la pregunta inicial con más votos
			print('id')
			print(preguntaSel.id_pregunta)

			#aqui se va a verificar que se mande el correo
			contador = 0
			for i in integrantesEquipo:
				#para cada integrante del equipo se verifican sus participaciones
				idsParticipacionUsuarioN = ParticipacionEst.objects.filter(estudiante_part=i).values_list('id_actividad', flat=True)
				print(idsParticipacionUsuarioN)
				if bool(set(idsParticipacionUsuarioN)&set(preguntasSecUsuario)):
					contador = contador + 1
					print(i)
			if contador == integrantesEquipo.count():
				print('se manda correo')

			#Se obtienen los comentarios de la pregunta ganadora para mostrarlos en la pantalla de definición de la pregunta inicial
			comentariosPregunta = ComentariosPreguntaInicial.objects.filter(pregunta_id = preguntaSel)	
			

	return render(request, "estudiante/DefinicionPreguntaIncial.html",{'id_tema': id_tema, 'id_grupo':id_grupo, 'preguntaSel':preguntaSel, 'comentariosPregunta':comentariosPregunta})

@student_required
@login_required
def PreguntasSecundarias(request,  id_tema, id_grupo):
	noPreguntasSec = DefinirProblema.objects.get(tema_definirProb_id = id_tema).preguntas_secundarias
	temaNombre = Tema.objects.get(id_tema=id_tema).nombre_tema
	current_user = get_object_or_404(User, pk=request.user.pk)
	equipo = Equipo.objects.get(estudiantes=current_user.id, grupo_equipo=id_grupo)
	defProbPreguntaQuery = DefinirProblema.objects.get(equipo_definirProb_id = equipo.id_equipo, tema_definirProb_id = id_tema)
	#Obtenemos todas las participaciones del equipo de nuestro actual usuario 
	numTotalPartici = Pregunta.objects.filter(definirProb_pregunta=defProbPreguntaQuery.id_definirProb, tipo_pregunta=2)

	#Obtenemos los integrantes del  equipo
	integrantesEquipo = Equipo.objects.filter(estudiantes__grupos_inscritos=equipo.grupo_equipo_id, temas_asignados__id_tema=id_tema)

	#Se obtienen los ids de las participaciones del usuario actual 
	idsUsuarioParticipacion = ParticipacionEst.objects.filter(estudiante_part=current_user.id).values_list('id_actividad', flat=True)
	#Se obtienen los id's de ComentariosPreguntaInicial asociados al tema asignado y equipo del usuario. Sacamos las participacionEst_id y aplicamos intersección para revisar si ya hay una participación previa 
	preguntasSecUsuario = Pregunta.objects.filter(definirProb_pregunta = defProbPreguntaQuery, tipo_pregunta=2 ).values_list('id_pregunta', flat=True)
	#Consulta para obtener la pregunta inicial ganadora y mostrala en el template
	pregunta = Pregunta.objects.get(definirProb_pregunta = defProbPreguntaQuery, ganadora=True)
	#Consutlar los id de los integrantes del equipo para mandar correo
	integrantesEquipoCorreo = Equipo.objects.filter(id_equipo=equipo.id_equipo).values_list('estudiantes', flat=True)

	#Se pregunta si el numero total de particiapciones con id_definirProb del equipo es igual al número de integrantes
	if numTotalPartici.count() == (integrantesEquipo.count() * noPreguntasSec):
		#Si el numero de integrantes coincide con el número de participaciones entonces pasamos al siguente paso
		return redirect('AMCE:EvaluacionPS', id_grupo=id_grupo, id_tema=id_tema)
		#Si no lo mandamos al modal de aviso 
	else:
		#Si faltan integrantes por retroalimentar la pregunta inicial, se verifica si ya retroalimentó anteriormente 
		if bool(set(idsUsuarioParticipacion)&set(preguntasSecUsuario)):
			#Si ya tiene una retroalimentación se le redireciona a la pantalla de No continuar
			return redirect('AMCE:PSAvisoNoContinuar' , id_grupo=id_grupo, id_tema=id_tema)
		else:
			if request.method == 'POST':
				comentario = request.POST.getlist('preguntaSecundaria')

				for i in comentario:
					#Creamos un elemento para nuestra tabla de actividad 
					nuevaParticipacion = ParticipacionEst(contentido = i,
															estudiante_part_id = current_user.id)
					nuevaParticipacion.save()
					#De igual menera creamos un elemento del modelo Pregunta con el id_actividad que se acabó de crear con la variable nuevaParticipacion
					nuevoCampoPregunta = Pregunta(id_pregunta_id=nuevaParticipacion.id_actividad, tipo_pregunta=2, definirProb_pregunta_id=defProbPreguntaQuery.id_definirProb)
					nuevoCampoPregunta.save()
					#Se redirige a la pregunta inicial para que se valide si puede avanzar o no al siguente paso
					messages.success(request, 'Preguntas secundarias guardadas correctamente')
					
					#Participación actual del estudiante del tema actual para verificar si es la uñtima participación que el equipo necesita para continuar con el sig paso
					par = Pregunta.objects.get(id_pregunta__estudiante_part_id = current_user.id ,definirProb_pregunta=defProbPreguntaQuery.id_definirProb, tipo_pregunta=2)
					#Entero el cual define la ultima participación del equipo
					ultimaParticipacion = integrantesEquipo.count()-1 * noPreguntasSec
					try:
						#Si la participación que hizo el estudiante es la ultima participación que se espera, manda el correo
						if par == numTotalPartici[ultimaParticipacion]:
							print('manda correo')
							#Se les notifica a los integrantes del equipo que todos han acabado
							for i in integrantesEquipoCorreo:
								nombreUsuario = User.objects.get(id=i)
								send_mail(
								'Tu equipo ya acabó de formular las preguntas secundaria!',
								f'Hola {nombreUsuario.first_name}, el último integrante de tu equipo ha terminado de formular las preguntas secundarias del tema {temaNombre}. Entra a Búsqueda Colaborativa y continua con tu proceso de investigación.',
								settings.EMAIL_HOST_USER,
								[nombreUsuario.email],
								fail_silently=False,
								)
					#Si no encuentra la participación de un usuario entonces manda correo a ese usuario quién no tiene la participación
					except IndexError:
						print('no se manda correo correo')
				return redirect('AMCE:PreguntasSecundarias',  id_grupo=id_grupo, id_tema=id_tema)


	return render(request, "estudiante/PreguntasSecundarias.html", {'id_tema':id_tema, 'id_grupo':id_grupo, 'range': range(noPreguntasSec), 'temaNombre':temaNombre, 'pregunta':pregunta, 'noPreguntasSec':noPreguntasSec})

@student_required
@login_required
def PSAvisoNoContinuar(request,  id_tema, id_grupo):
	current_user = get_object_or_404(User, pk=request.user.pk)
	#Se consulta el equipo actual del usuario para pasarselo como parámetro en defProbPreguntaQuery
	equipo = Equipo.objects.get(estudiantes=current_user.id, grupo_equipo=id_grupo)
	#Se obtiene el problema asignado a un equipo, esto para poder obtener el parámetro definirProb_pregunta_id
	defProbPreguntaQuery = DefinirProblema.objects.get(equipo_definirProb_id = equipo.id_equipo, tema_definirProb_id = id_tema)
	#Obtenemos todas las participaciones del equipo de nuestro actual usuario 
	numTotalPartici = Pregunta.objects.filter(definirProb_pregunta=defProbPreguntaQuery.id_definirProb, tipo_pregunta=2)
	#Obtenemos los integrantes del  equipo
	integrantesEquipo = Equipo.objects.filter(estudiantes__grupos_inscritos=equipo.grupo_equipo_id, temas_asignados__id_tema=id_tema)
	#Consulta para obtener los integrantes de equipo para mandar correo
	integrantesEquipoCorreo = Equipo.objects.filter(id_equipo=equipo.id_equipo).values_list('estudiantes', flat=True)
	temaNombre = Tema.objects.get(id_tema=id_tema).nombre_tema

	#Mandar correo a los que aún no tienen su participación de pregunta secundaria

	noPreguntasSec = DefinirProblema.objects.get(tema_definirProb_id = id_tema).preguntas_secundarias
	print(numTotalPartici.count())
	print(integrantesEquipo.count() * noPreguntasSec	)
	#Se pregunta si el numero total de particiapciones con id_definirProb del equipo es igual al número de integrantes
	if numTotalPartici.count() == (integrantesEquipo.count() * noPreguntasSec):
		#Si el numero de integrantes coincide con el número de participaciones entonces pasamos al siguente paso
		return redirect('AMCE:EvaluacionPS', id_grupo=id_grupo, id_tema=id_tema)
		#Si no lo mandamos al modal de aviso 
	else:
		print('entré al else')

	for i in integrantesEquipoCorreo:
		#Si se encuentra la participación de un usuario no pasa nada
		try:
			obj = Pregunta.objects.get(id_pregunta__estudiante_part=i, definirProb_pregunta_id=defProbPreguntaQuery, tipo_pregunta=2)
		#Si no encuentra la participación de un usuario entonces manda correo a ese usuario quién no tiene la participación
		except Pregunta.DoesNotExist:
			#Obtenemos el id para posteriormente usar el nombre del usuario en el cuerpo del mensaje
			obj2 = User.objects.get(id=i)
			send_mail(
    		'Aviso, Faltas tu!',
    		f'Hola {obj2.first_name}, tu equipo ya realizó la actividad de formular las preguntas secundarias del tema {temaNombre}, faltas tu! Entra a Búsqueda Colaborativa y continua con tu proceso de investigación.',
    		settings.EMAIL_HOST_USER,
    		[obj2.email],
    		fail_silently=False,
			)
	return render(request, "estudiante/PSAvisoNoContinuar.html", {'id_tema':id_tema, 'id_grupo':id_grupo})


@student_required
@login_required
def AvisoNoContinuarEvaPS(request, id_tema, id_grupo):
	'''
	Esta es una de las dos funciones semejantes que se tienen en el views de estudiante, la unica diferencia que tienen 
	es que regresan un template diferente. Las funciones cuentan los integrantes del equipo del usuario actual relacionado al tema 
	de la pregunta inicial 
		Args:
		tema (string): El tema asignado de la pregunta inicial

		codigo (string): codigo de la materia 
	'''
	current_user = get_object_or_404(User, pk=request.user.pk)
	equipo = Equipo.objects.get(estudiantes=current_user.id, grupo_equipo=id_grupo).id_equipo
	#obtengo todos los integrantes del equipo con ese id_equipo
	integrantesEquipo = Equipo.objects.filter(id_equipo=equipo).values_list('estudiantes', flat=True)
	#Se consulta el equipo actual del usuario para pasarselo como parámetro en defProbPreguntaQuery
	equipo = Equipo.objects.get(estudiantes=current_user.id, grupo_equipo=id_grupo)
	#Se obtiene el problema asignado a un equipo, esto para poder obtener el parámetro definirProb_pregunta_id
	defProbPreguntaQuery = DefinirProblema.objects.get(equipo_definirProb_id = equipo.id_equipo, tema_definirProb_id = id_tema)
	temaNombre = Tema.objects.get(id_tema=id_tema).nombre_tema
	#Por cada integrante del equipo se va a buscar su participación de la PI
	hora = datetime.datetime.now()
	for i in integrantesEquipo:
		#Si se encuentra la participación de un usuario no pasa nada
		try:
			#Consultamos si existe una paritcipación del usuario relacionada al tema actual
			obj = EvaPreguntaSecundarias.objects.get(estudiante=i ,id_definirProb_pregunta=defProbPreguntaQuery.id_definirProb)
		#Si no encuentra la participación de un usuario entonces manda correo a ese usuario quién no tiene la participación
		except EvaPreguntaSecundarias.DoesNotExist:
			#Obtenemos el id para posteriormente usar el nombre del usuario en el cuerpo del mensaje
			obj2 = User.objects.get(id=i)
			send_mail(
			'Aviso, Faltas tu!',
			f'Hola {obj2.first_name}, tu equipo ya realizó la actividad de evaluar las preguntas secundarias del tema {temaNombre}, faltas tu! Entra a Búsqueda Colaborativa y continua con tu proceso de investigación.\n {hora}',
			settings.EMAIL_HOST_USER,
			[obj2.email],
			fail_silently=False,
			)
	return render(request, 'estudiante/EvPsAvisoNoContinuar.html', {'id_tema':id_tema, 'id_grupo':id_grupo})



@student_required
@login_required
def EvaluacionPS(request,  id_tema, id_grupo):
	#corroborar que el numero de integrantes sea el numero de filter con defquerry 
	temaPreguntaInicial = Tema.objects.get(id_tema=id_tema)
	current_user = get_object_or_404(User, pk=request.user.pk)
	equipo = Equipo.objects.get(estudiantes=current_user.id, grupo_equipo=id_grupo)
	defProbPreguntaQuery = DefinirProblema.objects.get(equipo_definirProb_id = equipo.id_equipo, tema_definirProb_id = temaPreguntaInicial.id_tema)
	#identificamos si existe la participación de un usuario
	participacionPSusuario = EvaPreguntaSecundarias.objects.filter(estudiante=current_user ,id_definirProb_pregunta=defProbPreguntaQuery.id_definirProb)
	#identificamos las participaciones totales del equipo con el 
	participacionPSEquipo = EvaPreguntaSecundarias.objects.filter(id_definirProb_pregunta=defProbPreguntaQuery.id_definirProb)
	#si el usuario ya tiene un campo en EvaPreguntaSecundarias asociado a un definirproblema_id entonces ya hizo ese paso
	integrantesEquipo = Equipo.objects.filter(estudiantes__grupos_inscritos=equipo.grupo_equipo_id, temas_asignados__id_tema=id_tema)
	#corroboramos si existe participación
	if participacionPSusuario.exists():
		#si existe verificamos si el numero total de integrantes del equipo es el numero total de participaciones con el defProbPreguntaQuery_id del equipo
		if participacionPSEquipo.count() == integrantesEquipo.count():
			#redireccionar a pantalla de no continuar Evaluación preguntas seundarias
			return redirect('AMCE:PlanDeInvestigacion', id_grupo=id_grupo, id_tema=id_tema)
		else:
			return redirect('AMCE:AvisoNoContinuarEvaPS', id_grupo=id_grupo, id_tema=id_tema)

	return render(request, "estudiante/1EvaluacionPreguntasSecundarias.html", {'id_tema':id_tema, 'id_grupo':id_grupo})

@student_required
@login_required
def EvaluacionPreSec(request,  id_tema, id_grupo):
	current_user = get_object_or_404(User, pk=request.user.pk)
	temaNombre = Tema.objects.get(id_tema=id_tema).nombre_tema
	equipo = Equipo.objects.get(estudiantes=current_user.id, grupo_equipo=id_grupo)
	defProbPreguntaQuery = DefinirProblema.objects.get(equipo_definirProb_id = equipo.id_equipo, tema_definirProb_id = id_tema)
	#Consulta para obtener la pregunta inicial ganadora y mostrala en el template
	pregunta = Pregunta.objects.get(definirProb_pregunta = defProbPreguntaQuery, ganadora=True, tipo_pregunta=1)
	#Consulta que identifica las preguntas secundarias del equipo actual con el tema actual
	preguntasSec = Pregunta.objects.filter(definirProb_pregunta = defProbPreguntaQuery, tipo_pregunta=2)
	print(defProbPreguntaQuery)
	#verificamos si hay participación del usuario
	preSec = EvaPreguntaSecundarias.objects.filter(estudiante=current_user, id_definirProb_pregunta=defProbPreguntaQuery)
	participacionPSusuario = EvaPreguntaSecundarias.objects.filter(id_definirProb_pregunta=defProbPreguntaQuery.id_definirProb)
	integrantesEquipo = Equipo.objects.filter(estudiantes__grupos_inscritos=equipo.grupo_equipo_id, temas_asignados__id_tema=id_tema)
	#Consulta para obtener los integrantes de equipo para mandar correo
	integrantesEquipoCorreo = Equipo.objects.filter(id_equipo=equipo.id_equipo).values_list('estudiantes', flat=True)
	if preSec.exists():
		if participacionPSusuario.count() == integrantesEquipo.count():
			#redireccionar a pantalla de no continuar Evaluación preguntas seundarias
			return redirect('AMCE:PlanDeInvestigacion', id_grupo=id_grupo, id_tema=id_tema)
		else:
			return redirect('AMCE:AvisoNoContinuarEvaPS', id_grupo=id_grupo, id_tema=id_tema)
	else:
		#permitirle hacer el 
		print('aún no tienes participación')
		#Se hace un request POST para identificar que botón(me gusta, no me gusta, no le entiendo) selecciona el usuario 
		if request.method == 'POST':
			#definimos el numero de iteración del foorloop que lleva como tag name de nuestra template, esto para indetificar el botón que se está seleccinoando con valor 1 o -1
			numBoton = 1
			#iteramos el número de preguntas secundarias que el equipo debe de tener 
			for i in preguntasSec:
				#obtenemos el valor del botón que el usuario selecciona
				option = request.POST.get("options%s" % numBoton)
				numBoton = numBoton + 1
				print(i.id_pregunta)
				if option == '3':
					#se actualiza el valor a +1 en el campo votos
					i.votos = F('votos')+3
					i.save(update_fields=['votos'])
				elif option == '-2':
					#se actualiza el valor a -1 en el campo votos
					i.votos = (F('votos')-2)
					i.save(update_fields=['votos'])
				elif option == '-1':
					#se actualiza el valor a -1 en el campo votos
					i.votos = (F('votos')-1)
					i.save(update_fields=['votos'])
			nuevaPartPS = EvaPreguntaSecundarias(estudiante=current_user, id_definirProb_pregunta=defProbPreguntaQuery)
			nuevaPartPS.save()
			#Obtenemos todas las participaciones del equipo de nuestro actual usuario
			numTotalPartici = EvaPreguntaSecundarias.objects.filter(id_definirProb_pregunta=defProbPreguntaQuery.id_definirProb)
			#Participación actual del estudiante del tema actual para verificar si es la uñtima participación que el equipo necesita para continuar con el sig paso
			par = EvaPreguntaSecundarias.objects.get(estudiante=current_user, id_definirProb_pregunta=defProbPreguntaQuery.id_definirProb)
			#Entero el cual define la ultima participación del equipo
			ultimaParticipacion = integrantesEquipo.count()-1
			try:
				#Si la participación que hizo el estudiante es la ultima participación que se espera, manda el correo
				if par == numTotalPartici[ultimaParticipacion]:
					print('manda correo')
					#Se les notifica a los integrantes del equipo que todos han acabado
					for i in integrantesEquipoCorreo:
						nombreUsuario = User.objects.get(id=i)
						send_mail(
							'Tu equipo ya acabó de evaluar las preguntas secundarias!',
							f'Hola {nombreUsuario.first_name}, el último integrante de tu equipo ha terminado de evaluar la pregunta inicial del tema {temaNombre}. Entra a Búsqueda Colaborativa y continua con tu proceso de investigación.',
							settings.EMAIL_HOST_USER,
							[nombreUsuario.email],
							fail_silently=False,
						)
			#Si no encuentra la participación de un usuario entonces manda correo a ese usuario quién no tiene la participación
			except IndexError:
				print('no se manda correo correo')

			messages.success(request, 'Evaluación guardada correctamente')
			#redireccionar a la misma función para evaluar si sigue o no
			return redirect('AMCE:EvaluacionPreSec', id_grupo=id_grupo, id_tema=id_tema)
	return render(request, "estudiante/2EvaluacionPreguntasSecundarias.html", {'id_tema':id_tema, 'id_grupo':id_grupo, 'temaNombre':temaNombre, 'pregunta':pregunta, 'preguntasSec':preguntasSec})

@student_required
@login_required
def PlanDeInvestigacion(request,  id_tema, id_grupo):
	#Consulta para obtener la pregunta inicial ganadora y mostrala en el template
	current_user = get_object_or_404(User, pk=request.user.pk)
	equipo = Equipo.objects.get(estudiantes=current_user.id, grupo_equipo=id_grupo)
	defProbPreguntaQuery = DefinirProblema.objects.get(equipo_definirProb_id = equipo.id_equipo, tema_definirProb_id = id_tema)
	pregunta = Pregunta.objects.get(definirProb_pregunta = defProbPreguntaQuery, ganadora=True , tipo_pregunta=1)
	temaNombre = Tema.objects.get(id_tema=id_tema).nombre_tema

	#preguntasSec = Pregunta.objects.filter(definirProb_pregunta = defProbPreguntaQuery, tipo_pregunta=2).order_by('votos')
	'''
	for i in preguntasSec:
		if i.votos >= 2:
			i.ganadora = True
			i.save(update_fields=['ganadora'])
	'''
	#Se hace la consulta de las preguntas con más votos de manera ascendente
	preguntasSecGanadas = Pregunta.objects.filter(definirProb_pregunta = defProbPreguntaQuery, tipo_pregunta=2).order_by('votos')

	return render(request, "estudiante/PlanDeInvestigacion.html", {'id_tema':id_tema, 'id_grupo':id_grupo, 'temaNombre':temaNombre, 'pregunta':pregunta, 'preguntasSecGanadas':preguntasSecGanadas})

def ejemplo(request):

	return render(request, "estudiante/ejemplo.html")