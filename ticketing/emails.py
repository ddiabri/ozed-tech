"""
Email notification system for ticketing.
"""
from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from django.utils.html import strip_tags


class TicketEmailNotification:
    """Handle email notifications for tickets."""

    @staticmethod
    def send_ticket_created(ticket):
        """Send email when a new ticket is created."""
        subject = f"New Ticket Created: {ticket.ticket_number} - {ticket.subject}"

        context = {
            'ticket': ticket,
            'customer': ticket.customer,
            'site_url': settings.SITE_URL if hasattr(settings, 'SITE_URL') else 'http://localhost:8000',
        }

        # Render HTML email
        html_message = render_to_string('ticketing/emails/ticket_created.html', context)
        plain_message = strip_tags(html_message)

        # Send to customer
        if ticket.customer.email:
            TicketEmailNotification._send_email(
                subject=subject,
                message=plain_message,
                html_message=html_message,
                recipient_list=[ticket.customer.email],
            )

        # Send to assigned user
        if ticket.assigned_to and ticket.assigned_to.email:
            TicketEmailNotification._send_email(
                subject=f"Ticket Assigned to You: {ticket.ticket_number}",
                message=plain_message,
                html_message=html_message,
                recipient_list=[ticket.assigned_to.email],
            )

    @staticmethod
    def send_ticket_updated(ticket, changed_fields):
        """Send email when a ticket is updated."""
        subject = f"Ticket Updated: {ticket.ticket_number} - {ticket.subject}"

        context = {
            'ticket': ticket,
            'customer': ticket.customer,
            'changed_fields': changed_fields,
            'site_url': settings.SITE_URL if hasattr(settings, 'SITE_URL') else 'http://localhost:8000',
        }

        html_message = render_to_string('ticketing/emails/ticket_updated.html', context)
        plain_message = strip_tags(html_message)

        # Send to customer
        if ticket.customer.email:
            TicketEmailNotification._send_email(
                subject=subject,
                message=plain_message,
                html_message=html_message,
                recipient_list=[ticket.customer.email],
            )

    @staticmethod
    def send_ticket_assigned(ticket, assigned_to):
        """Send email when a ticket is assigned to someone."""
        subject = f"Ticket Assigned to You: {ticket.ticket_number}"

        context = {
            'ticket': ticket,
            'assigned_to': assigned_to,
            'site_url': settings.SITE_URL if hasattr(settings, 'SITE_URL') else 'http://localhost:8000',
        }

        html_message = render_to_string('ticketing/emails/ticket_assigned.html', context)
        plain_message = strip_tags(html_message)

        if assigned_to.email:
            TicketEmailNotification._send_email(
                subject=subject,
                message=plain_message,
                html_message=html_message,
                recipient_list=[assigned_to.email],
            )

    @staticmethod
    def send_status_changed(ticket, old_status, new_status):
        """Send email when ticket status changes."""
        subject = f"Ticket Status Changed: {ticket.ticket_number}"

        context = {
            'ticket': ticket,
            'old_status': old_status,
            'new_status': new_status,
            'site_url': settings.SITE_URL if hasattr(settings, 'SITE_URL') else 'http://localhost:8000',
        }

        html_message = render_to_string('ticketing/emails/status_changed.html', context)
        plain_message = strip_tags(html_message)

        # Send to customer
        if ticket.customer.email:
            TicketEmailNotification._send_email(
                subject=subject,
                message=plain_message,
                html_message=html_message,
                recipient_list=[ticket.customer.email],
            )

        # Send to assigned user
        if ticket.assigned_to and ticket.assigned_to.email:
            TicketEmailNotification._send_email(
                subject=subject,
                message=plain_message,
                html_message=html_message,
                recipient_list=[ticket.assigned_to.email],
            )

    @staticmethod
    def send_comment_added(ticket, comment):
        """Send email when a comment is added to a ticket."""
        # Don't send emails for internal comments to customers
        if comment.is_internal:
            recipients = []
            if ticket.assigned_to and ticket.assigned_to.email:
                recipients.append(ticket.assigned_to.email)
            if ticket.created_by and ticket.created_by.email and ticket.created_by != comment.author:
                recipients.append(ticket.created_by.email)
        else:
            recipients = []
            if ticket.customer.email:
                recipients.append(ticket.customer.email)
            if ticket.assigned_to and ticket.assigned_to.email:
                recipients.append(ticket.assigned_to.email)

        if not recipients:
            return

        subject = f"New Comment on Ticket: {ticket.ticket_number}"

        context = {
            'ticket': ticket,
            'comment': comment,
            'is_internal': comment.is_internal,
            'site_url': settings.SITE_URL if hasattr(settings, 'SITE_URL') else 'http://localhost:8000',
        }

        html_message = render_to_string('ticketing/emails/comment_added.html', context)
        plain_message = strip_tags(html_message)

        TicketEmailNotification._send_email(
            subject=subject,
            message=plain_message,
            html_message=html_message,
            recipient_list=list(set(recipients)),  # Remove duplicates
        )

    @staticmethod
    def send_ticket_resolved(ticket):
        """Send email when a ticket is resolved."""
        subject = f"Ticket Resolved: {ticket.ticket_number}"

        context = {
            'ticket': ticket,
            'site_url': settings.SITE_URL if hasattr(settings, 'SITE_URL') else 'http://localhost:8000',
        }

        html_message = render_to_string('ticketing/emails/ticket_resolved.html', context)
        plain_message = strip_tags(html_message)

        if ticket.customer.email:
            TicketEmailNotification._send_email(
                subject=subject,
                message=plain_message,
                html_message=html_message,
                recipient_list=[ticket.customer.email],
            )

    @staticmethod
    def send_ticket_closed(ticket):
        """Send email when a ticket is closed."""
        subject = f"Ticket Closed: {ticket.ticket_number}"

        context = {
            'ticket': ticket,
            'site_url': settings.SITE_URL if hasattr(settings, 'SITE_URL') else 'http://localhost:8000',
        }

        html_message = render_to_string('ticketing/emails/ticket_closed.html', context)
        plain_message = strip_tags(html_message)

        if ticket.customer.email:
            TicketEmailNotification._send_email(
                subject=subject,
                message=plain_message,
                html_message=html_message,
                recipient_list=[ticket.customer.email],
            )

    @staticmethod
    def send_overdue_notification(ticket):
        """Send email notification for overdue tickets."""
        subject = f"OVERDUE: Ticket {ticket.ticket_number} - {ticket.subject}"

        context = {
            'ticket': ticket,
            'site_url': settings.SITE_URL if hasattr(settings, 'SITE_URL') else 'http://localhost:8000',
        }

        html_message = render_to_string('ticketing/emails/ticket_overdue.html', context)
        plain_message = strip_tags(html_message)

        recipients = []
        if ticket.assigned_to and ticket.assigned_to.email:
            recipients.append(ticket.assigned_to.email)
        if ticket.created_by and ticket.created_by.email:
            recipients.append(ticket.created_by.email)

        if recipients:
            TicketEmailNotification._send_email(
                subject=subject,
                message=plain_message,
                html_message=html_message,
                recipient_list=list(set(recipients)),
            )

    @staticmethod
    def _send_email(subject, message, html_message, recipient_list):
        """Internal method to send emails."""
        try:
            from_email = settings.DEFAULT_FROM_EMAIL if hasattr(settings, 'DEFAULT_FROM_EMAIL') else 'noreply@ozedtech.com'

            # Create email with both plain text and HTML
            email = EmailMultiAlternatives(
                subject=subject,
                body=message,
                from_email=from_email,
                to=recipient_list,
            )
            email.attach_alternative(html_message, "text/html")
            email.send(fail_silently=False)

            return True
        except Exception as e:
            # Log the error
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Failed to send email: {str(e)}")
            return False
