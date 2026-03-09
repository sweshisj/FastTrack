from django.db import models
import uuid

class Claim(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    STATUS_CHOICES = [
        ('NEW', 'New'),
        ('EXCEPTION', 'Exception'),
        ('APPROVED', 'Approved'),
        ('READY_FOR_RPA', 'Ready for RPA'),
        ('PROCESSED', 'Processed'),
        ('FAILED', 'Failed'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='NEW')

    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Claim {self.id} - Status: {self.status}"
    
    def perform_triage(self):
        """
        Simple validation logic. 
        If 'urgent' is in the text but no date is provided, or if the 
        description is too short, move to EXCEPTION.
        """
        is_valid = True
        reason = ""

        if len(self.description) < 10:
            is_valid = False
            reason = "Description too short."

        if not is_valid:
            self.status = 'EXCEPTION'
            self.save()
            AuditEvent.objects.create(claim=self, action='TRIAGE_FAILED', details=reason)

        else:
            AuditEvent.objects.create(claim=self, action='TRIAGE_PASSED', details="Claim passed triage checks.")
    
class AuditEvent(models.Model):
    claim = models.ForeignKey(Claim, on_delete=models.CASCADE, related_name='audit_logs')
    action = models.CharField(max_length=100)
    timestamp = models.DateTimeField(auto_now_add=True)
    details = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.claim.id} - {self.action}"