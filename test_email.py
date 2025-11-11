"""
Quick script to test email configuration.
"""
import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ozed_tech_project.settings')
django.setup()

from django.core.mail import send_mail
from django.conf import settings

print("Testing email configuration...")
print(f"Email Backend: {settings.EMAIL_BACKEND}")
print(f"Email Host: {settings.EMAIL_HOST}")
print(f"Email Port: {settings.EMAIL_PORT}")
print(f"Email User: {settings.EMAIL_HOST_USER}")
print(f"Use TLS: {settings.EMAIL_USE_TLS}")
print(f"From Email: {settings.DEFAULT_FROM_EMAIL}")
print("-" * 50)

try:
    # Test SMTP connection
    from django.core.mail import get_connection

    print("\n1. Testing SMTP connection...")
    conn = get_connection()
    conn.open()
    print("   [OK] SMTP connection successful!")
    conn.close()

    # Send test email
    print("\n2. Sending test email...")
    result = send_mail(
        subject='Test Email from Ozed Tech',
        message='This is a test email to verify email configuration is working correctly.',
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[settings.EMAIL_HOST_USER],  # Send to yourself
        fail_silently=False,
    )

    if result == 1:
        print(f"   [OK] Test email sent successfully to {settings.EMAIL_HOST_USER}!")
        print("\n[SUCCESS] Email configuration is working correctly!")
    else:
        print("   [ERROR] Email sending failed (no exception but result = 0)")

except Exception as e:
    print(f"\n[ERROR] Error: {str(e)}")
    print("\nPossible issues:")
    print("1. Gmail App Password might be incorrect")
    print("2. 'Less secure app access' needs to be enabled (not recommended)")
    print("3. 2-Factor Authentication required with App Password")
    print("4. Email account might be blocked or have restrictions")
    print("\nTo fix:")
    print("- Make sure you're using a Gmail App Password, not your regular password")
    print("- Go to: https://myaccount.google.com/apppasswords")
    print("- Generate a new app password and update settings.py")
