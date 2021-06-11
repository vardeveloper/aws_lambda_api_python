import os
import json
import ftplib
from common.emblue import Emblue
from common.helpers import Helpers
from common.s3 import S3
from datetime import datetime, timedelta


class ServiceEmblue(object):

    def __init__(self):
        pass

    # subscription by form
    def subscription(self, req):
        brand = req.get('brand', None)
        email = req.get('email', None)
        name = req.get('name', '')
        last_name = req.get('last_name', '')

        if brand is None:
            return {'status': False, 'status_code': 400, 'message': 'brand is requerid'}

        if email is None:
            return {'status': False, 'status_code': 400, 'message': 'email is requerid'}

        if Emblue().brand_is_valid(brand) is False:
            return {'status': False, 'status_code': 400, 'message': 'brand ' + brand + ' don\'t exist'}

        # emblue
        if Emblue().brand_in_emblue(brand):
            account = Emblue().get_account_by_brand(brand)
            api_key = Emblue().get_apikey_by_account(account)
            if api_key is None:
                return {'status': False, 'status_code': 400, 'message': 'account ' + account + ' don\'t exist'}
            return self.subscriber_emblue(brand, api_key, email, name, last_name)

        # sendy
        return self.subscriber_sendy(brand, email, name)

    def subscriber_emblue(self, brand, api_key, email, name, last_name):
        try:
            url = os.getenv('ENDPOINT_EMBLUE')
            headers = {
                'Content-Type': 'application/json',
                'Authorization': 'Basic ' + api_key
            }
            payload = {
                'email': email,
                'eventName': 'subscription',
                'attributes': {
                    'name': name,
                    'last_name': last_name
                }
            }
            # print(json.dumps(payload, indent=4, sort_keys=True))
            # quit()
            response = Helpers().request(url, headers, payload)
            subject = 'NEWSLETTER ' + brand.upper() + ' - Error ' + str(self.subscriber_emblue.__name__) + ', status_code ' + str(response.status_code)
            if response.status_code != 200:
                # response.encoding = 'utf-8'
                body = str(payload) + '\n\n' + response.text
                #Helpers().send_mail(subject, body)
                Helpers().telegram_send_message(subject)
                Helpers().telegram_send_message(body)
        except Exception as e:
            Helpers().send_mail(subject + ', Exception ', str(e))
            raise Exception(e)
        return response.json()

    def subscriber_sendy(self, brand, email, name):
        list = os.getenv(brand.upper() + '_LIST')
        url = os.getenv('SENDY_API')
        try:
            data = {
                'email': email,
                'name': name,
                'list': list,
                'boolean': 'true'
            }
            res = Helpers().request_sendy(url, data)
        except Exception as e:
            raise Exception(e)
        return res

    # without use
    def unsubscription(self, req):
        if req.get('brand', None) is None:
            return {'status': False, 'status_code': 400, 'message': 'brand is requerid'}

        if req.get('email', None) is None:
            return {'status': False, 'status_code': 400, 'message': 'email is requerid'}

        brand = req.get('brand')
        api_key = Emblue().get_apikey_by_account(brand)
        email = req.get('email')

        if api_key is None:
            return {'status': False, 'status_code': 400, 'message': 'brand don\'t exist'}

        try:
            url = os.getenv('ENDPOINT_EMBLUE')
            headers = {
                'Content-Type': 'application/json',
                'Authorization': 'Basic ' + api_key
            }
            payload = {
                'email': email,
                'eventName': 'unsubscription'
            }
            response = Helpers().request(url, headers, payload)
        except Exception as e:
            raise Exception(e)

        return response.json()

    def subscription_by_topic(self, req):
        if req.get('brand', None) is None:
            return {'status': False, 'status_code': 400, 'message': 'brand is requerid'}

        if req.get('email', None) is None:
            return {'status': False, 'status_code': 400, 'message': 'email is requerid'}

        if len(req.get('topics')) == 0:
            return {'status': False, 'status_code': 400, 'message': 'topics is requerid'}

        brand = req.get('brand')
        email = req.get('email')
        topics = req.get('topics')

        if Emblue().brand_is_valid(brand) is False:
            return {'status': False, 'status_code': 400, 'message': 'brand ' + brand + ' don\'t exist'}

        account = Emblue().get_account_by_brand(brand)
        api_key = Emblue().get_apikey_by_account(account)
        if api_key is None:
            return {'status': False, 'status_code': 400, 'message': 'account ' + account + ' don\'t exist'}

        data = Emblue().get_bucket_config()
        items = []
        for topic in topics:
            group_id = Emblue().get_groupid_by_topic(data, account, topic)
            if group_id is None:
                return {'status': False, 'status_code': 400, 'message': 'topic ' + topic + ' don\'t exist'}
                break
            d = {
                'email': email,
                'attributes': {
                    'group_id': group_id
                }
            }
            items.append(d)

        try:
            url = os.getenv('ENDPOINT_EMBLUE_BULK')
            headers = {
                'Content-Type': 'application/json',
                'Authorization': 'Basic ' + api_key
            }
            payload = {
                'eventName': 'subscription_by_topic',
                'items': items
            }
            response = Helpers().request(url, headers, payload)

            subject = 'NEWSLETTER ' + brand.upper() + ' - Error ' + str(self.subscription_by_topic.__name__) + ', status_code ' + str(response.status_code)
            if response.status_code != 200:
                body = str(payload) + '\n\n' + response.text
                #Helpers().send_mail(subject, body)
                Helpers().telegram_send_message(subject)
                Helpers().telegram_send_message(body)

        except Exception as e:
            Helpers().send_mail(subject + ', Exception ', str(e))
            raise Exception(e)

        return response.json()

    def unsubscription_by_topic(self, req):
        if req.get('brand', None) is None:
            return {'status': False, 'status_code': 400, 'message': 'brand is requerid'}

        if req.get('email', None) is None:
            return {'status': False, 'status_code': 400, 'message': 'email is requerid'}

        if len(req.get('topics')) == 0:
            return {'status': False, 'status_code': 400, 'message': 'topics is requerid'}

        brand = req.get('brand')
        email = req.get('email')
        topics = req.get('topics')

        if Emblue().brand_is_valid(brand) is False:
            return {'status': False, 'status_code': 400, 'message': 'brand ' + brand + ' don\'t exist'}

        account = Emblue().get_account_by_brand(brand)
        api_key = Emblue().get_apikey_by_account(account)
        if api_key is None:
            return {'status': False, 'status_code': 400, 'message': 'account ' + account + ' don\'t exist'}

        data = Emblue().get_bucket_config()
        items = []
        for topic in topics:
            group_id = Emblue().get_groupid_by_topic(data, account, topic)
            if group_id is None:
                return {'status': False, 'status_code': 400, 'message': 'topic ' + topic + ' don\'t exist'}
                break
            d = {
                'email': email,
                'attributes': {
                    'group_id': group_id
                }
            }
            items.append(d)

        try:
            url = os.getenv('ENDPOINT_EMBLUE_BULK')
            headers = {
                'Content-Type': 'application/json',
                'Authorization': 'Basic ' + api_key
            }
            payload = {
                'eventName': 'unsubscription_by_topic',
                'items': items
            }
            response = Helpers().request(url, headers, payload)

            subject = 'Error ' + str(self.unsubscription_by_topic.__name__) + ', status_code ' + str(response.status_code)
            if response.status_code != 200:
                body = str(payload) + '\n\n' + response.text
                #Helpers().send_mail(subject, body)
                Helpers().telegram_send_message(subject)
                Helpers().telegram_send_message(body)

        except Exception as e:
            Helpers().send_mail(subject + ', Exception ', str(e))
            raise Exception(e)

        return response.json()

    ''' Methods of test '''

    def bucket_file_list(self, req):
        if req.get('brand', None) is None:
            return {'status': False, 'status_code': 400, 'message': 'brand is requerid'}

        brand = req.get('brand')
        if Emblue().brand_is_valid(brand) is False:
            return {'status': False, 'status_code': 400, 'message': 'brand ' + brand + ' don\'t exist'}

        campaign = req.get('campaign')
        flow = req.get('flow')

        try:
            bucket = os.getenv("BUCKET")
            path = 'campaign_' + brand + '/onboarding/quick_campaigner/update/'
            if campaign == 'remarketing':
                path = 'campaign_' + brand + '/automation/rmkt/flow/' + flow + '/'
            response = S3().directory_list_recursive(bucket, path)
            # response = S3().list_objects(bucket, path)
            return response
        except Exception as e:
            raise Exception(e)

    def bucket_file_get(self, req):
        if req.get('brand', None) is None:
            return {'status': False, 'status_code': 400, 'message': 'brand is requerid'}

        brand = req.get('brand')
        if Emblue().brand_is_valid(brand) is False:
            return {'status': False, 'status_code': 400, 'message': 'brand ' + brand + ' don\'t exist'}

        campaign = req.get('campaign')
        flow = req.get('flow')
        date = req.get('date', None)
        if date is None:
            date = self.nomenclature()

        # Onboarding
        path = 'campaign_' + brand + '/onboarding/quick_campaigner/update/'
        filename = 'IN_' + date + '.csv'

        # Remarketing
        if campaign == 'remarketing':
            path = 'campaign_' + brand + '/automation/rmkt/flow/' + flow + '/'
            filename = 'IN_' + brand.upper() + '_RMKT_FLOW_' + flow + '_' + date + '.json'

        try:
            self.download_bucket(path, filename)
            if campaign == 'onboarding':
                document = 'IN_' + brand.upper() + '_' + date + '.csv'
                self.rename_file(filename, document)
                filename = document
            environment = os.getenv('env')
            if environment == 'prod':
                self.transfer_data(brand, filename)
            return True
        except Exception as e:
            raise Exception(e)

    def test_method(self, req):
        print('Test Telegram send message')
        try:
            response = Helpers().telegram_send_message('Hola desde Emblue API')
            print(response)
            return response

        except Exception as e:
            raise Exception(e)

    def nomenclature(self):
        today = datetime.today()
        date = today.strftime('%Y%m%d')  # ('%Y-%m-%d %H:%M:%S')
        return date

    def yesterday(self):
        d = datetime.today() - timedelta(days=1)
        return d.strftime('%Y%m%d')

    def path_update(self):
        return 'campaign_gestion/onboarding/quick_campaigner/update/'

    def download_bucket(self, path, filename):
        try:
            bucket = os.getenv("BUCKET")
            key = path + filename  # remote
            file_name = '/tmp/' + filename  # local
            S3().downloadFile(bucket, key, file_name)
            print('File downloaded successfully:', filename)
            return True
        except Exception as e:
            # capture_exception(e)
            print('[' + self.download_bucket.__name__ + '] ' + str(e))
            print('don\'t file exists: ' + filename)
            return False

    def transfer_data(self, brand, filename):
        try:
            hostname = os.getenv('EMBLUE_FTP_HOST')
            username = os.getenv(brand.upper() + '_CAMPAIGN_ID')
            password = os.getenv(brand.upper() + '_CAMPAIGN_FTP_PASS')
            path = '/tmp/'
            path_remote = '/tmp/'
            Helpers().transfer_data(hostname, username, password, path, filename, path_remote)
            return True
        except Exception as e:
            # capture_exception(e)
            print('[' + self.transfer_data.__name__ + '] ' + str(e))
            print('Error method transfer_data: ' + filename)
            return False

    def rename_file(self, original, new):
        print('Renamed file:', new)
        os.rename('/tmp/' + original, '/tmp/' + new)