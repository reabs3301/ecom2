from django.http import HttpResponse
from django.shortcuts import render , redirect
from .models import SellProduct, Client, PanierItem, AuctionProduct, Seller, AuctionPanierItem
from django.conf import settings
from django.urls import resolve

import stripe
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from io import BytesIO
from PIL import Image


SELL = BUY = 0
AUCTION = BID = 1

CLIENT = 0
SELLER = 1

categories = ["All", "Electronics", "Clothing", ] 
class ProductResult:
    def __init__(self, product):
        self.product = product  
        self.id = product.id
        self.name = product.name
        self.price = product.price
        self.category = product.category
        self.image = product.image
        self.description = product.description

class AuctionProductResult(ProductResult):
    def __init__(self, product):
        super().__init__(product)
        self.is_there_bider = product.is_there_bider()
        self.is_closed = product.closed
        self.can_close = not product.closed and product.is_there_bider
        self.type = AUCTION

    @staticmethod
    def convert_all(products):
        return [AuctionProductResult(product) for product in products]
    
    @staticmethod
    def convert_one(product):
        return AuctionProductResult(product)

class SellProductResult(ProductResult):
    def __init__(self, product):
        super().__init__(product)
        self.type = SELL
        self.quantity = product.quantite

    @staticmethod
    def convert_all(products):
        return [SellProductResult(product) for product in products]
    
    @staticmethod
    def convert_one(product):
        return SellProductResult(product)


def create_result_from_panier_items(sell_product_items, auction_product_items):
    sell_products = [SellProductResult.convert_one(item.product) for item in sell_product_items]
    auction_products = [AuctionProductResult.convert_one(item.product) for item in auction_product_items]
    return sell_products + auction_products


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


def client_home(request, products=None, type=BUY, category=categories[0]):
    if products is None:
        products = []
        if type == BUY:
            products = SellProduct.objects.all()
        else:
            products = AuctionProduct.objects.all()
    
    return render(request , 'home.html' , {'products' : products, 'type': type, 'categories': categories, 'category': category})
    
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
    products = SellProductResult.convert_all(user.get_sell_products())
    return seller_home(request, products, SELL)

def seller_auction_products_view(request):
    print('seller auction products view')
    username = request.session['username']
    user = Seller.get_by_username(username)
    products = AuctionProductResult.convert_all(user.get_auction_products())
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
    AuctionPanierItem.create(product, user)
    product.close()

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
    product_list = create_result_from_panier_items(user.get_panier_items(), user.get_auction_panier_items())
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


# def searching(request):
#     text = request.POST['input']
#     type = int(request.POST['type'])
#     if text == '':
#         return client_home(request, type=type)        
    
#     get_by_name_like = lambda type, text, queryset=None: SellProduct.get_by_name_like(text, queryset) if type == BUY else AuctionProduct.get_by_name_like(text, queryset)
#     get_by_categorie = lambda type, text, queryset=None: SellProduct.get_by_categorie(text, queryset) if type == BUY else AuctionProduct.get_by_categorie(text, queryset)

#     if text[0] != ":":
#         products = get_by_name_like(type, text)
#         # return render(request , 'search.html' , {'products' : products, 'not_passed': False, 'searched': text, 'type': type})
#         return client_home(request, products, type)
    
#     invalid_search = lambda : render(request , 'search.html' , {'not_passed': True, 'message': f'invalid search: "{text}"'})

#     if not len(text) > 1:
#         return invalid_search()
    
#     slash = text.find('/')
#     if slash == 1 or slash == len(text) - 1:
#         return invalid_search()

#     if slash == -1:
#         categorie = text[1:] 
#     else:
#         categorie = text[1:slash]
#     products = get_by_categorie(type, categorie)

#     if slash != -1:
#         name = text[slash + 1:]
#         products = get_by_name_like(type, name, products)

#     # print(products)    
#     return render(request , 'search.html' , {'products' : products, 'not_passed': False, 'searched': text, 'type': type})
def searching(request):
    text = request.POST['input']
    type = int(request.POST['type'])
    category = request.POST['category']

    get_by_name_like = lambda type, text, queryset=None: SellProduct.get_by_name_like(text, queryset) if type == BUY else AuctionProduct.get_by_name_like(text, queryset)
    get_by_categorie = lambda type, text, queryset=None: SellProduct.get_by_category(text, queryset) if type == BUY else AuctionProduct.get_by_category(text, queryset)

    products = get_by_name_like(type, text)
    if category != 'All':
        products = get_by_categorie(type, category, products)

    print(text, type, category, products)

    return client_home(request, products, type, category)


def add_view(request):
    name = request.POST['name']
    category = request.POST['category']
    image = request.FILES['image']
    description = request.POST['description']
    price = int(request.POST['price'])
    type = int(request.POST['type'])
    seller = Seller.get_by_username(request.session['username'])

    if type == SELL:
        quantite = int(request.POST['quantite'])
        SellProduct.create(name, price, category, image, description, quantite, seller)
    else:
        AuctionProduct.create(name, price, category, image, description, seller)

    return render(request , "add.html" , {'message' : 'product added successfully'})


def add_page_view(request, type=SELL):
    return render(request , 'add.html', {'type': type, 'categories': categories[1:]})

stripe.api_key = settings.STRIPE_SECRET_KEY

def payment_page(request , total):
    
    if request.method == 'POST':
        try:
            intent = stripe.PaymentIntent.create(
                amount=total, 
                currency='usd',
                payment_method_types=['card'],
            )
            user = Client.get_by_username(request.session['username'])
            product_list = create_result_from_panier_items(user.get_panier_items(), user.get_auction_panier_items())

            generate_bill_pdf(product_list, total, filename=f"{settings.BASE_DIR}/{user.username}_bill.pdf")

            
            for item in product_list:
                # if item.type == SELL and item.quantity == 0 and not item.product.is_deleted():
                    # item.product.delete()
                if item.type == AUCTION:
                    item.product.delete()

            user.clear_all_panier_items()

            return render(request, 'payment.html', {
                'client_secret': intent.client_secret,
                'stripe_publishable_key': settings.STRIPE_PUBLISHABLE_KEY})
        except Exception as e:
            return render(request, 'error.html', {'error': str(e)})
        
    return render(request, 'pannier.html')


from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from datetime import datetime
from reportlab.lib.units import inch

def generate_bill_pdf(product_list, total_amount, filename):
    pdf = canvas.Canvas(filename, pagesize=letter)
    
    # Set up beautiful colors
    primary_color = colors.HexColor("#3498db")  # Blue
    secondary_color = colors.HexColor("#2c3e50")  # Dark blue
    accent_color = colors.HexColor("#e74c3c")  # Red
    
    # Draw beautiful header with rectangle
    pdf.setFillColor(primary_color)
    pdf.rect(0, 750, letter[0], 50, fill=True, stroke=False)
    
    # Add title
    pdf.setFont("Helvetica-Bold", 24)
    pdf.setFillColor(colors.white)
    pdf.drawCentredString(letter[0]/2, 765, "BILL RECEIPT")
    
    # Reset y position for content
    y_position = 700
    
    # Add date
    pdf.setFont("Helvetica", 12)
    pdf.setFillColor(secondary_color)
    pdf.drawString(72, y_position, f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    y_position -= 30
    
    # Add company info
    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawString(72, y_position, "E-Store")
    y_position -= 15
    pdf.setFont("Helvetica", 10)
    pdf.drawString(72, y_position, "123 Main Street, Algiers")
    y_position -= 15
    pdf.drawString(72, y_position, "Phone: +213 123 456 789")
    y_position -= 30
    
    # Add items purchased header
    pdf.setFont("Helvetica-Bold", 14)
    pdf.setFillColor(primary_color)
    pdf.drawString(72, y_position, "ITEMS PURCHASED")
    y_position -= 25
    
    # Draw line separator
    pdf.setStrokeColor(primary_color)
    pdf.line(72, y_position, letter[0]-72, y_position)
    y_position -= 20
    
    # Add items
    pdf.setFont("Helvetica", 12)
    pdf.setFillColor(secondary_color)
    
    for i, product in enumerate(product_list, 1):
        pdf.drawString(72, y_position, f"{i}. {product.name}")
        pdf.drawRightString(letter[0]-72, y_position, f"{product.price:,.2f} DZD")
        y_position -= 20
    
    # Draw total separator line
    pdf.setStrokeColor(accent_color)
    pdf.line(72, y_position-10, letter[0]-72, y_position-10)
    y_position -= 20
    
    # Add total amount
    pdf.setFont("Helvetica-Bold", 14)
    pdf.setFillColor(accent_color)
    pdf.drawString(72, y_position, "TOTAL AMOUNT:")
    pdf.drawRightString(letter[0]-72, y_position, f"{total_amount:,.2f} DZD")
    y_position -= 30
    
    # Add footer
    pdf.setFont("Helvetica-Oblique", 10)
    pdf.setFillColor(colors.blue)
    pdf.drawCentredString(letter[0]/2, 40, "Thank you for your purchase!")
    pdf.drawCentredString(letter[0]/2, 25, "For inquiries: contact@abcstore.dz")
    
    pdf.save()
    print(f"Bill saved as {filename}")

def print_view(request):
    return add_page_view(request, int(request.POST['type']))