from rest_framework import serializers
from .models import Claim, AuditEvent

class AuditEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = AuditEvent
        fields = ['timestamp', 'action', 'details']

class ClaimSerializer(serializers.ModelSerializer):
    # Include audit logs so the UI can show the history easily
    audit_logs = AuditEventSerializer(many=True, read_only=True)

    class Meta:
        model = Claim
        fields = ['id', 'status', 'description', 'created_at', 'audit_logs']
        read_only_fields = ['id', 'status', 'created_at']