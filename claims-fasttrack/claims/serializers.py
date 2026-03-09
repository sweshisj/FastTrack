from rest_framework import serializers
from .models import Claim

class ClaimSerializer(serializers.ModelSerializer):
    class Meta:
        model = Claim
        fields = ['id', 'status', 'description', 'created_at']
        read_only_fields = ['id', 'status', 'created_at']