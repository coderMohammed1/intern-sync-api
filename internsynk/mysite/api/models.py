from django.db import models
from django.utils import timezone

# parent class for student and compony.
class Users(models.Model):
    userName = models.CharField(max_length=45,blank=False,null=False,unique=True)
    role = models.CharField(max_length=1,blank=False,null=False) # c for compony and s for student
    password = models.CharField(max_length=150,blank=False,null=False)
    
    def __str__(self):
        return self.userName
    

class Compony(models.Model):
    name = models.CharField(max_length=45, blank=False, null=False, unique=True)
    hr_mail = models.EmailField(unique=True)
    website = models.URLField()
    uid = models.ForeignKey(Users, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

class Student(models.Model):
    Fullname = models.CharField(max_length=45, blank=False, null=False, unique=True)
    uid = models.ForeignKey(Users, on_delete=models.CASCADE)

    def __str__(self):
        return self.name
    
class Jobs(models.Model):
    WORK_MODE_CHOICES = [
        ('On-Site', 'On-Site'),
        ('Remote', 'Remote'),
        ('Hybrid', 'Hybrid'),
    ]
    
    WORK_TYPE_CHOICES = [
        ('Full-Time', 'Full-Time'),
        ('Part-Time', 'Part-Time'),
    ]
    
    title = models.CharField(max_length=45, blank=False, null=False)
    description = models.TextField(blank=False, null=False)
    short_description = models.TextField(blank=False, null=False)
    location = models.CharField(max_length=250, blank=False, null=False)
    end = models.CharField(max_length=12, blank=False, null=True) # replaced be deadline
    cid = models.ForeignKey(Compony, on_delete=models.CASCADE) # compony id 
    status = models.CharField(max_length=20, blank=False, null=False, default="draft")
    work_mode = models.CharField(max_length=10, choices=WORK_MODE_CHOICES, default='On-Site', blank=False, null=False)
    work_type = models.CharField(max_length=10, choices=WORK_TYPE_CHOICES, default='Full-Time', blank=False, null=False)
    application_deadline = models.DateTimeField(default=timezone.now)
    posted_date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.title
    
class Applications(models.Model):
    cid = models.ForeignKey(Compony, on_delete=models.CASCADE)
    sid = models.ForeignKey(Student, on_delete=models.CASCADE)
    jid = models.ForeignKey(Jobs, on_delete=models.CASCADE)
    application_date = models.DateTimeField(auto_now_add=True)
    status =  models.CharField(max_length=50, blank=False, null=False, default="pending")
    path = models.TextField(blank=False, null=False)
    cover_letter = models.TextField(blank=False, null=False,  default="Not provided")


    def __str__(self):
        return self.path
