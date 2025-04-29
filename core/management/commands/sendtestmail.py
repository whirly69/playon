from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.conf import settings

class Command(BaseCommand):
    help = "Invia un'email di test tramite il backend configurato"

    def handle(self, *args, **kwargs):
        subject = "✔️ Test invio email PlayOn"
        message = (
            "Ciao!\n\n"
            "Questa è una email di test inviata da PlayOn usando il backend:\n"
            f"{settings.EMAIL_BACKEND}\n\n"
            "Se la stai leggendo, significa che l'invio email funziona correttamente 🎉"
        )

        recipient = input("Inserisci l'email di destinazione per il test: ").strip()

        try:
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [recipient],
                fail_silently=False,
            )
            self.stdout.write(self.style.SUCCESS(f"✅ Email inviata a {recipient}"))
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"❌ Errore nell'invio: {e}"))
