from django.urls import path
from .views import (
    RefBookListView,
    RefBookElementsView,
    CheckElementView
)

urlpatterns = [
    path('refbooks/', RefBookListView.as_view(), name='refbooks'),
    path(
        'refbooks/<str:code>/elements/', RefBookElementsView.as_view(),
        name='refbook-elements'),
    path(
        'refbooks/<str:code>/check_element/',
        CheckElementView.as_view(), name='check-element'
    ),
]