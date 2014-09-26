from rest_framework.negotiation import DefaultContentNegotiation


class EmberCompliantContentNegotiation(DefaultContentNegotiation):

    def select_renderer(self, request, renderers, format_suffix):

        renderer = super(EmberCompliantContentNegotiation, self).select_renderer(request, renderers, format_suffix)

        print renderer

        return renderer
