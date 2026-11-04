from rest_framework import serializers
from .models import CoinType


class CoinTypeSerializer(serializers.ModelSerializer):
    icon_url = serializers.SerializerMethodField()
    min_coins = serializers.IntegerField(read_only=True)
    step_coins = serializers.IntegerField(read_only=True)
    pack_price_kes = serializers.IntegerField(read_only=True)

    class Meta:
        model = CoinType
        fields = ["id", "name", "slug", "price_per_1000", "conversion_rate",
                  "min_coins", "step_coins", "pack_price_kes", "icon_url", "active"]
                  
    def get_icon_url(self, obj):
        request = self.context.get("request")
        if obj.icon and request:
            return request.build_absolute_uri(obj.icon.url)
        return None
