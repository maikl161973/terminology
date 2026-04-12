from django.urls import path
from .views import (
    RefBookListView,
    RefBookElementsView,
    CheckElementView
)

urlpatterns = [
    path('refbooks/', RefBookListView.as_view(), name='refbooks'),
    path(
        'refbooks/<str:id>/elements/', RefBookElementsView.as_view(),
        name='refbook-elements'),
    path(
        'refbooks/<str:id>/check_element/',
        CheckElementView.as_view(), name='check-element'
    ),
]