"""
Views and ViewSets for the Ticketing system.
"""
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q, Count, Avg
from django.utils import timezone

from .models import Ticket, TicketComment, TicketAttachment, TicketHistory
from .serializers import (
    TicketListSerializer,
    TicketDetailSerializer,
    TicketCreateSerializer,
    TicketUpdateSerializer,
    TicketCommentSerializer,
    TicketAttachmentSerializer,
    TicketHistorySerializer
)


class TicketViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing support tickets.

    Provides CRUD operations plus custom actions for:
    - Filtering by status, priority, customer, assignee
    - Assigning tickets to users
    - Changing ticket status
    - Adding comments
    - Uploading attachments
    - Viewing ticket statistics
    """
    queryset = Ticket.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'priority', 'category', 'customer', 'assigned_to']
    search_fields = ['ticket_number', 'subject', 'description', 'tags']
    ordering_fields = ['created_at', 'updated_at', 'priority', 'due_date']
    ordering = ['-created_at']

    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action == 'list':
            return TicketListSerializer
        elif self.action == 'create':
            return TicketCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return TicketUpdateSerializer
        return TicketDetailSerializer

    def get_queryset(self):
        """
        Optionally filter tickets based on query parameters.
        """
        queryset = Ticket.objects.all().select_related(
            'customer', 'assigned_to', 'created_by'
        ).prefetch_related('comments', 'attachments')

        # Filter by overdue status
        if self.request.query_params.get('overdue') == 'true':
            queryset = queryset.filter(
                due_date__lt=timezone.now(),
                status__in=['new', 'open', 'in_progress', 'pending']
            )

        # Filter by assigned to me
        if self.request.query_params.get('my_tickets') == 'true':
            queryset = queryset.filter(assigned_to=self.request.user)

        # Filter by unassigned
        if self.request.query_params.get('unassigned') == 'true':
            queryset = queryset.filter(assigned_to__isnull=True)

        # Filter by date range
        created_after = self.request.query_params.get('created_after')
        if created_after:
            queryset = queryset.filter(created_at__gte=created_after)

        created_before = self.request.query_params.get('created_before')
        if created_before:
            queryset = queryset.filter(created_at__lte=created_before)

        return queryset

    @action(detail=True, methods=['post'])
    def assign(self, request, pk=None):
        """Assign ticket to a user."""
        ticket = self.get_object()
        user_id = request.data.get('user_id')

        if not user_id:
            return Response(
                {'error': 'user_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        from django.contrib.auth.models import User
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response(
                {'error': 'User not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        old_assignee = ticket.assigned_to
        ticket.assigned_to = user
        ticket.save()

        # Create history entry
        TicketHistory.objects.create(
            ticket=ticket,
            user=request.user,
            action='assigned',
            field_name='assigned_to',
            old_value=str(old_assignee) if old_assignee else '',
            new_value=str(user)
        )

        return Response({
            'message': f'Ticket assigned to {user.username}',
            'ticket': TicketDetailSerializer(ticket, context={'request': request}).data
        })

    @action(detail=True, methods=['post'])
    def change_status(self, request, pk=None):
        """Change ticket status."""
        ticket = self.get_object()
        new_status = request.data.get('status')

        if not new_status:
            return Response(
                {'error': 'status is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        valid_statuses = [choice[0] for choice in Ticket.STATUS_CHOICES]
        if new_status not in valid_statuses:
            return Response(
                {'error': f'Invalid status. Must be one of: {", ".join(valid_statuses)}'},
                status=status.HTTP_400_BAD_REQUEST
            )

        old_status = ticket.status
        ticket.status = new_status
        ticket.save()

        # Create history entry
        TicketHistory.objects.create(
            ticket=ticket,
            user=request.user,
            action='status_changed',
            field_name='status',
            old_value=old_status,
            new_value=new_status
        )

        return Response({
            'message': f'Ticket status changed from {old_status} to {new_status}',
            'ticket': TicketDetailSerializer(ticket, context={'request': request}).data
        })

    @action(detail=True, methods=['post'])
    def add_comment(self, request, pk=None):
        """Add a comment to the ticket."""
        ticket = self.get_object()
        content = request.data.get('content')
        is_internal = request.data.get('is_internal', False)

        if not content:
            return Response(
                {'error': 'content is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        comment = TicketComment.objects.create(
            ticket=ticket,
            author=request.user,
            content=content,
            is_internal=is_internal
        )

        # Create history entry
        TicketHistory.objects.create(
            ticket=ticket,
            user=request.user,
            action='comment_added',
            new_value=f"{'Internal' if is_internal else 'Public'} comment added"
        )

        return Response(
            TicketCommentSerializer(comment, context={'request': request}).data,
            status=status.HTTP_201_CREATED
        )

    @action(detail=True, methods=['post'])
    def add_attachment(self, request, pk=None):
        """Upload an attachment to the ticket."""
        ticket = self.get_object()
        file = request.FILES.get('file')
        description = request.data.get('description', '')

        if not file:
            return Response(
                {'error': 'file is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        attachment = TicketAttachment.objects.create(
            ticket=ticket,
            file=file,
            uploaded_by=request.user,
            description=description
        )

        # Create history entry
        TicketHistory.objects.create(
            ticket=ticket,
            user=request.user,
            action='attachment_added',
            new_value=f"File uploaded: {attachment.filename}"
        )

        return Response(
            TicketAttachmentSerializer(attachment, context={'request': request}).data,
            status=status.HTTP_201_CREATED
        )

    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Get ticket statistics."""
        queryset = self.get_queryset()

        stats = {
            'total_tickets': queryset.count(),
            'by_status': {},
            'by_priority': {},
            'by_category': {},
            'overdue_count': queryset.filter(
                due_date__lt=timezone.now(),
                status__in=['new', 'open', 'in_progress', 'pending']
            ).count(),
            'unassigned_count': queryset.filter(assigned_to__isnull=True).count(),
            'my_tickets_count': queryset.filter(assigned_to=request.user).count(),
        }

        # Count by status
        for status_choice in Ticket.STATUS_CHOICES:
            status_value = status_choice[0]
            stats['by_status'][status_value] = queryset.filter(status=status_value).count()

        # Count by priority
        for priority_choice in Ticket.PRIORITY_CHOICES:
            priority_value = priority_choice[0]
            stats['by_priority'][priority_value] = queryset.filter(priority=priority_value).count()

        # Count by category
        for category_choice in Ticket.CATEGORY_CHOICES:
            category_value = category_choice[0]
            stats['by_category'][category_value] = queryset.filter(category=category_value).count()

        # Average response and resolution times
        resolved_tickets = queryset.filter(resolved_at__isnull=False)
        if resolved_tickets.exists():
            stats['avg_resolution_time_hours'] = sum(
                t.resolution_time for t in resolved_tickets if t.resolution_time
            ) / resolved_tickets.count()

        return Response(stats)

    @action(detail=False, methods=['get'])
    def my_tickets(self, request):
        """Get tickets assigned to the current user."""
        tickets = self.get_queryset().filter(assigned_to=request.user)
        serializer = self.get_serializer(tickets, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def unassigned(self, request):
        """Get unassigned tickets."""
        tickets = self.get_queryset().filter(assigned_to__isnull=True)
        serializer = self.get_serializer(tickets, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def overdue(self, request):
        """Get overdue tickets."""
        tickets = self.get_queryset().filter(
            due_date__lt=timezone.now(),
            status__in=['new', 'open', 'in_progress', 'pending']
        )
        serializer = self.get_serializer(tickets, many=True)
        return Response(serializer.data)


class TicketCommentViewSet(viewsets.ModelViewSet):
    """ViewSet for ticket comments."""
    queryset = TicketComment.objects.all()
    serializer_class = TicketCommentSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['ticket', 'author', 'is_internal']

    def perform_create(self, serializer):
        """Set author to current user."""
        serializer.save(author=self.request.user)


class TicketAttachmentViewSet(viewsets.ModelViewSet):
    """ViewSet for ticket attachments."""
    queryset = TicketAttachment.objects.all()
    serializer_class = TicketAttachmentSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['ticket', 'uploaded_by']

    def perform_create(self, serializer):
        """Set uploaded_by to current user."""
        serializer.save(uploaded_by=self.request.user)


class TicketHistoryViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for ticket history (read-only)."""
    queryset = TicketHistory.objects.all()
    serializer_class = TicketHistorySerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['ticket', 'user', 'action']
