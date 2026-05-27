from rest_framework.generics import ListAPIView
from rest_framework.permissions import AllowAny
from .models import CoinType
from .serializers import CoinTypeSerializer


class CoinTypeListView(ListAPIView):
    """
    GET /api/coins/
    Returns all active coin types with their conversion rates.
    """
    queryset = CoinType.objects.filter(active=True)
    serializer_class = CoinTypeSerializer
    permission_classes = [AllowAny]
