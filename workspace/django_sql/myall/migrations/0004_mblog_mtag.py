# Generated by Django 3.0 on 2023-05-13 03:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myall', '0003_auto_20230508_0043'),
    ]

    operations = [
        migrations.CreateModel(
            name='MTag',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=10)),
            ],
            options={
                'verbose_name': 'M_Tag',
                'verbose_name_plural': 'M_Tag',
                'db_table': 'M_Tag',
                'unique_together': {('name',)},
            },
        ),
        migrations.CreateModel(
            name='MBlog',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=10)),
                ('content', models.CharField(max_length=40)),
                ('good_point', models.IntegerField(default=0)),
                ('tags', models.ManyToManyField(blank=True, related_name='tags_mtag', to='myall.MTag')),
            ],
            options={
                'verbose_name': 'M_Blog',
                'verbose_name_plural': 'M_Blog',
                'db_table': 'M_Blog',
                'unique_together': {('title',)},
            },
        ),
    ]
