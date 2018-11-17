from django.db import models

class Item(models.Model):
	category = models.CharField(max_length=30)
	description = models.CharField(max_length=50)
	shipping_weight = models.DecimalField(max_digits=6, decimal_places=3)
	image = models.ImageField()
	def __str__(self):
		return self.category, self.description, self.shipping_weight, self.image

class Distance(models.Model):
    location1 = models.ForeignKey('Location', on_delete=models.CASCADE, related_name='location1')
    location2 = models.ForeignKey('Location', on_delete=models.CASCADE, related_name='location2')
    distance = models.DecimalField(max_digits=5, decimal_places=2)
    def __str__(self):
    	return self.distance

class Location(models.Model):
	group = models.CharField(max_length=30)
	name = models.CharField(max_length=50)
	latitude = models.DecimalField(max_digits=11, decimal_places=6)
	longitude = models.DecimalField(max_digits=11, decimal_places=6)
	altitude = models.IntegerField()
	Distance = models.ManyToManyField("self", through='Distance', through_fields=('location1', 'location2'), symmetrical=False)
	def __str__(self):
		return self.group, self.name, self.latitude, self.longitude, self.altitude

class Order(models.Model):
	status = models.CharField(max_length=30)
	priority = models.IntegerField()
	combined_weights = models.DecimalField(max_digits=4, decimal_places=1)
	items = models.ManyToManyField(Item, through='Order_Item')
	location = models.ForeignKey(Location, on_delete=models.CASCADE)
	def __str__(self):
		return self.status, self.priority, self.combined_weights

class Order_Item(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantities = models.IntegerField()
    def __str__(self):
    	return self.quantities, self.item, self.order

class Shipping_Lable(models.Model):
	order = models.ForeignKey(Order, on_delete=models.CASCADE)
	contents = models.CharField(max_length=100)
	final_destination = models.CharField(max_length=20)
	def __str__(self):
		return self.contents, self.final_destination

class Itinerary(models.Model):
	location = models.ForeignKey(Location, on_delete=models.CASCADE)

class User(models.Model):
	userID = models.CharField(max_length=50)
	password = models.CharField(max_length=20)
	email = models.EmailField()
	clinic = models.ForeignKey('Location', on_delete=models.CASCADE)
	first_name = models.CharField(max_length=30)
	last_name = models.CharField(max_length=30)
	userType = models.CharField( max_length=10)
	def __str__(self):
		return self.password, self.email, self.clinic, self.first_name, self.last_name

class Forget_password(models.Model):
	user = models.ForeignKey(User, on_delete=models.CASCADE)

class Dispatch_Record(models.Model):
	order = models.ForeignKey(Order, on_delete=models.CASCADE)
	dispatch_date_time = models.DateTimeField()
	dispatch_weight = models.DecimalField(max_digits=4, decimal_places=1)
	def __str__(self):
		return self.dispatch_date_time, self.dispatch_weight

class Deliver_Record(models.Model):
	order = models.ForeignKey(Order, on_delete=models.CASCADE)
	delivered_date_time = models.DateTimeField()
	def __str__(self):
		return self.delivered_date_time

class Dispatch_Queue(models.Model):
	order = models.ForeignKey(Order, on_delete=models.CASCADE)

class Pack(models.Model):
	order = models.ForeignKey(Order, on_delete=models.CASCADE)
	csv = models.FileField()
	def __str__(self):
		return self.csv

class Packing_Queue(models.Model):
	order = models.ForeignKey(Order, on_delete=models.CASCADE)
	priority = models.IntegerField()