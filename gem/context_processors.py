from molo.profiles.forms import ProfilePasswordChangeForm


def default_forms(request):
    return {
        'password_change_form': ProfilePasswordChangeForm()
    }

# TODO: remove this context processor


def detect_freebasics(request):
    return {
        'is_via_freebasics':
            'Internet.org' in request.META.get('HTTP_VIA', '') or
            'InternetOrgApp' in request.META.get('HTTP_USER_AGENT', '') or
            'true' in request.META.get('HTTP_X_IORG_FBS', '')
    }
