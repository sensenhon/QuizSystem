from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from account.models import Profile
from .models import Quiz, Category
from django.db.models import Q
from quiztest.models import QuizSubmission
from django.contrib import messages

# Create your views here.
@login_required
def all_quiz_view(request):
    
    quizzes = Quiz.objects.order_by('-created_at')
    categories = Category.objects.all()
    
    context = {"quizzes": quizzes, "categories": categories}
    return render(request, 'all-quiz.html', context)

@login_required
def search_view(request, category):

    if request.GET.get('q') != None: #Search by search bar
        q = request.GET.get('q')
        query = Q(title__icontains=q) | Q(description__icontains=q)
        quizzes = Quiz.objects.filter(query)
        
    elif category != " ": #Search by category
        quizzes = Quiz.objects.filter(category__name=category).order_by('-created_at')

    else:
        quizzes = Quiz.objects.order_by('-created_at')

    categories = Category.objects.all()

    context = {"quizzes": quizzes, "categories": categories}
    return render(request, 'all-quiz.html', context)

@login_required
def quiz_view(request, quiz_id):
    
    # quiz = Quiz.objects.filter(id=quiz_id).first()
    quiz = get_object_or_404(Quiz, pk=quiz_id)
    
    # total_questions = quiz.question_set.all().count()
    
    if request.method == "POST":
        # get the score
        score = int(request.POST.get('score', 0))
        
        # check if the user has already submitted the quiz
        # if QuizSubmission.objects.filter(user=request.user, quiz=quiz).exists():
        #     messages.success(request, f"This time you got {score} out of {total_questions}")
        #     return redirect('quiz', quiz_id)
        
        #save the new quiz submission
        submission = QuizSubmission(user=request.user, quiz=quiz, score=score)
        submission.save()
        
        # show the result in message
        # messages.success(request, f"Quiz submitted successfully. You got {score} out of {total_questions}")
        # return redirect('quiz', quiz_id)
        
        return redirect("quiz_result", submission_id=submission.id)
            
    # if quiz != None:
    #     context = {"quiz": quiz}
    # else:
    #     return redirect('all_quiz')
    
    # return render(request, 'quiz.html', context)
    return render(request, 'quiz.html', {'quiz': quiz})

@login_required
def quiz_result_view(request, submission_id):
    
    submission = get_object_or_404(QuizSubmission, pk=submission_id)
    context = {'submission': submission}
    return render(request, 'quiz-result.html', context)