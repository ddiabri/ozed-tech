"""
Test ticket email notifications.
"""
import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ozed_tech_project.settings')
django.setup()

from ticketing.models import Ticket
from crm.models import Customer
from django.contrib.auth.models import User

print("Testing Ticket Email Notifications")
print("=" * 50)

# Get or create test data
print("\n1. Preparing test data...")
customer = Customer.objects.first()
user = User.objects.first()

if not customer:
    print("   [ERROR] No customers found. Please create a customer first.")
    sys.exit(1)

if not user:
    print("   [ERROR] No users found. Please create a user first.")
    sys.exit(1)

print(f"   Customer: {customer.company_name}")
print(f"   User: {user.username} ({user.email})")

# Check if customer has a contact with email
primary_contact = customer.contacts.filter(is_primary=True, is_active=True).first()
if primary_contact:
    print(f"   Primary Contact: {primary_contact.full_name} ({primary_contact.email})")
else:
    any_contact = customer.contacts.filter(is_active=True).first()
    if any_contact:
        print(f"   Contact: {any_contact.full_name} ({any_contact.email})")
    else:
        print(f"   [WARNING] Customer {customer.company_name} has no contacts!")
        print("   Email will only be sent to assigned user.")

print("\n2. Creating test ticket...")
try:
    ticket = Ticket.objects.create(
        subject='Email Notification Test Ticket',
        description='This is a test ticket to verify that email notifications are working correctly. You should receive an email for this ticket creation.',
        customer=customer,
        priority='high',
        category='technical',
        created_by=user,
        assigned_to=user,
    )
    print(f"   [OK] Created ticket: {ticket.ticket_number}")
    print(f"   Status: {ticket.status}")
    print(f"   Priority: {ticket.priority}")

    print("\n3. Email notifications should have been sent!")
    print("   Check your email inbox for:")
    contact = customer.contacts.filter(is_active=True, email__isnull=False).first()
    if contact and contact.email:
        print(f"   - {contact.email} (customer notification)")
    if user.email:
        print(f"   - {user.email} (assignment notification)")

    print("\n4. Testing comment notification...")
    from ticketing.models import TicketComment

    comment = TicketComment.objects.create(
        ticket=ticket,
        author=user,
        content='This is a test comment. You should receive an email notification for this as well.',
        is_internal=False
    )
    print(f"   [OK] Added comment to ticket")
    print("   Check your email for comment notification!")

    print("\n5. Testing status change notification...")
    ticket.status = 'in_progress'
    ticket.save()
    print(f"   [OK] Changed ticket status to: {ticket.status}")
    print("   Check your email for status change notification!")

    print("\n6. Testing resolution notification...")
    ticket.status = 'resolved'
    ticket.save()
    print(f"   [OK] Marked ticket as resolved")
    print("   Check your email for resolution notification!")

    print("\n" + "=" * 50)
    print("[SUCCESS] All email notifications have been triggered!")
    print("\nCheck your email inbox(es) for:")
    print("  1. Ticket Created notification")
    print("  2. Ticket Assigned notification")
    print("  3. Comment Added notification")
    print("  4. Status Changed notification (to 'In Progress')")
    print("  5. Status Changed notification (to 'Resolved')")
    print("  6. Ticket Resolved notification")
    print("\n[NOTE] Emails may take a few moments to arrive.")
    print(f"[NOTE] Test ticket created: {ticket.ticket_number}")

except Exception as e:
    print(f"\n[ERROR] Failed to create ticket or send emails: {str(e)}")
    import traceback
    traceback.print_exc()
