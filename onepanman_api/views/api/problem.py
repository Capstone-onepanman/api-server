from onepanman_api.permissions import IsAdminUser, IsLoggedInUserOrAdmin, UserReadOnly
from rest_framework import viewsets, status
from rest_framework.response import Response
from . import mixins

from onepanman_api import serializers, models, pagination


class ProblemViewSet(mixins.VersionedSchemaMixin,
                     viewsets.ModelViewSet):
    lookup_url_kwarg = 'id'
    serializer_class = serializers.ProblemSerializer
    http_method_names = ['get', 'post', 'delete', 'put']

    #permission_classes = [UserReadOnly]

    def list(self, request, *args, **kwargs):
        return self.get_response_list_for(models.Problem.objects.all(), serializers.ProblemSerializer)

    def retrieve(self, request, *args, **kwargs):
        return self.get_response_for(models.Problem.objects.get(id=kwargs['id']), False, serializers.ProblemSerializer)

    def create(self, request, *args, **kwargs):
        try:
            serializer = serializers.ProblemSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            data = serializer.validated_data
            print(self.request.user, request.user)
            instance = models.Problem.objects.create(editor=self.request.user,
                                                     title=data['title'],
                                                     description=data['description'],
                                                     limit_time=data['limit_time'],
                                                     limit_memory=data['limit_memory'],
                                                     level=data['level'],
                                                     popularity=data['popularity'],
                                                     icon=data['icon'],
                                                     thunmbnail=data['thumbnail'],
                                                     board_size=data['board_size'],
                                                     board_info=data['board_info'],
                                                     rule=data['rule'])

            return self.get_response_for(instance, True, serializers.ProblemSerializer)

        except Exception as e:
            print(e)    # 나중에 Log 작업 해라
            return Response(status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        try:
            serializer = serializers.ProblemSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            data = serializer.validated_data

            qs = models.Problem.objects.get(id=int(kwargs['id']))
            qs.title = data['title']
            qs.description = data['description']
            qs.limit_time = data['limit_time']
            qs.limit_memory = data['limit_memory']
            qs.level = data['level']
            qs.popularity = data['popularity']
            qs.icon = data['icon']
            qs.thumbnail = data['thumbnail']
            qs.board_size = data['board_size']
            qs.board_info = data['board_info']
            qs.rule = data['rule']
            qs.save()

            return self.get_response_for(qs, False, serializers.ProblemSerializer)

        except Exception as e:
            print(e)
            return Response(status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        try:
            models.Problem.objects.get(id=kwargs['id']).delete()

        except Exception as e:
            print(e)  # 나중에 Log 작업 해라
            return Response(status=status.HTTP_400_BAD_REQUEST)

        return Response(status=status.HTTP_400_BAD_REQUEST)


