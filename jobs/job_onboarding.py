try:
    import unzip_requirements
except ImportError:
    pass

import os
from datetime import datetime

from common.s3 import S3
from common.helpers import Helpers


def handler(event, context):
    main(event.get('brand'))
    main('elcomercio')


def main(brand):
    filename = 'IN_' + date_today() + '.csv'
    download_file(path_onboarding(brand), filename, brand)
    if file_exists(filename):
        sending_file_to_emblue(brand, filename)


def date_today():
    return datetime.today().strftime('%Y%m%d')


def path_onboarding(brand):
    return 'campaign_' + brand + '/onboarding/quick_campaigner/update/'


def download_file(path, filename, brand):
    try:
        bucket = os.getenv("BUCKET")
        key = path + filename  # remote
        file_name = '/tmp/' + filename  # local
        S3().downloadFile(bucket, key, file_name)
        print('File downloaded successfully:', filename)
    except Exception as e:
        # print('[' + download_bucket.__name__ + '] ' + str(e))
        print('Error: don\'t file exists', filename)
        subject = 'Onboarding ' + brand + ' - ' + str(download_file.__name__)
        Helpers().send_mail(subject, str(e))


def file_exists(filename):
    return os.path.isfile('/tmp/' + filename)


def rename_file(original, new):
    print('Renamed file:', new)
    os.rename('/tmp/' + original, '/tmp/' + new)


def sending_file_to_emblue(brand, filename):
    hostname = os.getenv('EMBLUE_FTP_HOST')
    username = os.getenv(brand.upper() + '_CAMPAIGN_ID')
    password = os.getenv(brand.upper() + '_CAMPAIGN_FTP_PASS')
    path = '/tmp/'
    document = 'IN_' + brand.upper() + '_' + date_today() + '.csv'
    rename_file(filename, document)
    environment = os.getenv('env')
    if environment == 'prod':
        Helpers().transfer_data(hostname, username, password, path, document)


def create_file_config_xml():
    import xml.etree.ElementTree as ET

    root = ET.Element("ArchivoXML")
    ET.SubElement(root, "Email").text = "soporte.prensapopular@ec.pe"
    ET.SubElement(root, "Group").text = "OFF"
    ET.SubElement(root, "Action").text = "OFF"

    filename = 'IN_UPDATED_' + date_today() + '.xml'
    tree = ET.ElementTree(root)
    tree.write('/tmp/' + filename)
    return filename
