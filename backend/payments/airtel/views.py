from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
from .services import process_airtel_callback


@csrf_exempt
@require_http_methods(["POST"])
def airtel_callback(request):
    """Handle Airtel Money callback/webhook"""
    try:
        callback_data = json.loads(request.body)
        result = process_airtel_callback(callback_data)
        
        if result.get('success'):
            return JsonResponse({
                'status': 'success',
                'message': 'Callback processed'
            })
        else:
            return JsonResponse({
                'status': 'error',
                'message': result.get('error', 'Processing failed')
            })
    
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        })
