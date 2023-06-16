
from .models import League
from .models import Static
from .models import SearchStats
from .models import Items
from .models import SearchesJson
from .models import SearchResultsJson
from .models import BulkSearchRequests
from .models import BulkSearchResults
from django.shortcuts import render
from Apollo.trade_functions import *
import json

# Create your views here.
from django.http import HttpResponse


def home(request):
    searches = BulkSearchResults.objects.order_by('-source_search_request_id','offer_amount')[:20]
    return render(request, 'home.html',{'searches': searches})

def data_refresh(request, type):
    if type == 'League':
        f_data_refresh(League, 'https://www.pathofexile.com/api/trade/data/leagues')
    if type == 'Static':
        f_data_refresh(Static, 'https://www.pathofexile.com/api/trade/data/static')
    if type == 'SearchStats':
        f_data_refresh(SearchStats, 'https://www.pathofexile.com/api/trade/data/stats')
    if type == 'Items':
        f_data_refresh(Items, 'https://www.pathofexile.com/api/trade/data/items')
    return render(request, 'data_refresh.html')

def search_trade_for_item(request,name,type):
    return(f_search_trade_for_item(name,type))

def item_list(request, search_string):
    items = Items.objects.filter(item_name__icontains=search_string)
    statics = Static.objects.filter(static_text__icontains=search_string)
    return render(request, 'item_list.html',{'items': items})
    
def get_search_json_by_id(request,id):
    search_result = SearchResultsJson.objects.get(id=id).response_json
    return HttpResponse(search_result)

def view_search_result_json(request,id):
    return render(request, 'view_search_result_json.html', {'id': id})

def view_search_result(request,id):
    items = json.loads(SearchResultsJson.objects.get(id=id).response_json)
    return render(request, 'view_search_result.html',{'items': items})

def bulk_exchange(request,want,have):
    f_bulk_exchange(want,have)
    return HttpResponse('Success!')

def refresh_every_5m(request, want, have):
    return render(request, 'refresh_every_5m.html', {'want': want, 'have': have})