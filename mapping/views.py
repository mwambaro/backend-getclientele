from rest_framework import generics, permissions, status
from rest_framework.response import Response
from .models import AlleyTrace
from .serializers import AlleyTraceStartSerializer, AlleyTraceStopSerializer


class StartTraceView(generics.CreateAPIView):
    serializer_class = AlleyTraceStartSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(mapper=self.request.user)


class StopTraceView(generics.UpdateAPIView):
    serializer_class = AlleyTraceStopSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = AlleyTrace.objects.all()
    lookup_field = 'id'

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.points = request.data.get('points', [])
        instance.active = False
        instance.save()
        # schedule map graph build
        try:
            from .tasks import build_map_graph
            build_map_graph.delay(instance.market_id)
        except Exception:
            pass
        return Response(self.get_serializer(instance).data)

    def post(self, request, *args, **kwargs):
        # allow POST to stop a trace (tests expect POST)
        return self.update(request, *args, **kwargs)
