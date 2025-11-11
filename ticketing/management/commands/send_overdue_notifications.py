"""
Management command to send notifications for overdue tickets.

Usage:
    python manage.py send_overdue_notifications

This command should be run via cron job or task scheduler daily.
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from ticketing.models import Ticket
from ticketing.emails import TicketEmailNotification


class Command(BaseCommand):
    help = 'Send email notifications for overdue tickets'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Run without actually sending emails',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']

        # Get overdue tickets that are not resolved or closed
        overdue_tickets = Ticket.objects.filter(
            due_date__lt=timezone.now().date(),
            status__in=['new', 'open', 'in_progress', 'pending']
        ).select_related('customer', 'assigned_to', 'created_by')

        self.stdout.write(
            self.style.SUCCESS(f'Found {overdue_tickets.count()} overdue tickets')
        )

        sent_count = 0
        error_count = 0

        for ticket in overdue_tickets:
            try:
                if dry_run:
                    self.stdout.write(
                        f'[DRY RUN] Would send overdue notification for: {ticket.ticket_number}'
                    )
                else:
                    TicketEmailNotification.send_overdue_notification(ticket)
                    self.stdout.write(
                        self.style.SUCCESS(f'Sent overdue notification for: {ticket.ticket_number}')
                    )
                sent_count += 1
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Failed to send notification for {ticket.ticket_number}: {str(e)}')
                )
                error_count += 1

        # Summary
        self.stdout.write(self.style.SUCCESS(f'\n--- Summary ---'))
        self.stdout.write(f'Total overdue tickets: {overdue_tickets.count()}')
        self.stdout.write(self.style.SUCCESS(f'Notifications sent: {sent_count}'))
        if error_count > 0:
            self.stdout.write(self.style.ERROR(f'Errors: {error_count}'))
        if dry_run:
            self.stdout.write(self.style.WARNING('\nThis was a dry run. No emails were actually sent.'))
