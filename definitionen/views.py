from django.shortcuts import render, get_object_or_404
from .models import Definition, Word, User, IpAddress
from django.views.generic import ListView, DetailView, CreateView
from django.db.models.functions import Lower
from django.urls import reverse
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import permission_required
from django.conf import settings

LETTERS = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T',
           'U', 'V', 'W', 'X', 'Y', 'Z']


#https://en.wikipedia.org/wiki/Levenshtein_distance
#dynamic implementation
def word_distance(s1, s2):
    if len(s1) < len(s2):
        return word_distance(s2, s1)

    if len(s2) == 0:
        return len(s1)

    previous_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row
    
    return previous_row[-1]

# View, die alle W�rter auf der Homepage anzeigt. Aktuell duplikate, wenn sich nur Cases der W�rter unterscheiden
def home(request):

    context = {}

    query = None

    if request.GET:
        query = request.GET["q"]
        context["query"] = str(query)
        
        
    context["results"], context["similars"]= search(query)
    context["buchstaben"] = LETTERS

    return render(request, template_name='definitionen/home.html', context=context)


def search(query):

    if not query or len(query) < 1 or query == " ":
        return None,None

    query = query.strip()

    queryset = []
    terms = query.split(" ")

    for term in terms:
        posts = Word.objects.filter(
            Q(word__icontains=term)
        ).distinct().exclude(word="NICHT_ZUGEORDNET")
        
        for post in posts:
            queryset.append(post)
    
    rest=list(set(Word.objects.distinct().exclude(word="NICHT_ZUGEORDNET"))-set(queryset))     
    similars=sorted(rest,key=lambda w: word_distance(str(w).lower(),query.lower()))
        
    return queryset,similars[:5]


# listing all words
def all_words(request):

    context = {'words': Word.objects.order_by('word').exclude(word="NICHT_ZUGEORDNET")}
    return render(request, template_name='definitionen/all_words.html', context=context)


# shows all words starting with given letter (route)
def letter_view(request, route):

    # if route is "Sonderzeichen", words starting with non-alphabetical characters are fetched
    if route == 'Sonderzeichen':
        words = Word.objects.filter(word__regex=r'^[^a-zA-Z].*').order_by('word').exclude(word="NICHT_ZUGEORDNET")

    # if route is a letter, all words starting with that letter are fetched
    else:
        words = Word.objects.filter(word__startswith=route).order_by('word').exclude(word="NICHT_ZUGEORDNET")

    context = {
        'words': words,
        'route': route,
        'legal_characters': LETTERS + ["Sonderzeichen"]
    }

    # render returns httpresponse (or exception)
    return render(request, template_name='definitionen/letter_words.html', context=context)


# listing all definitions for one word
def WordView(request, word):
    # all definitions corresponding to a word are being fetched

    # to prevent invalid words being entered in the URL
    try:
        word_definitions = Word.objects.get(word=word).definition_set.all().order_by("-likes")
    except:
        word_definitions = None

    word_object = Word.objects.get(word=word)
    print(word_object.display_title)

    return render(request, "definitionen/word.html", {"word": word_object, "definitions": word_definitions})


class DefinitionDetailView(DetailView):

    model = Definition


# Erstellen von Definitionen. Nutzer muss eingeloggt sein
class DefinitionCreateView(CreateView):

    model = Definition
    fields = ['title', 'content', 'example']
    template_name = 'definitionen/definition_form.html'

    # Feldnamen und kleinere Textfelder im Formular
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields['title'].label = 'Wort'
        form.fields['content'].label = 'Definition'
        form.fields['example'].label = 'Beispiel'
        form.fields['content'].widget.attrs['rows'] = 3
        form.fields['example'].widget.attrs['rows'] = 2
        return form

    # Hilfsattribut, das in der form_valid()-Methode gesetzt wird, damit es f�r die Success-Url gelesen werden kann
    # todo besser l�sen
    definition_title = None

    def add_definition_to_word(self, form):

        # getting word
        word_string = form.cleaned_data.get('title')
        word_string = word_string.lower()

        # counting how many words have the definition title as word attribute (should be either 0 or 1)
        num_words_equal_to_definition_title = Word.objects.filter(word=word_string).count()

        # if no words with definition title are found, create new word
        if num_words_equal_to_definition_title == 0:

            self.create_new_word(form, word_string)

        # if one word with definition title was found, assign this definition to word
        elif num_words_equal_to_definition_title == 1:

            self.add_to_existing_word(form, word_string)

        # should never happen
        else:
            raise ValueError("Es sollte nicht mehrere Worte mit dem gleichen Attribut 'word' geben.")

    def create_new_word(self, form, word_string):
        new_word = Word(word=word_string)
        new_word.save()
        form.instance.word = new_word

    def add_to_existing_word(self, form, word_string):
        existing_word = Word.objects.get(word=word_string)
        form.instance.word = existing_word

    #
    def form_valid(self, form):

        # if user is logged in, author field gets value of current user, otherwise field has value "anonym"
        if self.request.user.is_authenticated:
            form.instance.author = self.request.user

        self.add_definition_to_word(form)

        # setting support attribute
        self.definition_title = form.cleaned_data.get('title')

        return super().form_valid(form)

    # redirects to word view after successfully creating definition
    def get_success_url(self):
        return reverse('one-word', args=[str(self.definition_title.lower())])


# about-page, currently empty
def about(request):

    return render(request, template_name='definitionen/about.html', context={"title": "about"})


def legal_context(title):
    adresse = [z.strip() for z in settings.IMPRESSUM_ADRESSE.split('|') if z.strip()]
    return {
        "title": title,
        "impressum_name": settings.IMPRESSUM_NAME,
        "impressum_adresse": adresse,
        "impressum_email": settings.IMPRESSUM_EMAIL,
    }


def impressum(request):
    return render(request, 'definitionen/impressum.html', legal_context("Impressum"))


def datenschutz(request):
    return render(request, 'definitionen/datenschutz.html', legal_context("Datenschutz"))


#@permission_required(AllowAny)
def like_definition(request, pk):

    # copied from tutorial
    definition = get_object_or_404(Definition, id=request.POST.get('definition_id'))

    # voting is done via django-vote module (not anymore!)
    #definition.votes.up(request.user.id)
    if request.user.is_authenticated:
        #check if already disliked
        result = definition.dislikers.filter(id=request.user.id)
    
        if result:
            definition.dislikes-=1
            definition.dislikers.remove(result[0])
        
        result = definition.likers.filter(id = request.user.id)
    
        #check if already liked, else add user to database
        if result:
            definition.likes-=1
            definition.likers.remove(result[0])
        else:
            definition.likes+=1
            definition.likers.add(request.user)
            
    else:    
        ip = get_client_ip(request)
    
        #check if already disliked
        result = definition.anondislikers.filter(ip=ip)
    
        if result:
            definition.dislikes-=1
            definition.anondislikers.remove(result[0])
        
        result = definition.anonlikers.filter(ip=ip)
    
        #check if already liked, else add address to database
        if result:
            definition.likes-=1
            definition.anonlikers.remove(result[0])
        else:
            definition.likes+=1
            addr=IpAddress(ip=ip)
            addr.save()
            definition.anonlikers.add(addr)
        
    definition.save()
    
    # getting word corresponding to definition to redirect user after liking
    word = definition.word.word
    return HttpResponseRedirect(reverse('one-word', args=[word]))

#@permission_required(AllowAny)
def dislike_definition(request, pk):

    # copied from tutorial
    definition = get_object_or_404(Definition, id=request.POST.get('definition_id'))
        
    if request.user.is_authenticated:
        result = definition.likers.filter(id=request.user.id)

        if result:
            definition.likes-=1
            definition.likers.remove(result[0])

        result = definition.dislikers.filter(id = request.user.id)

        if result:
            definition.dislikes-=1
            definition.dislikers.remove(result[0])
        else:
            definition.dislikes+=1
            definition.dislikers.add(request.user)
            
    else:

        ip = get_client_ip(request)

        #check if already liked
        result = definition.anonlikers.filter(ip=ip)
        
        if result:
            definition.likes-=1
            definition.anonlikers.remove(result[0])
 
        result = definition.anondislikers.filter(ip=ip)
   
        #check if already disliked, else add address to database
        if result:
            definition.dislikes-=1
            definition.anondislikers.remove(result[0])
        else:
            definition.dislikes+=1
            addr = IpAddress(ip=ip)
            addr.save()
            definition.anondislikers.add(addr)
       
    definition.save()

    # voting is done via django-vote module(not anymore!)
    #definition.votes.down(request.user.id)

    # getting word corresponding to definition to redirect user after disliking
    word = definition.word.word
    return HttpResponseRedirect(reverse('one-word', args=[word]))

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

# currently in use
class WordListView(ListView):

    model = Word

    # changes template that ListView looks for
    template_name = 'definitionen/all_words.html'

    queryset=model.objects.order_by('word').exclude(word="NICHT_ZUGEORDNET")
    # changes name for objects that template loops over (connected to Definition model how?)
    context_object_name = 'words'
    # change ordering of posts
    ordering = ['word']
    paginate_by = 20

    # "Springe zu": für jeden Buchstaben die Seite, auf der seine Wörter beginnen
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        first_page = {}
        for i, w in enumerate(self.get_queryset().values_list('word', flat=True)):
            letter = w[:1].upper()
            if letter not in first_page:
                first_page[letter] = i // self.paginate_by + 1
        context['sprungmarken'] = [(l, first_page.get(l)) for l in LETTERS]
        # gängige Seitennavigation: ‹ 1 … 4 5 [6] 7 8 … 20 ›
        page = context.get('page_obj')
        if page:
            context['page_range'] = page.paginator.get_elided_page_range(page.number, on_each_side=2, on_ends=1)
        return context
