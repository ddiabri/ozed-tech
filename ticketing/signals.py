"""
Django signals for triggering email notifications.
"""
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from .models import Ticket, TicketComment
from .emails import TicketEmailNotification


@receiver(post_save, sender=Ticket)
def ticket_post_save(sender, instance, created, **kwargs):
    """
    Send email notifications after ticket is saved.
    """
    if created:
        # New ticket created
        try:
            TicketEmailNotification.send_ticket_created(instance)
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Failed to send ticket created email: {str(e)}")


@receiver(pre_save, sender=Ticket)
def ticket_pre_save(sender, instance, **kwargs):
    """
    Store previous state before saving to detect changes.
    """
    if instance.pk:
        try:
            old_instance = Ticket.objects.get(pk=instance.pk)
            instance._old_status = old_instance.status
            instance._old_assigned_to = old_instance.assigned_to
            instance._old_priority = old_instance.priority
        except Ticket.DoesNotExist:
            pass


@receiver(post_save, sender=Ticket)
def ticket_status_changed(sender, instance, created, **kwargs):
    """
    Send notifications when ticket status changes.
    """
    if not created and hasattr(instance, '_old_status'):
        old_status = instance._old_status
        new_status = instance.status

        if old_status != new_status:
            try:
                # Send status change notification
                TicketEmailNotification.send_status_changed(instance, old_status, new_status)

                # Send specific notifications for resolved/closed
                if new_status == 'resolved':
                    TicketEmailNotification.send_ticket_resolved(instance)
                elif new_status == 'closed':
                    TicketEmailNotification.send_ticket_closed(instance)

            except Exception as e:
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"Failed to send status change email: {str(e)}")

        # Clean up temp attributes
        delattr(instance, '_old_status')


@receiver(post_save, sender=Ticket)
def ticket_assignment_changed(sender, instance, created, **kwargs):
    """
    Send notification when ticket is assigned to someone.
    """
    if not created and hasattr(instance, '_old_assigned_to'):
        old_assigned_to = instance._old_assigned_to
        new_assigned_to = instance.assigned_to

        if old_assigned_to != new_assigned_to and new_assigned_to is not None:
            try:
                TicketEmailNotification.send_ticket_assigned(instance, new_assigned_to)
            except Exception as e:
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"Failed to send assignment email: {str(e)}")

        # Clean up temp attribute
        if hasattr(instance, '_old_assigned_to'):
            delattr(instance, '_old_assigned_to')


@receiver(post_save, sender=TicketComment)
def comment_added(sender, instance, created, **kwargs):
    """
    Send notification when comment is added to ticket.
    """
    if created:
        try:
            TicketEmailNotification.send_comment_added(instance.ticket, instance)
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Failed to send comment notification email: {str(e)}")
