import boto3
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)


class S3(object):
    config = None
    s3_client = None

    def __init__(self):
        self.s3_client = boto3.client('s3')

    def getObject(self, b, k):
        message = {"status": True, "menssage": ""}
        try:
            response = self.s3_client.get_object(Bucket=b, Key=k)
            return response
        except Exception as e:
            raise Exception("Error al leer el archivo {0}".format(e))

    def uploadFile(self, data, bucket, key, contentType):
        try:
            r = self.s3_client.put_object(Bucket=bucket,
                                          Key=key,
                                          Body=data,
                                          ContentType=contentType,
                                          CacheControl='max-age=300')
            return r
        except Exception as e:
            raise Exception("Error upload file to s3".format(e))

    def downloadFile(self, bucket, key, file_name):
        try:
            response = self.s3_client.download_file(Bucket=bucket, Key=key, Filename=file_name)
            return response
        except Exception as e:
            raise Exception("Error download file from s3".format(e))

    def list_objects(self, bucket, prefix):
        try:
            response = self.s3_client.list_objects(Bucket=bucket, Prefix=prefix)
            return response
        except Exception as e:
            raise Exception("Error method list objects from s3".format(e))

    def getBucketSite(self, bucket):
        message = {"status": True, "menssage": "", "data": ""}
        try:
            response = self.s3_client.get_bucket_website(
                Bucket=bucket
            )
            return response
        except Exception as e:
            return {"Error": str(e), "msj": str(e)}

    def getUrlS3(self, bucket, key):
        url = self.s3_client.generate_presigned_url(ClientMethod='get_object', Params={'Bucket': bucket, 'Key': key})
        return url.split('?')[0]

    def getUrl(self, bucket, key):
        url = '{0}/{1}/{2}'.format('https://s3.amazonaws.com', bucket, key)
        return url

    def directory_list_recursive(self, bucket, prefix):
        result = self.s3_client.list_objects_v2(Bucket=bucket, Prefix=prefix, Delimiter='/')
        keys = {}

        if result and result.get('Contents'):
            keys = {r['Key']: 1 for r in result['Contents']}

        if result and result.get('CommonPrefixes'):
            keys2 = {r['Prefix']: 1 for r in result['CommonPrefixes']}
            keys.update(keys2)

        if not keys: return keys
        newkeys = keys.copy()

        for key in keys:
            if key.endswith('/'):
                del newkeys[key]
                sublist = self.directory_list_recursive(key, bucket)
                for s in sublist:
                    newkeys[s] = 1

        return newkeys

    def upload_file(self, bucket, key, file_name):
        try:
            response = self.s3_client.upload_file(Bucket=bucket, Key=key, Filename=file_name)
            return response
        except Exception as e:
            raise Exception("Error upload file from s3".format(e))
