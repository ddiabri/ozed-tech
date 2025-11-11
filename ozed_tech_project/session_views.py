"""
Views for session management and status checking.
"""
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.conf import settings
from django.utils.decorators import method_decorator
from django.views import View


@require_http_methods(["GET"])
@login_required
def session_status(request):
    """
    API endpoint to check session status and return time remaining.

    This endpoint is called by the frontend JavaScript to:
    - Check if the session is still active
    - Get remaining time before timeout
    - Reset the session activity timer (since it's a valid request)

    Returns:
        JsonResponse with session information
    """
    last_activity = request.session.get('last_activity')

    if last_activity:
        # Parse last activity time
        if isinstance(last_activity, str):
            from django.utils.dateparse import parse_datetime
            last_activity = parse_datetime(last_activity)

        # Calculate time remaining
        now = timezone.now()
        timeout = getattr(settings, 'SESSION_INACTIVITY_TIMEOUT', 1800)
        time_since_activity = (now - last_activity).total_seconds()
        time_remaining = max(0, timeout - time_since_activity)

        # Determine if warning should be shown
        warning_threshold = getattr(settings, 'SESSION_WARNING_THRESHOLD', 300)
        show_warning = time_remaining <= warning_threshold

        return JsonResponse({
            'authenticated': True,
            'time_remaining': int(time_remaining),
            'show_warning': show_warning,
            'username': request.user.username,
            'last_activity': last_activity.isoformat() if last_activity else None,
        })
    else:
        # First request, initialize session
        return JsonResponse({
            'authenticated': True,
            'time_remaining': getattr(settings, 'SESSION_INACTIVITY_TIMEOUT', 1800),
            'show_warning': False,
            'username': request.user.username,
        })


class SessionManagementView(View):
    """
    Class-based view for session management operations.
    """

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get(self, request):
        """Get current session information."""
        session_data = {
            'session_key': request.session.session_key,
            'user': {
                'username': request.user.username,
                'email': request.user.email,
                'is_active': request.user.is_active,
            },
            'session_expiry': request.session.get_expiry_date().isoformat() if hasattr(request.session, 'get_expiry_date') else None,
            'last_activity': request.session.get('last_activity'),
        }
        return JsonResponse(session_data)

    def delete(self, request):
        """Manually expire/logout the session."""
        from django.contrib.auth import logout
        logout(request)
        return JsonResponse({
            'message': 'Session terminated successfully',
            'status': 'logged_out'
        })


@login_required
def extend_session(request):
    """
    Endpoint to manually extend the current session.
    Simply accessing this endpoint will reset the activity timer.
    """
    return JsonResponse({
        'message': 'Session extended successfully',
        'time_remaining': getattr(settings, 'SESSION_INACTIVITY_TIMEOUT', 1800),
    })
