from rest_framework import generics, permissions
from .models import ShoppingSession
from .serializers import ShoppingSessionSerializer
from rest_framework.response import Response
from rest_framework import status


class CreateSessionView(generics.CreateAPIView):
    serializer_class = ShoppingSessionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(shopper=self.request.user)


class SessionDetailView(generics.RetrieveAPIView):
    queryset = ShoppingSession.objects.all()
    serializer_class = ShoppingSessionSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'id'


class AddItemView(generics.UpdateAPIView):
    queryset = ShoppingSession.objects.all()
    serializer_class = ShoppingSessionSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'id'

    def update(self, request, *args, **kwargs):
        session = self.get_object()
        item = request.data.get('item')
        if not item:
            return Response({'detail': 'item required'}, status=status.HTTP_400_BAD_REQUEST)
        session.cart.append(item)
        session.save()
        return Response(self.get_serializer(session).data)

    def post(self, request, *args, **kwargs):
        # tests expect POST to add an item
        return self.update(request, *args, **kwargs)
