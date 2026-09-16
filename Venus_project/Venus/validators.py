import re
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _


class CustomPasswordValidator:
    def validate(self, password, user=None):
        if not re.search('[a-zA-Z]', password):
            raise ValidationError(
                PASSWORD_VALIDATION_MSG.get('numeric', _("Le mot de passe doit contenir au moins une lettre.")),
                code='password_no_letter',
            )
        if password.isdigit():
            raise ValidationError(
                PASSWORD_VALIDATION_MSG.get('numeric', _("Le mot de passe ne peut pas être entièrement numérique.")),
                code='password_entirely_numeric',
            )



    def get_help_text(self):
        return _(
            "Votre mot de passe doit contenir au moins une lettre et ne peut pas être entièrement numérique."
        )


PASSWORD_VALIDATION_MSG = {
    'min_length': 'Votre mot de passe doit comporter au moins 8 caractères.',
    'numeric': 'Votre mot de passe ne peut pas être entièrement numérique.',
    # Ajoutez d'autres messages d'erreur personnalisés ici
}
