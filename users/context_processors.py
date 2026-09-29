from .models import effective_tab_config


def tab_config(request):
    colony = getattr(request, 'colony', None)
    if colony is None:
        return {'tab_config': []}
    return {'tab_config': effective_tab_config(colony)}
