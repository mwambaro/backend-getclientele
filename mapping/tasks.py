from celery import shared_task
from .models import AlleyTrace

@shared_task
def build_map_graph(market_id):
    # Placeholder: aggregate traces and build a graph (nodes/edges)
    traces = AlleyTrace.objects.filter(market_id=market_id)
    # perform aggregation - here we just return counts for demo
    return {'market_id': market_id, 'trace_count': traces.count()}
