from rest_framework import status
from django.conf import settings
import jwt
from ..models import Compony
from rest_framework.exceptions import NotFound
from ..models import Jobs
from rest_framework.response import Response
from rest_framework.views import APIView 
from django.utils.html import escape
from rest_framework.pagination import PageNumberPagination
from ..serializers import JobSerializer
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

@method_decorator(csrf_exempt, name='dispatch')
class Post_job(APIView):
    def post(self, request,  format = None):
        print(f"POST /api/jobs/add - Headers: {dict(request.headers)}")
        print(f"POST /api/jobs/add - Body: {request.data}")
        
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            print("Authorization header missing or invalid")
            return Response({'error': 'Authorization header missing or invalid'}, status=status.HTTP_401_UNAUTHORIZED)
        
        token = auth_header.split(' ')[1]

        try:
            payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
            print(f"Decoded JWT payload: {payload}")
            
            job_name = escape(request.data.get("title"))
            end_date = escape(request.data.get("endDate"))
            description = escape(request.data.get("job_description"))
            short_description = escape(request.data.get("short_description"))
            location = escape(request.data.get("location"))
            work_mode = escape(request.data.get("work_mode", "On-Site"))
            work_type = escape(request.data.get("work_type", "Full-Time"))

            print(f"Job data - Title: {job_name}, End Date: {end_date}, Description: {description[:50]}...")
            
            if payload['role'] == 'c':
                compony_details = Compony.objects.get(id=payload['cid'])
                print(f"Company found: {compony_details.name}")
                
                post = Jobs(title=job_name,cid=compony_details, description=description, short_description=short_description, location=location, end=end_date, work_mode=work_mode, work_type=work_type)
                post.save()
                print(f"Job saved with ID: {post.id}")
                
                return Response({'success': 'Job has been posted!', 'job_id': post.id}, status=status.HTTP_200_OK)
            else:
                print(f"User role '{payload['role']}' is not authorized to post jobs")
                return Response({'error': 'This service is for companies only!'}, status=status.HTTP_401_UNAUTHORIZED)    
            
        except jwt.ExpiredSignatureError:
            print("JWT token has expired")
            return Response({'error': 'Token has expired'}, status=status.HTTP_401_UNAUTHORIZED)
        except jwt.InvalidTokenError as e:
            print(f"Invalid JWT token: {e}")
            return Response({'error': 'Invalid token'}, status=status.HTTP_401_UNAUTHORIZED)
        except Compony.DoesNotExist:
            print(f"Company not found for cid: {payload.get('cid')}")
            return Response({'error': 'Company not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            print(f"Unexpected error posting job: {e}")
            return Response({'error': f'Something went wrong: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

class Get_jobs(APIView):
    def get(self, request, format = None):
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return Response({'error': 'Authorization header missing or invalid'}, status=status.HTTP_401_UNAUTHORIZED)
        
        token = auth_header.split(' ')[1]

        try:
            payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
            if payload["role"] == "c":
                jobs = Jobs.objects.filter(cid=payload["cid"]).exclude(status="deleted").select_related('cid').order_by('-id')
                 # Pagination setup
                paginator = PageNumberPagination()
                paginator.page_size = 4  # Jobs per page
                result_page = paginator.paginate_queryset(jobs, request)
                
                serialized_jobs = JobSerializer(result_page, many=True)
                return Response(serialized_jobs.data,status=status.HTTP_200_OK)
            else:
                # student
                jobs = Jobs.objects.filter(status = "active").select_related('cid').order_by('-id')
                 # Pagination setup
                paginator = PageNumberPagination()
                paginator.page_size = 4  # Jobs per page
                result_page = paginator.paginate_queryset(jobs, request)
                
                serialized_jobs = JobSerializer(result_page, many=True)
                return Response(serialized_jobs.data,status=status.HTTP_200_OK)
        except jwt.ExpiredSignatureError:
            return Response({'error': 'Token has expired'}, status=status.HTTP_401_UNAUTHORIZED)
        except jwt.InvalidTokenError:
            return Response({'error': 'Invalid token'}, status=status.HTTP_401_UNAUTHORIZED)
        except NotFound:
            return Response({'detail': 'Invalid page number'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception:
            return Response({'error': 'something went wrong!'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

