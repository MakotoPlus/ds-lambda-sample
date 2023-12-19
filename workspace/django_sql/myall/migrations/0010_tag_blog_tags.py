# Generated by Django 3.0 on 2023-08-12 15:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myall', '0009_blogtag_create_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='tag',
            name='blog_tags',
            field=models.ManyToManyField(through='myall.BlogTag', to='myall.Blog'),
        ),
    ]