from rest_framework.views import APIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
from django.db.models import Q
import jwt
from ..models import Jobs
from ..serializers import JobSerializer

class SearchAndSort(APIView):
    def get(self, request, format=None):
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return Response({'error': 'Authorization header missing or invalid'}, status=status.HTTP_401_UNAUTHORIZED)
        
        token = auth_header.split(' ')[1]
        try:
            payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
            # if payload.get("role") != "s":
            #     return Response({'error': 'Student only!'}, status=status.HTTP_401_UNAUTHORIZED)

            search = request.GET.get("searchJobs", "")
            work_type = request.GET.get("work_type")
            work_mode = request.GET.get("work_mode")
            stat = request.GET.get("status")
            jobs = ""

            if work_type not in dict(Jobs.WORK_TYPE_CHOICES) and work_type is not None or \
               work_mode not in dict(Jobs.WORK_MODE_CHOICES) and work_mode is not None:
                return Response({'error': 'Invalid work_type or work_mode'}, status=status.HTTP_400_BAD_REQUEST)
            filters = Q() 
            if search:
                filters &= (
                    Q(title__icontains=search) |
                    Q(short_description__icontains=search) |
                    Q(location__icontains=search) |
                    Q(cid__name__icontains=search)
                )
            if work_type:
                filters &= Q(work_type=work_type) # &= means in case it was provided add it to the query
            if work_mode:
                filters &= Q(work_mode=work_mode)
            if stat:
                filters &= Q(status=stat)
            if payload['role'] == 'c': # for comp...
                filters &= Q(cid=payload['cid'])
                jobs = Jobs.objects.filter(filters).exclude(status="deleted").select_related('cid').order_by('-id')
            else:
                filters &= Q(status='active')
                jobs = Jobs.objects.filter(filters).select_related('cid').order_by('-id')

            paginator = PageNumberPagination()
            paginator.page_size = 4
            result_page = paginator.paginate_queryset(jobs, request)
            serialized = JobSerializer(result_page, many=True)
            return Response(serialized.data, status=status.HTTP_200_OK)

        except jwt.ExpiredSignatureError:
            return Response({'error': 'Token has expired'}, status=status.HTTP_401_UNAUTHORIZED)
        except jwt.InvalidTokenError:
            return Response({'error': 'Invalid token'}, status=status.HTTP_401_UNAUTHORIZED)
        except Exception as e:
            return Response({'error': 'Something went wrong!'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
