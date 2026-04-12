from django.test import TestCase
from django.urls import reverse
from datetime import date
from .models import RefBook, Version, Element


class ReferenceBookAPITestCase(TestCase):
    """Тесты для API."""

    def setUp(self):
        self.refbook1 = RefBook.objects.create(
            code='SPEC',
            name='Специальности работников',
            description='Справочник медицинских специальностей'
        )
        self.version1_1 = Version.objects.create(
            ref_book=self.refbook1,
            version='1.0',
            start_date=date(2025, 1, 1)
        )
        self.version1_2 = Version.objects.create(
            ref_book=self.refbook1,
            version='2.0',
            start_date=date(2026, 1, 1)
        )
        Element.objects.create(
            version=self.version1_1,
            code='1',
            value='Терапевт'
        )
        Element.objects.create(
            version=self.version1_1,
            code='2',
            value='Лор'
        )

        self.refbook2 = RefBook.objects.create(
            code='DISEASES',
            name='Болезни',
            description='Справочник болезней'
        )
        self.version2_1 = Version.objects.create(
            ref_book=self.refbook2,
            version='2024',
            start_date=date(2026, 6, 1)
        )
        Element.objects.create(
            version=self.version1_2,
            code='1',
            value='Терапевт (новый)'
        )
        Element.objects.create(
            version=self.version2_1,
            code='EAR',
            value='Болезнь уха'
        )

    def test_refbooks_without_date(self):
        """Получение списка без даты."""

        response = self.client.get(reverse('refbooks'))
        self.assertEqual(response.status_code, 200)

        self.assertIn('refbooks', response.data)
        refbooks = response.data['refbooks']
        self.assertEqual(len(refbooks), 2)
        self.assertEqual(refbooks[0]['code'], 'SPEC')
        self.assertEqual(refbooks[1]['code'], 'DISEASES')

    def test_refbooks_with_date_filter(self):
        """Получение списка на дату."""

        response = self.client.get(reverse('refbooks'), {'date': '2025-05-01'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        refbooks = response.data['refbooks']
        self.assertEqual(refbooks[0]['code'], 'SPEC')

    def test_elements_without_version(self):
        """Получение элементов без указания версии"""

        response = self.client.get(
             reverse('refbook-elements', args=['SPEC'])
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn('elements', response.data)
        elements = response.data['elements']
        self.assertEqual(len(elements), 1)
        self.assertEqual(elements[0]['code'], '1')
        self.assertEqual(elements[0]['value'], 'Терапевт (новый)')

    def test_elements_with_specific_version(self):
        """Получение элементов справочника с указанием версии."""

        response = self.client.get(
            reverse('refbook-elements', args=['SPEC']),
            {'version': '1.0'}
        )
        self.assertEqual(response.status_code, 200)
        elements = response.data['elements']
        self.assertEqual(len(elements), 2)
        codes = {elem['code'] for elem in elements}
        self.assertEqual(codes, {'1', '2'})

    def test_elements_nonexistent_refbook(self):
        """Получение элементов несуществующего справочника."""

        response = self.client.get(
            reverse('refbook-elements', args=['NOREF']))
        self.assertEqual(response.status_code, 404)

    def test_elements_nonexistent_version(self):
        """Получение элементов с несуществующей версией."""

        response = self.client.get(
            reverse('refbook-elements', args=['SPEC']),
            {'version': '99.0'}
        )
        self.assertEqual(response.status_code, 404)

    def test_check_element_exists(self):
        """Проверка наличия элемента"""

        response = self.client.get(
            reverse('check-element', args=['SPEC']),
            {
                'code': '1',
                'value': 'Терапевт',
                'version': '1.0'
            }
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data['exists'])

    def test_check_element_not_exists(self):
        """Проверка отсутствия элемента (неверный код или значение)"""

        response = self.client.get(
            reverse('check-element', args=['SPEC']),
            {
                'code': '1',
                'value': 'Педиатр',
                'version': '1.0'
            }
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.data['exists'])

    def test_check_element_without_version(self):
        """Проверка элемента без версии (текущая)."""

        response = self.client.get(
            reverse('check-element', args=['SPEC']),
            {
                'code': '1',
                'value': 'Терапевт (новый)',
            }
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data['exists'])

    def test_check_element_missing_params(self):
        """Проверка элемента без обязательных параметров (code, value)."""

        response = self.client.get(
            reverse('check-element', args=['SPEC']),
            {'code': '1'}
        )
        self.assertEqual(response.status_code, 400)

    def test_check_element_nonexist_refbook(self):
        """Проверка элемента несуществующего справочника."""

        response = self.client.get(
            reverse('check-element', args=['NOREF']),
            {'code': '1', 'value': 'test'}
        )
        self.assertEqual(response.status_code, 404)
