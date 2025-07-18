from rest_framework import status
from django.conf import settings
import jwt
from ..models import Applications, Compony
from rest_framework.response import Response
from rest_framework.views import APIView 
from django.shortcuts import get_object_or_404
import json

class UpdateApplicationStatus(APIView):
    def put(self, request, application_id, format=None):
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return Response({'error': 'Authorization header missing or invalid'}, status=status.HTTP_401_UNAUTHORIZED)
        
        token = auth_header.split(' ')[1]

        try:
            payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
            
            # Only companies can update application status
            if payload['role'] != 'c':
                return Response({"error": "Only companies can update application status!"}, status=status.HTTP_401_UNAUTHORIZED)
            
            # Get the application and verify it belongs to this company
            application = get_object_or_404(Applications, id=application_id, cid=payload['cid'])
            
            # Get the new status from request data
            data = json.loads(request.body) if request.body else {}
            new_status = data.get('status')
            
            if not new_status:
                return Response({'error': 'Status is required'}, status=status.HTTP_400_BAD_REQUEST)
            
            # Valid status options
            valid_statuses = ['pending', 'under_review', 'shortlisted', 'interview_scheduled', 'accepted', 'rejected']
            
            if new_status not in valid_statuses:
                return Response({
                    'error': f'Invalid status. Valid options are: {", ".join(valid_statuses)}'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Update the application status
            application.status = new_status
            application.save()
            
            return Response({
                'message': 'Application status updated successfully',
                'application_id': application.id,
                'new_status': new_status
            }, status=status.HTTP_200_OK)
            
        except jwt.ExpiredSignatureError:
            return Response({'error': 'Token has expired'}, status=status.HTTP_401_UNAUTHORIZED)
        except jwt.InvalidTokenError:
            return Response({'error': 'Invalid token'}, status=status.HTTP_401_UNAUTHORIZED)
        except Exception as e:
            return Response({'error': 'Something went wrong!'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
