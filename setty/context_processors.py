import setty


def setty_settings(request):
    """
    Adds the Setty settings config into theRequestContext.

    Add 'setty.context_processors.setty_settings' to the
    TEMPLATE_CONTEXT_PROCESSORS setting to ensure this can be used.
    """
    return {'setty': setty.config}
