
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
from django.db import connection
from datetime import datetime

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

def house_of_mirrors_results(request):
    # Your raw SQL query
    raw_query = """select source_search_request_id, 
                    ab.for_tag, 
                    datetime(min(result_datetime), '-4 hours') the_date ,
                    --strftime('%m/%d/%Y ', min(result_datetime)) || 
                    --case when cast(strftime('%H', min(result_datetime))as int)=0 then '12' when cast(strftime('%H', min(result_datetime))as int) <= 12 then cast(cast(strftime('%H', min(result_datetime)) as int) as varchar) else cast(strftime('%H', min(result_datetime))as int)-12 end ||
                    --strftime(':%M ', min(result_datetime)) || case when cast(strftime('%H', min(result_datetime))as int)< 12 then ' AM' else ' PM' end the_date,
                    min(offer_amount) price
                    from Apollo_bulksearchresults ab
                    group by source_search_request_id, ab.for_tag
                    order by 1 DESC
                    LIMIT 100;"""

    with connection.cursor() as cursor:
        cursor.execute(raw_query)
        # Fetch all the results
        results = cursor.fetchall()

    # Process the results if needed
    # For example, convert them to a list of dictionaries:
    processed_results = [{'item': row[1], 'the_date': datetime.strptime(row[2], '%Y-%m-%d %H:%M:%S'), 'price': row[3]} for row in results]

    return render(request, 'house_of_mirrors_results.html', {'results': processed_results})
