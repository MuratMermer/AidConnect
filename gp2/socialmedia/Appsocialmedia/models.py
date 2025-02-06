from django.db import models
from django.contrib.auth.models import User
# Create your models here.
class Profil(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    image=models.ImageField(upload_to="Profil-image")
    bio=models.TextField()
    def __str__(self):
        return self.user.username
    def post_count(self):
        return Post.objects.filter(profil=self).count()  

class Post(models.Model):
    profil=models.ForeignKey(Profil,on_delete=models.CASCADE, null=True)
    image=models.ImageField(upload_to="Post-image")
    description=models.TextField()
    likes=models.ManyToManyField(Profil, related_name="Begenenler", blank=True)
    post_save=models.ManyToManyField(Profil,related_name="kaydedenler", blank =True)
    comment_count=models.IntegerField(default=0)
    date=models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.profil.user.username
class Message(models.Model):
    sender = models.ForeignKey(Profil, related_name='sent_messages', on_delete=models.CASCADE)
    receiver = models.ForeignKey(Profil, related_name='received_messages', on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.content
 
class comment(models.Model):
    profil=models.ForeignKey(Profil,on_delete=models.CASCADE , null=True)
    post=models.ForeignKey(Post, on_delete=models.CASCADE)
    comment_text=models.TextField()
    date=models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.profil.user.username


class Takip(models.Model):
    profil=models.ForeignKey(Profil,related_name="TakipProfil", on_delete=models.CASCADE)
    takip_edilen=models.ForeignKey(Profil,related_name="Takip_edilen", on_delete=models.CASCADE)

    def __str__(self):
        return self.user.username
class Takipci(models.Model):
    profil=models.ForeignKey(Profil,related_name="TakipciProfil", on_delete=models.CASCADE)
    takip_eden=models.ForeignKey(Profil,related_name="takipeden", on_delete=models.CASCADE)
    def __str__(self):
        return self.user.username