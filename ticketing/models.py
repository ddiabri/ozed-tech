from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from crm.models import Customer


class Ticket(models.Model):
    """
    Support ticket model for tracking customer issues and requests.
    """

    STATUS_CHOICES = [
        ('new', 'New'),
        ('open', 'Open'),
        ('in_progress', 'In Progress'),
        ('pending', 'Pending Customer Response'),
        ('resolved', 'Resolved'),
        ('closed', 'Closed'),
        ('reopened', 'Reopened'),
    ]

    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
        ('critical', 'Critical'),
    ]

    CATEGORY_CHOICES = [
        ('technical', 'Technical Issue'),
        ('billing', 'Billing/Payment'),
        ('product', 'Product Inquiry'),
        ('feature_request', 'Feature Request'),
        ('bug', 'Bug Report'),
        ('general', 'General Question'),
        ('complaint', 'Complaint'),
        ('other', 'Other'),
    ]

    # Basic Information
    ticket_number = models.CharField(max_length=20, unique=True, editable=False)
    subject = models.CharField(max_length=255)
    description = models.TextField()

    # Status and Priority
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium')
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='general')

    # Relationships
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='tickets')
    assigned_to = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_tickets'
    )
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_tickets'
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    closed_at = models.DateTimeField(null=True, blank=True)

    # SLA and Tracking
    due_date = models.DateTimeField(null=True, blank=True)
    estimated_hours = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    actual_hours = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)

    # Tags for better organization
    tags = models.CharField(max_length=255, blank=True, help_text="Comma-separated tags")

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['ticket_number']),
            models.Index(fields=['status']),
            models.Index(fields=['priority']),
            models.Index(fields=['customer']),
            models.Index(fields=['assigned_to']),
        ]

    def __str__(self):
        return f"#{self.ticket_number} - {self.subject}"

    def save(self, *args, **kwargs):
        # Auto-generate ticket number if not exists
        if not self.ticket_number:
            last_ticket = Ticket.objects.all().order_by('id').last()
            if last_ticket:
                last_number = int(last_ticket.ticket_number.replace('TKT-', ''))
                new_number = last_number + 1
            else:
                new_number = 1
            self.ticket_number = f'TKT-{new_number:06d}'

        # Set resolved/closed timestamps
        if self.status == 'resolved' and not self.resolved_at:
            self.resolved_at = timezone.now()
        elif self.status == 'closed' and not self.closed_at:
            self.closed_at = timezone.now()

        super().save(*args, **kwargs)

    @property
    def is_overdue(self):
        """Check if ticket is overdue."""
        if self.due_date and self.status not in ['resolved', 'closed']:
            return timezone.now() > self.due_date
        return False

    @property
    def response_time(self):
        """Calculate time to first response."""
        first_comment = self.comments.filter(is_internal=False).first()
        if first_comment:
            return (first_comment.created_at - self.created_at).total_seconds() / 60  # minutes
        return None

    @property
    def resolution_time(self):
        """Calculate time to resolution."""
        if self.resolved_at:
            return (self.resolved_at - self.created_at).total_seconds() / 3600  # hours
        return None


class TicketComment(models.Model):
    """
    Comments/responses on tickets.
    """
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    content = models.TextField()
    is_internal = models.BooleanField(
        default=False,
        help_text="Internal notes not visible to customers"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"Comment on {self.ticket.ticket_number} by {self.author}"


class TicketAttachment(models.Model):
    """
    File attachments for tickets.
    """
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name='attachments')
    file = models.FileField(upload_to='ticket_attachments/%Y/%m/%d/')
    filename = models.CharField(max_length=255)
    file_size = models.IntegerField(help_text="File size in bytes")
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    description = models.CharField(max_length=255, blank=True)

    class Meta:
        ordering = ['-uploaded_at']

    def __str__(self):
        return f"{self.filename} - {self.ticket.ticket_number}"

    def save(self, *args, **kwargs):
        if self.file and not self.filename:
            self.filename = self.file.name
        if self.file and not self.file_size:
            self.file_size = self.file.size
        super().save(*args, **kwargs)


class TicketHistory(models.Model):
    """
    Audit trail for ticket changes.
    """
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name='history')
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    action = models.CharField(max_length=50)  # e.g., 'status_changed', 'assigned', 'commented'
    field_name = models.CharField(max_length=50, blank=True)
    old_value = models.TextField(blank=True)
    new_value = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']
        verbose_name_plural = 'Ticket histories'

    def __str__(self):
        return f"{self.ticket.ticket_number} - {self.action} at {self.timestamp}"
