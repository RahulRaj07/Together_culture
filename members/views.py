from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from .models import Interest, Member
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from .forms import MembershipApplicationForm
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Q
from django.http import JsonResponse
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.urls import reverse


def homepage(request):
    return render(request, 'login.html')

def login_user(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)

            print("[DEBUG] Logged in:", user.username)
            print("[DEBUG] is_admin =", getattr(user, 'is_admin', 'Not Found'))

            if hasattr(user, 'is_admin') and user.is_admin:
                print("[DEBUG] Redirecting to admin_home")
                return redirect('admin_home')
            elif user.is_approved:
                return redirect('user_dashboard')
            else:
                messages.error(request, 'Your account is not yet approved.')
                return redirect('login')
        else:
            messages.error(request, 'Invalid login credentials.')
            print("[DEBUG] Invalid credentials")
    else:
        form = AuthenticationForm()

    return render(request, 'login.html', {'form': form})



def apply_for_membership(request):
    if request.method == 'POST':
        form = MembershipApplicationForm(request.POST)
        if form.is_valid():
            member = form.save(commit=False)
            member.username = member.email  # Use email as username
            member.set_unusable_password()  # No password until approved
            member.save()
            form.save_m2m()  # Save many-to-many (interests)
            messages.success(request, "Application submitted! Await admin approval.")
            return redirect('home')
    else:
        form = MembershipApplicationForm()
    return render(request, 'apply.html', {'form': form})


from django.shortcuts import render, redirect

def apply_for_membership(request):
    if request.method == 'POST':
        form = MembershipApplicationForm(request.POST)
        if form.is_valid():
            member = form.save(commit=False)
            member.username = member.email
            member.set_unusable_password()
            member.save()
            form.save_m2m()
            return redirect('application_success')
    else:
        form = MembershipApplicationForm()
    return render(request, 'apply.html', {'form': form})

def application_success(request):
    return render(request, 'application_success.html')

def is_admin(user):
    return user.is_authenticated and user.is_admin

@login_required
@user_passes_test(is_admin)
def admin_home(request):
    query = request.GET.get("q")
    status = request.GET.get("status")

    members = Member.objects.all()

    if query:
        members = members.filter(
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(email__icontains=query)
        )

    if status == 'approved':
        members = members.filter(is_approved=True)
    elif status == 'pending':
        members = members.filter(is_approved=False)

    return render(request, "admin_home.html", {
        "members": members,
        "query": query,
        "status": status,
    })


@login_required
@user_passes_test(is_admin)
def approve_member(request, member_id):
    member = Member.objects.get(id=member_id)
    member.is_approved = not member.is_approved
    member.save()

    if member.is_approved:
        uid = urlsafe_base64_encode(force_bytes(member.pk))
        token = default_token_generator.make_token(member)
        reset_link = request.build_absolute_uri(
            reverse('password_reset_confirm', kwargs={'uidb64': uid, 'token': token})
        )
        send_mail(
            subject="Set up your password – Together Culture",
            message=(
                f"Hello {member.first_name or ''},\n\n"
                f"Your membership has been approved!\n\n"
                f"Please click the link below to set your password and log in:\n\n{reset_link}\n\n"
                f"If you did not apply, you can ignore this message.\n\n"
                f"- Together Culture Team"
            ),
            from_email=None,
            recipient_list=[member.email],
            fail_silently=False
        )

    return redirect('admin_home')


@login_required
@user_passes_test(is_admin)
def member_details(request, member_id):
    try:
        member = Member.objects.get(id=member_id)
        data = {
            "name": f"{member.first_name} {member.last_name}",
            "email": member.email,
            "phone": member.phone_number,
            "location": member.location,
            "interests": [i.name for i in member.interests.all()],
            "background": member.professional_background,
            "why_join": member.why_join,
            "how_contribute": member.how_contribute,
            "approved": member.is_approved,
        }
        return JsonResponse(data)
    except Member.DoesNotExist:
        return JsonResponse({"error": "Member not found"}, status=404)


@login_required
def user_dashboard(request):
    if not request.user.is_admin:
        return render(request, "user_dashboard.html")
    return redirect('admin_home')
