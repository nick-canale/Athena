import datetime
from django.shortcuts import render
from .models import League
from .models import Static
from .models import SearchStats
from .models import Items
from .models import SearchesJson
from .models import SearchResultsJson
from .models import BulkSearchRequests
from .models import BulkSearchResults
import requests
import json
import copy

# Create your views here.
from django.http import HttpResponse

header = {
    'User-Agent': 'npikes@gmail.com'
}

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

def f_data_refresh(model, url):
    for l in model.objects.all():
        l.delete()
    response = requests.get(url, headers=header)
    data = json.loads(response.content)['result']
    if model._meta.object_name == 'League':
        for l in data:
            model.objects.create(league_id=l['id'],league_realm=l['realm'],league_text=l['text'])
    elif model._meta.object_name == 'Static':
        for l in data:
            id = l['id']
            label = l['label']
            for e in l['entries']:
                model.objects.create(static_type_id=id,
                                     static_type_label=label,
                                     static_id=e['id'],
                                     static_text=e.get('text'),
                                     static_image_url=e.get('image'))
    elif model._meta.object_name == 'SearchStats':
        for l in data:
            id = l['id']
            label = l['label']
            for e in l['entries']:
                model.objects.create(search_stat_id=id,
                                     search_stat_label=label,
                                     stat_id=e['id'],
                                     stat_text=e['text'],
                                     stat_type=e['type'])
    elif model._meta.object_name == 'Items':
        for l in data:
            id = l['id']
            label = l['label']
            for e in l['entries']:
                model.objects.create(item_type_id=id,
                                     item_type_label=label,
                                     item_name=e.get('name'),
                                     item_type=e.get('type'),
                                     item_text=e.get('text'),
                                     item_json_flags=e.get('flags'))

def search_trade_for_item(request,name,type):
    url = 'https://www.pathofexile.com/api/trade/search/Crucible'
    
    data = {
            "query": {
                "status": {
                    "option": "online"
                },
                "name": name,#e.g. The Pariah
                "type": type,#e.g. Unset Ring
                "stats": [{
                        "type": "and",
                        "filters": []
                    }]
                },
                "sort": {
                    "price": "asc"
                }
            }
    data_string = json.dumps(data)
    json_header = copy.copy(header)
    json_header['Content-Type'] = 'application/json'
    response = requests.post(url=url, data=data_string, headers=json_header)
    # Check the response status code
    if response.status_code == 200:
        search = SearchesJson.objects.create(search_url=url,search_json=data,response_json=response.text,search_date=datetime.datetime.now())
        resp = json.loads(response.text)
        url = f'https://www.pathofexile.com/api/trade/fetch/{",".join(resp["result"][:10])}?query={resp["id"]}'
        response = requests.get(url=url, headers=header)
        if response.status_code == 200:
            result = SearchResultsJson.objects.create(result_url=url,response_json=response.text,result_date=datetime.datetime.now(),search=search)
            return HttpResponse('POST request was successful! Response:' + result.response_json)
        else:
            return HttpResponse('POST request failed with status code:' + str(response.status_code))
    else:
        return HttpResponse('POST request failed with status code:' + str(response.status_code) + ' - ' + str(response.text))
    
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

def f_bulk_exchange(want,have):
    url = 'http://www.pathofexile.com/api/trade/exchange/Crucible'
    
    data = {
                "exchange": {
                    "want": [
                    want
                    ],
                    "have": [
                    have
                    ],
                    "status": "online"
                }
            }    
    data_string = json.dumps(data)
    json_header = copy.copy(header)
    json_header['Content-Type'] = 'application/json'
    request = BulkSearchRequests.objects.create(want=want,have=have,request_datetime=datetime.datetime.now())
    response = requests.post(url=url, data=data_string, headers=json_header)
    if response.status_code == 200:
        for r in json.loads(response.content)['result']:
            result = json.loads(response.content)['result'][r]
            bulk_search_result = BulkSearchResults.objects.create(result_datetime=datetime.datetime.now(), 
                                             account_name=result['listing']['account']['name'],
                                             last_character_name=result['listing']['account']['lastCharacterName'],
                                             offer_tag=result['listing']['offers'][0]['exchange']['currency'],
                                             offer_amount=result['listing']['offers'][0]['exchange']['amount'],
                                             for_tag=result['listing']['offers'][0]['item']['currency'],
                                             for_amount=result['listing']['offers'][0]['item']['amount'],
                                             for_stock=result['listing']['offers'][0]['item']['stock'],
                                             whisper=result['listing']['whisper'].format(result['listing']['offers'][0]['item']['whisper'].format(result['listing']['offers'][0]['item']['amount']),
                                                                                         result['listing']['offers'][0]['exchange']['whisper'].format(result['listing']['offers'][0]['exchange']['amount'])),
                                             source_search_request=request)
    else:
        raise ValueError("GGG did not like your query")


def refresh_every_5m(request, want, have):
    return render(request, 'refresh_every_5m.html', {'want': want, 'have': have})