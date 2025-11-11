"""
Session Security Middleware for tracking user activity and enforcing timeouts.
"""
from django.contrib.auth import logout
from django.utils import timezone
from django.conf import settings
from datetime import timedelta
import logging

logger = logging.getLogger(__name__)


class SessionSecurityMiddleware:
    """
    Middleware to track user activity and enforce session timeouts.

    This middleware:
    - Tracks last activity time for each session
    - Enforces inactivity timeout (auto-logout)
    - Logs security-related session events
    - Provides warnings before session expiration
    """

    def __init__(self, get_response):
        self.get_response = get_response
        # Get timeout from settings, default to 30 minutes
        self.timeout = getattr(settings, 'SESSION_INACTIVITY_TIMEOUT', 1800)
        # Warning threshold (e.g., show warning at 5 minutes before expiry)
        self.warning_threshold = getattr(settings, 'SESSION_WARNING_THRESHOLD', 300)

    def __call__(self, request):
        # Process the request
        if request.user.is_authenticated:
            self._check_session_activity(request)

        response = self.get_response(request)

        # Update last activity time after successful request
        if request.user.is_authenticated:
            self._update_activity(request, response)

        return response

    def _check_session_activity(self, request):
        """Check if session has exceeded inactivity timeout."""
        last_activity = request.session.get('last_activity')

        if last_activity:
            # Convert string to datetime if needed
            if isinstance(last_activity, str):
                from django.utils.dateparse import parse_datetime
                last_activity = parse_datetime(last_activity)

            # Calculate time since last activity
            now = timezone.now()
            time_since_activity = (now - last_activity).total_seconds()

            # Check if session has expired
            if time_since_activity > self.timeout:
                logger.warning(
                    f"Session timeout for user {request.user.username}. "
                    f"Inactive for {time_since_activity:.0f} seconds."
                )
                # Store reason for logout
                request.session['logout_reason'] = 'inactivity_timeout'
                logout(request)

    def _update_activity(self, request, response):
        """Update the last activity timestamp in session."""
        # Only update for non-static requests
        if not request.path.startswith(settings.STATIC_URL):
            now = timezone.now()
            request.session['last_activity'] = now.isoformat()

            # Calculate time until session expires
            last_activity = request.session.get('last_activity')
            if isinstance(last_activity, str):
                from django.utils.dateparse import parse_datetime
                last_activity = parse_datetime(last_activity)

            time_remaining = self.timeout - (now - last_activity).total_seconds()

            # Add time remaining to response header for client-side tracking
            response['X-Session-Timeout-Remaining'] = str(int(time_remaining))

            # Add warning flag if approaching timeout
            if time_remaining <= self.warning_threshold:
                response['X-Session-Warning'] = 'true'


class SessionAuditMiddleware:
    """
    Middleware for auditing session-related security events.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Track session creation
        session_key_before = request.session.session_key if hasattr(request, 'session') else None

        response = self.get_response(request)

        # Log new session creation
        if hasattr(request, 'session'):
            session_key_after = request.session.session_key
            if session_key_before != session_key_after and request.user.is_authenticated:
                logger.info(
                    f"New session created for user {request.user.username} "
                    f"from IP {self._get_client_ip(request)}"
                )

        return response

    def _get_client_ip(self, request):
        """Get client IP address from request."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
