from django.db import models
from django import forms
# Create your models here.

class User(models.Model):
    id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=50, unique=True)
    password = models.CharField(max_length=50)

    class Meta:
        abstract = True

    @classmethod
    def create(cls, username, password):
        client = cls.objects.create(username=username, password=password)
        client.save()
        return client
    
    @classmethod
    def get_by_username(cls, username):
        try:
            return cls.objects.get(username=username)
        except:
            return None
    
class Client(User):    
    def get_panier_items(self):
        return self.panier.all()
    
    def get_auction_panier_items(self):
        return self.auction_panier.all()


    def clear_all_panier_items(self):
        self.panier.all().delete()
        self.auction_panier.all().delete()
        self.save()

class Seller(User):

    def get_sell_products(self):
        return self.sell_products.all()
    
    def get_auction_products(self):
        return self.auction_products.all()
    


class Product(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)
    price = models.FloatField()
    category = models.CharField(max_length=20)
    image = models.ImageField(upload_to='media/')
    description = models.CharField(max_length=500)
    class Meta:
        abstract = True



    @classmethod
    def get_by_name_like(cls, name, queryset=None):
        if queryset is None:
            queryset = cls.objects.all()
        return queryset.filter(name__contains=name)   

    @classmethod
    def get_by_category(cls, category, queryset=None):
        if queryset is None:
            queryset = cls.objects.all()
        return queryset.filter(category=category)
    
    @classmethod
    def get_by_id(cls, id):
        try:
            return cls.objects.get(id=id)
        except cls.DoesNotExist:
            return None
        
    def is_deleted(self):
        return self.get_by_id(self.id) is None
        

class SellProduct(Product):
    seller = models.ForeignKey(Seller, on_delete=models.CASCADE, related_name='sell_products')
    quantite = models.IntegerField()

    @staticmethod
    def create(_name, _price, _category, _image, _description, _quantite, _seller):
        temp = SellProduct.objects.create(name=_name, price=_price, quantite=_quantite, category=_category, image=_image, description=_description, seller=_seller)
        temp.save()
        return temp


class AuctionProduct(Product):
    seller = models.ForeignKey(Seller, on_delete=models.CASCADE, related_name='auction_products', null=True, blank=True)
    best_bider = models.ForeignKey(Client, on_delete=models.CASCADE, default=None, null=True, related_name='won_auctions')
    biders = models.ManyToManyField(Client, related_name='bids')
    closed = models.BooleanField(default=False)
    
    @staticmethod
    def create(_name, _price, _category, _image, _description, _seller):
        temp = AuctionProduct.objects.create(name=_name, price=_price, category=_category, image=_image, description=_description, seller=_seller)
        temp.save()
        return temp
    
    def add_bider(self, bider, price):
        self.biders.add(bider)
        if self.price < price:
            self.price = price
            self.best_bider = bider
            self.save()
        

    def can_bid(self, client):
        return not self.biders.filter(id=client.id).exists()
    
    def is_there_bider(self):
        return self.best_bider is not None
    
    def close(self):
        self.closed = True
        self.save()
        
    

class PanierItem(models.Model):
    id = models.AutoField(primary_key=True)
    product = models.ForeignKey(SellProduct, on_delete=models.CASCADE)
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='panier')

    @staticmethod
    def create(product, client):
        item = PanierItem.objects.create(product=product, client=client)
        item.save()
        return item
    
class AuctionPanierItem(models.Model):
    id = models.AutoField(primary_key=True)
    product = models.ForeignKey(AuctionProduct, on_delete=models.CASCADE)
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='auction_panier')

    @staticmethod
    def create(product, client):
        item = AuctionPanierItem.objects.create(product=product, client=client)
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
