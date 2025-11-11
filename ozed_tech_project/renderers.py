from rest_framework import renderers
from django.template.loader import render_to_string


class SimpleHTMLRenderer(renderers.TemplateHTMLRenderer):
    """
    Simple HTML renderer for API endpoints
    """
    template_name = 'api_simple.html'

    def get_template_context(self, data, renderer_context):
        view = renderer_context['view']
        request = renderer_context['request']

        # Get the view name and description
        view_name = view.get_view_name()
        view_description = view.get_view_description()

        # Check if this is a list or detail view
        is_list = isinstance(data, list) or (isinstance(data, dict) and 'results' in data)

        context = {
            'data': data,
            'view_name': view_name,
            'view_description': view_description,
            'is_list': is_list,
            'request': request,
            'user': request.user,
        }

        return context
