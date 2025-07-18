from rest_framework import status
from django.conf import settings
import jwt
from ..models import Jobs
import boto3
from botocore.client import Config
from ..models import Student
from ..models import Applications
from rest_framework.response import Response
from rest_framework.views import APIView 
from django.utils.html import escape
import base64
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import os
import uuid


@method_decorator(csrf_exempt, name='dispatch')
class Applly(APIView):
    def post(self,request,jid,format = None):
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return Response({'error': 'Authorization header missing or invalid'}, status=status.HTTP_401_UNAUTHORIZED)
        token = auth_header.split(' ')[1]

        try:
            payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
            print(f"Decoded JWT payload: {payload}")
            
            # Setup MinIO S3 client
            try:
                s3_client = boto3.client(
                    's3',
                    endpoint_url=f"https://{settings.MINIO_ENDPOINT}:{settings.MINIO_PORT}",
                    aws_access_key_id=settings.MINIO_ACCESS_KEY,
                    aws_secret_access_key=settings.MINIO_SECRET_KEY,
                    region_name=settings.MINIO_REGION,
                    use_ssl=settings.MINIO_USE_SSL,
                    config=Config(signature_version='s3v4')
                )
                print("MinIO S3 client created successfully")
            except Exception as e:
                print(f"Error creating MinIO S3 client: {e}")
                return Response({'error': 'Storage service configuration error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            # jid = escape(request.data.get("jid"))
            cv_b64 = request.data.get("cv")
            cover = escape(request.data.get("cover"))
            print(f"Application request - JID: {jid}, CV length: {len(cv_b64) if cv_b64 else 0}")
            
            if payload["role"] == "s" and jid != "None" and cv_b64:
                if Applications.objects.filter(jid=jid, sid=payload['sid']).exists():
                    return Response({'error': 'You have already applied to this job!'}, status=status.HTTP_400_BAD_REQUEST)

                # file_path = settings.CV_STORAGE_PATH
                # file_name = f"{uuid.uuid4().hex}.pdf"

                header = cv_b64[:30]
                if "JVBER" not in header.upper():  # basic PDF magic check (Not for security reason as this can be easly bypassed)
                    print(f"Invalid PDF format detected. Header: {header}")
                    return Response({'error': 'Invalid file format'}, status=status.HTTP_400_BAD_REQUEST)
                
                try:
                    # save the CV
                    MAX_CV_SIZE = 5 * 1024 * 1024  # 5MB
                    cv_bytes = base64.b64decode(cv_b64)
                    print(f"CV decoded, size: {len(cv_bytes)} bytes")
                    
                    if len(cv_bytes) > MAX_CV_SIZE:
                        return Response({'error': 'CV file size exceeds the 5MB limit'}, status=status.HTTP_400_BAD_REQUEST)
                    
                    object_key = f"uploads/CVs/{uuid.uuid4().hex}.pdf"
                    print(f"Uploading to MinIO with key: {object_key}")
                    
                    # Upload to MinIO
                    s3_client.put_object(
                        Bucket=settings.MINIO_BUCKET,
                        Key=object_key,
                        Body=cv_bytes,
                        ContentType='application/pdf'
                    )
                    print("File uploaded to MinIO successfully")
                    
                    # full_path = os.path.join(file_path, file_name)
                    # os.makedirs(file_path, exist_ok=True)  # Ensure directory exists
                    # with open(full_path, "wb") as f:
                    #     f.write(cv_bytes)

                    uid = payload["user_id"]
                    student = get_object_or_404(Student, uid__id=uid)
                    job = get_object_or_404(Jobs, id=jid)
                    compony = job.cid

                    application = Applications(
                        cid=compony,
                        sid=student,
                        jid=job,
                        path=object_key,
                        cover_letter=cover
                    )
                    application.save()
                    print("Application saved to database successfully")
                    return Response({'success': 'You successfuly applied!'},status=status.HTTP_200_OK)
                except Exception as e:
                    print(f"Error during application processing: {e}")
                    return Response({'error': "Something went wrong!"}, status=status.HTTP_400_BAD_REQUEST)
            else:
                print(f"Invalid application data - Role: {payload.get('role')}, JID: {jid}, CV present: {bool(cv_b64)}")
                return Response({"error":"You must be a student!"}, status=status.HTTP_401_UNAUTHORIZED)
                
        except jwt.ExpiredSignatureError:
            print("JWT token expired")
            return Response({'error': 'Token has expired'}, status=status.HTTP_401_UNAUTHORIZED)
        except jwt.InvalidTokenError:
            print("Invalid JWT token")
            return Response({'error': 'Invalid token'}, status=status.HTTP_401_UNAUTHORIZED)
        except Exception as e:
            print(f"Unexpected error in application processing")
            return Response({'error': 'something went wrong!'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)