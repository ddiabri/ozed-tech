from django.contrib import admin
from django.utils.html import format_html
from .models import Ticket, TicketComment, TicketAttachment, TicketHistory


class TicketCommentInline(admin.TabularInline):
    """Inline admin for ticket comments."""
    model = TicketComment
    extra = 0
    readonly_fields = ['author', 'created_at', 'updated_at']
    fields = ['author', 'content', 'is_internal', 'created_at']


class TicketAttachmentInline(admin.TabularInline):
    """Inline admin for ticket attachments."""
    model = TicketAttachment
    extra = 0
    readonly_fields = ['uploaded_by', 'uploaded_at', 'file_size']
    fields = ['file', 'filename', 'description', 'uploaded_by', 'uploaded_at']


class TicketHistoryInline(admin.TabularInline):
    """Inline admin for ticket history."""
    model = TicketHistory
    extra = 0
    readonly_fields = ['user', 'action', 'field_name', 'old_value', 'new_value', 'timestamp']
    can_delete = False

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    """Admin interface for Tickets."""

    list_display = [
        'ticket_number', 'subject', 'status_badge', 'priority_badge',
        'customer', 'assigned_to', 'created_at', 'is_overdue_badge'
    ]
    list_filter = ['status', 'priority', 'category', 'created_at', 'assigned_to']
    search_fields = ['ticket_number', 'subject', 'description', 'customer__company_name']
    readonly_fields = [
        'ticket_number', 'created_at', 'updated_at', 'resolved_at',
        'closed_at', 'is_overdue', 'response_time', 'resolution_time'
    ]
    autocomplete_fields = ['customer', 'assigned_to', 'created_by']
    inlines = [TicketCommentInline, TicketAttachmentInline, TicketHistoryInline]

    fieldsets = (
        ('Basic Information', {
            'fields': ('ticket_number', 'subject', 'description', 'customer')
        }),
        ('Status & Priority', {
            'fields': ('status', 'priority', 'category', 'tags')
        }),
        ('Assignment', {
            'fields': ('assigned_to', 'created_by')
        }),
        ('Scheduling', {
            'fields': ('due_date', 'estimated_hours', 'actual_hours')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'resolved_at', 'closed_at'),
            'classes': ('collapse',)
        }),
        ('Metrics', {
            'fields': ('is_overdue', 'response_time', 'resolution_time'),
            'classes': ('collapse',)
        }),
    )

    def status_badge(self, obj):
        """Display status with color badge."""
        colors = {
            'new': '#007bff',
            'open': '#17a2b8',
            'in_progress': '#ffc107',
            'pending': '#fd7e14',
            'resolved': '#28a745',
            'closed': '#6c757d',
            'reopened': '#dc3545',
        }
        color = colors.get(obj.status, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; '
            'border-radius: 3px; font-size: 11px;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'

    def priority_badge(self, obj):
        """Display priority with color badge."""
        colors = {
            'low': '#28a745',
            'medium': '#ffc107',
            'high': '#fd7e14',
            'urgent': '#dc3545',
            'critical': '#721c24',
        }
        color = colors.get(obj.priority, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; '
            'border-radius: 3px; font-size: 11px;">{}</span>',
            color,
            obj.get_priority_display()
        )
    priority_badge.short_description = 'Priority'

    def is_overdue_badge(self, obj):
        """Display overdue status."""
        if obj.is_overdue:
            return format_html(
                '<span style="color: #dc3545; font-weight: bold;">⚠ OVERDUE</span>'
            )
        return '-'
    is_overdue_badge.short_description = 'Overdue'


@admin.register(TicketComment)
class TicketCommentAdmin(admin.ModelAdmin):
    """Admin interface for Ticket Comments."""

    list_display = ['ticket', 'author', 'is_internal', 'created_at', 'content_preview']
    list_filter = ['is_internal', 'created_at', 'author']
    search_fields = ['content', 'ticket__ticket_number', 'ticket__subject']
    readonly_fields = ['created_at', 'updated_at']
    autocomplete_fields = ['ticket', 'author']

    def content_preview(self, obj):
        """Show preview of comment content."""
        return obj.content[:100] + '...' if len(obj.content) > 100 else obj.content
    content_preview.short_description = 'Preview'


@admin.register(TicketAttachment)
class TicketAttachmentAdmin(admin.ModelAdmin):
    """Admin interface for Ticket Attachments."""

    list_display = ['filename', 'ticket', 'uploaded_by', 'file_size_display', 'uploaded_at']
    list_filter = ['uploaded_at', 'uploaded_by']
    search_fields = ['filename', 'description', 'ticket__ticket_number']
    readonly_fields = ['uploaded_at', 'file_size']
    autocomplete_fields = ['ticket', 'uploaded_by']

    def file_size_display(self, obj):
        """Display file size in human-readable format."""
        size = obj.file_size
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} TB"
    file_size_display.short_description = 'File Size'


@admin.register(TicketHistory)
class TicketHistoryAdmin(admin.ModelAdmin):
    """Admin interface for Ticket History."""

    list_display = ['ticket', 'action', 'user', 'field_name', 'timestamp']
    list_filter = ['action', 'timestamp', 'user']
    search_fields = ['ticket__ticket_number', 'action', 'field_name']
    readonly_fields = ['ticket', 'user', 'action', 'field_name', 'old_value', 'new_value', 'timestamp']

    def has_add_permission(self, request):
        """Prevent manual creation of history records."""
        return False

    def has_delete_permission(self, request, obj=None):
        """Prevent deletion of history records."""
        return False
