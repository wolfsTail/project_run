from rest_framework.decorators import api_view
from rest_framework.filters import SearchFilter
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.filters import OrderingFilter
from rest_framework.pagination import PageNumberPagination
from rest_framework import viewsets
from rest_framework import status

from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from django.http import Http404
from django_filters.rest_framework import DjangoFilterBackend

from .models import Run
from .serializers import RunSerializer, UserSerializer

@api_view(['GET'])
def contacts_view(request):
    return Response(
        {
            'company_name': 'Рога и панцирь',
            'slogan': 'Бегаем или за кем-то или от кого-то',
            'contacts': 'NDA'
        }
    )


class PagePagination(PageNumberPagination):
    page_size = 5
    page_size_query_param = 'size'
    max_page_size = 50

class OptionalPagePagination(PageNumberPagination):
    page_size = None
    page_size_query_param = 'size'
    max_page_size = 50

    def get_page_size(self, request):
        if self.page_size_query_param in request.query_params:
            try:
                return self._get_size_from_query(request)
            except ValueError:
                return None
        return None

    def _get_size_from_query(self, request):
        raw = request.query_params[self.page_size_query_param]
        size = int(raw)
        if size <= 0:
            raise ValueError("size must be positive")
        if self.max_page_size:
            size = min(size, self.max_page_size)
        return size


class StartRunApiView(APIView):
    def post(self, request, run_id):
        current = get_object_or_404(Run, id=run_id)

        if current.status != Run.STATUS_CHOICES[0][0]:
            return Response(
                {
                    "detail": "Run already started or finished!",
                    "id": current.id,
                    "status": current.status,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        current.status = Run.STATUS_CHOICES[1][0]
        current.save(update_fields=["status"])

        return Response(
            {
                "id": current.id,
                "status": current.status,
            },
            status=status.HTTP_200_OK,
        )


class StopRunApiView(APIView):
    def post(self, request, run_id):
        current = get_object_or_404(Run, id=run_id)

        if current.status != Run.STATUS_CHOICES[1][0]:
            return Response(
                {
                    "detail": "Run already started or finished!",
                    "id": current.id,
                    "status": current.status,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        current.status = Run.STATUS_CHOICES[2][0]
        current.save(update_fields=["status"])

        return Response(
            {
                "id": current.id,
                "status": current.status,
            },
            status=status.HTTP_200_OK,
        )


class RunViewSet(viewsets.ModelViewSet):
    queryset = Run.objects.select_related('athlete').all()
    serializer_class = RunSerializer
    pagination_class = OptionalPagePagination
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['status', 'athlete']
    ordering_fields = ['created_at']


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    pagination_class = OptionalPagePagination
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['=first_name', '=last_name']
    ordering_fields = ['date_joined']

    def get_queryset(self):
        qs = self.queryset.exclude(is_superuser=True)
        type = self.request.query_params.get('type', None)
        if not type:
            return qs
        if type == 'coach':
            return qs.filter(is_staff=True)
        if type == 'athlete':
            return qs.filter(is_staff=False)
        return qs
