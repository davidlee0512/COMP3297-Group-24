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
	items = models.ManyToManyField(Item, through='Order_Item')
	location = models.ForeignKey(Location, on_delete=models.CASCADE)
	orderTime = models.DateTimeField(null = True)
	dispatchedTime = models.DateTimeField(null = True)
	deliveredTime = models.DateTimeField(null = True)
	def __str__(self):
		return self.status, self.priority

	def getCombinedWeight(self):
		totalWeight = 0.0
		for item in self.items.all():
			totalWeight += float(item.shipping_weight) * Order_Item.objects.get(item_id = item.id, order_id = self.id).quantity
		return totalWeight

class Order_Item(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    def __str__(self):
    	return self.quantity, self.item, self.order


class User(models.Model):
	userID = models.CharField(max_length=50)
	password = models.CharField(max_length=20)
	email = models.EmailField()
	clinic = models.ForeignKey('Location', on_delete=models.CASCADE, null = True)
	first_name = models.CharField(max_length=30)
	last_name = models.CharField(max_length=30)
	userType = models.CharField( max_length=20)
	def __str__(self):
		return self.password, self.email, self.clinic, self.first_name, self.last_name

class Forget_password(models.Model):
	user = models.ForeignKey(User, on_delete=models.CASCADE)
	token = models.CharField(max_length=6)

class Pack(models.Model):
	order = models.ManyToManyField(Order)
	itinerary = models.ManyToManyField(Distance)

class Token(models.Model):
	token = models.CharField(max_length=6)
	email = models.EmailField()
	userType = models.CharField(max_length=10)