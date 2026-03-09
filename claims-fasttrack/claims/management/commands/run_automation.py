from django.core.management.base import BaseCommand
import time
from claims.models import Claim, AuditEvent

class Command(BaseCommand):
    help = 'Simulates the background processing of APPROVED claims for RPA'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Worker started... Monitoring for APPROVED claims.'))

        while True:
            # 1. Fetch claims that are ready for processing
            batch = Claim.objects.filter(status='APPROVED')

            if not batch.exists():
                time.sleep(5) # Wait 5 seconds before checking again
                continue

            for claim in batch:
                self.stdout.write(f'Processing Claim: {claim.id}')
                
                # 2. Update status to READY_FOR_RPA (This is our "Idempotency Key" logic)
                # By changing the status immediately, we ensure no other worker grabs it.
                claim.status = 'READY_FOR_RPA'
                claim.save()

                # 3. Simulate the "Heavy Lifting" (Wait 3 seconds)
                time.sleep(3)

                # 4. Record the success
                AuditEvent.objects.create(
                    claim=claim,
                    action='SENT_TO_LEGACY',
                    details="Background worker successfully queued data for RPA portal update."
                )
                
                self.stdout.write(self.style.SUCCESS(f'Successfully moved {claim.id} to RPA Queue.'))

            time.sleep(2)