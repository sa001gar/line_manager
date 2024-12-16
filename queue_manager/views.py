from django.shortcuts import render, redirect
from django.http import JsonResponse
from .models import Organization, Line
from django.contrib.auth.decorators import login_required

# View to render the homepage (search and view available lines)
def home(request):
    # Fetch all organizations
    organizations = Organization.objects.all()
    lines = Line.objects.all()

    context = {
        'organizations': organizations,
        'lines': lines
    }
    return render(request, 'queue_manager/landing/index.html', context)

# View to handle the organization type and line search
def search_lines(request):
    if request.method == "POST":
        # Get data from POST request
        org_type = request.POST.get('org_type')
        org_name = request.POST.get('org_name')

        # Filter organizations based on selected type and name
        organizations = Organization.objects.filter(type=org_type)
        lines = Line.objects.filter(organization__name=org_name)

        return render(request, 'followup/home.html', {
            'organizations': organizations,
            'lines': lines,
            'org_type': org_type,
            'org_name': org_name
        })

    return redirect('home')

# View for user registration for a queue
@login_required
def register_for_queue(request, line_id):
    try:
        line = Line.objects.get(id=line_id)
    except Line.DoesNotExist:
        return JsonResponse({'error': 'Line not found'}, status=404)

    user = request.user
    # Register user for the selected line (assuming you have a model for registrations)
    line.users.add(user)

    return redirect('home')  # Or redirect to user dashboard if needed

# A view to handle showing a user's current queue status (can be used in the dashboard)
@login_required
def user_dashboard(request):
    user = request.user
    # Assuming you have a relation between users and lines
    user_lines = Line.objects.filter(users=user)

    context = {
        'user_lines': user_lines
    }
    return render(request, 'followup/dashboard.html', context)

