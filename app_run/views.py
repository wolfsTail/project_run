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
from django.db import transaction
from django.db.models import Count, Q

from .models import AthleteInfo, Challenge, Position, Run
from .serializers import (
    RunSerializer, 
    UserSerializer, 
    AthleteInfoSerializer, 
    ChallengeSerializer,
    PositionSerializer,
)



TEN_RUNS_CHALLENGE = "Сделай 10 Забегов!"

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

        with transaction.atomic():
            current.status = Run.STATUS_CHOICES[2][0]
            current.save(update_fields=["status"])

            finished_count = Run.objects.filter(
                athlete=current.athlete, status="finished"
            ).count()

            if finished_count == 10 and not Challenge.objects.filter(
                athlete=current.athlete, full_name=TEN_RUNS_CHALLENGE
            ).exists():
                Challenge.objects.create(
                    athlete=current.athlete, full_name=TEN_RUNS_CHALLENGE
                )

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

        t = self.request.query_params.get('type')
        if t == 'coach':
            qs = qs.filter(is_staff=True)
        elif t == 'athlete':
            qs = qs.filter(is_staff=False)

        return qs


class AthleteInfoView(APIView):
    def get_user(self, user_id: int) -> User:
        return get_object_or_404(User, pk=user_id)

    def get(self, request, user_id: int):
        user = self.get_user(user_id)
        info, _ = AthleteInfo.objects.get_or_create(user=user)
        data = AthleteInfoSerializer(info).data
        return Response(data, status=status.HTTP_200_OK)

    def put(self, request, user_id: int):
        user = self.get_user(user_id)
        info, _ = AthleteInfo.objects.get_or_create(user=user)
        serializer = AthleteInfoSerializer(instance=info, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class ChallengeViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Challenge.objects.select_related("athlete").order_by("-created_at")
    serializer_class = ChallengeSerializer
    pagination_class = OptionalPagePagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["athlete"]


class PositionViewSet(viewsets.ModelViewSet):
    queryset = Position.objects.select_related("run").order_by("id")
    serializer_class = PositionSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["run"]
    http_method_names = ["get", "post", "delete", "head", "options"]

    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    def get_queryset(self):
        qs = super().get_queryset()
        run_id = self.request.query_params.get("run")
        if run_id:
            qs = qs.filter(run_id=run_id)
        return qs
