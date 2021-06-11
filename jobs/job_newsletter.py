try:
    import unzip_requirements
except ImportError:
    pass

import os
import json
import logging


logging.basicConfig(level=logging.INFO)

from common.s3 import S3
from common.emblue import Emblue
from common.helpers import Helpers

logger = logging.getLogger(__name__)


def handler(event, context):
    main(event.get('brand'), event.get('group'), event.get('newsletter'))


def main(brand, group, newsletter):
    logger.info('Generate files for the service Quick Campigner of Emblue for brand: {}, newsletter: {} and group: {} '.format(brand, newsletter, group))
    
    xml = get_config_xml(brand, group)
    filename = nomenclature(brand, group)
    content = get_content_service(brand, newsletter)
    subject = get_subject(group, content['asunto'])

    # quit()
    generate_csv(filename)
    generate_xml(filename, xml, subject)
    generate_html(filename, content['html'])
    generate_zip(filename)
    upload_file_to_s3(brand, filename)
    sending_file_to_emblue(brand, filename)


def get_config_xml(brand, group):
    with open('./config_xml.json', 'r') as f:
        data = json.load(f)
    return data[brand][group]


def datetime_today():
    from datetime import datetime
    import pytz
    tz = pytz.timezone('America/Lima')
    return datetime.today().astimezone(tz)


def today():
    return datetime_today().strftime('%Y%m%d')


def hour():
    return datetime_today().strftime('%H%M')


def nomenclature(brand, group):
    return 'IN_' + brand.upper() + '_' + group.upper() + '_' + today() + '_' + hour() + 'HS'


def get_content_service(brand, newsletter):
    url = 'http://newsletter.minoticia.pe/newsletter/elcomercio/service_topic/' + newsletter
    if brand == 'gestion':
        url = 'http://newsletter.minoticia.pe/newsletter/gestion/service_topic/' + newsletter
    print(url)

    import requests
    response = requests.get(url=url)
    content = response.json()

    if not "html" in content.keys():
        print('data of service is empty')
        subject = 'Newsletter ' + brand + ' - ' + str(get_content_service.__name__)
        Helpers().send_mail(subject, str('data of service is empty'))
        quit()

    return content


def get_subject(group, subject):
    if group == 'test':
        return 'Test - ' + subject
    return subject


def get_key(brand, filename):
    key = os.path.join(
        'newsletter_' + brand,
        today(),
        filename + '.zip'
    )
    return key


def generate_csv(filename):
    logging.info('GENERATE CSV...')
    import csv

    csv_data = [['email', 'nombre']]
    l = ['soporte.prensapopular@ec.pe', 'Prensa Popular']
    csv_data.append(l)

    with open('/tmp/' + filename + '.csv', 'w', newline='') as csvFile:
        writer = csv.writer(csvFile, delimiter=';')
        writer.writerows(csv_data)
    csvFile.close()


def generate_xml(filename, xml, subject):
    logging.info('GENERATE XML...')
    import xml.etree.ElementTree as ET
    root = ET.Element("ArchivoXML")
    ET.SubElement(root, "Email").text = xml['Email']
    ET.SubElement(root, "Confirm").text = xml['Confirm']
    ET.SubElement(root, "Return").text = xml['Return']
    ET.SubElement(root, "Detail").text = xml['Detail']
    ET.SubElement(root, "SenderId").text = xml['SenderId']
    ET.SubElement(root, "Campaign").text = xml['Campaign']
    ET.SubElement(root, "Group").text = xml['Group']
    ET.SubElement(root, "Action").text = xml['Action']
    ET.SubElement(root, "Subject").text = subject
    tree = ET.ElementTree(root)
    tree.write('/tmp/' + filename + '.xml', encoding='utf-8', xml_declaration=True)


def generate_html(filename, html):
    logging.info('GENERATE HTML...')
    with open('/tmp/' + filename + '.html', 'w+') as f:
        f.write(html)


def generate_zip(filename):
    logging.info('GENERATE ZIP...')
    import zipfile

    zf = zipfile.ZipFile('/tmp/' + filename + '.zip', mode='w')
    try:
        zf.write('/tmp/' + filename + '.csv', filename + '.csv')
        zf.write('/tmp/' + filename + '.xml', filename + '.xml')
        zf.write('/tmp/' + filename + '.html', filename + '.html')
    finally:
        zf.close()

    # print(zf.infolist())
    print(zf.namelist())


def upload_file_to_s3(brand, filename):
    logging.info('SENDING ZIP TO S3...')
    try:
        bucket = os.getenv("BUCKET")
        key = get_key(brand, filename)  # path
        print(key)
        file_name = '/tmp/' + filename + '.zip'  # filename
        S3().upload_file(bucket, key, file_name)
        print('File uploaded successfully:', filename + '.zip')
    except Exception as e:
        print('[' + upload_file_to_s3.__name__ + '] ' + str(e))


def sending_file_to_emblue(brand, filename):
    logging.info('SENDING ZIP TO EMBLUE...')
    hostname = os.getenv('EMBLUE_FTP_HOST')
    username = os.getenv(brand.upper() + '_NEWSLETTER_ID')
    password = os.getenv(brand.upper() + '_NEWSLETTER_FTP_PASS')
    path = '/tmp/'
    path_remote = '/tmp/'
    environment = os.getenv('env')
    if environment == 'prod':
        path_remote = '/'
    Helpers().transfer_data(hostname, username, password, path, filename + '.zip', path_remote)
