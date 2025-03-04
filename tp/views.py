from django.shortcuts import render , redirect
from .models import product,client, acheter # Import the Product model
from .forms import  productform
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
    return render(request , 'pannier.html' , {'products' : product_list , 'msg' : msg , 'total' : price})

def delete_from_pannier(request , prod_id):
    for item in product_list:
        if item.id == prod_id :
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