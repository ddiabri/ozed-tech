"""
Script to create test data for the ticketing system.
"""
import os
import django
import sys
from datetime import timedelta
from django.utils import timezone

# Setup Django environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ozed_tech_project.settings')
django.setup()

from django.contrib.auth.models import User
from crm.models import Customer
from ticketing.models import Ticket, TicketComment, TicketHistory


def create_test_tickets():
    """Create sample tickets for testing."""

    print("Creating test tickets...")

    # Get or create test users
    admin_user = User.objects.filter(is_superuser=True).first()
    if not admin_user:
        print("No admin user found. Please create a superuser first.")
        return

    # Get other users or use admin
    users = list(User.objects.all()[:3])
    if not users:
        users = [admin_user]

    # Get customers
    customers = list(Customer.objects.all())
    if not customers:
        print("No customers found. Creating sample customers...")
        # Create sample customers
        customers = [
            Customer.objects.create(
                company_name="Tech Solutions Inc",
                email="contact@techsolutions.com",
                phone="555-0101",
                address="123 Tech Street",
                city="San Francisco",
                state="CA",
                country="USA"
            ),
            Customer.objects.create(
                company_name="Global Enterprises",
                email="info@globalent.com",
                phone="555-0102",
                address="456 Business Ave",
                city="New York",
                state="NY",
                country="USA"
            ),
            Customer.objects.create(
                company_name="StartUp Innovations",
                email="hello@startupinno.com",
                phone="555-0103",
                address="789 Innovation Blvd",
                city="Austin",
                state="TX",
                country="USA"
            ),
        ]
        print(f"Created {len(customers)} sample customers")

    # Sample ticket data
    sample_tickets = [
        {
            'subject': 'Login Issues After Password Reset',
            'description': 'Customer is unable to login after resetting their password. They receive an "Invalid credentials" error even with the new password.',
            'status': 'open',
            'priority': 'high',
            'category': 'technical',
            'tags': 'login, authentication, password',
        },
        {
            'subject': 'Billing Discrepancy in Last Invoice',
            'description': 'Customer noticed they were charged twice for the same service in the latest invoice. Need to review and issue credit.',
            'status': 'in_progress',
            'priority': 'urgent',
            'category': 'billing',
            'tags': 'billing, invoice, refund',
        },
        {
            'subject': 'Feature Request: Dark Mode',
            'description': 'Customer has requested a dark mode option for the application to reduce eye strain during night usage.',
            'status': 'new',
            'priority': 'low',
            'category': 'feature_request',
            'tags': 'feature, UI, enhancement',
        },
        {
            'subject': 'Application Crashes on Data Export',
            'description': 'When attempting to export large datasets (>10,000 rows), the application crashes with a timeout error.',
            'status': 'open',
            'priority': 'critical',
            'category': 'bug',
            'tags': 'bug, export, performance',
        },
        {
            'subject': 'Product Information Request',
            'description': 'Customer inquiring about enterprise pricing plans and features comparison with current plan.',
            'status': 'pending',
            'priority': 'medium',
            'category': 'product',
            'tags': 'sales, pricing, enterprise',
        },
        {
            'subject': 'API Integration Documentation Needed',
            'description': 'Customer needs detailed API documentation for integrating with their existing CRM system.',
            'status': 'open',
            'priority': 'medium',
            'category': 'general',
            'tags': 'API, documentation, integration',
        },
        {
            'subject': 'Slow Performance During Peak Hours',
            'description': 'Application response time significantly degrades during peak usage hours (9am-11am EST).',
            'status': 'in_progress',
            'priority': 'high',
            'category': 'technical',
            'tags': 'performance, optimization, scaling',
        },
        {
            'subject': 'Unable to Upload Large Files',
            'description': 'Customer cannot upload files larger than 5MB. Error message: "File size exceeds limit".',
            'status': 'resolved',
            'priority': 'medium',
            'category': 'bug',
            'tags': 'upload, file-size, resolved',
        },
        {
            'subject': 'User Permissions Not Working Correctly',
            'description': 'Admin users are unable to modify certain user permissions. The save button appears disabled.',
            'status': 'new',
            'priority': 'urgent',
            'category': 'bug',
            'tags': 'permissions, admin, security',
        },
        {
            'subject': 'Request for Training Session',
            'description': 'Customer would like to schedule a training session for their team on advanced features.',
            'status': 'pending',
            'priority': 'low',
            'category': 'general',
            'tags': 'training, onboarding, support',
        },
    ]

    created_tickets = []

    for i, ticket_data in enumerate(sample_tickets):
        # Assign to different customers and users
        customer = customers[i % len(customers)]
        assigned_user = users[i % len(users)] if i % 3 != 0 else None  # Leave some unassigned

        # Create due date (some overdue, some upcoming)
        if i % 4 == 0:
            # Make some tickets overdue
            due_date = timezone.now() - timedelta(days=2)
        elif i % 3 == 0:
            # Some tickets due soon
            due_date = timezone.now() + timedelta(days=1)
        else:
            # Others due in the future
            due_date = timezone.now() + timedelta(days=7)

        # Create ticket
        ticket = Ticket.objects.create(
            subject=ticket_data['subject'],
            description=ticket_data['description'],
            status=ticket_data['status'],
            priority=ticket_data['priority'],
            category=ticket_data['category'],
            customer=customer,
            assigned_to=assigned_user,
            created_by=admin_user,
            due_date=due_date,
            estimated_hours=2.0 + (i % 5),
            tags=ticket_data['tags']
        )

        # Add some comments to tickets
        if i % 2 == 0:
            TicketComment.objects.create(
                ticket=ticket,
                author=admin_user,
                content="Thank you for reporting this issue. We are looking into it.",
                is_internal=False
            )

        if i % 3 == 0:
            TicketComment.objects.create(
                ticket=ticket,
                author=admin_user,
                content="Internal note: This is a recurring issue. Need to implement permanent fix.",
                is_internal=True
            )

        # If resolved, set resolved time and add final comment
        if ticket.status == 'resolved':
            ticket.resolved_at = timezone.now() - timedelta(hours=5)
            ticket.actual_hours = 3.5
            ticket.save()

            TicketComment.objects.create(
                ticket=ticket,
                author=admin_user,
                content="Issue has been resolved. Increased file upload limit to 50MB.",
                is_internal=False
            )

        created_tickets.append(ticket)
        print(f"  [OK] Created ticket: {ticket.ticket_number} - {ticket.subject}")

    print(f"\n[SUCCESS] Successfully created {len(created_tickets)} test tickets!")
    print("\nTicket Summary:")
    print(f"  - New: {Ticket.objects.filter(status='new').count()}")
    print(f"  - Open: {Ticket.objects.filter(status='open').count()}")
    print(f"  - In Progress: {Ticket.objects.filter(status='in_progress').count()}")
    print(f"  - Pending: {Ticket.objects.filter(status='pending').count()}")
    print(f"  - Resolved: {Ticket.objects.filter(status='resolved').count()}")
    print(f"\nPriority Summary:")
    print(f"  - Critical: {Ticket.objects.filter(priority='critical').count()}")
    print(f"  - Urgent: {Ticket.objects.filter(priority='urgent').count()}")
    print(f"  - High: {Ticket.objects.filter(priority='high').count()}")
    print(f"  - Medium: {Ticket.objects.filter(priority='medium').count()}")
    print(f"  - Low: {Ticket.objects.filter(priority='low').count()}")
    print(f"\nOther Statistics:")
    print(f"  - Assigned: {Ticket.objects.filter(assigned_to__isnull=False).count()}")
    print(f"  - Unassigned: {Ticket.objects.filter(assigned_to__isnull=True).count()}")
    print(f"  - Overdue: {sum(1 for t in Ticket.objects.all() if t.is_overdue)}")
    print(f"\nYou can now:")
    print(f"  - View tickets at: http://localhost:8000/api/ticketing/tickets/")
    print(f"  - Manage in admin: http://localhost:8000/admin/ticketing/ticket/")
    print(f"  - View statistics: http://localhost:8000/api/ticketing/tickets/statistics/")


if __name__ == '__main__':
    try:
        create_test_tickets()
    except Exception as e:
        print(f"\n[ERROR] Error creating test tickets: {e}")
        import traceback
        traceback.print_exc()
