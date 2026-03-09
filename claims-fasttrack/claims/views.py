from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import Claim, AuditEvent
from .serializers import ClaimSerializer

class ClaimViewSet(viewsets.ModelViewSet):
    serializer_class = ClaimSerializer

    def get_queryset(self):
        queryset = Claim.objects.all()
        status_param = self.request.query_params.get('status', None)
        if status_param:
            queryset = queryset.filter(status=status_param)
        return queryset
    
    def perform_create(self, serializer):
        claim = serializer.save()
        AuditEvent.objects.create(claim=claim, action='CLAIM_CREATED', details=f'Claim created with status {claim.status}.')
        claim.perform_triage()  # Perform triage after saving the claim

    @action(detail=True, methods=['get'])
    def audit(self, request, pk=None):
        claim = self.get_object()
        audit_events = claim.audit_logs.all().order_by('-timestamp')
        data = [{'action': event.action, 'timestamp': event.timestamp, 'details': event.details} for event in audit_events]
        return Response(data)
    
    # claims/views.py

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """Endpoint: POST /api/claims/{id}/approve/"""
        claim = self.get_object()
        
        # In a real app, you might update the description here too
        claim.status = 'APPROVED'
        claim.save()

        AuditEvent.objects.create(
            claim=claim,
            action='HUMAN_APPROVAL',
            details=f"Claim approved by staff. Ready for next steps."
        )
        
        return Response({'status': 'Claim approved successfully'})

    @action(detail=True, methods=['post'])
    def retry(self, request, pk=None):
        """Endpoint: POST /api/claims/{id}/retry/"""
        claim = self.get_object()
        
        # Reset to NEW and run triage again
        claim.status = 'NEW'
        claim.save()

        AuditEvent.objects.create(
            claim=claim,
            action='RETRY_TRIGGERED',
            details="Manual retry initiated by staff."
        )

        # Re-run the triage logic from Day 3
        claim.perform_triage()
        
        return Response({'status': 'Triage retried', 'current_status': claim.status})