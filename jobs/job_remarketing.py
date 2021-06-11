try:
    import unzip_requirements
except ImportError:
    pass

import os
import csv
import json
import time
from datetime import datetime, timedelta
import pandas as pd

import sentry_sdk
from sentry_sdk import capture_exception
from sentry_sdk.integrations.flask import FlaskIntegration

from common.helpers import Helpers
from common.s3 import S3

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()


def handler(event, context):
    sentry_sdk.init(
        os.getenv('SENTRY_DNS'),
        integrations=[FlaskIntegration()],
        environment=os.getenv('env', 'dev')
    )
    main(event.get('brand'))


def main(brand):
    date = date_today()
    extract_data(brand, date)
    processing_data(brand, date)
    #transform_csv('base_test.csv')
    return True


def extract_data(brand, date):
    logging.info(' DOWNLOADING FILES FROM S3...')
    start = time.time()
    for flow in range(1, 11):
        document = get_document(brand, flow, date)
        path = path_remarketing(brand, flow)
        download_file(path, document, brand)
    end = time.time()
    processing_time = '%0.2f' % (end - start)
    logger.info(' time: {} s'.format(processing_time))


def processing_data(brand, date):
    logging.info(' SENDING FILES TO EMBLUE...')
    start = time.time()
    for flow in range(1, 11):
        document = get_document(brand, flow, date)
        if file_exists(document):
            data = json_load(document)

            if len(data['items']) == 0:
                print('Error: don\'t data exists', document)
                '''environment = os.getenv('env')
                if environment == 'prod':
                    subject = 'RMKT ' + brand.upper() + ' - Error: don\'t data exists ' + document
                    body = subject
                    Helpers().send_mail(subject, body)'''
                continue

            document = generate_csv(data, brand)
            transform_csv(document)
            send_data(brand, document)

            '''
            api_key = os.getenv(brand.upper() + '_CAMPAIGN_API_KEY')
            event_name = data['eventName']

            l = data['items'][:]
            r = 50
            i = 0
            j = r

            while l[i:j]:
                list = data_filter(l[i:j])
                if environment == 'prod':
                    True
                    # response = request_endpoint(api_key, event_name, list, brand)
                    # time.sleep(1)

                i = j
                j += r
            '''
    end = time.time()
    print('time: %0.2f s' % (end - start))


def download_file(path, filename, brand):
    try:
        bucket = os.getenv("BUCKET")
        key = path + filename  # remote
        file_name = '/tmp/' + filename  # local
        S3().downloadFile(bucket, key, file_name)
        print('File downloaded successfully:', filename)
    except Exception as e:
        print('Error: don\'t file exists', filename)
        environment = os.getenv('env')
        if environment == 'prod':
            subject = 'RMKT ' + brand.upper() + ' - Error: don\'t file exists ' + filename
            body = subject + ', ' + str(download_file.__name__)
            Helpers().send_mail(subject, body)


def data_filter(items):
    data = []
    for item in items:
        d = {
            'email': item['email'],
            'attributes': {
                'nombre': item['attributes']['nombre'],
                'pw_pantalla': item['attributes']['pw_pantalla'],
                'suscrito_print': item['attributes']['suscrito_print']
            }
        }
        data.append(d)
    return data


def request_endpoint(api_key, event_name, items, brand):
    environment = os.getenv('env')
    try:
        url = os.getenv('ENDPOINT_EMBLUE_BULK')
        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'Basic ' + api_key
        }
        payload = {
            'eventName': event_name,
            'items': items
        }
        # print(json.dumps(payload, indent=4, sort_keys=False))
        response = Helpers().request(url, headers, payload)

        subject = 'RMKT ' + brand.upper() + ' - ' + str(request_endpoint.__name__)
        subject = subject + ', Error: status_code ' + str(response.status_code)
        if response.status_code != 200:
            content = json.dumps(payload, indent=4, sort_keys=False)
            body = str(content) + ' <br><br> ' + response.text
            if environment == 'prod':
                Helpers().send_mail(subject, body)

    except Exception as e:
        print(str(e))
        capture_exception(e)
        subject = 'RMKT ' + brand.upper() + ' - ' + str(request_endpoint.__name__)
        subject = subject + ', Exception '
        body = str(response.status_code) + '\n\n' + response.text + '\n\n' + str(e)
        if environment == 'prod':
            Helpers().send_mail(subject, body)

    return response.json()


def json_load(filename):
    with open('/tmp/' + filename) as f:
        data = json.load(f)
    # print(json.dumps(data, indent=4, sort_keys=False))
    return data


def json_create(brand, flow, part, event_name, items):
    filename = 'IN_' + brand.upper() + '_RMKT_FLOW_' + str(flow) + '_PART_' + str(part) + '_' + date_today() + '.json'
    data = json_content(event_name, items)
    json_save(filename, data)

    environment = os.getenv('env')
    if environment == 'prod':
        hostname = os.getenv('EMBLUE_FTP_HOST')
        username = os.getenv(brand.upper() + '_CAMPAIGN_ID')
        password = os.getenv(brand.upper() + '_CAMPAIGN_FTP_PASS')
        path = '/tmp/'
        Helpers().transfer_data(hostname, username, password, path, filename)


def json_content(event_name, items):
    content = {
        'eventName': event_name,
        'items': items
    }
    return content


def json_save(filename, data):
    with open('/tmp/' + filename, 'w+') as outfile:
        json.dump(data, outfile)


def generate_csv(data, brand):

    document = data['eventName'] + '.csv'

    csv_data = [
        ['email', 'nombre', 'pw_pantalla', 'suscrito_print']
    ]

    for item in data['items']:
        l = [
            item['email'],
            item['attributes']['nombre'],
            item['attributes']['pw_pantalla'],
            item['attributes']['suscrito_print']
        ]
        csv_data.append(l)

    with open('/tmp/' + document, 'w+') as csvFile:
        writer = csv.writer(csvFile, delimiter=',')
        writer.writerows(csv_data)
    csvFile.close()

    return document


def transform_csv(document):
    # logging.info('PANDAS...')
    df = pd.read_csv('/tmp/' + document, delimiter=',')
    #print(df.head())
    df['suscrito_print'].fillna('null', inplace=True)
    df.drop_duplicates(['email'], keep='first', inplace=True)
    df.sort_values(by=['email'], inplace=True)
    df.to_csv('/tmp/' + document, sep=',', encoding='utf-8', mode='w', index=False)


def send_data(brand, document):
    # logging.info('SYNC FTP...')
    hostname = os.getenv('EMBLUE_FTP_HOST')
    username = os.getenv(brand.upper() + '_CAMPAIGN_ID')
    password = os.getenv(brand.upper() + '_CAMPAIGN_FTP_PASS')
    path = '/tmp/'
    path_remote = '/tmp/'
    environment = os.getenv('env')
    if environment == 'prod':
        path_remote = '/Flows/'
    Helpers().transfer_data(hostname, username, password, path, document, path_remote)


def date_today():
    return datetime.today().strftime('%Y%m%d')


def date_yesterday():
    d = datetime.today() - timedelta(days=1)
    return d.strftime('%Y%m%d')


def path_remarketing(brand, flow):
    return 'campaign_' + brand + '/automation/rmkt/flow/' + str(flow) + '/'


def get_document(brand, flow, date):
    return 'IN_' + brand.upper() + '_RMKT_FLOW_' + str(flow) + '_' + date + '.json'


def file_exists(filename):
    return os.path.isfile('/tmp/' + filename)
