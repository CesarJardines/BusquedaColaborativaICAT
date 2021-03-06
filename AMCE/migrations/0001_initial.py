# Generated by Django 3.2.5 on 2022-06-15 01:21

import django.contrib.auth.models
import django.contrib.auth.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='Grupo',
            fields=[
                ('id_grupo', models.CharField(max_length=10, primary_key=True, serialize=False)),
                ('nombre_grupo', models.CharField(max_length=100)),
                ('materia', models.CharField(blank=True, max_length=100, null=True)),
                ('institucion', models.CharField(blank=True, max_length=100, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='ParticipacionEst',
            fields=[
                ('id_actividad', models.AutoField(primary_key=True, serialize=False)),
                ('fecha', models.DateTimeField(default=django.utils.timezone.now)),
                ('contentido', models.TextField(null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Tema',
            fields=[
                ('id_tema', models.AutoField(primary_key=True, serialize=False)),
                ('nombre_tema', models.CharField(max_length=100)),
                ('preguntas_secundarias', models.IntegerField(default=1)),
            ],
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(error_messages={'unique': 'A user with that username already exists.'}, help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.', max_length=150, unique=True, validators=[django.contrib.auth.validators.UnicodeUsernameValidator()], verbose_name='username')),
                ('first_name', models.CharField(blank=True, max_length=150, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('email', models.EmailField(blank=True, max_length=254, verbose_name='email address')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('es_estudiante', models.BooleanField(default=False)),
                ('es_profesor', models.BooleanField(default=False)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.Group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.Permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
                'abstract': False,
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='Estudiante',
            fields=[
                ('user_estudiante', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to='AMCE.user')),
            ],
        ),
        migrations.CreateModel(
            name='Profesor',
            fields=[
                ('user_profesor', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to='AMCE.user')),
            ],
        ),
        migrations.CreateModel(
            name='Equipo',
            fields=[
                ('id_equipo', models.AutoField(primary_key=True, serialize=False)),
                ('nombre_equipo', models.CharField(max_length=100)),
                ('grupo_equipo', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='AMCE.grupo')),
                ('temas_asignados', models.ManyToManyField(blank=True, to='AMCE.Tema')),
            ],
        ),
        migrations.CreateModel(
            name='DefinirProblema',
            fields=[
                ('id_definirProb', models.AutoField(primary_key=True, serialize=False)),
                ('preguntas_secundarias', models.IntegerField(default=1)),
                ('fuentes', models.IntegerField(default=1)),
                ('equipo_definirProb', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='AMCE.equipo')),
                ('tema_definirProb', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='AMCE.tema')),
            ],
        ),
        migrations.AddField(
            model_name='tema',
            name='profesor_tema',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='AMCE.profesor'),
        ),
        migrations.CreateModel(
            name='Pregunta',
            fields=[
                ('id_pregunta', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to='AMCE.participacionest')),
                ('tipo_pregunta', models.PositiveSmallIntegerField(choices=[(1, 'inicial'), (2, 'secundaria'), (10, 'otro')], default=10)),
                ('votos', models.IntegerField(default=0)),
                ('ganadora', models.BooleanField(default=False)),
                ('definirProb_pregunta', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='AMCE.definirproblema')),
            ],
        ),
        migrations.AddField(
            model_name='participacionest',
            name='estudiante_part',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='post', to='AMCE.estudiante'),
        ),
        migrations.AddField(
            model_name='grupo',
            name='profesor_grupo',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='AMCE.profesor'),
        ),
        migrations.CreateModel(
            name='EvaluacionPreguntaSecundarias',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('id_definirProb_pregunta', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='AMCE.definirproblema')),
                ('estudiantes', models.ManyToManyField(blank=True, to='AMCE.Estudiante')),
            ],
        ),
        migrations.AddField(
            model_name='estudiante',
            name='grupos_inscritos',
            field=models.ManyToManyField(blank=True, to='AMCE.Grupo'),
        ),
        migrations.AddField(
            model_name='equipo',
            name='estudiantes',
            field=models.ManyToManyField(blank=True, to='AMCE.Estudiante'),
        ),
        migrations.CreateModel(
            name='ComentariosPreguntaInicial',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('participacionEst', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='AMCE.participacionest')),
                ('pregunta', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='AMCE.pregunta')),
            ],
        ),
    ]
