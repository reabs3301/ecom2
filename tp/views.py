from django.http import HttpResponse
from django.shortcuts import render , redirect
from .models import SellProduct, Client, PanierItem, AuctionProduct
from .forms import  productform
from django.conf import settings
from django.urls import resolve

import stripe
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from io import BytesIO
from PIL import Image

# decorators 

authenticated_users = []

def authenticate(get_response):
    exception_urls = ['welcome', 'login', 'signup', 'login_page', 'signup_page',]
    def wrapper(request):
        print('authenticate middleware')
        print(authenticated_users)
        if resolve(request.path_info).url_name in exception_urls:
            return get_response(request)
        try:
            if request.session['username'] in authenticated_users:
                return get_response(request)
            else:
                return login_page(request, invalid_credentials=True) 
        except:
            return login_page(request, invalid_credentials=True) 
    return wrapper



# views

def welcome(request):
    image = r'/media/background.jpg'
    return render(request , 'welcome.html' , {'image' : image})

def disconnect_view(request):
    authenticated_users.remove(request.session['username'])
    return redirect('welcome')


def login_signup_page(request, args):
    return render(request, 'login.html', args)

def login_page(request, invalid_credentials=False):
    return login_signup_page(request, {'type': 'login', 'invalid_credentials': invalid_credentials})

def signup_page(request, username_exists=False):
     return login_signup_page(request, {'type': 'signup', 'username_exists': username_exists})


def home(request, sell_products=True):
    products = []
    if sell_products:
        products = SellProduct.objects.all()
    else:
        products = AuctionProduct.objects.all()
    return render(request , 'home.html' , {'products' : products, 'sell_products': sell_products})
    

def home_view(request):
    return home(request)


def login_page_view(request):
    return login_page(request)

def signup_page_view(request):
    return signup_page(request)


def login_view(request):

    print('login view')
    username = request.POST['username']
    password = request.POST['password']

    user = Client.get_by_username(username)

    if user is not None and user.password == password:
        request.session['username'] = username
        authenticated_users.append(username)
        return home(request)

    print('wrong credentials')
    return login_page(request, True)


def signup_view(request):
    print('signup view')

    username = request.POST['username']
    password = request.POST['password']

    user = Client.get_by_username(username)
    if user is not None:
        print('username already exists')
        return signup_page(request, True)
    
    Client.create(username, password)

    return login_page(request)


# to finish
def aution_page_view(request):
    return render(request, 'aution.html')


# gets the product and assigns the user and new price to it if the price is higher than the previous one
def aution_view(request):
    username = request.POST['username']
    user = Client.get_by_username(username)
    id = request.POST['id']
    product = AuctionProduct.get_by_id(id)
    price = request.POST['price']
    if price > product.price:
        product.price = price
        product.user = user
        product.save()

    return home(request)


# generates the bill for the user and deletes this product
def close_aution_view(request):
    id = request.POST['id']
    product = AuctionProduct.get_by_id(id)
    user = product.user
    generate_bill_pdf([product], product.price, filename=f"{settings.BASE_DIR}/{user.username}_bill.pdf")
    product.delete()

    return home(request)


def details(request , prod_id , quantite):
    products = SellProduct.objects.get(id = prod_id)

    return render(request , 'details.html' , {'products' : products , 'quantite' : quantite})

product_list = []

def decrease(request , prod_id ):
    product = SellProduct.get_by_id(id = prod_id)

    if product.quantite > 0:  
        product.quantite -= 1
        product.save()

        PanierItem.create(product, Client.get_by_username(request.session['username']))
        
    return redirect('home')   

def pannier(request):
    price = 0
    user = Client.get_by_username(request.session['username'])
    product_list = [item.product for item in user.get_panier_items()]

    for item in product_list:
        price += item.price
    if price == 0:
        msg = 'no purcahse attempt yet'
    else:
        msg = 'your total is : '
        price = int(price)
    return render(request , 'pannier.html' , {'products' : product_list , 'msg' : msg , 'total' : price})

def delete_from_pannier(request , prod_id):
    user = Client.get_by_username(request.session['username'])
    panier_items = user.get_panier_items()
    for item in panier_items:
        product = item.product
        if product.id == prod_id:
            product.quantite +=1
            product.save()
            item.delete()
            break
    return redirect('pannier')


def searching(request):

    if request.method == 'POST':
        to_search = request.POST['input_to_pass']
        if not to_search :
            not_passed = True
            return render(request , 'search.html', {'not_passed' : not_passed , 'msg' : 'you need to type something to search'})
        else :
            if to_search[0] == ':':
                
                category_to_search = to_search[ 1 : to_search.find('/')]
                if len(to_search[to_search.find('/')+1 : ].strip()) == 0:
                    returned_items = {'products_returned' : SellProduct.objects.filter(categorie = category_to_search) , 'searched' : to_search[to_search.find('/')+1 : ]}
                else:
                    returned_items = {'products_returned' : SellProduct.objects.filter(categorie = category_to_search , name__contains = to_search[to_search.find('/')+1 : ]) , 'searched' : to_search[to_search.find('/')+1 : ]}
                return render(request , "search.html" , returned_items)
            elif to_search[0] != ':':
                returned_items = {'products_returned' : SellProduct.objects.filter(name__contains = to_search) , 'searched' : to_search}
                return render(request , "search.html" , returned_items)
        return render(request , "search.html" , {'msg' : "you must type something"})


def add_view(request):
    print(request.POST)
    print(request.FILES)


    name = request.POST['name']
    price = request.POST['price']
    categorie = request.POST['categorie']
    image = request.FILES['image']
    description = request.POST['description']
    quantite = request.POST['quantite']
    SellProduct.create(name, price, categorie, image, description, quantite)

    return render(request , "add.html" , {'message' : 'product added successfully'})


def add_page_view(request):
    return render(request , 'add.html')

stripe.api_key = settings.STRIPE_SECRET_KEY

def payment_page(request , total):
    
    if request.method == 'POST':
        try:
            intent = stripe.PaymentIntent.create(
                amount=total, 
                currency='usd',
                payment_method_types=['card'],
            )
            price = 0
            user = Client.get_by_username(request.session['username'])
            panier_items = user.get_panier_items()

            for item in panier_items:
                price += item.product.price
            price = int(price)
            generate_bill_pdf((item.product for item in panier_items) , price, filename=f"{settings.BASE_DIR}/{user.username}_bill.pdf")
            user.clear_panier(panier_items)

            return render(request, 'payment.html', {
                'client_secret': intent.client_secret,
                'stripe_publishable_key': settings.STRIPE_PUBLISHABLE_KEY})
        except Exception as e:
            return render(request, 'error.html', {'error': str(e)})
    return render(request, 'pannier.html')


from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from datetime import datetime

def generate_bill_pdf(product_list, total_amount, filename):
    pdf = canvas.Canvas(filename, pagesize=letter)
    pdf.setFont("Helvetica", 12)

    pdf.drawString(100, 750, "Bill Receipt")
    pdf.drawString(100, 730, f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    pdf.drawString(100, 710, "Items Purchased:")

    y = 690
    for product in product_list:
        pdf.drawString(120, y, f"- {product.price} ({product.price} dzd)")
        y -= 20

    pdf.drawString(100, y - 20, f"Total Amount: {total_amount} dzd")

    pdf.save()
    print(f"Bill saved as {filename}")
