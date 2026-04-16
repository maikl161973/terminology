from django.urls import reverse
from datetime import date
from django.contrib.auth.models import User, Group
from django.conf import settings
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase
from .models import RefBook, Version, Element, Role, GroupRole
from .permissions import IsAccessPermissionGroup
from rest_framework.test import APIRequestFactory
from rest_framework.request import Request


class ReferenceBookAPITestCase(APITestCase):
    """Тесты для API."""

    def setUp(self):
        super().setUp()
        
        # Создаем тестовые данные справочников
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
        
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.token = Token.objects.create(user=self.user)
        
        self.manager_group = Group.objects.create(name='Руководители')
        self.user.groups.add(self.manager_group)
        self.manager_role = Role.objects.create(
            name='Руководители',
            code=settings.ACCESS_ROLE_CODE
        )
        GroupRole.objects.create(
            group=self.manager_group,
            role=self.manager_role
        )
        
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')

    def test_refbooks_without_date(self):
        """Получение списка без даты."""

        response = self.client.get(reverse('refbooks'))
        self.assertEqual(response.status_code, 200)

        self.assertIn('refbooks', response.data)
        refbooks = response.data['refbooks']
        # Ожидаем 2 справочника: SPEC, DISEASES (роли больше нет в справочниках)
        self.assertEqual(len(refbooks), 2)
        # Проверяем, что все ожидаемые справочники присутствуют
        codes = {ref['code'] for ref in refbooks}
        self.assertEqual(codes, {'SPEC', 'DISEASES'})

    def test_refbooks_with_date_filter(self):
        """Получение списка с фильтром по дате."""

        response = self.client.get(reverse('refbooks'), {'date': '2025-05-01'})
        self.assertEqual(response.status_code, 200)

        self.assertIn('refbooks', response.data)
        refbooks = response.data['refbooks']
        # Ожидаем 1 справочник: SPEC (у него есть версия с датой <= 2025-05-01)
        self.assertEqual(len(refbooks), 1)
        codes = {ref['code'] for ref in refbooks}
        self.assertEqual(codes, {'SPEC'})

    def test_elements_without_version(self):
        """Получение элементов справочника без указания версии."""

        response = self.client.get(reverse('refbook-elements', args=['SPEC']))
        self.assertEqual(response.status_code, 200)

        self.assertIn('elements', response.data)
        elements = response.data['elements']
        # Ожидаем 1 элемент из текущей версии (2.0)
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

        self.assertIn('elements', response.data)
        elements = response.data['elements']
        # Ожидаем 2 элемента из версии 1.0
        self.assertEqual(len(elements), 2)
        codes = {el['code'] for el in elements}
        self.assertEqual(codes, {'1', '2'})

    def test_elements_nonexistent_refbook(self):
        """Запрос элементов несуществующего справочника."""

        response = self.client.get(reverse('refbook-elements', args=['NONEXISTENT']))
        self.assertEqual(response.status_code, 404)

    def test_elements_nonexistent_version(self):
        """Запрос элементов с несуществующей версией."""

        response = self.client.get(
            reverse('refbook-elements', args=['SPEC']),
            {'version': '999.0'}
        )
        self.assertEqual(response.status_code, 404)

    def test_check_element_exists(self):
        """Проверка существования элемента."""

        response = self.client.get(
            reverse('check-element', args=['SPEC']),
            {'code': '1', 'value': 'Терапевт (новый)'}
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn('exists', response.data)
        self.assertTrue(response.data['exists'])

    def test_check_element_not_exists(self):
        """Проверка несуществующего элемента."""

        response = self.client.get(
            reverse('check-element', args=['SPEC']),
            {'code': '999', 'value': 'Несуществующий'}
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn('exists', response.data)
        self.assertFalse(response.data['exists'])

    def test_check_element_without_version(self):
        """Проверка элемента без указания версии (используется текущая)."""

        response = self.client.get(
            reverse('check-element', args=['SPEC']),
            {'code': '1', 'value': 'Терапевт (новый)'}
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data['exists'])

    def test_check_element_missing_params(self):
        """Проверка элемента без обязательных параметров."""

        response = self.client.get(
            reverse('check-element', args=['SPEC']),
            {'code': '1'}
        )
        self.assertEqual(response.status_code, 400)

        response = self.client.get(
            reverse('check-element', args=['SPEC']),
            {'value': 'Терапевт'}
        )
        self.assertEqual(response.status_code, 400)

    def test_check_element_nonexist_refbook(self):
        """Проверка элемента для несуществующего справочника."""

        response = self.client.get(
            reverse('check-element', args=['NONEXISTENT']),
            {'code': '1', 'value': 'Терапевт'}
        )
        self.assertEqual(response.status_code, 404)


class AuthenticationAndPermissionTestCase(APITestCase):
    """Тесты аутентификации и разрешений."""
    
    def setUp(self):
        super().setUp()
        
        self.manager_user = User.objects.create_user(
            username='manager',
            password='password123'
        )
        self.regular_user = User.objects.create_user(
            username='regular',
            password='password123'
        )
        
        self.manager_token = Token.objects.create(user=self.manager_user)
        self.regular_token = Token.objects.create(user=self.regular_user)
        
        self.manager_group = Group.objects.create(name='Руководители')
        self.manager_user.groups.add(self.manager_group)
        
        self.manager_role = Role.objects.create(
            name='Руководители',
            code=settings.ACCESS_ROLE_CODE
        )
        
        GroupRole.objects.create(
            group=self.manager_group,
            role=self.manager_role
        )
        
        self.test_refbook = RefBook.objects.create(
            code='TEST',
            name='Тестовый справочник',
            description='Для тестирования'
        )
        self.test_version = Version.objects.create(
            ref_book=self.test_refbook,
            version='1.0',
            start_date=date(2025, 1, 1)
        )
        Element.objects.create(
            version=self.test_version,
            code='TEST1',
            value='Тестовое значение'
        )
    
    def test_token_authentication_endpoint(self):
        """Тест получения токена."""

        response = self.client.post(
            reverse('api_token_auth'),
            {'username': 'manager', 'password': 'password123'},
            format='json'
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn('token', response.data)
        self.assertEqual(response.data['token'], self.manager_token.key)
        
        response = self.client.post(
            reverse('api_token_auth'),
            {'username': 'manager', 'password': 'wrong'},
            format='json'
        )
        self.assertEqual(response.status_code, 400)
    
    def test_api_access_without_token(self):
        """Тест доступа без токена."""

        self.client.credentials()
        response = self.client.get(reverse('refbooks'))
        self.assertEqual(response.status_code, 401)
    
    def test_api_access_with_token_but_without_role(self):
        """Тест доступа с токеном, но без роли."""

        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.regular_token.key}')
        response = self.client.get(reverse('refbooks'))
        self.assertEqual(response.status_code, 403)
    
    def test_api_access_with_token_and_role(self):
        """Тест доступа к API с токеном и с ролью."""

        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.manager_token.key}')
        response = self.client.get(reverse('refbooks'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('refbooks', response.data)
    
    def test_all_endpoints_protected(self):
        """Проверка, что все эндпоинты защищены."""

        endpoints = [
            {'url': reverse('refbooks'), 'params': {}},
            {'url': reverse('refbook-elements', args=['TEST']), 'params': {}},
            {
                'url': reverse(
                    'check-element', args=['TEST']),
                'params': {'code': 'TEST1', 'value': 'Тестовое значение'}},
        ]
        
        self.client.credentials()
        for endpoint in endpoints:
            response = self.client.get(endpoint['url'], endpoint['params'])
            self.assertEqual(
                response.status_code,
                401,
                f'URL: {endpoint["url"]}')
        
        self.client.credentials(
            HTTP_AUTHORIZATION=f'Token {self.regular_token.key}')
        for endpoint in endpoints:
            response = self.client.get(endpoint['url'], endpoint['params'])
            self.assertEqual(
                response.status_code,
                403,
                f'URL: {endpoint["url"]}')
        
        self.client.credentials(
            HTTP_AUTHORIZATION=f'Token {self.manager_token.key}')
        for endpoint in endpoints:
            response = self.client.get(endpoint['url'], endpoint['params'])
            self.assertEqual(
                response.status_code,
                200,
                f'URL: {endpoint["url"]}')
    
    def test_permission_class_logic(self):
        """Тест логики разрешения IsAccessPermissionGroup."""

        permission = IsAccessPermissionGroup()

        factory = APIRequestFactory()
        request = factory.get('/')
        request.user = self.manager_user
        
        self.assertTrue(permission.has_permission(request, None))
        
        request.user = self.regular_user
        self.assertFalse(permission.has_permission(request, None))
        
        request.user = None
        self.assertFalse(permission.has_permission(request, None))
        
        self.manager_role.delete()
        request.user = self.manager_user
        self.assertFalse(permission.has_permission(request, None))
