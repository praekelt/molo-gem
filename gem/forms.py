import re
from django import forms
from django.forms import Form, CheckboxSelectMultiple
from django.utils.translation import gettext_lazy as _
from gem.constants import GENDERS
from gem import models
from molo.profiles.forms import RegistrationForm, EditProfileForm, DoneForm
from gem.settings import REGEX_EMAIL, REGEX_PHONE

from wagtail.core.models import Site


def validate_no_email_or_phone(input):
    regexes = [REGEX_EMAIL, REGEX_PHONE]
    for regex in regexes:
        match = re.search(regex, input)
        if match:
            return False

    return True


class GemAliasMixin(object):

    def _clean_alias(self):
        """
        Check for email addresses, telephone numbers and any other keywords or
        patterns defined through GemSettings.
        """
        alias = self.cleaned_data['alias']

        if not validate_no_email_or_phone(alias):
            raise forms.ValidationError(
                _(
                    "Sorry, but that is an invalid display name. Please don't"
                    " use your email address or phone number in your display"
                    " name.")
            )

        site = Site.objects.get(is_default_site=True)
        settings = models.GemSettings.for_site(site)

        banned_list = [REGEX_EMAIL, REGEX_PHONE]

        banned_names_with_offensive_language = \
            settings.banned_names_with_offensive_language.split('\n') \
            if settings.banned_names_with_offensive_language else []

        banned_list += banned_names_with_offensive_language

        for keyword in banned_list:
            keyword = keyword.replace('\r', '')
            match = re.search(keyword, alias.lower())
            if match:
                raise forms.ValidationError(
                    _(
                        'Sorry, the name you have used is not allowed. '
                        'Please, use a different name for your display name.'
                    )
                )

        return alias


class PermissionGroupCheckboxSelect(CheckboxSelectMultiple):
    template_name = 'admin/permission_group_checkbox_select.html'

    def create_option(
            self, name, value, label, selected, index,
            subindex=None, attrs=None):

        opt = super().create_option(
            name, value, label, selected, index,
            subindex=subindex, attrs=attrs)
        opt.update({
            'permissions': self.choices.queryset.get(name=label)
            .permissions.all().values_list('name', flat=True)
        })
        return opt


class GemRegistrationForm(GemAliasMixin, RegistrationForm):
    gender = forms.ChoiceField(
        label=_("Gender"),
        choices=GENDERS,
        required=True
    )

    alias = forms.RegexField(
        regex=r'^[\w.@+-]+$',
        widget=forms.TextInput(
            attrs=dict(
                required=True,
                max_length=30,
            )
        ),
        label=_("Display Name"),
        error_messages={
            'invalid': _("This value must contain only letters, "
                         "numbers and underscores."),
        }
    )

    def clean_username(self):
        username = super(GemRegistrationForm, self).clean_username()

        if not validate_no_email_or_phone(username):
            raise forms.ValidationError(
                _(
                    "Sorry, but that is an invalid username. Please don't use"
                    " your email address or phone number in your username."
                )
            )

        return username

    def clean_alias(self):
        return self._clean_alias()

    def clean_email(self):
        return None

    def clean_location(self):
        return None

    def clean_mobile_number(self):
        return None

    def __init__(self, *args, **kwargs):
        super(GemRegistrationForm, self).__init__(*args, **kwargs)
        self.fields['email'].required = False
        self.fields['location'].required = False
        self.fields['mobile_number'].required = False


class GemEditProfileForm(GemAliasMixin, EditProfileForm):
    alias = forms.RegexField(
        regex=r'^[\w.@+-]+$',
        widget=forms.TextInput(
            attrs=dict(
                required=True,
                max_length=30,
            )
        ),
        label=_("Display Name"),
        error_messages={
            'invalid': _("This value must contain only letters, "
                         "numbers and underscores."),
        }
    )

    gender = forms.ChoiceField(
        label=_("Gender"),
        choices=GENDERS,
        required=False
    )

    def clean_alias(self):
        return self._clean_alias()


class GemRegistrationDoneForm(DoneForm):
    gender = forms.ChoiceField(
        label=_("Gender"),
        choices=GENDERS,
        required=False
    )


class ReportCommentForm(Form):
    CHOICES = (
        ('Spam', _('Spam')),
        ('Offensive Language', _('Offensive Language')),
        ('Bullying', _('Bullying')),
        ('Other', _('Other'))
    )

    report_reason = forms.ChoiceField(
        widget=forms.RadioSelect,
        choices=CHOICES
    )
