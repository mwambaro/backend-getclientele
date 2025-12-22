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
        # schedule map graph build: in tests Celery runs tasks eagerly (synchronously),
        # so call `.delay()` directly to keep existing behavior. In normal dev, delegate
        # the .delay() call to a background thread to avoid blocking when the broker
        # is unreachable.
        try:
            from .tasks import build_map_graph
            from celery import current_app
            from threading import Thread

            def _enqueue(market_id):
                try:
                    build_map_graph.delay(market_id)
                except Exception as exc:
                    import logging
                    logging.getLogger(__name__).exception("Failed to enqueue build_map_graph: %s", exc)

            if getattr(current_app.conf, 'task_always_eager', False):
                # run synchronously (tests rely on this)
                _enqueue(instance.market_id)
            else:
                Thread(target=_enqueue, args=(instance.market_id,), daemon=True).start()
        except Exception:
            pass
        return Response(self.get_serializer(instance).data)

    def post(self, request, *args, **kwargs):
        # allow POST to stop a trace (tests expect POST)
        return self.update(request, *args, **kwargs)
