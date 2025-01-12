import random

from django.db.models import F
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from examples.filters import ExampleFilter
from examples.models import Example, ExampleState
from examples.serializers import ExampleSerializer
from projects.models import Project
from projects.permissions import IsProjectAdmin, IsProjectStaffAndReadOnly


class ExampleList(generics.ListCreateAPIView):
    serializer_class = ExampleSerializer
    permission_classes = [IsAuthenticated & (IsProjectAdmin | IsProjectStaffAndReadOnly)]
    filter_backends = (DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter)
    ordering_fields = ("created_at", "updated_at", "score")
    search_fields = ("text", "filename")
    model = Example
    filterset_class = ExampleFilter

    @property
    def project(self):
        return get_object_or_404(Project, pk=self.kwargs["project_id"])

    def get_queryset(self):
        queryset = self.model.objects.filter(project=self.project)
        examples = queryset.values("id")
        status = self.request.GET.get("status")
        id = self.request.GET.get("id")

        if status == "none":
            if id != '0':
                queryset = self.model.objects.filter(project=self.project, id=id)
            else:
                queryset = self.model.objects.filter(project=self.project)

        else:
            # get finished examples
            if self.project.collaborative_annotation:
                finished = ExampleState.objects.filter(example_id__in=examples).values("example_id")
            else:
                finished = ExampleState.objects.filter(example_id__in=examples, confirmed_by=self.request.user).values("example_id")

            if status == "inprogress":
                if id != '0':
                    queryset = self.model.objects.filter(project=self.project, id=id).exclude(id__in=finished)
                else:
                    queryset = self.model.objects.filter(project=self.project).exclude(id__in=finished)
                    
            elif status == "finished":
                if id != '0':
                    queryset = self.model.objects.filter(project=self.project, id=id, id__in=finished)
                else:
                    queryset = self.model.objects.filter(project=self.project, id__in=finished)
                    
        if self.project.random_order:
            # Todo: fix the algorithm.
            random.seed(self.request.user.id)
            value = random.randrange(2, 20)
            queryset = queryset.annotate(sort_id=F("id") % value).order_by("sort_id", "id")
        else:
            queryset = queryset.order_by("created_at")
        return queryset

    def perform_create(self, serializer):
        serializer.save(project=self.project)

    def delete(self, request, *args, **kwargs):
        queryset = self.project.examples
        delete_ids = request.data["ids"]
        if delete_ids:
            queryset.filter(pk__in=delete_ids).delete()
        else:
            queryset.all().delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ExampleDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Example.objects.all()
    serializer_class = ExampleSerializer
    lookup_url_kwarg = "example_id"
    permission_classes = [IsAuthenticated & (IsProjectAdmin | IsProjectStaffAndReadOnly)]
