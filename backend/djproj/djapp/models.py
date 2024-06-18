from django.db import models
from django.contrib.auth.models import AbstractBaseUser,PermissionsMixin,BaseUserManager
import random
import uuid
import string


class UserAccountManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Users must have an email address')

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)

        user.set_password(password)
        user.save()

        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_admin', True)  # Ensure superusers are admins by default

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)



class UserAccount(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(max_length=255, unique=True)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    is_admin = models.BooleanField(default =False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    usn = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    profile_photo = models.ImageField(upload_to='profile_photos/', blank=True, null=True)
    first_letter = models.CharField(max_length=15, blank=True, null=True)
    color = models.CharField(max_length=15, blank=True, null=True)

    objects = UserAccountManager()
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    def get_full_name(self):
        return self.first_name
   
    def get_short_name(self):
        return self.first_name
   
    def __str__(self):
        return self.email

    def get_random_color(self):
        return "#{:06x}".format(random.randint(0, 0xFFFFFF))

    def generate_placeholder_picture(self, email):
        return {
            "background_color": self.get_random_color(),
            "initial": email[0].upper() if email else ''
        }

    def save(self, *args, **kwargs):
        if not self.pk:  # Check if the instance is being created
            placeholder = self.generate_placeholder_picture(self.email)
            self.color = placeholder["background_color"]
            self.first_letter = placeholder["initial"]
        super(UserAccount, self).save(*args, **kwargs)

class Project(models.Model):
        projectname = models.CharField(max_length=100)
        projectid = models.CharField(primary_key=True, max_length=20)
        teamlead_email = models.EmailField( null=True)

        def __str__(self):
            return f"{self.projectid} - {self.projectname}"

class Project_TeamMember(models.Model):
        project = models.ForeignKey(Project, on_delete=models.CASCADE)
        team_member_email = models.EmailField(null=True)

        def __str__(self):
            return f"{self.project.projectid} - {self.team_member_email}"


class Sprint(models.Model):
    
    sprint = models.CharField(primary_key=True, max_length=20, default=None)
    sprintName = models.CharField( max_length=20, default="",unique=True,null=True)
    start_date = models.DateField(null=True, blank=True, default=None)
    end_date = models.DateField(null=True, blank=True, default=None)
    sprint_goal=models.TextField(null=True,default="")
    status=models.CharField( max_length=20, default="start")
    project = models.ForeignKey(Project, on_delete=models.SET_NULL, null=True, blank=True)
    
class Epic(models.Model):
    EpicName = models.CharField( max_length=20, default=None)
    projectId = models.ForeignKey(Project, on_delete=models.SET_NULL, null=True, blank=True,default="null")
    Epic_id = models.UUIDField(primary_key=True,default=uuid.uuid4, editable=False, unique=True)
    start_date = models.DateField()
    end_date = models.DateField(default='')
    status = models.CharField( max_length=20, default=None)
    assignee = models.CharField( max_length=80, default=None)
    assigned_by = models.CharField( max_length=80, default=None)
    description = models.TextField(max_length=300,default="")
    file_field = models.FileField(upload_to='uploads/', default='default_file.txt')
    StoryPoint = models.IntegerField(default=1)
    Priority = models.CharField(max_length=30,default="")

    

class issue(models.Model):
    IssueName = models.CharField(max_length=30,default="",unique=True)
    issue_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    sprint = models.ForeignKey(Sprint, on_delete=models.SET_NULL, null=True, blank=True,default="null")
    projectId = models.ForeignKey(Project, on_delete=models.SET_NULL, null=True, blank=True,default="null")
    IssueType=models.CharField(max_length=30,default="")
    status=models.CharField(max_length=30,default="To-Do")
    assignee=models.CharField(max_length=30,default="",null=True)
    assigned_by=models.CharField(max_length=30,default="")
    description=models.TextField(max_length=30,default="")
    file_field = models.FileField(upload_to='uploads/', default='default_file.txt')
    assigned_epic=models.ForeignKey(Epic, on_delete=models.SET_NULL, null=True, blank=True,default="")
    StoryPoint = models.IntegerField(default=1)
    Priority = models.CharField(max_length=30,default="")

from django.utils import timezone
class Comments(models.Model):
    CommentId = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    IssueId = models.ForeignKey(issue, on_delete=models.CASCADE, null=True, blank=True, default="null")
    ProjectId = models.ForeignKey(Project, on_delete=models.SET_NULL, null=True, blank=True, default="null")
    WrittenBy = models.CharField(max_length=50, default='')
    CreatedAt = models.DateTimeField(default=timezone.now)
    EditedAt = models.DateTimeField(default=timezone.now)
    CommentBody = models.TextField(max_length=300, default='')