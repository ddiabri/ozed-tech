"""
Serializers for the Ticketing system.
"""
from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Ticket, TicketComment, TicketAttachment, TicketHistory
from crm.models import Customer
from crm.serializers import CustomerSerializer


class UserSerializer(serializers.ModelSerializer):
    """Simple user serializer for ticket assignments."""

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']
        read_only_fields = fields


class TicketCommentSerializer(serializers.ModelSerializer):
    """Serializer for ticket comments."""
    author = UserSerializer(read_only=True)
    author_name = serializers.SerializerMethodField()

    class Meta:
        model = TicketComment
        fields = [
            'id', 'ticket', 'author', 'author_name', 'content',
            'is_internal', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'author', 'created_at', 'updated_at']

    def get_author_name(self, obj):
        if obj.author:
            return f"{obj.author.first_name} {obj.author.last_name}".strip() or obj.author.username
        return "Unknown"


class TicketAttachmentSerializer(serializers.ModelSerializer):
    """Serializer for ticket attachments."""
    uploaded_by = UserSerializer(read_only=True)
    file_url = serializers.SerializerMethodField()

    class Meta:
        model = TicketAttachment
        fields = [
            'id', 'ticket', 'file', 'file_url', 'filename',
            'file_size', 'uploaded_by', 'uploaded_at', 'description'
        ]
        read_only_fields = ['id', 'uploaded_by', 'uploaded_at', 'file_size']

    def get_file_url(self, obj):
        if obj.file:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.file.url)
            return obj.file.url
        return None


class TicketHistorySerializer(serializers.ModelSerializer):
    """Serializer for ticket history/audit trail."""
    user = UserSerializer(read_only=True)
    user_name = serializers.SerializerMethodField()

    class Meta:
        model = TicketHistory
        fields = [
            'id', 'ticket', 'user', 'user_name', 'action',
            'field_name', 'old_value', 'new_value', 'timestamp'
        ]
        read_only_fields = fields

    def get_user_name(self, obj):
        if obj.user:
            return f"{obj.user.first_name} {obj.user.last_name}".strip() or obj.user.username
        return "System"


class TicketListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for ticket lists."""
    customer_name = serializers.CharField(source='customer.company_name', read_only=True)
    assigned_to_name = serializers.SerializerMethodField()
    created_by_name = serializers.SerializerMethodField()
    is_overdue = serializers.BooleanField(read_only=True)
    comment_count = serializers.SerializerMethodField()

    class Meta:
        model = Ticket
        fields = [
            'id', 'ticket_number', 'subject', 'status', 'priority',
            'category', 'customer', 'customer_name', 'assigned_to',
            'assigned_to_name', 'created_by_name', 'created_at',
            'updated_at', 'due_date', 'is_overdue', 'comment_count'
        ]
        read_only_fields = ['id', 'ticket_number', 'created_at', 'updated_at']

    def get_assigned_to_name(self, obj):
        if obj.assigned_to:
            return f"{obj.assigned_to.first_name} {obj.assigned_to.last_name}".strip() or obj.assigned_to.username
        return None

    def get_created_by_name(self, obj):
        if obj.created_by:
            return f"{obj.created_by.first_name} {obj.created_by.last_name}".strip() or obj.created_by.username
        return None

    def get_comment_count(self, obj):
        return obj.comments.count()


class TicketDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for individual tickets."""
    customer = CustomerSerializer(read_only=True)
    customer_id = serializers.PrimaryKeyRelatedField(
        queryset=Customer.objects.all(),
        source='customer',
        write_only=True
    )
    assigned_to_detail = UserSerializer(source='assigned_to', read_only=True)
    created_by_detail = UserSerializer(source='created_by', read_only=True)
    comments = TicketCommentSerializer(many=True, read_only=True)
    attachments = TicketAttachmentSerializer(many=True, read_only=True)
    history = TicketHistorySerializer(many=True, read_only=True)

    # Computed fields
    is_overdue = serializers.BooleanField(read_only=True)
    response_time = serializers.FloatField(read_only=True)
    resolution_time = serializers.FloatField(read_only=True)

    class Meta:
        model = Ticket
        fields = [
            'id', 'ticket_number', 'subject', 'description',
            'status', 'priority', 'category',
            'customer', 'customer_id',
            'assigned_to', 'assigned_to_detail',
            'created_by', 'created_by_detail',
            'created_at', 'updated_at', 'resolved_at', 'closed_at',
            'due_date', 'estimated_hours', 'actual_hours',
            'tags', 'is_overdue', 'response_time', 'resolution_time',
            'comments', 'attachments', 'history'
        ]
        read_only_fields = [
            'id', 'ticket_number', 'created_at', 'updated_at',
            'resolved_at', 'closed_at', 'created_by'
        ]

    def create(self, validated_data):
        # Set created_by from request user
        user = self.context['request'].user
        validated_data['created_by'] = user
        return super().create(validated_data)


class TicketCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating tickets."""

    class Meta:
        model = Ticket
        fields = [
            'subject', 'description', 'priority', 'category',
            'customer', 'assigned_to', 'due_date',
            'estimated_hours', 'tags'
        ]

    def create(self, validated_data):
        user = self.context['request'].user
        validated_data['created_by'] = user
        ticket = Ticket.objects.create(**validated_data)

        # Create history entry
        TicketHistory.objects.create(
            ticket=ticket,
            user=user,
            action='ticket_created',
            new_value=f"Ticket created: {ticket.subject}"
        )

        return ticket


class TicketUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating tickets."""

    class Meta:
        model = Ticket
        fields = [
            'subject', 'description', 'status', 'priority', 'category',
            'assigned_to', 'due_date', 'estimated_hours', 'actual_hours', 'tags'
        ]

    def update(self, instance, validated_data):
        user = self.context['request'].user

        # Track changes for history
        changes = []
        for field, new_value in validated_data.items():
            old_value = getattr(instance, field)
            if old_value != new_value:
                changes.append({
                    'field': field,
                    'old': str(old_value) if old_value else '',
                    'new': str(new_value) if new_value else ''
                })

        # Update the instance
        ticket = super().update(instance, validated_data)

        # Create history entries for changes
        for change in changes:
            TicketHistory.objects.create(
                ticket=ticket,
                user=user,
                action=f"{change['field']}_changed",
                field_name=change['field'],
                old_value=change['old'],
                new_value=change['new']
            )

        return ticket
