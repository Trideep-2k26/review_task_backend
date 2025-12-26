from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response


@api_view(['GET'])
@permission_classes([AllowAny])
def api_root(request):
    return Response({
        'message': 'Review API',
        'version': '1.0',
        'endpoints': {
            'authentication': {
                'register': '/api/register/',
                'login': '/api/login/',
            },
            'reviews': {
                'create_review': '/api/reviews/',
            },
            'places': {
                'search_places': '/api/places/search/',
                'place_details': '/api/places/{id}/',
            }
        },
        'documentation': {
            'auth_required': 'All endpoints except register and login require Token authentication',
            'auth_header': 'Authorization: Token <your-token>',
            'rate_limit': '60 requests per minute'
        }
    })
