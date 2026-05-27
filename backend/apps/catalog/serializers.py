from rest_framework import serializers
from .models import CoinType


class CoinTypeSerializer(serializers.ModelSerializer):
    icon_url = serializers.SerializerMethodField()

    class Meta:
        model = CoinType
        fields = ["id", "name", "slug", "conversion_rate", "icon_url", "active"]

    def get_icon_url(self, obj):
        request = self.context.get("request")
        if obj.icon and request:
            return request.build_absolute_uri(obj.icon.url)
        return None
