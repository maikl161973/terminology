from django.shortcuts import get_object_or_404
from django.utils.dateparse import parse_date
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import RefBook, Version, Element
from .serializers import RefBookSerializer, ElementSerializer


class RefBookListView(APIView):
    """Список справочников."""

    serializer_class = RefBookSerializer

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                'date',
                openapi.IN_QUERY,
                description="Дата в формате ГГГГ-ММ-ДД",
                type=openapi.TYPE_STRING,
                required=False,
                max_length=50
            ),
        ]
    )
    def get(self, request, *args, **kwargs):
        # Валидация даты
        date_param = request.query_params.get('date')
        queryset = RefBook.objects.all()

        if date_param:
            on_date = parse_date(date_param)
            queryset = queryset.filter(
                versions__start_date__lte=on_date
            )
        return Response({
            'refbooks':self.serializer_class(queryset, many=True).data})


class RefBookElementsView(APIView):
    """Элементы справочника."""

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                'version',
                openapi.IN_QUERY,
                description="Версия справочника",
                type=openapi.TYPE_STRING,
                required=False,
                max_length=50
            ),
        ]
    )
    def get(self, request, id):
        ref_book = get_object_or_404(RefBook, code=id)
        version_param = request.query_params.get('version')
        if version_param:
            version = get_object_or_404(
                Version,
                ref_book=ref_book,
                version=version_param
            )
        else:
            version = ref_book.current_version()
            if not version:
                return Response(
                    {
                        'detail': 'Нет текущей версии для данного справочника'},
                    status=status.HTTP_404_NOT_FOUND
                )

        elements = version.elements.all()
        serializer = ElementSerializer(elements, many=True)
        return Response({'elements': serializer.data})


class CheckElementView(APIView):
    """Проверка элемента справочника"""

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                'code',
                openapi.IN_QUERY,
                description="Код элемента",
                type=openapi.TYPE_STRING,
                max_length=100,
                min_length=1,
                required=True,
            ),
            openapi.Parameter(
                'value',
                openapi.IN_QUERY,
                description="Значение элемента",
                type=openapi.TYPE_STRING,
                max_length=300,
                min_length=1,
                required=True,
            ),
            openapi.Parameter(
                'version',
                openapi.IN_QUERY,
                description="Версия справочника",
                type=openapi.TYPE_STRING,
                max_length=50,
                required=False,
            ),
        ]
    )
    def get(self, request, id):
        ref_book = get_object_or_404(RefBook, code=id)
        code_param = request.query_params.get('code')
        value_param = request.query_params.get('value')
        version_param = request.query_params.get('version')

        if not code_param or not value_param:
            return Response(
                {'detail': 'Не указаны code или value'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if version_param:
            version = get_object_or_404(
                Version,
                ref_book=ref_book,
                version=version_param
            )
        else:
            version = ref_book.current_version()
            if not version:
                return Response({'exists': False})

        find = Element.objects.filter(
            version=version,
            code=code_param,
            value=value_param
        ).exists()

        return Response({'exists': find})
