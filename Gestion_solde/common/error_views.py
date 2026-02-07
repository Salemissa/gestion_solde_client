from django.http import  HttpResponseNotFound, HttpResponseForbidden, HttpResponseBadRequest
import json

def page_not_found(request, exception):
    """
    Custom 404 handler.
    """
    # if request.path.startswith('/api/'):
    return HttpResponseNotFound(json.dumps({'detail':'Resource not found'}), content_type='application/json')

def forbidden(request, exception):
    
    return HttpResponseForbidden(json.dumps({'detail':'Forbidden'}), content_type='application/json')

def bad_request(request, exception):
    
    return HttpResponseBadRequest(json.dumps({'detail':'Bade Request'}), content_type='application/json')