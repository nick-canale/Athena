import datetime
import requests
import json
import copy
from django.http import HttpResponse
from .models import SearchesJson
from .models import SearchResultsJson
from .models import BulkSearchRequests
from .models import BulkSearchResults

header = {
    'User-Agent': 'npikes@gmail.com'
}

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
                

def f_search_trade_for_item(name,type,searches_json):
    url = 'https://www.pathofexile.com/api/trade/search/Ancestor'
    
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
        search = searches_json.objects.create(search_url=url,search_json=data,response_json=response.text,search_date=datetime.datetime.now())
        resp = json.loads(response.text)
        url = f'https://www.pathofexile.com/api/trade/fetch/{",".join(resp["result"][:10])}?query={resp["id"]}'
        response = requests.get(url=url, headers=header)
        if response.status_code == 200:
            result = searches_json.objects.create(result_url=url,response_json=response.text,result_date=datetime.datetime.now(),search=search)
            return HttpResponse('POST request was successful! Response:' + result.response_json)
        else:
            return HttpResponse('POST request failed with status code:' + str(response.status_code))
    else:
        return HttpResponse('POST request failed with status code:' + str(response.status_code) + ' - ' + str(response.text))
    
def f_bulk_exchange(want,have):
    url = 'http://www.pathofexile.com/api/trade/exchange/Ancestor'
    
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
            BulkSearchResults.objects.create(result_datetime=datetime.datetime.now(), 
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
        raise ValueError(f"GGG did not like your query, error code {str(response.status_code)}, header {json_header}, data {data_string}, url {url}")