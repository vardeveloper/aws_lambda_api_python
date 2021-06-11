import os
import json
from common.s3 import S3


class Emblue(object):

    def __init__(self):
        pass

    @staticmethod
    def brand_is_valid(brand):
        diaries = ['gestion', 'comercio', 'elcomercio', 'peru21', 'trome', 'depor', 'correo']
        if brand in diaries:
            return True
        return False

    @staticmethod
    def brand_in_emblue(brand):
        diaries = ['gestion', 'comercio', 'elcomercio']
        if brand in diaries:
            return True
        return False

    @staticmethod
    def get_account_by_brand(brand):
        if brand == 'elcomercio':
            brand = 'comercio'
        return brand + '_newsletter'

    @staticmethod
    def get_apikey_by_account(account):
        return {
            os.getenv('GESTION_NEWSLETTER_CODE'): os.getenv('GESTION_NEWSLETTER_API_KEY'),
            os.getenv('COMERCIO_NEWSLETTER_CODE'): os.getenv('COMERCIO_NEWSLETTER_API_KEY'),
        }.get(account)

    @staticmethod
    def get_bucket_config():
        try:
            # s3
            '''bucket = os.getenv('BUCKET')
            key = "config/topics.json"
            obj = S3().getObject(bucket, key)
            data = json.loads(obj['Body'].read().decode('utf-8'))'''

            # local
            with open('./topics.json', 'r') as f:
                data = json.load(f)

            return data
        except Exception as e:
            raise Exception(e)

    @staticmethod
    def get_groupid_by_topic(data, brand, topic):
        try:
            group_id = None
            for account in data['accounts']:
                if brand in account:
                    if len(account[brand]):
                        for group in account[brand]['groups']:
                            if group['code'] == topic:
                                group_id = group['id']
                                break
            return group_id
        except Exception as e:
            raise Exception(e)
