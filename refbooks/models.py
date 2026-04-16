from django.db import models
from django.contrib.auth.models import Group


class RefBook(models.Model):
    """Справочник"""

    code = models.CharField(
        max_length=100,
        verbose_name='Код справочника',
        unique=True
    )
    name = models.CharField(
        max_length=300,
        verbose_name='Наименование',
    )
    description = models.TextField(
        verbose_name='Описание',
        blank=True,
        null=True
    )

    class Meta:
        db_table='ref_book'
        verbose_name = verbose_name_plural = 'Справочники'

    def __str__(self):
        return f'{self.code} - {self.name}'



class Version(models.Model):
    """Версия справочника"""

    ref_book = models.ForeignKey(
        RefBook,
        on_delete=models.CASCADE,
        related_name='versions',
    )
    version = models.CharField(max_length=50, verbose_name='Версия')
    start_date = models.DateField(verbose_name='Дата начала действия')

    class Meta:
        db_table='ref_book_versions'
        verbose_name = verbose_name_plural = 'Версия справочников'
        unique_together = [
            ('ref_book', 'version'),
            ('ref_book', 'start_date'),
        ]

    def __str__(self):
        return f'{self.ref_book.code}: {self.version} ({self.start_date})'


class Element(models.Model):
    """Элемент справочника"""

    version = models.ForeignKey(
        Version,
        on_delete=models.CASCADE,
        related_name='elements',
        verbose_name='Версия справочника'
    )
    code = models.CharField(
        max_length=100,
        verbose_name='Код элемента справочника'
    )
    value = models.CharField(
        max_length=300,
        verbose_name='Значение элемента справочника'
    )

    class Meta:
        db_table = 'ref_book_elements'
        verbose_name = verbose_name_plural = 'Элементы справочников'
        unique_together = [('version', 'code')]

    def __str__(self):
        return f'{self.code}: {self.value}'


class Role(models.Model):
    """Справочник ролей (только наименование)"""
    
    code = models.CharField(
        max_length=5,
        verbose_name='Код роли',
        unique=True,
        null=True,
        blank=True
    )
    name = models.CharField(
        max_length=100,
        verbose_name='Наименование роли',
        unique=True
    )
    
    class Meta:
        db_table = 'roles'
        verbose_name = verbose_name_plural = 'Справочник ролей'
    
    def __str__(self):
        return f'{self.code} - {self.name}'


class GroupRole(models.Model):
    """Связь группы с ролью из справочника ролей."""
    
    group = models.OneToOneField(
        Group,
        on_delete=models.CASCADE,
        related_name='group_role',
        verbose_name='Группа'
    )
    role = models.ForeignKey(
        Role,
        on_delete=models.CASCADE,
        related_name='group_roles',
        verbose_name='Роль'
    )
    
    class Meta:
        db_table = 'group_roles'
        verbose_name = verbose_name_plural = 'Роли групп'
        unique_together = [('group', 'role')]
    
    def __str__(self):
        return f'{self.group.name} - {self.role.name}'
