from django.contrib import admin
from django.urls import include, path
from AMCE.forms import CustomAuthForm
from django.contrib.auth import views as auth_views

#se agrega para heroku
#from django.conf import settings 
#from django.conf.urls.static import static

# Views
import AMCE.views as views

app_name = "AMCE"
urlpatterns = [
#URLS CRECIÓN DE TIPOS DE USUARIOS
path('estudiante/vistaEstudiante/', views.vistaAlumno, name = 'vistaAlumno'),
path('profesor/vistaProfesor/', views.vistaProfesor, name = 'vistaProfesor'),
# URLS COMPARTIDAS
path('', views.index, name = 'index'),
path('registro/', views.signup, name = 'signup'),
path('registro/estudiante/', views.EstSignup.as_view(), name='EstSignup'),
path('registro/profesor/', views.ProfSignup.as_view(), name='ProfSignup'),
# URLS ESTUDIANTE
path('estudiante/MisGrupos/', views.EstMisGrupos, name = 'EstMisGrupos'),
path('estudiante/InscribirGrupo/', views.EstInscribirGrupo, name = 'EstInscribirGrupo'),
path('estudiante/Grupo/<str:id_grupo>/', views.EstPaginaGrupo, name = 'EstPaginaGrupo'),
path('estudiante/Grupo/<str:id_grupo>/Tema/<str:id_tema>/actividad/aviso', views.AvisoNoContinuar, name = 'AvisoNoContinuar'),

path('estudiante/Grupo/<str:id_grupo>/Tema/<str:id_tema>/', views.AnalisisPreguntaInicial, name = 'AnalisisPreguntaInicial'),
path('estudiante/Grupo/<str:id_grupo>/Tema/<str:id_tema>/PreguntaInicial/', views.postPreguntaInicial, name = 'PreguntaInicial'),
path('estudiante/Grupo/<str:id_grupo>/Tema/<str:id_tema>/PreguntaInicial/actividad/aviso', views.AvisoNoContinuarAnalisis, name = 'AvisoNoContinuarAnalisis'), 
path('estudiante/Grupo/<str:id_grupo>/Tema/<str:id_tema>/PreguntaInicial/FeedPreguntaInicial/', views.feedPIHecha, name = 'feedPIHecha'),
path('estudiante/Grupo/<str:id_grupo>/Tema/<str:id_tema>/PreguntaInicial/DefiniciónPreguntaInicial/', views.defPreguntaInicial, name = 'defPreguntaInicial'),
path('estudiante/Grupo/<str:id_grupo>/Tema/<str:id_tema>/PreguntasSecundarias/', views.PreguntasSecundarias, name = 'PreguntasSecundarias'),
path('estudiante/Grupo/<str:id_grupo>/Tema/<str:id_tema>/PreguntasSecundarias/actividad/aviso', views.PSAvisoNoContinuar, name = 'PSAvisoNoContinuar'),
path('estudiante/Grupo/<str:id_grupo>/Tema/<str:id_tema>/PreguntasSecundarias/evaluación', views.EvaluacionPS, name = 'EvaluacionPS'),
path('estudiante/Grupo/<str:id_grupo>/Tema/<str:id_tema>/PreguntasSecundarias/evaluación/evaluacionsecundarias', views.EvaluacionPreSec, name = 'EvaluacionPreSec'),
path('estudiante/Grupo/<str:id_grupo>/Tema/<str:id_tema>/PreguntasSecundarias/evaluación/aviso', views.AvisoNoContinuarEvaPS, name = 'AvisoNoContinuarEvaPS'),
path('estudiante/Grupo/<str:id_grupo>/Tema/<str:id_tema>/PreguntasSecundarias/evaluación/actividad/plandeevaluación', views.PlanDeInvestigacion, name = 'PlanDeInvestigacion'),
path('estudiante/ejemplo', views.ejemplo, name = 'ejemplo'),
# URLS PROFESOR
path('profesor/MisGrupos/', views.ProfMisGrupos, name = 'ProfMisGrupos'),
path('profesor/CrearGrupo/', views.ProfCrearGrupo, name = 'ProfCrearGrupo'),
path('profesor/Grupo/<str:id_grupo>/', views.ProfPaginaGrupo, name = 'ProfPaginaGrupo'),
path('profesor/Grupo/<str:id_grupo>/CrearEquipo/', views.ProfCrearEquipo, name = 'ProfCrearEquipo'),
path('profesor/Grupo/<str:id_grupo>/Equipo/<int:id_equipo>/', views.ProfPaginaEquipo, name = 'ProfPaginaEquipo'),
path('profesor/Grupo/<str:id_grupo>/AsignarTema/', views.ProfAsignarTemaGrupo, name = 'ProfAsignarTemaGrupo'),
path('profesor/Grupo/<str:id_grupo>/Tema/<int:id_tema>/', views.ProfTemaAsignado, name = 'ProfTemaAsignado'),
path('profesor/Grupo/<str:id_grupo>/Tema/<int:id_tema>/Equipo/<int:id_equipo>', views.ProfProgresoEquipo, name = 'ProfProgresoEquipo'),
path('profesor/MisTemas/', views.ProfMisTemas, name = 'ProfMisTemas'),
path('profesor/CrearTema/', views.ProfCrearTema, name = 'ProfCrearTema')
]

