from rest_framework import status
from django.conf import settings
from rest_framework.exceptions import NotFound
import jwt
import boto3
from botocore.client import Config
from rest_framework.pagination import PageNumberPagination
from ..models import Applications
from ..serializers import ApplicationsSerializer
from rest_framework.response import Response
from rest_framework.views import APIView 
from django.utils.html import escape
import base64
from django.shortcuts import get_object_or_404
import os

class Aplicants(APIView): # make this give u the applications for a spesfic job(jid)
    def get(self,request,apid, format = None):
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return Response({'error': 'Authorization header missing or invalid'}, status=status.HTTP_401_UNAUTHORIZED)
        
        token = auth_header.split(' ')[1]

        try:
            payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
            if payload['role'] == 'c':
                # Fetch applications for this post
                apps = Applications.objects.filter(cid=payload['cid'], jid=apid).select_related('sid', 'jid').order_by('-id')
                paginator = PageNumberPagination()
                paginator.page_size = 4  # applications per page

                result_page = paginator.paginate_queryset(apps, request)
                serialized = ApplicationsSerializer(result_page, many=True)
                return Response(serialized.data,status=status.HTTP_200_OK)
            else:# student apps
               apps = Applications.objects.filter(sid=payload['sid']).select_related('sid', 'jid').order_by('-id')
               paginator = PageNumberPagination()
               paginator.page_size = 4  # applications per page

               result_page = paginator.paginate_queryset(apps, request)
               serialized = ApplicationsSerializer(result_page, many=True)
               print(payload['user_id'])
               return Response(serialized.data,status=status.HTTP_200_OK)
        except jwt.ExpiredSignatureError:
            return Response({'error': 'Token has expired'}, status=status.HTTP_401_UNAUTHORIZED)
        except jwt.InvalidTokenError:
            return Response({'error': 'Invalid token'}, status=status.HTTP_401_UNAUTHORIZED)
        except NotFound:
            return Response({'detail': 'Invalid page number'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': 'something went wrong!'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CV(APIView):
    def get(self, request,apId , format = None):
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return Response({'error': 'Authorization header missing or invalid'}, status=status.HTTP_401_UNAUTHORIZED)
        
        token = auth_header.split(' ')[1]
        try:
         payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
         if payload["role"] == "c":
            cv = Applications.objects.filter(id=apId,cid=payload['cid']).values('path').first()
            object_key = cv['path']
            cv_file = ""

            # with open(cv_path,'rb') as file:
            #     cv_file = file.read()
            s3_client = boto3.client(
                's3',
                endpoint_url=f"https://{settings.MINIO_ENDPOINT}:{settings.MINIO_PORT}",
                aws_access_key_id=settings.MINIO_ACCESS_KEY,
                aws_secret_access_key=settings.MINIO_SECRET_KEY,
                region_name=settings.MINIO_REGION,
                use_ssl=settings.MINIO_USE_SSL,
                config=Config(signature_version='s3v4')
            )
            response = s3_client.get_object(Bucket=settings.MINIO_BUCKET, Key=object_key)
            cv_file = response['Body'].read()
            encoded_cv= base64.b64encode(cv_file).decode()
            return Response({'cv':encoded_cv},status=status.HTTP_200_OK)
         else:
            return Response({"error":"You must be a compony!"}, status=status.HTTP_401_UNAUTHORIZED)
         
        except jwt.ExpiredSignatureError:
         return Response({'error': 'Token has expired'}, status=status.HTTP_401_UNAUTHORIZED)
        except jwt.InvalidTokenError:
         return Response({'error': 'Invalid token'}, status=status.HTTP_401_UNAUTHORIZED)
        except Exception as e:
         return Response({'error': f"something went wrong!"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class StudentApplications(APIView):
    def get(self, request, format=None):
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return Response({'error': 'Authorization header missing or invalid'}, status=status.HTTP_401_UNAUTHORIZED)
        
        token = auth_header.split(' ')[1]

        try:
            payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
            if payload['role'] == 's':  # Only students can access this
                # Get all applications for this student
                apps = Applications.objects.filter(sid=payload['sid']).select_related('sid', 'jid').order_by('-id')
                serialized = ApplicationsSerializer(apps, many=True)
                return Response(serialized.data, status=status.HTTP_200_OK)
            else:
                return Response({"error": "Only students can access this endpoint!"}, status=status.HTTP_401_UNAUTHORIZED)
        except jwt.ExpiredSignatureError:
            return Response({'error': 'Token has expired'}, status=status.HTTP_401_UNAUTHORIZED)
        except jwt.InvalidTokenError:
            return Response({'error': 'Invalid token'}, status=status.HTTP_401_UNAUTHORIZED)
        except Exception as e:
            return Response({'error': 'Something went wrong!'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
