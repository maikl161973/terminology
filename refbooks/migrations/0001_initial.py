import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='RefBook',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(max_length=100, unique=True, verbose_name='Код справочника')),
                ('name', models.CharField(max_length=300, verbose_name='Наименование')),
                ('description', models.TextField(blank=True, null=True, verbose_name='Описание')),
            ],
            options={
                'verbose_name': 'Справочники',
                'verbose_name_plural': 'Справочники',
                'db_table': 'ref_book',
            },
        ),
        migrations.CreateModel(
            name='Version',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('version', models.CharField(max_length=50, verbose_name='Версия')),
                ('start_date', models.DateField(verbose_name='Дата начала действия')),
                ('ref_book', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='versions', to='refbooks.refbook')),
            ],
            options={
                'verbose_name': 'Версия справочников',
                'verbose_name_plural': 'Версия справочников',
                'db_table': 'ref_book_versions',
                'unique_together': {('ref_book', 'start_date'), ('ref_book', 'version')},
            },
        ),
        migrations.CreateModel(
            name='Element',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(max_length=100, verbose_name='Код элемента справочника')),
                ('value', models.CharField(max_length=300, verbose_name='Значение элемента справочника')),
                ('version', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='elements', to='refbooks.version', verbose_name='Версия справочника')),
            ],
            options={
                'verbose_name': 'Элементы справочников',
                'verbose_name_plural': 'Элементы справочников',
                'db_table': 'ref_book_elements',
                'unique_together': {('version', 'code')},
            },
        ),
    ]
