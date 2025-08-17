from django.shortcuts import render, HttpResponse, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from account.models import Profile
from quiztest.models import UserRank, Quiz, QuizSubmission, Question
from .models import Message, Blog
import datetime
import math
from django.db.models.functions import ExtractYear
from django.db.models import Count, Q

# Create your views here.
def home(request):
    
    leaderboard_users = UserRank.objects.order_by('rank')
    
    context = {"leaderboard_users": leaderboard_users}
        
    return render(request, 'welcome.html', context)

@login_required
def leaderboard_view(request):
    
    leaderboard_users = UserRank.objects.order_by('rank')
    
    context = {'leaderboard_users': leaderboard_users}
    return render(request, "leaderboard.html", context)

def is_superuser(user):
    return user.is_superuser

@user_passes_test(is_superuser)
@login_required
def dashboard_view(request):
    
    #total_numbers
    total_users = User.objects.all().count()
    total_quizzes = Quiz.objects.all().count()
    total_quiz_submit = QuizSubmission.objects.all().count()
    total_questions = Question.objects.all().count()
    
    #today_numers
    today_users = User.objects.filter(date_joined__date=datetime.date.today()).count()
    today_quizzes = Quiz.objects.filter(created_at__date=datetime.date.today()).count()
    today_quizzes_objs = Quiz.objects.filter(created_at__date=datetime.date.today())
    today_quiz_submit = QuizSubmission.objects.filter(submitted_at__date=datetime.date.today()).count()
    today_questions = 0
    for quiz in today_quizzes_objs:
        today_questions += quiz.question_set.count()
    
    #gain_numbers
    gain_users = gain_percentage(today_users, total_users)
    gain_quizzes = gain_percentage(today_quizzes, total_quizzes)
    gain_quiz_submit = gain_percentage(today_quiz_submit, total_quiz_submit)
    gain_questions = gain_percentage(today_questions, total_questions)
    
    #inbox messages
    messages = Message.objects.filter(created_at__date=datetime.date.today()).order_by('-created_at')
        
    context = {
        "total_users": total_users,
        "total_quizzes": total_quizzes,
        "total_quiz_submit": total_quiz_submit,
        "total_questions": total_questions,
        "today_users": today_users,
        "today_quizzes": today_quizzes,
        "today_quiz_submit": today_quiz_submit,
        "today_questions": today_questions,
        "gain_users": gain_users,
        "gain_quizzes": gain_quizzes,
        "gain_quiz_submit": gain_quiz_submit,
        "gain_questions": gain_questions,
        "messages": messages,
    }
    return render(request, "dashboard.html", context)

def gain_percentage(today, total):
    if total > 0 and today > 0:
        gain = math.floor((today * 100)/total)
        return gain
    
def about_view(request):
    return render(request, "about.html")

def blogs_view(request):
    
    year_blog_count = Blog.objects.annotate(year=ExtractYear('created_at')).values('year').annotate(count=Count('id')).order_by('-year').filter(status='public')
    blogs = Blog.objects.filter(status='public').order_by('-created_at')
    
    context = {'year_blog_count': year_blog_count, 'blogs': blogs}
    return render(request, "blogs.html", context)

@login_required
def blog_view(request, blog_id):
        
    # blog = Blog.objects.filter(id=blog_id).first()
    blog = get_object_or_404(Blog, pk=blog_id)
    
    context = {'blog': blog}

    return render(request, "blog.html", context)

@login_required
def contact_view(request):
    
    if request.method == "POST":
        subject = request.POST.get('subject')
        message = request.POST.get('message')
        
        if subject is not None and message is not None:
            form = Message.objects.create(user=request.user, subject=subject, message=message)
            form.save()
            messages.success(request, "We got your message. We will resolve your query soon.")
            return redirect('profile', request.user.username)
        else:
            return redirect('contact')

    return render(request, "contact.html")

@user_passes_test(is_superuser)
@login_required
def message_view(request, id):
    
    # message = Message.objects.filter(id=int(id)).first()
    message = get_object_or_404(Message, id=id)
    
    if not message.is_read:
        message.is_read = True
        message.save()
    
    context = {"message": message}
    return render(request, "message.html", context)
    
def terms_view(request):
    return render(request, "terms.html")

@login_required
def downloads_view(request):
    return render(request, "downloads.html")

def search_users_view(request):
    
    query = request.GET.get('q')
    
    if query:
        users = User.objects.filter(
            Q(username__icontains=query) | Q(first_name__icontains=query) | Q(last_name__icontains=query)
        ).order_by('date_joined')
    else:
        users = []
    
    context = {"query": query, "users": users}

    return render(request, 'search-users.html', context)

def custom_404_view(request, exception):
    return render(request, '404.html', status=404)