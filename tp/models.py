from django.db import models
from django.contrib.auth.models import User
from django import forms
# Create your models here.

class Client(models.Model):
    id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=50, unique=True)
    password = models.CharField(max_length=50)

    @staticmethod
    def create(username, password):
        client = Client.objects.create(username=username, password=password)
        client.save()
        return client
    
    @staticmethod
    def get_by_username(username):
        try:
            return Client.objects.get(username=username)
        except:
            return None
        
    def get_panier_items(self):
        return self.panier.all()
    
    def clear_panier(self, panier=None):
        if panier is None:
            panier = self.get_panier_items()
        panier.delete()


class Product(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)
    price = models.FloatField()
    categorie = models.CharField(max_length=20)
    image = models.ImageField(upload_to='media/')
    description = models.CharField(max_length=500)

class SellProduct(Product):
    quantite = models.IntegerField()

    @staticmethod
    def create(_name, _price, _categorie, _image, _description, _quantite):
        temp = SellProduct(name=_name, price=_price, categorie=_categorie, image=_image, description=_description, quantite=_quantite)
        temp.save()
        return temp

    @staticmethod
    def get_by_id(id):
        return SellProduct.objects.get(id=id)

class AuctionProduct(Product):
    user = models.ForeignKey(Client, on_delete=models.CASCADE)

    @staticmethod
    def get_by_id(id):
        return AuctionProduct.objects.get(id=id)
    
    @staticmethod
    def create(_id, _name, _price, _categorie, _image, _description, _user):
        temp = AuctionProduct(id=_id, name=_name, price=_price, categorie=_categorie, image=_image, description=_description, user=_user)
        temp.save()
        return temp
    

class PanierItem(models.Model):
    id = models.AutoField(primary_key=True)
    product = models.ForeignKey(SellProduct, on_delete=models.CASCADE)
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='panier')

    @staticmethod
    def create(product, client):
        item = PanierItem.objects.create(product=product, client=client)
        item.save()
        return item


class acheter(models.Model):
    id = models.AutoField(primary_key=True)
    id_product = models.CharField(max_length=100)
    id_client = models.CharField(max_length=10)
    total_amount = models.FloatField()



# to initialize the database
def init_sell_products():
    SellProduct.create('Xbox Controlor', 4000, 'controlor', '../media/870a4b_42698bd69e164d14b7d8e21d8c828426mv2_7QsjsZf.webp', 'description1', 10)
