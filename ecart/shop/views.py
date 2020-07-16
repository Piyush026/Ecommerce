from django.shortcuts import render
from django.http import HttpResponse
import json
# Create your views here.
from .models import Product, Contact, Order, UpdateOrder
from math import ceil
from django.views.decorators.csrf import csrf_exempt
from paytm import checksum

MERCHANT_KEY = 'LStM1G@9dpuMw#57'


def view_info(request):
    objs = Product.objects.all()
    print("objs", objs)
    return render(request, 'shop/table.html', {'objs': objs})


def index(request):
    # Show all product
    # products = Product.objects.all()
    # n = len(products)
    # nSlides = n // 4 + ceil((n / 4) - (n // 4))
    # param = {'product': products, 'no_of_slides': nSlides, 'range': range(1, nSlides)}
    allprods = []
    catprods = Product.objects.values('category', 'id')
    cats = {item['category'] for item in catprods}
    for cat in cats:
        prod = Product.objects.filter(category=cat)
        n = len(prod)
        nSlides = n // 4 + ceil((n / 4) - (n // 4))
        allprods.append([prod, range(1, nSlides), nSlides])
    # replica
    # allprods = [[products, range(1, nSlides), nSlides],
    #             [products, range(1, nSlides), nSlides]]
    param = {'allprods': allprods}
    # print(f"products{param}")
    return render(request, 'shop/index.html', param)


def searchmatch(query, item):
    if query in item.product_name.lower() or query in item.category.lower() or query in item.subcategory.lower() or query in item.desc.lower():
        return True
    else:
        return False


def search(request):
    query = request.GET.get('search')
    allprods = []
    catprods = Product.objects.values('category', 'id')
    cats = {item['category'] for item in catprods}
    for cat in cats:
        prodtemp = Product.objects.filter(category=cat)
        prod = [item for item in prodtemp if searchmatch(query, item)]
        n = len(prod)
        nSlides = n // 4 + ceil((n / 4) - (n // 4))
        if len(prod) != 0:
            allprods.append([prod, range(1, nSlides), nSlides])
    param = {'allprods': allprods, 'msg': ''}
    if len(allprods) == 0 or len(query) < 4:
        param = {'msg': 'pls enter another item'}
    return render(request, 'shop/search.html', param)


def contact(request):
    if request.method == 'POST':
        name = request.POST.get('name', '')
        email = request.POST.get('email', '')
        phone = request.POST.get('phone', '')
        desc = request.POST.get('desc', '')
        print("data", name, email, phone, desc)
        contacts = Contact(name=name, email=email, phone=phone, desc=desc)
        contacts.save()
        thank = True
        return render(request, 'shop/contact.html', {'thank': thank})
    return render(request, 'shop/contact.html')


def about(request):
    return render(request, 'shop/about.html')


def tracker(request):
    updates = []
    gh = []
    if request.method == 'POST':
        order_id = request.POST.get('orderId', '')
        email = request.POST.get('email', '')
        try:
            order = Order.objects.filter(order_id=order_id, email=email)
            if len(order) > 0:
                update = UpdateOrder.objects.filter(order_id=order_id)
                for item in update:
                    updates.append({'text': item.update_desc, 'time': item.timestamp})
                jsn = json.loads(order[0].order_json)
                for x in jsn.values():
                    gh.append({'qty': x[0], "name": x[1]})
            else:
                data = True
                return render(request, 'shop/tracker.html', {'data': data})
        except Exception as e:
            data = True
            return render(request, 'shop/tracker.html', {'data': data})
    return render(request, 'shop/tracker.html', {'text': updates, 'jsn': gh})


def productView(request, myid):
    prod = Product.objects.filter(id=myid)
    print("product", prod)
    return render(request, "shop/product.html", {'product': prod[0]})


def checkout(request):
    if request.method == 'POST':
        order_json = request.POST.get('order_json', '')
        name = request.POST.get('name', '')
        amount = request.POST.get('amount', '')
        email = request.POST.get('email', '')
        phone = request.POST.get('phone', '')
        address = request.POST.get('address1', '') + " " + request.POST.get('address2', '')
        city = request.POST.get('city', '')
        state = request.POST.get('state', '')
        zip_code = request.POST.get('zip_code', '')
        order = Order(order_json=order_json, name=name, email=email, phone=phone, address=address, city=city,
                      state=state, zip_code=zip_code, amount=amount)
        gh = json.loads(order_json)
        if len(gh) != 0:
            order.save()
            id = order.order_id
            thank = True
            update = UpdateOrder(order_id=order.order_id, update_desc="The Order has been Placed")
            update.save()
            # return render(request, 'shop/checkout.html', {'thank': thank, 'id': id})
            # Request Paytm to transfer the amount in your account
            param_dict = {

                'MID': 'lEFTkL88232363901160',
                'ORDER_ID': str(order.order_id),
                'TXN_AMOUNT': str(amount),
                'CUST_ID': email,
                'INDUSTRY_TYPE_ID': 'Retail',
                'WEBSITE': 'WEBSTAGING',
                'CHANNEL_ID': 'WEB',
                'CALLBACK_URL': 'http://127.0.0.1:8000/shop/handlerequest/',

            }
            param_dict['CHECKSUMHASH'] = checksum.generate_checksum(param_dict, MERCHANT_KEY)
            return render(request, 'shop/paytm.html', {'param_dict': param_dict,'thank': thank})
    return render(request, 'shop/checkout.html')


@csrf_exempt
def handlerequest(request):
    # paytm will send you post request here
    form = request.POST
    reponse_dict = {}
    for i in form.keys():
        reponse_dict[i] = form[i]
        if i == 'CHECKSUMHASH':
            checkssum = form[i]

    verify = checksum.verify_checksum(reponse_dict, MERCHANT_KEY, checkssum)
    if verify:
        if reponse_dict['RESPCODE'] == '01':
            print("order Successful")
            thank = True
        else:
            print('order was not successful because' + reponse_dict['RESPMSG'])
    return render(request, 'shop/paymentstatus.html', {'response': reponse_dict,'thank': thank})
