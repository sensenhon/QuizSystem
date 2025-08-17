from django.db import models
import pandas as pd
from django.contrib.auth.models import User
from django.db.models import Sum
from django.db.models.signals import post_save
from django.dispatch import receiver

# Create your models here.
class Category(models.Model):
    name = models.CharField(max_length=15)
    
    class Meta:
        verbose_name_plural = "Categories"
    
    def __str__(self): #To return the name instead of "Category object (x)" on Admin page
        return self.name

class Quiz(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    quiz_file = models.FileField(upload_to='quiz/')    
    duration_minutes = models.PositiveIntegerField(default=10)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = "Quizzes"
    
    def __str__(self):
        return self.title
    
    # Call the function on quiz save
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.quiz_file:
            self.import_quiz_from_excel()
    
    # Extract excel file        
    def import_quiz_from_excel(self):
        # read excel file
        df = pd.read_excel(self.quiz_file.path)
        # iterate over the each row
        for index, row in df.iterrows():
            # extract question text, choices and correct answer from the row
            question_text = row['Question']
            choice1 = row['A']
            choice2 = row['B']
            choice3 = row['C']
            choice4 = row['D']
            correct_answer = row['Answer']
            is_multiple = False
            if 'is_multiple' in row and (row['is_multiple'] == True or str(row['is_multiple']).lower() in ['1', 'true', 'yes']):
                is_multiple = True
            elif len(correct_answer) > 1:
                is_multiple = True
            
            # create the question object
            # question = Question.objects.get_or_create(quiz=self, text=question_text)

            # create questions object with multiple choice
            question, _ = Question.objects.get_or_create(
                quiz=self, text=question_text,
                defaults={'is_multiple': is_multiple}
            )
            question.is_multiple = is_multiple
            question.save()

            # create choices object
            # choice_1 = Choice.objects.get_or_create(question=question[0], text=choice1, is_correct=correct_answer == 'A')
            # choice_2 = Choice.objects.get_or_create(question=question[0], text=choice2, is_correct=correct_answer == 'B')
            # choice_3 = Choice.objects.get_or_create(question=question[0], text=choice3, is_correct=correct_answer == 'C')
            # choice_4 = Choice.objects.get_or_create(question=question[0], text=choice4, is_correct=correct_answer == 'D')
            
            # create choices object with multiple correct answers
            choice_1 = Choice.objects.get_or_create(question=question, text=choice1, is_correct='A' in correct_answer)
            choice_2 = Choice.objects.get_or_create(question=question, text=choice2, is_correct='B' in correct_answer)
            choice_3 = Choice.objects.get_or_create(question=question, text=choice3, is_correct='C' in correct_answer)
            choice_4 = Choice.objects.get_or_create(question=question, text=choice4, is_correct='D' in correct_answer)

class Question(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    text = models.TextField()
    # Is this question multiple choice?
    is_multiple = models.BooleanField(default=False)
    
    def __str__(self):
        return self.text[:50]
    
class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    text = models.CharField(max_length=255)
    is_correct = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.question.text[:50]}, {self.text[:20]}"
    
class QuizSubmission(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    score = models.IntegerField()
    submitted_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user}, {self.quiz.title}"
    
class UserRank(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    rank = models.IntegerField(null=True, blank=True)
    total_score = models.IntegerField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.rank}, {self.user.username}"
    
@receiver(post_save, sender=QuizSubmission)
def update_leaderboard(sender, instance, created, **kwargs):
    if created:
        update_leaderboard()

def update_leaderboard():
    # Count the sum of scores for all users
    user_scores = QuizSubmission.objects.values('user').annotate(total_score=Sum('score')).order_by('-total_score')
    
    # Update rank based on the sorted list
    rank = 1
    for entry in user_scores:
        user_id = entry['user']
        total_score = entry['total_score']
        
        user_rank, created = UserRank.objects.get_or_create(user_id=user_id)
        user_rank.rank = rank
        user_rank.total_score = total_score
        user_rank.save()
        
        rank += 1