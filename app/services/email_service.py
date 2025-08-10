"""
Simple email service - simplified version that won't break imports
"""

def send_email(email_to: str, subject: str, html_content: str, background_tasks=None):
    """Simplified email function that doesn't actually send emails but logs them"""
    print(f"📧 Email would be sent to: {email_to}")
    print(f"📧 Subject: {subject}")
    print(f"📧 Content: {html_content[:100]}...")
    return {"message": "Email queued (simulation)"}

def send_payment_confirmation(email_to: str, amount: float, background_tasks=None):
    """Send payment confirmation email"""
    return send_email(
        email_to=email_to,
        subject="Payment Confirmation",
        html_content=f"<h1>Payment Confirmed</h1><p>Amount: ${amount}</p>",
        background_tasks=background_tasks
    )
