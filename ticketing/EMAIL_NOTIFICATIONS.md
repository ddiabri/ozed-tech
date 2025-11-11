# Email Notifications for Ticketing System

Comprehensive email notification system for the ticketing module.

## Features

### Automatic Email Notifications

The system automatically sends email notifications for the following events:

1. **Ticket Created** - When a new ticket is created
   - Sent to: Customer, Assigned user (if assigned)
   - Template: `ticket_created.html`

2. **Ticket Assigned** - When a ticket is assigned to a user
   - Sent to: Assigned user
   - Template: `ticket_assigned.html`

3. **Status Changed** - When ticket status changes
   - Sent to: Customer, Assigned user
   - Template: `status_changed.html`

4. **Ticket Resolved** - When a ticket is marked as resolved
   - Sent to: Customer
   - Template: `ticket_resolved.html`

5. **Ticket Closed** - When a ticket is closed
   - Sent to: Customer
   - Template: `ticket_closed.html`

6. **Comment Added** - When a comment is added to a ticket
   - Public comments: Sent to customer and assigned user
   - Internal comments: Sent only to team members
   - Template: `comment_added.html`

7. **Overdue Notification** - For tickets past their due date
   - Sent to: Assigned user, Ticket creator
   - Template: `ticket_overdue.html`
   - Triggered via management command (manual or scheduled)

## Configuration

### Development Setup (Console Backend)

For development, emails are printed to the console instead of being sent.

This is already configured in `settings.py`:
```python
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
```

When you create/update tickets, you'll see the email content in your terminal/console.

### Production Setup (SMTP)

For production, configure SMTP settings:

**1. Update `settings.py`:**
```python
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'  # Your SMTP server
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your-email@example.com'
EMAIL_HOST_PASSWORD = 'your-app-password'
DEFAULT_FROM_EMAIL = 'noreply@ozedtech.com'
SITE_URL = 'https://your-domain.com'
```

**2. Or use environment variables (recommended):**

Create a `.env` file:
```bash
EMAIL_BACKEND=smtp
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@example.com
EMAIL_HOST_PASSWORD=your-app-specific-password
DEFAULT_FROM_EMAIL=noreply@ozedtech.com
SITE_URL=https://your-domain.com
```

Then update `settings.py` to read from environment:
```python
import os

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend' if os.getenv('EMAIL_BACKEND') == 'smtp' else 'django.core.mail.backends.console.EmailBackend'
EMAIL_HOST = os.getenv('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = int(os.getenv('EMAIL_PORT', 587))
EMAIL_USE_TLS = os.getenv('EMAIL_USE_TLS', 'True') == 'True'
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD', '')
DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL', 'noreply@ozedtech.com')
SITE_URL = os.getenv('SITE_URL', 'http://localhost:8000')
```

## Email Providers

### Gmail

**Setup:**
1. Enable 2-factor authentication on your Google account
2. Create an app-specific password:
   - Go to Google Account Settings > Security
   - 2-Step Verification > App passwords
   - Generate a password for "Mail"
3. Use the app password in `EMAIL_HOST_PASSWORD`

```python
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your-email@gmail.com'
EMAIL_HOST_PASSWORD = 'your-16-char-app-password'
```

### SendGrid

```python
EMAIL_HOST = 'smtp.sendgrid.net'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'apikey'
EMAIL_HOST_PASSWORD = 'your-sendgrid-api-key'
```

### Amazon SES

```python
EMAIL_BACKEND = 'django_ses.SESBackend'
AWS_ACCESS_KEY_ID = 'your-access-key'
AWS_SECRET_ACCESS_KEY = 'your-secret-key'
AWS_SES_REGION_NAME = 'us-east-1'
AWS_SES_REGION_ENDPOINT = 'email.us-east-1.amazonaws.com'
```

### Mailgun

```python
EMAIL_HOST = 'smtp.mailgun.org'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'postmaster@your-domain.mailgun.org'
EMAIL_HOST_PASSWORD = 'your-mailgun-password'
```

## Email Templates

All email templates are located in `ticketing/templates/ticketing/emails/`

### Template Structure

- `base_email.html` - Base template with header, footer, and styling
- `ticket_created.html` - New ticket notification
- `ticket_assigned.html` - Assignment notification
- `status_changed.html` - Status change notification
- `comment_added.html` - New comment notification
- `ticket_resolved.html` - Resolution notification
- `ticket_closed.html` - Closure notification
- `ticket_overdue.html` - Overdue alert
- `ticket_updated.html` - General update notification

### Customizing Templates

Templates use Django template language. You can customize:

1. **Styling**: Edit the `<style>` section in `base_email.html`
2. **Content**: Edit individual template files
3. **Branding**: Update header, footer, and colors

Example customization:
```html
<!-- base_email.html -->
<div class="header" style="background-color: #YOUR_COLOR;">
    <h1>Your Company Name</h1>
</div>
```

## Programmatic Email Sending

You can manually send emails from your code:

```python
from ticketing.emails import TicketEmailNotification
from ticketing.models import Ticket

# Get a ticket
ticket = Ticket.objects.get(id=1)

# Send specific notifications
TicketEmailNotification.send_ticket_created(ticket)
TicketEmailNotification.send_ticket_assigned(ticket, user)
TicketEmailNotification.send_status_changed(ticket, 'open', 'resolved')
TicketEmailNotification.send_comment_added(ticket, comment)
TicketEmailNotification.send_ticket_resolved(ticket)
TicketEmailNotification.send_ticket_closed(ticket)
TicketEmailNotification.send_overdue_notification(ticket)
```

## Overdue Notifications

Overdue notifications are NOT sent automatically. You need to set up a scheduled task.

### Manual Execution

```bash
python manage.py send_overdue_notifications
```

### Dry Run (test without sending)

```bash
python manage.py send_overdue_notifications --dry-run
```

### Scheduling with Cron (Linux/Mac)

Edit crontab:
```bash
crontab -e
```

Add this line to run daily at 9 AM:
```cron
0 9 * * * cd /path/to/project && /path/to/venv/bin/python manage.py send_overdue_notifications
```

### Scheduling with Task Scheduler (Windows)

1. Open Task Scheduler
2. Create Basic Task
3. Name: "Send Overdue Ticket Notifications"
4. Trigger: Daily at 9:00 AM
5. Action: Start a program
   - Program: `C:\path\to\venv\Scripts\python.exe`
   - Arguments: `manage.py send_overdue_notifications`
   - Start in: `C:\path\to\project`

### Scheduling with Celery (Recommended for Production)

Install Celery:
```bash
pip install celery redis
```

Create `ticketing/tasks.py`:
```python
from celery import shared_task
from ticketing.models import Ticket
from ticketing.emails import TicketEmailNotification
from django.utils import timezone

@shared_task
def send_overdue_notifications():
    overdue_tickets = Ticket.objects.filter(
        due_date__lt=timezone.now().date(),
        status__in=['new', 'open', 'in_progress', 'pending']
    )

    for ticket in overdue_tickets:
        TicketEmailNotification.send_overdue_notification(ticket)

    return f'Sent {overdue_tickets.count()} notifications'
```

Configure periodic task in `celery.py`:
```python
from celery.schedules import crontab

app.conf.beat_schedule = {
    'send-overdue-notifications': {
        'task': 'ticketing.tasks.send_overdue_notifications',
        'schedule': crontab(hour=9, minute=0),  # Daily at 9 AM
    },
}
```

## Disabling Notifications

To temporarily disable email notifications:

**1. Change email backend to console:**
```python
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
```

**2. Or use dummy backend (no emails at all):**
```python
EMAIL_BACKEND = 'django.core.mail.backends.dummy.EmailBackend'
```

**3. Or disable specific signals:**

In `ticketing/signals.py`, comment out the signal you don't want:
```python
# @receiver(post_save, sender=Ticket)
# def ticket_post_save(sender, instance, created, **kwargs):
#     # Disabled
#     pass
```

## Testing Emails

### Test in Console

1. Ensure console backend is enabled
2. Create a ticket or update one
3. Check your terminal for email output

### Test with Real SMTP

```python
# In Django shell
python manage.py shell

from django.core.mail import send_mail

send_mail(
    'Test Email',
    'This is a test message.',
    'noreply@ozedtech.com',
    ['recipient@example.com'],
    fail_silently=False,
)
```

### Test All Templates

Create a test ticket and trigger all events:
```python
from ticketing.models import Ticket, TicketComment
from crm.models import Customer
from django.contrib.auth.models import User

# Create test ticket
customer = Customer.objects.first()
user = User.objects.first()

ticket = Ticket.objects.create(
    subject='Test Ticket',
    description='Testing email notifications',
    customer=customer,
    priority='high',
    created_by=user
)

# Assign it
ticket.assigned_to = user
ticket.save()

# Add comment
TicketComment.objects.create(
    ticket=ticket,
    author=user,
    content='Test comment',
    is_internal=False
)

# Change status
ticket.status = 'resolved'
ticket.save()

# Close it
ticket.status = 'closed'
ticket.save()
```

## Troubleshooting

### Emails Not Sending

1. **Check email backend:**
   ```python
   from django.conf import settings
   print(settings.EMAIL_BACKEND)
   ```

2. **Check SMTP credentials:**
   - Verify username/password
   - Check if 2FA is enabled (use app password)
   - Verify SMTP server and port

3. **Check for errors in logs:**
   ```bash
   # Enable logging
   LOGGING = {
       'version': 1,
       'handlers': {
           'console': {
               'class': 'logging.StreamHandler',
           },
       },
       'loggers': {
           'ticketing.emails': {
               'handlers': ['console'],
               'level': 'DEBUG',
           },
       },
   }
   ```

4. **Test SMTP connection:**
   ```python
   from django.core.mail import get_connection

   conn = get_connection()
   conn.open()  # Should not raise an error
   conn.close()
   ```

### Gmail Blocking Emails

- Enable "Less secure app access" (not recommended)
- Use app-specific password with 2FA (recommended)
- Check Google security alerts
- Verify domain isn't blacklisted

### Emails Going to Spam

- Set up SPF, DKIM, and DMARC records
- Use a verified domain
- Don't send too many emails at once
- Include unsubscribe link
- Use proper email formatting

## Best Practices

1. **Use environment variables** for sensitive data
2. **Test in development** with console backend first
3. **Use a dedicated email service** (SendGrid, Mailgun) for production
4. **Monitor email delivery** and bounce rates
5. **Respect user preferences** (add unsubscribe option)
6. **Rate limit** to avoid being flagged as spam
7. **Log email failures** for debugging
8. **Use queues** (Celery) for sending emails asynchronously
9. **Customize templates** to match your branding
10. **Test all notification types** before deploying

## Future Enhancements

- [ ] Email preferences per user (opt-in/opt-out)
- [ ] Email digest (daily summary of tickets)
- [ ] Rich text emails with attachments
- [ ] Email tracking (open rates, click rates)
- [ ] Customizable email templates per customer
- [ ] Multi-language email support
- [ ] Email bounce handling
- [ ] Unsubscribe management

---

**Email notifications are now active!** 📧

For support or questions, refer to this documentation or check the Django email documentation at: https://docs.djangoproject.com/en/stable/topics/email/
