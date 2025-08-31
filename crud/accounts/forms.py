from allauth.account.forms import SignupForm
from captcha.fields import CaptchaField
from django.utils.translation import gettext_lazy as _

class CustomSignupForm(SignupForm):
    captcha = CaptchaField(label=_('Verificación'))
    
    def __init__(self, *args, **kwargs):
        super(CustomSignupForm, self).__init__(*args, **kwargs)
    