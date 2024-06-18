from sqlite3 import IntegrityError
from django.shortcuts import render
from django.http import HttpResponseBadRequest, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import *
from rest_framework import status
from rest_framework.response import Response
from django.middleware.csrf import get_token
from djproj.settings import EMAIL_HOST_USER
from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer
from django.core.mail import send_mail
from .serializers import *
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from rest_framework import generics
import json
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
from django.views.decorators.http import require_POST
from social_django.models import UserSocialAuth
from django.core.exceptions import ObjectDoesNotExist
import random

@csrf_exempt 
def ReactViews(request):
    if request.method == 'GET':
        

        project_id = request.GET.get('projectId')

        try:
            pid1 = Project.objects.get(projectid=project_id)
            issues = issue.objects.filter(projectId=pid1,sprint__isnull=True)
            
            
            serializer = IssueSerializer(issues, many=True)
            
            
            return JsonResponse(serializer.data,safe=False)
        except Project.DoesNotExist:
            return JsonResponse({"error": "Project not found"}, status=status.HTTP_404_NOT_FOUND)
        except issue.DoesNotExist:
            return JsonResponse({"error": "Issues not found for this project"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@csrf_exempt      
def add_issue(request):
  
    if request.method == 'POST':
        data = json.loads(request.body)
        issue_name = data.get('IssueName') 
        pid=data.get('projectId') 
        sprint=data.get('sprint') 
        assigned_epic=data.get('assigned_epic')
        issueType=data.get('IssueType')
        
        pid1 = Project.objects.get(projectid =pid)
        if sprint!=None:
            sprint=Sprint.objects.get(sprint=sprint)

        if issue_name:
            try:
                new_issue = issue.objects.create(IssueName=issue_name, projectId=pid1,sprint=sprint,assigned_epic=assigned_epic,IssueType=issueType)

                return JsonResponse({'success': True, 'message': 'Issue added successfully', 'issue_id': new_issue.issue_id})
            
            except IntegrityError :
                print("eroorrrrrrrrrrrrr hai")
                return Response({"error": "An issue with this name already exists in the project."},
                                status=status.HTTP_400_BAD_REQUEST)
            except Exception as e:
                return JsonResponse({'success': False, 'message': str(e)})
        else:
            return JsonResponse({'success': False, 'message': 'Issue name is required'})
    else:
        return JsonResponse({'success': False, 'message': 'Invalid request method'})
@csrf_exempt 
@csrf_exempt
def create_project(request):
    print("before")
    if request.method == 'POST':
        print(request)
        # Parse request body as JSON
        data = json.loads(request.body)
        project_name = data.get('projectname')
        teamlead = data.get('teamlead')
        projectid = data.get('projectid')
        if project_name:
            project = Project(projectid=projectid,projectname=project_name, teamlead_email=teamlead)
       
            project.save()
            # Create a dictionary with all parameters
            response_data = {
                'message': 'Project created successfully',
                'projectid': project.projectid,
                'projectname': project.projectname,
                'teamlead_email': project.teamlead_email,
            }
           
            return JsonResponse(response_data, status=201)
        else:
            return JsonResponse({'error': 'Project name is required'}, status=400)
    else:
        return JsonResponse({'error': 'Only POST requests are allowed'}, status=405)

@csrf_exempt
def csrf_token(request):
   
    csrf_token = get_token(request)
    print(csrf_token)
    
    return JsonResponse({'csrfToken': csrf_token})
@csrf_exempt
def generate_invitation_token(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        email = data.get('email')
        projectid = data.get('projectid')
          # Get projectid from the request data
        serializer = URLSafeTimedSerializer('your-secret-key')
        token = serializer.dumps(email)
        try:
            project_ins = Project.objects.get(projectid=projectid)
        except Project.DoesNotExist:
            return JsonResponse({'error': 'Project not found'}, status=404)
        
        if Project_TeamMember.objects.filter(team_member_email=email,project=project_ins).exists() or project_ins.teamlead_email == email :
            return JsonResponse({'error': 'Email is already associated with this project'}, status=400)

        else:
            invitation_link = f'http://localhost:3000/accept-invitation?projectid={projectid}&token={token}'

            subject = "Join Project"
            message = f"Welcome! You're invited to join the project with ID {projectid}. Click the link below to accept:\n{invitation_link}"
            
            send_mail(subject, message, EMAIL_HOST_USER, [email], fail_silently=True)
            print("sent")
            return JsonResponse({'token': token})
       
    else:
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    

@csrf_exempt
def verify_invitation_token(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        token = data.get('token')
        projectid = data.get('projectId')
        print(token, "gfkkkkkkkkkkkkkkkkkkkkverify")
        serializer = URLSafeTimedSerializer('your-secret-key')
        try:
            email = serializer.loads(token, max_age=18000)  # Token expires in 5 hours
            user_exists = UserAccount.objects.filter(email=email).exists()
            print(user_exists,"jjjjj")
            if user_exists:
                return JsonResponse({'action': 'login','projectid':projectid})  # Email is associated with an existing user
            else:
                return JsonResponse({'action': 'signup','projectid':projectid})  # Email is not associated with any user account
        except SignatureExpired:
            return JsonResponse({'error': 'Token has expired'}, status=400)
        except BadSignature:
            return JsonResponse({'error': 'Invalid token'}, status=400)
        
@csrf_exempt
def process_invitation_token(request):
    if request.method == 'POST':
        # Extract email, project ID, and invitation token from the request data
        data = json.loads(request.body)
        email = data.get('email')
        project_id = data.get('projectid')
        
        try:
            project_ins = Project.objects.get(projectid=project_id)
        except Project.DoesNotExist:
            return JsonResponse({'error': 'Project not found'}, status=404)
        
        # Check if the email is already a team member for the given project
        if Project_TeamMember.objects.filter(team_member_email=email, project=project_ins).exists():
            return JsonResponse({'message': 'Email is already a team member for this project'}, status=400)
        
        # Add the new team member to the project
        team_member = Project_TeamMember.objects.create(team_member_email=email, project=project_ins)
        team_member.save()
        
        return JsonResponse({'message': 'Invitation processed successfully'})
    else:
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    

@csrf_exempt
def project_list(request):
    if request.method == 'GET':
        email = request.GET.get('email', None)
        
        if not email:
            return JsonResponse({'error': 'Email parameter is missing'}, status=400)
        
        try:
            user = UserAccount.objects.get(email=email)
        except UserAccount.DoesNotExist:
            return JsonResponse({'error': 'User does not exist'}, status=404)
        
        if user.is_admin:
            projects = Project.objects.all()
        else:
            # Retrieve projects where the email matches the team lead
            projects_lead = Project.objects.filter(teamlead_email=email)

            # Retrieve projects where the email matches a team member
            projects_member = Project_TeamMember.objects.filter(team_member_email=email).values('project')  # Retrieve project IDs

            # Combine both lists of projects
            projects = list(projects_lead) + list(Project.objects.filter(pk__in=projects_member))
        
        # Create a list of project data including team lead information
        project_data = [
            {
                'projectid': project.projectid,
                'projectname': project.projectname,
                'teamlead_email': project.teamlead_email
            } 
            for project in projects
        ]
        
        return JsonResponse(project_data, safe=False)
    else:
        return JsonResponse({'error': 'Only GET requests are allowed'}, status=405)

@csrf_exempt
def get_team_members(request):
    if request.method == 'GET':
        project_id = request.GET.get('projectid')
        
        print("inside memeber",project_id)
        if project_id:
            try:
                print("hellllllllllllllllllllllllllllllllll")
                # Fetch all team members for the specified project from the database
                team_members_emails = Project_TeamMember.objects.filter(project__projectid=project_id).values_list('team_member_email', flat=True)
                print("members:",team_members_emails)
                
                # Fetch user details for team members
                team_members = UserAccount.objects.filter(email__in=team_members_emails).values('email', 'first_name', 'last_name')

                # Convert queryset to list of dictionaries
                team_members_list = list(team_members)

                return JsonResponse({'team_members': team_members_list})
            except Exception as e:
                return JsonResponse({'error': f'An error occurred: {str(e)}'}, status=500)
        else:
            return JsonResponse({'error': 'Project ID is required'}, status=400)
    else:
        return JsonResponse({'error': 'Method not allowed'}, status=405)

@csrf_exempt
def get_sprints(request):
    if request.method == 'GET':
        project_id = request.GET.get('projectid')
        # print("pid", project_id)
        if project_id:
            sprints = Sprint.objects.filter(project__projectid=project_id).values('sprint', 'start_date', 'end_date')
            sprint_list = list(sprints)
            # print(sprint_list)
            return JsonResponse({'sprint_in_project': sprint_list})
        else:
            return JsonResponse({'error': 'Project ID is required'}, status=400)
    else:
        return JsonResponse({'error': 'Method not allowed'}, status=405)
@csrf_exempt
def get_activesprints(request):
    if request.method == 'GET':
        project_id = request.GET.get('projectid')
        if project_id:
            sprints = Sprint.objects.filter(project__projectid=project_id, status='complete').values('sprint', 'start_date', 'end_date')
            sprint_list = list(sprints)
            return JsonResponse({'sprint_in_project': sprint_list})
        else:
            return JsonResponse({'error': 'Project ID is required'}, status=400)
    else:
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
@csrf_exempt
def create_issue(request):
    print("i got the issue")
    if request.method == 'POST':
        print("im inside post")
        data = json.loads(request.body)
        pid1 = Project.objects.get(projectid=data.get('ProjectId'))
        if data.get('Sprint') != "":
            sprint = Sprint.objects.get(sprint=data.get('Sprint'))
        else:
            sprint = None
        print("sprint", sprint)
        assigned_epic_name = data.get('Assigned_epic')
        if assigned_epic_name:
            try:
                epic = Epic.objects.get(EpicName=assigned_epic_name)
            except Epic.DoesNotExist:
                epic = None
                print("Epic with name '{}' does not exist".format(assigned_epic_name))
        else:
            epic = None
        print("epic", epic)
        file = request.FILES.get('attachment')
        new_issue = issue.objects.create(
            IssueName=data.get('IssueName'),
            IssueType=data.get('IssueType'),
            sprint=sprint,
            projectId=pid1,
            status=data.get('Status', 'TODO'),
            assignee=data.get('Assignee', ''),
            assigned_by=data.get('Assigned_by', ""),
            description=data.get('Description', ""),
            assigned_epic=epic,
            StoryPoint = data.get('storyPoint', 1),
            Priority = data.get('priority', 'Medium'),
            file_field = file,
        )
        return JsonResponse({'message': 'Issue created successfully'})
    else:
        return JsonResponse({'error': 'Only POST method allowed'}, status=405)
@csrf_exempt
def get_epics(request):
    if request.method == 'GET':
        project_id = request.GET.get('projectid')
        print(f"Project ID received: {project_id}")
        if project_id:
            try:
                print("Before fetching epics")
                epics = Epic.objects.filter(projectId_id=project_id).values('Epic_id', 'EpicName')
                print(f"Epics fetched: {list(epics)}")
                return JsonResponse({'epics_in_project': list(epics)})
            except Exception as e:
                print("Exception occurred while fetching epics:")
                traceback.print_exc()  # Prints the full traceback to the console
                return JsonResponse({'error': str(e)}, status=500)
        else:
            print("Project ID not provided")
            return JsonResponse({'error': 'Project ID not provided'}, status=400)
    else:
        print("Only GET method allowed")
        return JsonResponse({'error': 'Only GET method allowed'}, status=405)

@csrf_exempt
def create_epic(request):
    print("i got the epic")
    if request.method == 'POST':
        print("im inside epc post")
        data = json.loads(request.body)
        pid1 = Project.objects.get(projectid=data.get('ProjectId'))
        file = request.FILES.get('attachment')
        new_epic = Epic.objects.create(
            EpicName = data.get('epicName', 'TODO'),
            projectId=pid1,
            status=data.get('Status', 'TODO'),
            assignee=data.get('Assignee',''),
            assigned_by=data.get('Assigned_by',""),
            description=data.get('Description',""),
            start_date=data.get('StartDate',""),
            end_date=data.get('DueDate',""),
            StoryPoint = data.get('storyPoint', 1),
            Priority = data.get('priority', 'Medium'),
            file_field = file,
        )
        return JsonResponse({'message': 'Issue created successfully'})
    else:
        return JsonResponse({'error': 'Only POST method allowed'}, status=405)

import traceback  # For detailed exception traceback

@csrf_exempt
def filters_function(request):
    print("I'm getting the function call..")
    if request.method == 'GET':
        projectid = request.GET.get('projectid')
        filter_type = request.GET.get('filter')
        status = request.GET.get('status')
        current_user = request.GET.get('currentUser')
        print(projectid, filter_type, status, current_user)

        if not projectid:
            return JsonResponse({"error": "Project ID is required"}, status=400)
        
        issues = []
        
        if projectid == 'allprojects':
                issues = list(issue.objects.filter(assignee=current_user).values())
        else:
            if filter_type == 'all_issues':
                issues = list(issue.objects.filter(projectId_id=projectid).values())
                
            elif filter_type == 'assigned_to_me':
                issues = list(issue.objects.filter(projectId_id=projectid, assignee=current_user).values())
                
            elif filter_type == 'unassigned':
                issues = list(issue.objects.filter(projectId_id=projectid, assignee='').values())
               
            elif filter_type == 'epics':
                issues = list(Epic.objects.filter(projectId_id=projectid).values())
                
            elif filter_type == 'Status':
                issues = list(issue.objects.filter(projectId_id=projectid, status=status).values())
                
            else:
                return JsonResponse({"error": "Invalid filter type"}, status=400)

        return JsonResponse(issues, safe=False)
    else:
        return JsonResponse({"error": "Invalid request method"}, status=405)



@csrf_exempt
def update_issue(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        print(data)
        try:
            issue_obj = issue.objects.get(issue_id=data['issue_id'])
            issue_obj.IssueType = data.get('IssueType', issue_obj.IssueType)
            issue_obj.description = data.get('description', issue_obj.description)
            issue_obj.status = data.get('status', issue_obj.status)
            issue_obj.assignee = data.get('assignee', issue_obj.assignee)
            issue_obj.assigned_by = data.get('assigned_by', issue_obj.assigned_by)
            issue_obj.assigned_epic_id = data.get('assigned_epic_id', issue_obj.assigned_epic_id)
            issue_obj.sprint_id = data.get('sprint_id', issue_obj.sprint_id)
            issue_obj.projectId_id = data.get('projectId_id', issue_obj.projectId_id)
            issue_obj.file_field = data.get('file_field', issue_obj.file_field)
            
            # Validate and convert StoryPoint to integer
            story_point = data.get('StoryPoint')
            if story_point is not None:
                try:
                    issue_obj.StoryPoint = int(story_point)
                except ValueError:
                    return JsonResponse({'status': 'error', 'message': 'StoryPoint must be a number'})
            
            issue_obj.save()
            return JsonResponse({'status': 'success'})
        except issue.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Issue not found'})
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})
from datetime import datetime
from django.shortcuts import get_object_or_404


@csrf_exempt
def create_comment(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        issue_id = data.get('issue_id')
        project_id = data.get('project_id')
        written_by = data.get('written_by')
        comment_body = data.get('comment_body')

        issue_obj = get_object_or_404(issue, issue_id=issue_id)

        comment = Comments(
            IssueId=issue_obj,
            ProjectId=issue_obj.projectId,
            WrittenBy=written_by,
            CommentBody=comment_body,
            CreatedAt=timezone.now(),
            EditedAt=timezone.now()
        )
        comment.save()
        return JsonResponse({'message': 'Comment created successfully'}, status=201)
    return JsonResponse({'error': 'Invalid request method'}, status=400)

def fetch_comments(request, issue_id):
    if request.method == 'GET':
        print(request, issue_id)
        comments = Comments.objects.filter(IssueId=issue_id).order_by('-CreatedAt')
        comments_list = [
            {
                'comment_id': comment.CommentId,
                'issue_id': comment.IssueId.issue_id,
                'project_id': comment.ProjectId.projectid if comment.ProjectId else None,
                'written_by': comment.WrittenBy,
                'comment_body': comment.CommentBody,
                'created_at': comment.CreatedAt.strftime('%Y-%m-%d %H:%M:%S'),
                'edited_at': comment.EditedAt.strftime('%Y-%m-%d %H:%M:%S'),
            } for comment in comments
        ]
        return JsonResponse(comments_list, safe=False)
    return JsonResponse({'error': 'Invalid request method'}, status=400)

from datetime import timedelta

@csrf_exempt
def edit_comment(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        comment_id = data.get('comment_id')
        new_comment_body = data.get('comment_body')
        user_email = data.get('user_email')

        comment = get_object_or_404(Comments, CommentId=comment_id)

        if comment.WrittenBy != user_email:
            return JsonResponse({'error': 'You are not authorized to edit this comment'}, status=403)

        # if timezone.now() - comment.CreatedAt > timedelta(minutes=15):
        #     return JsonResponse({'error': 'You can only edit comments within the first 15 minutes'}, status=403)

        comment.CommentBody = new_comment_body
        comment.EditedAt = timezone.now()
        comment.save()

        return JsonResponse({'message': 'Comment edited successfully'}, status=200)

    return JsonResponse({'error': 'Invalid request method'}, status=400)

from django.db.models import Count

@csrf_exempt
def project_issue_statistics(request, project_id):
    assigned_issues = issue.objects.filter(projectId=project_id).values('assignee').annotate(total=Count('id'))
    done_issues = issue.objects.filter(projectId=project_id, status='Done').values('assignee').annotate(total=Count('id'))
    
    assigned_data = {item['assignee']: item['total'] for item in assigned_issues}
    done_data = {item['assignee']: item['total'] for item in done_issues}
    print(done_data, assigned_data)
    return JsonResponse({'assigned_data': assigned_data, 'done_data': done_data})
@csrf_exempt
def create_sprint(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        project_id = data.get('project')
        sprint_id = data.get('sprint')


        try:
            pid1 = Project.objects.get(projectid=project_id)
        except Project.DoesNotExist:
            return JsonResponse({'message': 'Project not found'}, status=404)

        try:
            sprint_instance = Sprint.objects.get(sprint=sprint_id, project=pid1)
          
            sprint_instance.sprintName=data.get("sprint_name")
            sprint_instance.start_date = data.get('start_date')
            sprint_instance.end_date = data.get('end_date')
            sprint_instance.sprint_goal = data.get('sprint_goal')
            sprint_instance.status = data.get('status')
            sprint_instance.save()

            return JsonResponse({'message': 'Sprint updated successfully'})

        except Sprint.DoesNotExist:
            return JsonResponse({'message': 'Sprint not found'}, status=404)

    return JsonResponse({'message': 'Invalid request method'}, status=400)


@csrf_exempt
def update_sprintName(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            sprint_name = data.get('sprintName', None)
            pid1 = Project.objects.get(projectid=data.get("projectid"))

            if sprint_name:
                sprint = Sprint.objects.create(
                    sprint=sprint_name,project=pid1,sprintName=sprint_name
                )

                return JsonResponse({"message": "Sprint name is required"})
            else:
                return JsonResponse({"message": "Sprint name is required"}, status=400)
        except json.JSONDecodeError:
            return JsonResponse({"message": "Invalid JSON format in request body"}, status=400)
    else:
        return JsonResponse({"message": "Only POST requests are allowed"}, status=405)
    

@csrf_exempt
def countsprints(request):
    if request.method == 'GET':
        project_id = request.GET.get('projectId')
        pid1 = Project.objects.get(projectid=project_id)
        if project_id:
            try:
                sprints = Sprint.objects.filter(project_id=pid1)
                sprints_count = sprints.count()
                serialized_sprints = SprintSerializer( sprints,many=True) 
                
                return JsonResponse({"count": sprints_count, "sprints": serialized_sprints.data}, status=200)
            except Exception as e:
                return JsonResponse({"error": str(e)}, status=500)
        else:
            return JsonResponse({"error": "Project ID is required"}, status=400)
    else:
        return JsonResponse({"error": "Only GET requests are allowed"}, status=405)

@csrf_exempt
def issuesOfSprint(request):
    if request.method == 'GET':
        project_id = request.GET.get('projectId')
        sprint = request.GET.get('sprintName')
        
        pid1 = Project.objects.get(projectid=project_id)
        sprint1 = Sprint.objects.get(sprint=sprint)
        
        try:
            issues = issue.objects.filter(projectId=pid1,sprint=sprint1)
           
            serializer = IssueSerializer(issues, many=True)
            
            return JsonResponse(serializer.data, safe=False)
        
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
    
    else:
        return JsonResponse({"error": "Project ID is required"}, status=400)

@csrf_exempt
def update_issueStatus(request):
    
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            issue_name = data.get('issue', None)
            new_status = data.get('status', None)
            
            pid1 = Project.objects.get(projectid=data.get("projectId"))
            print(data,issue_name,new_status)

            if issue_name:
                Issue = issue.objects.get(IssueName=issue_name,projectId=pid1)
                print(" motto",Issue)
                Issue.status = new_status
                Issue.save()

                return JsonResponse({"message": "Issue status updated"})
            else:
                return JsonResponse({"message": "issue name is required"}, status=400)
        except json.JSONDecodeError:
            return JsonResponse({"message": "Invalid JSON format in request body"}, status=400)
    else:
        return JsonResponse({"message": "Only POST requests are allowed"}, status=405)
@csrf_exempt
def delete_sprint(request):
    print("inside delete")
    if request.method == 'GET':
        try:
            project_id = request.GET.get('projectId')
            sprint_name = request.GET.get('sprintName')
            pid1 = Project.objects.get(projectid=project_id)
            sprintInstance = Sprint.objects.get(sprint=sprint_name, project=pid1)
            sprintInstance.delete()
            return JsonResponse({'message': 'Sprint deleted successfully'}, status=200)
        except Sprint.DoesNotExist:
            return JsonResponse({'error': 'Sprint not found'}, status=404)
        except Project.DoesNotExist:
            return JsonResponse({'error': 'Project not found'}, status=404)
    return JsonResponse({'error': 'Invalid request method'}, status=400)
@csrf_exempt
def delete_issue(request):
    print("inside delete")
    if request.method == 'GET':
        try:
            project_id = request.GET.get('projectId')
            issue_name = request.GET.get('issueName')
            pid1 = Project.objects.get(projectid=project_id)
            issueInstance = issue.objects.get(IssueName=issue_name, projectId=pid1)
            issueInstance.delete()
            return JsonResponse({'message': 'Sprint deleted successfully'}, status=200)
        except Sprint.DoesNotExist:
            return JsonResponse({'error': 'Sprint not found'}, status=404)
        except Project.DoesNotExist:
            return JsonResponse({'error': 'Project not found'}, status=404)
    return JsonResponse({'error': 'Invalid request method'}, status=400)


@csrf_exempt
def updateSprintStatus(request):
    if request.method == 'GET':
        project_id = request.GET.get('projectId')
        sprint_name = request.GET.get('sprintName')

        try:
            project = Project.objects.get(projectid=project_id)
            sprint = Sprint.objects.get(sprint=sprint_name, project=project)

           
            sprint.status = 'completed'
            sprint.save()
            return JsonResponse({"message": "Sprint status updated to completed"}, status=200)

           

        except Project.DoesNotExist:
            return JsonResponse({"error": "Project not found"}, status=404)
        except Sprint.DoesNotExist:
            return JsonResponse({"error": "Sprint not found"}, status=404)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    else:
        return JsonResponse({"error": "Invalid request method"}, status=400)
@csrf_exempt
def update_issueSprint(request):
    
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            issue_name = data.get('issue', None)
            new_sprint = data.get('sprint', None)
            
            pid1 = Project.objects.get(projectid=data.get("projectId"))
            sprint = Sprint.objects.get(sprint=new_sprint, project=pid1)

            if issue_name:
                Issue = issue.objects.get(IssueName=issue_name,projectId=pid1)
                print(" motto",Issue)
                Issue.sprint = sprint
                Issue.save()

                return JsonResponse({"message": "Issue status updated"})
            else:
                return JsonResponse({"message": "issue name is required"}, status=400)
        except json.JSONDecodeError:
            return JsonResponse({"message": "Invalid JSON format in request body"}, status=400)
    else:
        return JsonResponse({"message": "Only POST requests are allowed"}, status=405)
# @csrf_exempt
# def get_epics(request):
#     if request.method == 'GET':
#         project_id = request.GET.get('projectid')
        
#         pid1 = Project.objects.get(projectid=project_id)
#         if project_id:
#             epics = Epic.objects.filter(projectId=pid1).values('EpicName')
#             epic_list = list(epics)
#             print("epic listtttt",epic_list)
#             return JsonResponse({'epic_in_project': epic_list})
#         else:
#             return JsonResponse({'error': 'Project ID is required'}, status=400)
#     else:
#         return JsonResponse({'error': 'Method not allowed'}, status=405)
    
@csrf_exempt
def update_issue_name(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            old_issue_name = data.get('oldIssueName', None)
            new_issue_name = data.get('newIssueName', None)
            
            project_id = data.get('projectId')
          
            print("iniside updte issue name")
            print(old_issue_name)
            
            
            issue_obj = issue.objects.get(projectId=project_id, IssueName=old_issue_name)
           
            issue_obj.IssueName = new_issue_name
            issue_obj.save()
            
            return JsonResponse({'message': 'Issue name updated successfully'})
        except issue.DoesNotExist:
            return JsonResponse({'error': 'Issue not found'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    else:
        return JsonResponse({'error': 'Only POST method is allowed'}, status=405)
@csrf_exempt
def update_issueassignee(request):
    
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            issue_name = data.get('issue', None)
            assignee = data.get('assignee', None)
            
            pid1 = Project.objects.get(projectid=data.get("projectId"))
            

            if issue_name:
                Issue = issue.objects.get(IssueName=issue_name,projectId=pid1)
                print("meeeeeeeeeeeeeeeeeeeee",assignee)
                print(" motto",Issue)
                Issue.assignee = assignee
                Issue.save()

                return JsonResponse({"message": "Issue status updated"})
            else:
                return JsonResponse({"message": "issue name is required"}, status=400)
        except json.JSONDecodeError:
            return JsonResponse({"message": "Invalid JSON format in request body"}, status=400)
    else:
        return JsonResponse({"message": "Only POST requests are allowed"}, status=405)
@csrf_exempt

def gantt_chart_data(request):
    projectid = request.GET.get('projectid')
    print(projectid,"gantt")
    if projectid:
        sprints = Sprint.objects.filter(project_id=projectid).values('sprint', 'sprintName', 'start_date', 'end_date', 'sprint_goal', 'status')
    else:
        sprints = Sprint.objects.none().values('sprint', 'sprintName', 'start_date', 'end_date', 'sprint_goal', 'status')  # returns an empty QuerySet
    
    sprint_data = list(sprints)
    return JsonResponse({'sprints': sprint_data})

@csrf_exempt

def get_random_color():
    
    return "#{:06x}".format(random.randint(0, 0xFFFFFF))

def generate_placeholder_picture(email):
    """Generate a placeholder picture with random background color and initial."""
    return {
        "background_color": get_random_color(),
        "initial": email[0].upper() if email else ''
    }

def get_team_lead(request, projectid):
    if request.method == "GET":
        try:
            project = get_object_or_404(Project, projectid=projectid)
            team_lead_email = project.teamlead_email

            try:
                team_lead_user = UserAccount.objects.get(email=team_lead_email)
                print(team_lead_user)

                team_lead_social_auth = UserSocialAuth.objects.get(uid=team_lead_email)
                team_lead_picture_url = team_lead_social_auth.extra_data.get('picture', None)
            except ObjectDoesNotExist:
                team_lead_picture_url = None

            if not team_lead_picture_url:
                team_lead_picture_url = {
                     "background_color": team_lead_user.color ,
                    "initial":team_lead_user.first_letter }

            # Include team lead data in team_members_data list
            team_members_data = [{
                'email': team_lead_email,
                'picture_url': team_lead_picture_url
            }]

            team_members = Project_TeamMember.objects.filter(project=projectid)
            print(team_members)

            for team_member in team_members:
                try:
                    team_member_user = UserAccount.objects.get(email=team_member.team_member_email)
                    try:
                        team_member_social_auth = UserSocialAuth.objects.get(provider='google-oauth2', uid=team_member.team_member_email)
                        team_member_picture_url = team_member_social_auth.extra_data.get('picture', None)
                    except ObjectDoesNotExist:
                        team_member_picture_url = None

                    if not team_member_picture_url:
                        team_member_picture_url = team_lead_picture_url = {
                     "background_color": team_member_user.color ,
                    "initial":team_member_user.first_letter }


                    team_members_data.append({
                        'email': team_member.team_member_email,
                        'picture_url': team_member_picture_url
                    })
                except ObjectDoesNotExist:
                    team_members_data.append({
                        'email': team_member.team_member_email,
                        'picture_url': generate_placeholder_picture(team_member.team_member_email)
                    })
            print(team_members_data)

            return JsonResponse({
                'team_lead_email': team_lead_email,
                'team_lead_picture_url': team_lead_picture_url,
                'team_members': team_members_data
            })
        except Exception as e:
            print(e)
            return JsonResponse({'error': 'An error occurred'}, status=500)
        
@csrf_exempt
def get_user_details(request):
    if request.method == 'GET':
        email = request.GET.get('email')
        if email:
            try:
                user = UserAccount.objects.get(email=email)
                data = {
                    'email': user.email,
                    'is_admin': user.is_admin
                    # Add other user details you need
                }
                
                return JsonResponse(data)
            except UserAccount.DoesNotExist:
                return JsonResponse({'error': 'User not found'}, status=404)
        else:
            return JsonResponse({'error': 'Email parameter is missing'}, status=400)
    else:
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    

@csrf_exempt
def get_user_profile(request):
    print("getting the request hellloooooooooooooooo")
    if request.method == 'GET':
        
        email = request.GET.get('email')
        user = UserAccount.objects.get(email = email)
        data = {
            'first_name': user.first_name,
            'last_name': user.last_name,
            'email': user.email,
            'usn': user.usn,
            'phone_number': user.phone_number,
            'first_letter' : user.first_letter,
            'color': user.color,
        }
        print(data)
    return JsonResponse(data)


@csrf_exempt
def get_assignee(request):
    if request.method == 'GET':
        project_id = request.GET.get('projectid')
        pid1 = Project.objects.get(projectid=project_id)
       
        print("inside memeber",project_id)
        if project_id:
            try:
                print("goooooooooooooooooooooaad")
                # Fetch all team members for the specified project from the database
                team_members_emails = Project_TeamMember.objects.filter(project=project_id).values_list('team_member_email', flat=True)
                print("members:",team_members_emails)
               
                # Fetch user details for team members
                team_members = UserAccount.objects.filter(email__in=team_members_emails).values('email', 'first_name', 'last_name')
                print("this is inside the functionnnn")
                # Convert queryset to list of dictionaries
                team_members_list = list(team_members)
                print("doneeeeeeeeeeee")
                print(team_members_list)

                return JsonResponse({'team_members': team_members_list})
            except Exception as e:
                return JsonResponse({'error': f'An error occurred: {str(e)}'}, status=500)
        else:
            return JsonResponse({'error': 'Project ID is required'}, status=400)
    else:
        return JsonResponse({'error': 'Method not allowed'}, status=405)


@csrf_exempt
def fetch_assignee_color(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        assignee_email = data.get('assignee')
        print(assignee_email)
        print("inside the fetch______")
        try:
         
            user = UserAccount.objects.get(email=assignee_email)
            print(user)
            user_data = {
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'usn': user.usn,
                'phone_number': user.phone_number,
                'profile_photo': user.profile_photo.url if user.profile_photo else None,
                'first_letter': user.first_letter,
                'color': user.color
            }
            print(user_data)
            return JsonResponse({'user': user_data}, status=200)
        except UserAccount.DoesNotExist:
            return JsonResponse({'error': 'User not found'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    else:
        return JsonResponse({'error': 'Only POST requests are allowed'}, status=405)

   




