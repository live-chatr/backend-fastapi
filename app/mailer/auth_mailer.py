from .base_mailer import BaseMailer

class AuthMailer(BaseMailer):
    def send_verification_email(self, user_email: str, user_name: str, token: str):
        verification_url = f"{self.frontend_url}/auth/verify-email?token={token}"

        context = {
            'user_name': user_name,
            'verification_url': verification_url,
            'expiry_hours': 24,
            'support_url': f"{self.frontend_url}/support"
        }

        return self.send_email(
            to_email=user_email,
            subject="Verify Your Email Address",
            template_name="verification_email.html",
            context=context
        )

    def send_welcome_email(self, user_name: str, user_email: str):
        context = {
            'user_name': user_name,
            'dashboard_url': f"{self.frontend_url}/dashboard",
            'support_url': f"{self.frontend_url}/support"
        }

        return self.send_email(
            to_email=user_email,
            subject="Welcome to Our Platform!",
            template_name="welcome_email.html",
            context=context
        )

    def send_password_reset_email(self, user_email: str, user_name: str, token: str):
        reset_url = f"{self.frontend_url}/auth/reset-password?token={token}"

        context = {
            'user_name': user_name,
            'reset_url': reset_url,
            'expiry_minutes': 30,
            'support_url': f"{self.frontend_url}/support"
        }

        return self.send_email(
            to_email=user_email,
            subject="Reset Your Password",
            template_name="password_reset.html",
            context=context
        )

    def mailer_dir(self):
        return 'auth'