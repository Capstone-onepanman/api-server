# Generated by Django 2.2.10 on 2020-03-19 08:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('onepanman_api', '0012_auto_20200319_1658'),
    ]

    operations = [
        migrations.AlterField(
            model_name='language',
            name='name',
            field=models.CharField(choices=[('C', 'C'), ('C++', 'C++'), ('PYTHON', 'PYTHON'), ('JAVA', 'JAVA')], db_column='NAME', max_length=30, unique=True, verbose_name='language name'),
        ),
    ]
