from rest_framework import status
from django.conf import settings
import jwt
from ..models import Jobs
from rest_framework.response import Response
from rest_framework.views import APIView 
from django.utils.html import escape

class Edit(APIView):
    def put(self, request,jid,format = None):
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return Response({'error': 'Authorization header missing or invalid'}, status=status.HTTP_401_UNAUTHORIZED)
        
        token = auth_header.split(' ')[1]

        try:
            payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
            jid = escape(jid)
            job_name = escape(request.data.get("title"))
            end_date = escape(request.data.get("endDate"))

            description = escape(request.data.get("job_description"))
            short_description = escape(request.data.get("short_description"))
            location = escape(request.data.get("location"))
            stat = escape(request.data.get("status"))
            work_mode = escape(request.data.get("work_mode", "On-Site"))
            work_type = escape(request.data.get("work_type", "Full-Time"))

            if payload['role'] == 'c' and (stat =="draft" or  stat == "active" or stat =="closed" or stat == "deleted") and  jid != "None" and job_name != "None" and end_date != "None" and description != "None" and short_description != "None" and location != "None":
                updated_count = Jobs.objects.filter(id=jid, cid=payload['cid']).update(
                title=job_name,
                description=description,
                short_description=short_description,
                location=location,
                end=end_date,
                status = stat,
                work_mode = work_mode,
                work_type = work_type
            )
            
            else:
                return Response({'error': 'Missing fields'}, status=status.HTTP_400_BAD_REQUEST)
                
            if updated_count == 0:
                return Response({'error': 'Job not found or no permission'}, status=status.HTTP_404_NOT_FOUND)
            return Response({'success': 'Job updated'}, status=status.HTTP_200_OK)
        except jwt.ExpiredSignatureError:
            return Response({'error': 'Token has expired'}, status=status.HTTP_401_UNAUTHORIZED)
        except jwt.InvalidTokenError:
            return Response({'error': 'Invalid token'}, status=status.HTTP_401_UNAUTHORIZED)
        except Exception as e:
            return Response({'error': 'something went wrong!'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)