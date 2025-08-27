from django.db import models

# Create your models here.
class Task(models.Model):
    title = models.CharField(max_length=250)
    due_date = models.DateField()
    description = models.TextField(null=True,blank=True)
    document = models.FileField(upload_to='documents/', null=True, blank=True)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
