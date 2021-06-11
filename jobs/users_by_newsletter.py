try:
    import unzip_requirements
except ImportError:
    pass

import os
import csv
import json
import pandas as pd

from common.emblue import Emblue
from common.helpers import Helpers
from models.preference import Preference

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


''' generates a csv list of users by newsletter for the quick flow service '''
def handler(event, context):
    main(event.get('brand'), event.get('group'))


def main(brand, group):
    logger.info('Loading preferences of user by brand {} into DB'.format(brand))
    preferences = Preference()
    data = preferences.get_rows_by_brand(brand=brand)
    # print(json.dumps(data, indent=4, sort_keys=False))
    document = generate_csv(brand, data, group)
    transform_data(document)

    environment = os.getenv('env')
    if environment == 'prod':
        sending_file_to_emblue(brand, document)


def generate_csv(brand, data, group):
    logging.info('GENERATE CSV...')
    environment = os.getenv('env')
    document = environment + '_' + brand + '_users_by_' + group + '_newsletter.csv'
    config = Emblue().get_bucket_config()
    account = Emblue().get_account_by_brand(brand)
    
    csv_data = [
        ['email', 'group_id']
    ]

    for item in data:
        if len(item['attributes']['preferences']) == 0:
            continue

        for group_name in item['attributes']['preferences']:
            if group_name == group:
                group_id = Emblue().get_groupid_by_topic(config, account, group_name)
                l = [
                    item['email'],
                    group_id,
                ]
                csv_data.append(l)
                break

    with open('/tmp/' + document, 'w+') as csvFile:
        writer = csv.writer(csvFile, delimiter=',')
        writer.writerows(csv_data)
    csvFile.close()

    return document


def transform_data(document):
    logging.info('PANDAS...')
    df = pd.read_csv('/tmp/' + document, delimiter=',')
    df.sort_values(by=['email'], inplace=True)
    df.dropna(subset=['email'], inplace=True)
    # print(df.head())
    # missing_data = df['email'].isna().sum()
    # print(missing_data)
    df.to_csv('/tmp/' + document, sep=',', encoding='utf-8', mode='w', index=False)


def sending_file_to_emblue(brand, document):
    logging.info('SENDING FILE TO EMBLUE...')
    hostname = os.getenv('EMBLUE_FTP_HOST')
    username = os.getenv(brand.upper() + '_NEWSLETTER_ID')
    password = os.getenv(brand.upper() + '_NEWSLETTER_FTP_PASS')
    path = '/tmp/'
    path_remote = '/data/'
    Helpers().transfer_data(hostname, username, password, path, document, path_remote)
