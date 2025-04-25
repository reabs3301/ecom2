from django.http import HttpResponse
from django.shortcuts import render , redirect
from .models import SellProduct, Client, PanierItem, AuctionProduct, Seller, AuctionPanierItem
from .forms import  productform
from django.conf import settings
from django.urls import resolve

import stripe
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from io import BytesIO
from PIL import Image

class AuctionProductResult:
    def __init__(self, product):
        self.id = product.id
        self.name = product.name
        self.price = product.price
        self.categorie = product.categorie
        self.image = product.image
        self.description = product.description
        self.is_there_bider = product.is_there_bider()
        
    @staticmethod
    def convert_one(product):
        return AuctionProductResult(product)
    
    @staticmethod
    def convert_all(products):
        return [AuctionProductResult(product) for product in products]
        

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


SELL = BUY = 0
AUCTION = BID = 1

CLIENT = 0
SELLER = 1

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


def client_home(request, products=None, type=BUY):
    if products is None:
        products = []
        if type == BUY:
            products = SellProduct.objects.all()
        else:
            products = AuctionProduct.objects.all()
    return render(request , 'home.html' , {'products' : products, 'type': type})
    
def seller_home(request, products=None, type=SELL):
    if products is None:
        products = []
        username = request.session['username']
        user = Seller.get_by_username(username)
        if type == SELL:
            products = user.get_sell_products()
        else:
            products = AuctionProductResult.convert_all(user.get_auction_products())
    return render(request, 'seller/home.html', {'products': products, 'type': type})

def seller_home_view(request):
    return seller_home(request)

def home_view(request):
    return client_home(request)


def login_page_view(request):
    return login_page(request)

def signup_page_view(request):
    return signup_page(request)


def login_view(request):

    print('login view')
    username = request.POST['username']
    password = request.POST['password']
    role = int(request.POST['role'])

    if role == CLIENT:
        user = Client.get_by_username(username)
    else:
        user = Seller.get_by_username(username)

    if user is not None and user.password == password:
        request.session['username'] = username
        request.session['role'] = role
        authenticated_users.append(username)
        if role == CLIENT:
            return client_home(request)
        else:
            return seller_home(request)

    print('wrong credentials')
    return login_page(request, True)


def signup_view(request):
    print('signup view')

    username = request.POST['username']
    password = request.POST['password']
    role = int(request.POST['role'])
    if role == CLIENT:
        user = Client.get_by_username(username)
    else:
        user = Seller.get_by_username(username)

    if user is not None:
        print('username already exists')
        return signup_page(request, True)
    
    if role == CLIENT:
        Client.create(username, password)
    else:
        Seller.create(username, password)

    return login_page(request)

def seller_sell_products_view(request):
    print('seller sell products view')
    username = request.session['username']
    user = Seller.get_by_username(username)
    products = user.get_sell_products()
    print(products)
    return seller_home(request, products, SELL)

def seller_auction_products_view(request):
    print('seller auction products view')
    username = request.session['username']
    user = Seller.get_by_username(username)
    products = user.get_auction_products()
    products = AuctionProductResult.convert_all(products)

    print(products)
    return seller_home(request, products, AUCTION)

def seller_details_view(request, prod_id, type):
    product = SellProduct.get_by_id(prod_id) if type == BUY else AuctionProductResult.convert_one(AuctionProduct.get_by_id(prod_id))
    print(prod_id, type, product)
    return render(request , 'seller/details.html' , {'product' : product, 'type': type})

# gets the product and assigns the user and new price to it if the price is higher than the previous one
def bid_view(request):
    username = request.session['username']
    user = Client.get_by_username(username)
    id = request.POST['id']
    product = AuctionProduct.get_by_id(id)

    price = int(request.POST['price'])
    product.add_bider(user, price)

    return client_home(request)


# generates the bill for the user and deletes this product
def seller_close_auction_view(request, prod_id):
    product = AuctionProduct.get_by_id(prod_id)
    user = product.best_bider
    if user is not None:
        # generate_bill_pdf([product], product.price, filename=f"{settings.BASE_DIR}/{user.username}_bill.pdf")
        # product.delete()
        AuctionPanierItem.create(product, user)


    return seller_home(request, type=AUCTION)

def auction_page_view(request, prod_id):
    product = AuctionProduct.get_by_id(prod_id)
    username = request.session['username']
    user = Client.get_by_username(username)
    
    if product.can_bid(user):
        print('can bid')
        return render(request , 'auction.html' , {'product' : product})
    else:
        print('cannot bid')
        return client_home(request, type=AUCTION)

def details(request, prod_id, type):
    
    product = SellProduct.get_by_id(prod_id) if type == BUY else AuctionProduct.get_by_id(prod_id)
    print(prod_id, type, product)
    return render(request , 'details.html' , {'product' : product, 'type': type}) 

def details_view(request, prod_id, type):
    return details(request, prod_id, int(type))

product_list = []

def add_to_pannier_view(request , prod_id ):
    product = SellProduct.get_by_id(prod_id)

    if product.quantite > 0:  
        product.quantite -= 1
        product.save()

        PanierItem.create(product, Client.get_by_username(request.session['username']))
        
    return client_home(request)   

def pannier_page_view(request):
    price = 0
    user = Client.get_by_username(request.session['username'])
    product_list = []
    product_list.extend([item.product for item in user.get_panier_items()])
    print('panier items', product_list)
    product_list.extend([item.product for item in user.get_auction_panier_items()])
    print('all panier items', product_list)

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
    return redirect('pannier_page')


def searching(request):
    text = request.POST['input']
    type = int(request.POST['type'])
    if text == '':
        return client_home(request, type=type)        
    
    get_by_name_like = lambda type, text, queryset=None: SellProduct.get_by_name_like(text, queryset) if type == BUY else AuctionProduct.get_by_name_like(text, queryset)
    get_by_categorie = lambda type, text, queryset=None: SellProduct.get_by_categorie(text, queryset) if type == BUY else AuctionProduct.get_by_categorie(text, queryset)

    if text[0] != ":":
        products = get_by_name_like(type, text)
        # return render(request , 'search.html' , {'products' : products, 'not_passed': False, 'searched': text, 'type': type})
        return client_home(request, products, type)
    
    invalid_search = lambda : render(request , 'search.html' , {'not_passed': True, 'message': f'invalid search: "{text}"'})

    if not len(text) > 1:
        return invalid_search()
    
    slash = text.find('/')
    if slash == 1 or slash == len(text) - 1:
        return invalid_search()

    if slash == -1:
        categorie = text[1:] 
    else:
        categorie = text[1:slash]
    products = get_by_categorie(type, categorie)

    if slash != -1:
        name = text[slash + 1:]
        products = get_by_name_like(type, name, products)

    # print(products)    
    return render(request , 'search.html' , {'products' : products, 'not_passed': False, 'searched': text, 'type': type})

        

def add_view(request):
    name = request.POST['name']
    categorie = request.POST['categorie']
    image = request.FILES['image']
    description = request.POST['description']
    price = int(request.POST['price'])
    type = int(request.POST['type'])
    seller = Seller.get_by_username(request.session['username'])

    if type == SELL:
        quantite = int(request.POST['quantite'])
        SellProduct.create(name, price, categorie, image, description, quantite, seller)
    else:
        AuctionProduct.create(name, price, categorie, image, description, seller)

    return render(request , "add.html" , {'message' : 'product added successfully'})


def add_page_view(request, type=SELL):
    return render(request , 'add.html', {'type': type})

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


def print_view(request):
    return add_page_view(request, int(request.POST['type']))