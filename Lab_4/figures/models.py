# figures/models.py
from django.contrib.auth.models import User
from django.db import models



class Part(models.Model):
    title = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.title


class Figure(models.Model):
    name = models.CharField(max_length=100)
    img_url = models.URLField(blank=True)         # зображення
    hover_img_url = models.URLField(blank=True)   # при наведенні
    part = models.ForeignKey(Part, on_delete=models.CASCADE, related_name="figures")

    def __str__(self):
        return self.name



class UserFigure(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_figures")
    figure = models.ForeignKey(Figure, on_delete=models.CASCADE, related_name="user_figures")
    owned = models.BooleanField(default=False)

    class Meta:
        unique_together = ('user', 'figure')

    def __str__(self):
        return f"{self.user.username} - {self.figure.name} ({'має' if self.owned else 'немає'})"


class Feedback(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)