/**
 * Session Security Manager
 * Tracks user activity and displays warnings before session expiration
 */

class SessionSecurityManager {
    constructor(options = {}) {
        this.warningTime = options.warningTime || 300; // 5 minutes default
        this.checkInterval = options.checkInterval || 30000; // Check every 30 seconds
        this.warningDisplayed = false;
        this.warningModal = null;
        this.timeoutTimer = null;

        this.init();
    }

    init() {
        // Track user activity
        this.trackActivity();

        // Check session status periodically
        this.startSessionCheck();

        // Create warning modal
        this.createWarningModal();
    }

    /**
     * Track user activity events
     */
    trackActivity() {
        const events = ['mousedown', 'keypress', 'scroll', 'touchstart', 'click'];

        events.forEach(event => {
            document.addEventListener(event, () => {
                this.resetWarning();
            }, true);
        });
    }

    /**
     * Start periodic session status checks
     */
    startSessionCheck() {
        this.timeoutTimer = setInterval(() => {
            this.checkSessionStatus();
        }, this.checkInterval);
    }

    /**
     * Check session status from server
     */
    async checkSessionStatus() {
        try {
            const response = await fetch('/api/session-status/', {
                method: 'GET',
                credentials: 'same-origin',
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            });

            if (response.ok) {
                const timeRemaining = response.headers.get('X-Session-Timeout-Remaining');
                const showWarning = response.headers.get('X-Session-Warning');

                if (timeRemaining) {
                    const remaining = parseInt(timeRemaining);

                    // Show warning if approaching timeout
                    if (showWarning === 'true' && !this.warningDisplayed) {
                        this.showWarning(remaining);
                    }

                    // Update countdown if warning is displayed
                    if (this.warningDisplayed) {
                        this.updateCountdown(remaining);
                    }
                }
            } else if (response.status === 401 || response.status === 403) {
                // User is no longer authenticated
                this.handleSessionExpired();
            }
        } catch (error) {
            console.error('Error checking session status:', error);
        }
    }

    /**
     * Show session expiration warning
     */
    showWarning(timeRemaining) {
        this.warningDisplayed = true;
        this.warningModal.style.display = 'block';
        this.updateCountdown(timeRemaining);
    }

    /**
     * Update countdown timer in warning modal
     */
    updateCountdown(seconds) {
        const minutes = Math.floor(seconds / 60);
        const secs = seconds % 60;
        const countdownEl = document.getElementById('session-countdown');

        if (countdownEl) {
            countdownEl.textContent = `${minutes}:${secs.toString().padStart(2, '0')}`;
        }

        // Auto-redirect if time expires
        if (seconds <= 0) {
            this.handleSessionExpired();
        }
    }

    /**
     * Reset warning state
     */
    resetWarning() {
        if (this.warningDisplayed) {
            this.warningDisplayed = false;
            this.warningModal.style.display = 'none';
        }
    }

    /**
     * Handle session expiration
     */
    handleSessionExpired() {
        clearInterval(this.timeoutTimer);

        // Show expiration message
        alert('Your session has expired due to inactivity. Please log in again.');

        // Redirect to login page
        window.location.href = '/admin/login/?next=' + encodeURIComponent(window.location.pathname);
    }

    /**
     * Extend session by making a lightweight request
     */
    async extendSession() {
        try {
            const response = await fetch('/api/session-status/', {
                method: 'GET',
                credentials: 'same-origin',
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            });

            if (response.ok) {
                this.resetWarning();
            }
        } catch (error) {
            console.error('Error extending session:', error);
        }
    }

    /**
     * Create warning modal HTML
     */
    createWarningModal() {
        const modal = document.createElement('div');
        modal.id = 'session-warning-modal';
        modal.style.cssText = `
            display: none;
            position: fixed;
            z-index: 10000;
            left: 0;
            top: 0;
            width: 100%;
            height: 100%;
            background-color: rgba(0,0,0,0.5);
        `;

        modal.innerHTML = `
            <div style="
                background-color: white;
                margin: 15% auto;
                padding: 20px;
                border: 1px solid #888;
                border-radius: 8px;
                width: 400px;
                max-width: 90%;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            ">
                <h2 style="margin-top: 0; color: #d9534f;">
                    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" style="vertical-align: middle; margin-right: 8px;">
                        <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"></path>
                        <line x1="12" y1="9" x2="12" y2="13"></line>
                        <line x1="12" y1="17" x2="12.01" y2="17"></line>
                    </svg>
                    Session Expiring Soon
                </h2>
                <p style="color: #666; font-size: 14px;">
                    Your session will expire in <strong id="session-countdown">5:00</strong> due to inactivity.
                </p>
                <p style="color: #666; font-size: 14px;">
                    Click "Stay Logged In" to continue your session, or you will be automatically logged out.
                </p>
                <div style="margin-top: 20px; text-align: right;">
                    <button id="session-extend-btn" style="
                        background-color: #5cb85c;
                        color: white;
                        border: none;
                        padding: 10px 20px;
                        border-radius: 4px;
                        cursor: pointer;
                        font-size: 14px;
                        margin-left: 10px;
                    ">
                        Stay Logged In
                    </button>
                </div>
            </div>
        `;

        document.body.appendChild(modal);
        this.warningModal = modal;

        // Add event listener to extend button
        document.getElementById('session-extend-btn').addEventListener('click', () => {
            this.extendSession();
        });
    }
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    // Only initialize if user is authenticated
    // Check for Django's auth indicator or customize based on your app
    if (document.body.classList.contains('authenticated') ||
        document.querySelector('[data-user-authenticated]')) {
        new SessionSecurityManager({
            warningTime: 300,      // Show warning 5 minutes before expiry
            checkInterval: 30000   // Check every 30 seconds
        });
    }
});
