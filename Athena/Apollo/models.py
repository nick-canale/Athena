from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class League(models.Model):
    league_id = models.CharField(max_length=200)
    league_realm = models.CharField(max_length=200)
    league_text = models.CharField(max_length=200)
    def __str__(self):
        return self.league_text
    
class Static(models.Model):
    static_type_id = models.CharField(max_length=200,null=True)
    static_type_label = models.CharField(max_length=200,null=True)
    static_id = models.CharField(max_length=200,null=True)
    static_text = models.CharField(max_length=200,null=True)
    static_image_url = models.CharField(max_length=2000,null=True)
    def __str__(self):
        return self.static_type_label + self.static_text
    
class SearchStats(models.Model):
    search_stat_id = models.CharField(max_length=200)
    search_stat_label = models.CharField(max_length=200)
    stat_id = models.CharField(max_length=200)
    stat_text = models.CharField(max_length=200)
    stat_type = models.CharField(max_length=200)
    def __str__(self):
        return self.search_stat_label + self.stat_text
    
class Items(models.Model):
    item_type_id = models.CharField(max_length=200)
    item_type_label = models.CharField(max_length=200,null=True)
    item_name = models.CharField(max_length=200,null=True)
    item_type = models.CharField(max_length=200,null=True)
    item_text = models.CharField(max_length=200,null=True)
    item_json_flags = models.CharField(max_length=200,null=True)
    def __str__(self):
        return self.text
    
class SearchesJson(models.Model):
    search_url = models.CharField(max_length=2000)
    search_json = models.TextField()
    response_json = models.TextField()
    search_datetime = models.DateTimeField()
    def __str__(self):
        return self.search_url
    
class SearchResultsJson(models.Model):
    result_url = models.TextField()
    response_json = models.TextField()
    result_datetime = models.DateTimeField()
    search = models.ForeignKey(SearchesJson, on_delete=models.CASCADE)
    def __str__(self):
        return self.result_url
    
class ItemSearchDetails(models.Model):
    item_name = models.CharField(max_length=400)
    search_datetime = models.DateTimeField()
    price_type = models.CharField(max_length=200)
    currency = models.CharField(max_length=200)
    amount = models.DecimalField(decimal_places=2, max_digits=18)
    price_rank = models.IntegerField()
    account_name = models.CharField(max_length=200)
    source_search_result = models.ForeignKey(SearchResultsJson, on_delete=models.CASCADE)
    def __str__(self):
        return self.item_name
    
class ItemTags(models.Model):
    item_type = models.CharField(max_length=400)
    item_name = models.CharField(max_length=400)
    image_url = models.TextField()
    item_tag = models.CharField(max_length=400)
    def __str__(self):
        return self.item_name
    
class BulkSearchRequests(models.Model):
    want = models.TextField()
    have = models.TextField()
    request_datetime = models.DateTimeField()
    def __str__(self):
        return self.want + ' for ' + self.have
    
class BulkSearchResults(models.Model):
    result_datetime = models.DateTimeField(null=True)
    account_name = models.CharField(max_length=400)
    last_character_name = models.CharField(max_length=400)
    offer_tag = models.CharField(max_length=200)
    offer_amount = models.DecimalField(decimal_places=2, max_digits=18)
    for_tag = models.CharField(max_length=200)
    for_amount = models.IntegerField()
    for_stock = models.IntegerField()
    whisper = models.TextField()
    source_search_request = models.ForeignKey(BulkSearchRequests, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return self.offer_tag + ' for ' + self.for_tag