from rest_framework import serializers
from .models import Users
from .models import Jobs, Applications, Student, Compony

class UsersSerializer(serializers.ModelSerializer):
    class Meta:
        model = Users
        fields = ["id","userName","role"]


class StudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = ["id", "Fullname"]

class CompanySerializer(serializers.ModelSerializer):
    # job_count = serializers.SerializerMethodField()
    class Meta:
        model = Compony
        fields = ["id", "name", "hr_mail", "website"]
    
    # def get_job_count(self, obj):
    #     return Jobs.objects.filter(cid=obj).exclude(status="deleted").count()

class JobSerializer(serializers.ModelSerializer):
    cid = CompanySerializer()  # nested company info
    applicants_count = serializers.SerializerMethodField()

    class Meta:
        model = Jobs
        fields = ["short_description","description","title","location","end","id","cid","status","work_mode","work_type","applicants_count","application_deadline","posted_date"]
    
    def get_applicants_count(self, obj):
        return Applications.objects.filter(jid=obj).count()

class ApplicationsSerializer(serializers.ModelSerializer):
    sid = StudentSerializer()  # nested student info
    jid = JobSerializer()      # nested job info

    class Meta:
        model = Applications
        fields = ["id", "application_date", "status", "sid", "jid", "cover_letter"]