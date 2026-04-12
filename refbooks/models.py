import datetime

from django.db import models


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

    def current_version(self, date=datetime.date.today()):
        """Текущая версия справочника на дату."""

        return self.versions.filter(
            start_date__lte=date
        ).order_by('-start_date').first()


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
