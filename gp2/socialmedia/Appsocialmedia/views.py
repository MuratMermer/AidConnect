from django.shortcuts import render ,redirect
from django.contrib.auth import login,logout,authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from . models import *
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.shortcuts import render, redirect
from .models import Profil, Message
from django.db.models import Q
# Create your views here.
@login_required(login_url='/login/')
@csrf_exempt

def index(request):
    posts = Post.objects.all().order_by("-date")  # Tüm postları alıyoruz ve tarihe göre sıralıyoruz
    girisli_profil = Profil.objects.filter(user=request.user).first()  # Kullanıcının profilini alıyoruz
    comments = comment.objects.all()  # Tüm yorumları alıyoruz

    if request.method == "POST":
        post_id = request.POST.get("post_id")  # post_id'yi alıyoruz
        button = request.POST.get("button")  # Butonun ismini alıyoruz (like ya da comment)
        print(post_id)
        print(button)

        # Post oluşturma işlemi
        if request.POST.get("postbtn") == "btnpost":
            image = request.FILES.get("image")  # Post resmini alıyoruz
            description = request.POST.get("description")  # Açıklamayı alıyoruz
            new_post = Post.objects.create(profil=girisli_profil, image=image, description=description)
            return redirect("index")  # Yeni post oluşturduktan sonra tekrar index'e yönlendiriyoruz
        
        # Post beğenme işlemi
        elif button == "btnlike":
            try:
                post = Post.objects.get(id=post_id)  # Post'u alıyoruz
                if post.likes.filter(id=girisli_profil.id).exists():  # Kullanıcı zaten beğendi mi kontrolü
                    post.likes.remove(girisli_profil)  # Beğeniyi kaldırıyoruz
                    liked_request_user = False
                else:
                    post.likes.add(girisli_profil)  # Beğeni ekliyoruz
                    liked_request_user = True

                return JsonResponse({
                    "like_count": post.likes.count(),  # Beğeni sayısını geri döndürüyoruz
                    "liked_request_user": liked_request_user  # Kullanıcının beğenip beğenmediğini belirtiyoruz
                })

            except Post.DoesNotExist:
                return JsonResponse({"error": "Post not found"}, status=404)

        # Yorum ekleme işlemi
        elif button == "btncomment":
            comment_text = request.POST.get("comment")  # Yorum metnini alıyoruz
            try:
                post = Post.objects.get(id=post_id)  # Yorum yapılacak post'u alıyoruz

                # Yorum ekliyoruz
                new_comment = comment.objects.create(profil=girisli_profil, post=post, comment_text=comment_text)
                new_comment.save()

                return JsonResponse({
                    "comment_count": post.comment_set.count(),  # Posta ait yorum sayısını döndürüyoruz
                    "comment_id": new_comment.id,
                    "profil_foto": new_comment.profil.image.url,
                    "comment": new_comment.comment_text,
                    "profil": new_comment.profil.user.username
                })

            except Post.DoesNotExist:
                return JsonResponse({"error": "Post not found"}, status=404)

    # Context ile verileri template'e gönderiyoruz
    context = {
        "posts": posts,  # Tüm postları gönderiyoruz
        "girisli_profil": girisli_profil,  # Kullanıcının profilini gönderiyoruz
        "comments": comments  # Tüm yorumları gönderiyoruz
    }

    return render(request, "index.html", context)  # Template'i render ediyoruz


     
@login_required(login_url='/login/')       
def profil(request, username):
    profil = Profil.objects.get(user__username=username) 
    girisli_profil = Profil.objects.get(user=request.user)
    girisli_profil_takip = Takip.objects.filter(profil=girisli_profil)
    profil_takipler = Takip.objects.filter(profil=profil)
    profil_takipciler = Takip.objects.filter(profil=profil)
    profil_gonderi_sayisi = Post.objects.filter(profil=profil).count()

    # Sadece ziyaret edilen profilin postlarını getirmek için değiştirildi
    posts = Post.objects.filter(profil=profil)

    if request.method == "POST":
        if request.POST.get("profileditbtn") == "btnprofileedit":
            image = request.FILES.get("image")
            email = request.POST.get("email")
            first_name = request.POST.get("first_name")
            last_name = request.POST.get("last_name")
            password = request.POST.get("password")
            bio = request.POST.get("bio")

            if image is None:
                profil.image = profil.image

            if profil.user.check_password(password):
                profil.image = image
                profil.bio = bio
                profil.save()
                user = User.objects.get(username=profil.user.username)
                user.email = email
                user.username = username
                user.first_name = first_name
                user.last_name = last_name
                user.save()
                return redirect(f"/profil/{profil}")
            else:
                messages.warning(request, "Parola hatalıdır. Yeniden deneyiniz")
        else:
            if girisli_profil_takip:
                for takip in girisli_profil_takip:
                    if takip.takip_edilen == profil:
                        takip = Takip.objects.get(takip_edilen=username)
                        takip.delete()
                        takipci = Takipci.objects.get(takip_eden=girisli_profil)
                        takipci.delete()
                        return redirect(f"/profil/{profil}")
                    else:
                        takip = Takip.objects.create(profil=girisli_profil, takip_edilen=profil)
                        takip.save()
                        takipci = Takipci.objects.create(profil=profil, takip_eden=girisli_profil)
                        takipci.save()
                        return redirect(f"/profil/{profil}")
            else:
                takip = Takip.objects.create(profil=girisli_profil, takip_edilen=profil)
                takip.save()
                takipci = Takipci.objects.create(profil=profil, takip_eden=girisli_profil)
                takipci.save()
                return redirect(f"/profil/{profil}")

    return render(request, 'profil.html', {
        'profil': profil,
        'girisli_profil': girisli_profil,
        'girisli_profil_takip': girisli_profil_takip,
        'profil_takipler': profil_takipler,
        'profil_takipciler': profil_takipciler,
        'profil_gonderi_sayisi': profil_gonderi_sayisi,
        'posts': posts,
    })

    
@csrf_exempt
def Search(request):
    if "query" in request.GET and request.GET.get("query") != "":
        query = request.GET.get("query")
        profils = Profil.objects.filter(user__username__icontains = query)

    if request.method == "POST":
        query = request.POST.get("query")

        if not query:
            return JsonResponse({"profils":[]})

        profils = Profil.objects.filter(user__username__icontains = query)

        profiller = []
        for profil in profils:
            profiller.append({
                "profil":profil.user.username,
                
            })
        return JsonResponse({"profiller":profiller})

    context={
        "profils":profils
    }
    return render(request, "searchbtn.html",context)


def Login(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        # E-posta adresiyle kullanıcıyı bul
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            messages.warning(request, "Bu e-posta adresine sahip bir kullanıcı bulunamadı.")
            return redirect('login')  # Hatalı e-posta ile login sayfasına geri dön

        # Şifreyi doğrula
        if user.check_password(password):
            # Giriş işlemini gerçekleştir
            login(request, user)
            return redirect("index")  # Giriş başarılıysa anasayfaya yönlendir
        else:
            messages.warning(request, "Geçersiz şifre. Lütfen tekrar deneyin.")  # Şifre hatalı

    return render(request, "login.html")



def message_list(request, receiver_id):
    try:
        sender_profile = Profil.objects.get(user=request.user)
        receiver_profile = Profil.objects.get(id=receiver_id)
    except Profil.DoesNotExist:
        return redirect('error_page')  # Hata sayfasına yönlendirebiliriz.

    # Mesajları al, eski tarihten yeniye doğru sıralanmış
    messages = Message.objects.filter(
        (Q(sender=sender_profile) & Q(receiver=receiver_profile)) |
        (Q(sender=receiver_profile) & Q(receiver=sender_profile))
    ).order_by('created_at')

    # Arama yapılmışsa
    query = request.GET.get('q', '')
    if query:
        messages = messages.filter(content__icontains=query)

    if request.method == 'POST':
        content = request.POST.get('content')
        if content:
            # Yeni mesajı oluştur
            message = Message.objects.create(
                sender=sender_profile,
                receiver=receiver_profile,
                content=content
            )
            # Yeni mesajın sadece veritabanına kaydedildiğini ve sayfa yenilenmeden döndüğünü belirtiyoruz
            return JsonResponse({
                'content': message.content,
                'sender': message.sender.user.username,
                'created_at': message.created_at.strftime("%d-%m-%Y %H:%M")
            })

    return render(request, 'message.html', {'messages': messages, 'receiver': receiver_profile})


def Register(request):
    if request.method == "POST":
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        email = request.POST.get("email")
        username = request.POST.get("username")
        password = request.POST.get("password")

        if not User.objects.filter(username=username).exists():
            if not User.objects.filter(email=email).exists():
                user = User.objects.create_user(
                    first_name=first_name,
                    last_name=last_name,
                    username=username,
                    email=email,
                    password=password
                )
                user.save()
                login(request, user)
                return redirect(f"/profil/{user.username}")
            else:
                messages.warning(request, "Bu e-posta adresi başka biri tarafından kullanılıyor.")
        else:
            messages.warning(request, "Bu kullanıcı adı başka biri tarafından kullanılıyor.")
    
    return render(request, "register.html")

def Logout(request):
    logout(request)
    return redirect("login")
