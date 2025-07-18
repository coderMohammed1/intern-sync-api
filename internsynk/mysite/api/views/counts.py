from rest_framework import status
from django.conf import settings
from rest_framework.views import APIView 
import jwt
from rest_framework.response import Response
from ..models import Jobs, Applications
from django.db.models import Q

class Counts(APIView): # number of posted jobs
    def get(self, request, format=None):
        try:
            auth_header = request.headers.get('Authorization')
            if not auth_header or not auth_header.startswith('Bearer '):
                return Response({'error': 'Authorization header missing or invalid'}, status=status.HTTP_401_UNAUTHORIZED)
            token = auth_header.split(' ')[1]
            payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])

            if payload["role"] != 'c':
                return Response({'error': 'Compony only!'}, status=status.HTTP_401_UNAUTHORIZED)

            JobsCount = Jobs.objects.filter(cid=payload['cid'],status="active").count()
            return Response({"postedJobs#":JobsCount}, status=status.HTTP_200_OK)
        except jwt.ExpiredSignatureError:
            return Response({'error': 'Token has expired'}, status=status.HTTP_401_UNAUTHORIZED)
        except jwt.InvalidTokenError:
            return Response({'error': 'Invalid token'}, status=status.HTTP_401_UNAUTHORIZED)
        except Exception as e:
            return Response({'error': 'something went wrong!'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class Applicants_number(APIView):
    def get(self, request, format = None):
        try:
            auth_header = request.headers.get('Authorization')
            if not auth_header or not auth_header.startswith('Bearer '):
                return Response({'error': 'Authorization header missing or invalid'}, status=status.HTTP_401_UNAUTHORIZED)
            token = auth_header.split(' ')[1]
            payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])

            if payload["role"] != 'c':
                return Response({'error': 'Compony only!'}, status=status.HTTP_401_UNAUTHORIZED)

            numberOfApplications = Applications.objects.filter(
                cid=payload['cid']
            ).exclude(
                Q(status__startswith="rejected") | Q(status__startswith="accepted")
            ).count()
            return Response({"#Applications":numberOfApplications}, status=status.HTTP_200_OK)
        except jwt.ExpiredSignatureError:
            return Response({'error': 'Token has expired'}, status=status.HTTP_401_UNAUTHORIZED)
        except jwt.InvalidTokenError:
            return Response({'error': 'Invalid token'}, status=status.HTTP_401_UNAUTHORIZED)
        except Exception as e:
            return Response({'error': f'something went wrong!'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class StudentApplications(APIView):
    def get(self, request,stat, format=None):
        try:
            auth_header = request.headers.get('Authorization')
            if not auth_header or not auth_header.startswith('Bearer '):
                return Response({'error': 'Authorization header missing or invalid'}, status=status.HTTP_401_UNAUTHORIZED)
            token = auth_header.split(' ')[1]
            payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])

            if payload["role"] != 's':
                return Response({'error': 'Student only!'}, status=status.HTTP_401_UNAUTHORIZED)
            
            if not stat:
                return Response({"error":"Invalid status"}, status=status.HTTP_400_BAD_REQUEST)
            
            if stat == "pending":
                pendingApllications = Applications.objects.filter(
                    sid=payload['sid']
                ).filter(
                    Q(status__startswith="pending")
                ).count()
                return Response({"#pending":pendingApllications}, status=status.HTTP_200_OK)
            elif stat == "accepted":
                acceptedApllications = Applications.objects.filter(
                    sid=payload['sid']
                ).filter(
                    Q(status__startswith="accepted")
                ).count()
                return Response({"#accepted":acceptedApllications}, status=status.HTTP_200_OK)
            elif stat == "under_review":
                under_review = Applications.objects.filter(
                    sid=payload['sid']
                ).filter(
                    Q(status__startswith="under_review")
                ).count()
                return Response({"#under_review":under_review}, status=status.HTTP_200_OK)
            else:
                return Response({"error":"Invalid status"}, status=status.HTTP_400_BAD_REQUEST)

        except jwt.ExpiredSignatureError:
            return Response({'error': 'Token has expired'}, status=status.HTTP_401_UNAUTHORIZED)
        except jwt.InvalidTokenError:
            return Response({'error': 'Invalid token'}, status=status.HTTP_401_UNAUTHORIZED)
        except Exception as e:
            return Response({'error': f'something went wrong!'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        