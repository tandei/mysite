# Generated by Django 2.2.4 on 2019-09-09 00:20

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0004_auto_20190908_0240'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='blog',
            name='read_num',
        ),
        migrations.CreateModel(
            name='ReadNum',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('read_num', models.IntegerField(default=0)),
                ('blog', models.OneToOneField(on_delete=django.db.models.deletion.DO_NOTHING, to='blog.Blog')),
            ],
        ),
    ]
