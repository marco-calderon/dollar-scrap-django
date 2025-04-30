from dollar_info.el_dolar_info_scrapper import ElDolarInfoScrapper
from .models import Entry
import os
from django.shortcuts import render

# Create your views here.
def scrap(request):
    secret = os.getenv('TOKEN')
    if ('key' in request.GET and request.GET['key'] == secret):
        scrapper = ElDolarInfoScrapper()
        scrap_entry = scrapper.scrap_today()

        entry = Entry()
        entry.buy_price = scrap_entry['buy_price']
        entry.sell_price = scrap_entry['sell_price']
        entry.date = scrap_entry['date']
        entry.save()

        scrapper.close()
        return render(request, 'entries/scrap.html', { 'message': '', 'ok': True, 'entry': entry })
    else:
        return render(request, 'entries/scrap.html', { 'message': 'Invalid key', 'ok': False })