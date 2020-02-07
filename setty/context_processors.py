import setty
from django.conf import settings
from django.urls import resolve


def setty_settings(request):
    """
    Adds the Setty settings config into theRequestContext.

    Add 'setty.context_processors.setty_settings' to the
    TEMPLATE_CONTEXT_PROCESSORS setting to ensure this can be used.
    """

    app_name = resolve(request.path).app_name
    tags = {'setty_current_app': setty.config.get_for_app(app_name), 'setty': setty.config}

    return tags
