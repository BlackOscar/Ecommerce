from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from .models import Item, OrderItem, Order, BillingAddress
from django.views.generic import ListView, DetailView, View
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import CheckoutForm
from django.conf import settings



# `source` is obtained with Stripe.js; see https://stripe.com/docs/payments/accept-a-payment-charges#web-create-token

# Create your views here.


class HomeView(ListView):
	model = Item
	paginate_by = 10
	template_name = 'ecom/home-page.html'


class ItemDetailView(DetailView):
	print("ITEM DETAIL WORKING")
	model = Item
	template_name = 'ecom/product-page.html'



class CheckoutView(View):
	def get(self, *args, **kwargs):
		form = CheckoutForm()
		context = {
			'form': form
		}

		return render(self.request, 'ecom/checkout-page.html', context)

	def post(self, *args, **kwargs):
		form = CheckoutForm(self.request.POST or None)
		try:
			order = Order.objects.get(user=self.request.user, ordered=False)
			order_item = OrderItem.objects.filter(user=self.request.user, ordered=False)
			print("Order item: ", order_item)
			if form.is_valid():
				street_address = form.cleaned_data.get('street_address')
				apartment_address = form.cleaned_data.get('apartment_address')
				country = form.cleaned_data.get('country')
				zip = form.cleaned_data.get('zip')
				#same_billing_address = form.cleaned_data.get('same_billing_address')
				#save_info = form.cleaned_data.get('save_info')
				#payment_option = form.cleaned_data.get('payment_option')

				billing_address = BillingAddress(
					user = self.request.user,
					street_address = street_address,
					apartment_address = apartment_address,
					countries = country,
					zip = zip
					)
				billing_address.save()
				order.billing_address = billing_address
				order.ordered = True
				order.save()
				for item in order_item:
					item.ordered = True
					item.save()
				messages.error(self.request, 'Đặt hàng thành công!')
				return redirect('core:home')
		except ObjectDoesNotExist:
			
			return redirect('core:checkout')
@login_required
def add_to_cart(request, slug):
	
	item = get_object_or_404(Item, slug=slug)
	order_item, created = OrderItem.objects.get_or_create(item=item, user=request.user, ordered=False)

	
	order_qs = Order.objects.filter(user=request.user, ordered=False)
	#print("Order_qs: ", order_qs[0].user)
	if order_qs.exists():
		order = order_qs[0]
		#print(order.items)
		#order.items.filter(item__slug=item.slug) tra ve OrderItem
		if order.items.filter(item__slug=item.slug).exists():
			order_item.quantity += 1
			order_item.save()
			messages.info(request, "Số lượng đã được cập nhật!")
		else:
			
			order.items.add(order_item)
			messages.info(request, "Thêm vào giỏ hàng!")
			return redirect("core:product", slug=slug)

	else:
		ordered_date = timezone.now()
		order = Order.objects.create(user=request.user, ordered_date=ordered_date )
		order.items.add(order_item)
	#print("Order_qs: ", order_qs[0])

	return redirect("core:product", slug=slug)
@login_required
def remove_from_cart(request, slug):
	item = get_object_or_404(Item, slug=slug)
	#print("Order_item: ",order_item, "created: ", created)
	order_qs = Order.objects.filter(user=request.user, ordered=False)
	#print("Order_qs: ", order_qs[0].user)
	if order_qs.exists():
		order = order_qs[0]
		#print(order.items)
		#order.items.filter(item__slug=item.slug) tra ve OrderItem
		if order.items.filter(item__slug=item.slug).exists():
			print("1: ", order.items.filter(item__slug=item.slug))

			#k can dong nay cung dc, neu ma k dung dong nay thi se la (order.items.remove(order.items.filter(item__slug=item.slug)[0]))
			order_item = OrderItem.objects.filter(item=item, user=request.user, ordered=False)[0]
			
			print('2: ', order_item)
			
			
			order.items.remove(order_item)
			order_item.quantity = 1
			order_item.save()
			messages.info(request, "Đã xóa mặt hàng!")
		else:
			messages.info(request, "Mặt hàng này không có trong giỏ hàng của bạn!")
			return redirect("core:product", slug=slug)

	else:
		messages.info(request, "Bạn chưa đặt hàng!")
		return redirect("core:product", slug=slug)
	
	return redirect("core:product", slug=slug)	

@login_required
def remove_item_quantity_from_cart(request, slug):
	item = get_object_or_404(Item, slug=slug)
	print("item: ", item)
	order_qs = Order.objects.filter(user=request.user, ordered=False)
	#print("Order_qs: ", order_qs[0].user)
	if order_qs.exists():
		order = order_qs[0]
		#print(order.items)
		#order.items.filter(item__slug=item.slug) tra ve OrderItem
		if order.items.filter(item__slug=item.slug).exists():
			
			
			#k can dong nay cung dc, neu ma k dung dong nay thi se la (order.items.remove(order.items.filter(item__slug=item.slug)[0]))
			order_item = OrderItem.objects.filter(item=item, user=request.user, ordered=False)[0]
			if order_item.quantity > 1:
				order_item.quantity -= 1
				messages.info(request, "Số lượng đã được cập nhật!")
				order_item.save()
			else:
				order.items.remove(order_item)
			
		else:
			messages.info(request, "Mặt hàng này không có trong giỏ hàng của bạn!")
			return redirect("core:order-summary")

	else:
		messages.info(request, "Bạn chưa có đơn hàng nào!")
		return redirect("core:order-summary")
	
	return redirect("core:order-summary")	

class OrderSummary(LoginRequiredMixin, View):
	def get(self, *args, **kwargs):
		try:
			order = Order.objects.get(user=self.request.user, ordered=False)
			context = {
				'object': order
			}
			return render(self.request, 'ecom/order_summary.html', context )
		except ObjectDoesNotExist:
			messages.error(self.request, 'Bạn chưa có đơn hàng nào')
			return redirect("/")
		

