from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse

# anon user as default (for when a user is deleted or a definition is created without an account)
# id 4 because account was the fourth one that was created
ANON_USER_ID = 4

# word NICHT_ZUGEORDNET with ID 1 is used as a default word (for deletion behavior)
DEFAULT_WORD_ID = 1


# words are internally represented via lowercase letters
class Word(models.Model):
    word = models.CharField(max_length=40)

    # what the word is displayed as on the website frontend
    display_title = models.CharField(max_length=40)

    def __str__(self):
        return self.word

    # returns model url
    # todo make it work
    def get_absolute_url(self):
        # return reverse('definition-detail', kwargs={'pk': self.pk})
        pass

    # when a word is created (through a definition) for the first time, the display title becomes the definition
    # title in lowercase
    # this definition title can later be changed in the admin page (for example if the word is a noun)
    def save(self, *args, **kwargs):
        if not self.display_title:
            self.display_title = self.word

        super(Word, self).save(*args, **kwargs)
        
        
class IpAddress(models.Model):
    #TODO: maybe another type of field is more suitable?
    ip = models.CharField(primary_key=True, max_length=40)
     
    def __str__(self):
         return self.ip
         

class Definition(models.Model):
    title = models.CharField(max_length=40)
    content = models.TextField()
    example = models.TextField()

    # auto_now_add sets date when definition was created as its date
    date_posted = models.DateTimeField(auto_now_add=True)

    # if an account is deleted the author of its definitions is set to the anon user
    author = models.ForeignKey(User, on_delete=models.SET_DEFAULT, default=ANON_USER_ID)

    # definitions have a foreign key (many to one relation) for words
    word = models.ForeignKey(Word, on_delete=models.SET_DEFAULT, default=DEFAULT_WORD_ID)

    #users that have liked the posts    
    likers = models.ManyToManyField(User, related_name="likers")
    dislikers =models.ManyToManyField(User, related_name="dislikers")

    #ip addresses of anonymous likers/dislikers
    anonlikers = models.ManyToManyField(IpAddress,related_name="anonlikers")
    anondislikers = models.ManyToManyField(IpAddress,related_name="anondislikers")
    
    likes= models.IntegerField(default=0)
    dislikes= models.IntegerField(default=0)

    # internal flag: definition was written by AI (not shown on the website)
    ai_generated = models.BooleanField(default=False)
    
    # anonyme Definitionen zeigen keinen Autor an
    @property
    def is_anonym(self):
        return self.author_id == ANON_USER_ID

    def __str__(self):
        return self.title

    # returns model url
    def get_absolute_url(self):
        return reverse('definition-detail', kwargs={'pk': self.pk})
