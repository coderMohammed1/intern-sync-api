from rest_framework import status
from ..models import Users
from ..models import Student
from django.conf import settings
import jwt
import datetime
from ..models import Compony
from rest_framework.response import Response
from rest_framework.views import APIView # custom
from django.contrib.auth.hashers import make_password
from django.utils.html import escape
from django.contrib.auth.hashers import check_password

class Regester(APIView):
    def post(self, request, format = None):
        uname = escape(request.data.get("userName")).strip()
        role = escape(request.data.get("role")) # escap is used to filter against xss
        password=request.data.get("password")
        if len(password) > 40:
            return Response({'error': 'Password is too long!'}, status=status.HTTP_400_BAD_REQUEST)
        password = make_password(request.data.get("password"))

        if uname != "None" and password and role != "None" and (role == "c" or role == "s"):
            if  not Users.objects.filter(userName=uname).exists():
                try:
                    user = Users(userName=uname, role=role, password=password)
                    user.save()

                    # now we complete the data based on the role:
                    if role == "s":
                        fullName = escape(request.data.get("fullName"))
                        if fullName != "None":
                            try:
                                student = Student(Fullname=fullName,uid=user)
                                student.save()
                                return Response({'message' :"Data is completed."}, status=status.HTTP_200_OK)
                            except Exception as e:
                                return Response({'Error' :f'Error:Somthing went wrong!'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                    else:
                        componyName = escape(request.data.get("componyName"))
                        website = escape(request.data.get("website")) # test this
                        hr_mail = escape(request.data.get("HRMail"))

                        if hr_mail != "None" and website != "None" and componyName != "None":
                            comp = Compony(name=componyName, website=website,hr_mail=hr_mail,uid=user)
                            comp.save()
                            return Response({'message' :"Data is completed."}, status=status.HTTP_200_OK)
                        else:
                            return Response({'error': 'Missing fields'}, status=status.HTTP_400_BAD_REQUEST)
                except Exception as e:
                    return Response({'Error' :f'{e}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            else:
                return Response({'message': f'User: {uname} has been registered!'}, status=status.HTTP_200_OK) #for security reasones (we do not like username enum) this will make sense  when we add email varification

        return Response({'error': 'Missing fields'}, status=status.HTTP_400_BAD_REQUEST)
    


class Login(APIView):
     def post(self, request, format = None):
        uname = escape(request.data.get("userName"))
        password = request.data.get("password")
        user = Users.objects.filter(userName=uname).first()
        if len(password) > 40:
            return Response({'error': 'Password is too long!'}, status=status.HTTP_400_BAD_REQUEST)
             
        if user and check_password(password, user.password):
            token = ""
            if user.role == "s":
                student = Student.objects.filter(uid=user.id).first()
                payload = {
                        'user_id': user.id,
                        'userName': user.userName,
                        'fullName': student.Fullname,
                        'role': user.role,
                        'sid': student.id,
                        'exp': datetime.datetime.utcnow() + datetime.timedelta(seconds=settings.JWT_EXP_DELTA_SECONDS),
                        'iat': datetime.datetime.utcnow()
                    }
                token = jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
            else:
                compony = Compony.objects.filter(uid=user.id).first()
                payload = {
                        'user_id': user.id,
                        'userName': user.userName,
                        'compony': compony.name,
                        'hr_mail':compony.hr_mail,
                        'website':compony.website,
                        'cid':compony.id,
                        'role': user.role,
                        'exp': datetime.datetime.utcnow() + datetime.timedelta(seconds=settings.JWT_EXP_DELTA_SECONDS),
                        'iat': datetime.datetime.utcnow()
                    }
                token = jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
            return Response({'message' :"AUTHED!","token":token}, status=status.HTTP_200_OK)
        else:
            return Response({'message' :"wrong."}, status=status.HTTP_401_UNAUTHORIZED)
