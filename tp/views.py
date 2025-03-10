from django.http import HttpResponse
from django.shortcuts import render , redirect
from .models import product,client, acheter # Import the Product model
from .forms import  productform
from django.conf import settings
import stripe
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from io import BytesIO
# Create your views here.

def home(request):
    products = product.objects.all()
    return render(request , 'home.html' , {'products' : products})

def details(request , prod_id , quantite):
    products = product.objects.get(id = prod_id)

    return render(request , 'details.html' , {'products' : products , 'quantite' : quantite})

product_list = []

def decrease(request , prod_id ):
    products = product.objects.get(id = prod_id)

    if products.quantite > 0:  
        products.quantite -= 1
        products.save()
        #client_buy = client.objects.get(id = client_id)
        
        
        product_list.append(products)
    return redirect('home')   
    #return render(request, 'details.html', {'products': product_list})

def pannier(request):
    price = 0

    for item in product_list:
        price += item.price
    if price == 0:
        msg = 'no purcahse attempt yet'
    else:
        msg = 'your total is : '
        price = int(price)
    return render(request , 'pannier.html' , {'products' : product_list , 'msg' : msg , 'total' : price})

def delete_from_pannier(request , prod_id):
    for item in product_list:
        if item.id == prod_id :
            item.quantite +=1
            item.save()
            product_list.remove(item)
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
                    returned_items = {'products_returned' : product.objects.filter(categorie = category_to_search) , 'searched' : to_search[to_search.find('/')+1 : ]}
                else:
                    returned_items = {'products_returned' : product.objects.filter(categorie = category_to_search , name__contains = to_search[to_search.find('/')+1 : ]) , 'searched' : to_search[to_search.find('/')+1 : ]}
                return render(request , "search.html" , returned_items)
            elif to_search[0] != ':':
                returned_items = {'products_returned' : product.objects.filter(name__contains = to_search) , 'searched' : to_search}
                return render(request , "search.html" , returned_items)
        return render(request , "search.html" , {'msg' : "you must type something"})


def add(request):
    if request.method == 'POST':
        form = productform(request.POST , request.FILES)

        if form.is_valid() : 
            form.save()
            form = productform()
            return render(request , "add.html" , {'form' : form , 'message' : 'product added successfully'})
    else :
        form = productform()
        return render(request , 'add.html' , {'form' : form , 'message' : form.errors})
    return render(request , 'add.html' , {'form' : form , 'message' : form.errors})

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
            for item in product_list:
                price += item.price
            price = int(price)
            generate_bill_pdf(product_list , price , filename=r"D:\s2\E-COM\bill.pdf")
            product_list.clear()
            return render(request, 'payment.html', {
                'client_secret': intent.client_secret,
                'stripe_publishable_key': settings.STRIPE_PUBLISHABLE_KEY})
        except Exception as e:
            return render(request, 'error.html', {'error': str(e)})
    return render(request, 'pannier.html')


from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from datetime import datetime

def generate_bill_pdf(product_list, total_amount, filename=r"D:\s2\E-COM\bill1.pdf"):
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
