from django import template

register = template.Library()


@register.simple_tag(takes_context=True)
def query_transform(context, **kwargs):
    """Devuelve el querystring actual con los parámetros de kwargs sobreescritos.

    Un valor None elimina el parámetro (se usa para los enlaces "Todas").
    """
    request = context['request']
    actualizado = request.GET.copy()
    for clave, valor in kwargs.items():
        if valor is None:
            actualizado.pop(clave, None)
        else:
            actualizado[clave] = valor
    return actualizado.urlencode()