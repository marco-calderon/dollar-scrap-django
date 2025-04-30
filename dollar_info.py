import click
import logging
import os
from dollar_info.db import UnitOfWork
from dollar_info.el_dolar_info_scrapper import ElDolarInfoScrapper
from datetime import datetime, timedelta
import django

# Configure Django for using models outside app.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "dollar_charts.settings")
django.setup()


LOG_DIR = 'logs'


# Configuration to save the logs into a file
if not os.path.isdir(LOG_DIR):
    os.mkdir(LOG_DIR)
logging.basicConfig(filename='{0}/{1}.log'.format(LOG_DIR, datetime.now().strftime('%Y%m%d_%H%M')), level=logging.DEBUG)

# uow = UnitOfWork()

@click.group()
def main():
    pass


@main.command('initdb')
def initdb():
    # uow.db.init()
    pass
    

@main.command('createschema')
def createschema():
    # uow.db.sample_data()
    pass


@main.command('history')
def history():
    from dollar_charts_webapp.models import Entry

    logging.info('Beginning scraping from history...')
    print('Beginning scraping from history...')

    scrapper = ElDolarInfoScrapper()

    for h in scrapper.scrap_history():
        entry = Entry(date=h['date'], buy_price=h['buy_price'], sell_price=h['sell_price'])
        entry.save()
        logging.info('Saved entry with id {0} ({1})'.format(entry.id, str(entry)))
        print('Saved entry with id {0} ({1})'.format(entry.id, str(entry)))
    
    scrapper.close()


@main.command('scrap_today')
def scrap_today():
    logging.info('Scrapping todays record...')
    scrapper = ElDolarInfoScrapper()
    entry = scrapper.scrap_today()
    scrapper.close()
    print(entry)


@main.group('database')
def database():
    pass


@database.command('dumps')
@click.option('--format', '-f')
@click.option('--output', '-o')
def dumps(format, output):
    from dollar_charts_webapp.models import Entry

    entries = list(Entry.objects.all().order_by('date'))
    if format == 'csv':
        with open(output, 'w') as f:
            f.write('id,date,buy_price,sell_price\n')
            for entry in entries:
                f.write('{0},{1},{2:.4f},{3:.4f}\n'.format(entry.id, entry.date, entry.buy_price, entry.sell_price))
    else:
        print('Invalid format. Possible values are [csv]')


@database.command('get_latest')
def get_latest():
    from dollar_charts_webapp.models import Entry

    entries = list(Entry.objects.all().order_by('date'))
    print(entries[0])


@database.command('get_first')
def get_latest():
    from dollar_charts_webapp.models import Entry

    entries = list(Entry.objects.all().order_by('-date'))
    print(entries[0])


@database.command('update_today')
def update():
    from dollar_charts_webapp.models import Entry

    logging.info('Updating today dollar price...')
    start_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    end_date = start_date + timedelta(hours=23, minutes=59)
    logging.debug('start_date used: {0}'.format(start_date.isoformat()))
    
    scrapper = ElDolarInfoScrapper()
    today_record = scrapper.scrap_today()
    scrapper.close()

    current_entry = Entry.objects.filter(date__gte=start_date, date__lte=end_date).first()
    
    if today_record is None:
        logging.error('Today record not found on website!')
        print('Today record not found on website!')
        return

    if current_entry is not None:
        logging.info('Entry for today exists. Updating with website values...')
        print('Entry for today exists. Updating with website values...')
        logging.debug(today_record)
        print(today_record)
        logging.debug(current_entry)
        print(current_entry)
        current_entry.buy_price = today_record['buy_price']
        current_entry.sell_price = today_record['sell_price']
        current_entry.save()
    else:
        logging.info('Entry for today does not exist on database. Creating with website values...')
        print('Entry for today does not exist on database. Creating with website values...')
        logging.debug(today_record)
        print(today_record)
        current_entry = Entry(
            date=start_date,
            buy_price=today_record['buy_price'],
            sell_price=today_record['sell_price']
        )
        current_entry.save()


@database.command('delete')
@click.option('--id', '-i')
def delete(id):
    from dollar_charts_webapp.models import Entry

    entry = Entry.objects.filter(id=id)
    if entry is not None:
        entry.delete()
    else:
        print('Entry not found.')


if __name__ == "__main__":
    main()