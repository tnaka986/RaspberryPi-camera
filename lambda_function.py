from future import print_function
import urllib.parse
import boto3
from decimal import Decimal
import json
import urllib
from datetime import datetime
import random
import subprocess
import requests

print('Loading function')

rekognition = boto3.client('rekognition')
s3 = boto3.resource('s3')

#----関数----
#Rekognitionで画像解析する
def detect_labels(bucket, key):
    response = rekognition.detect_labels(Image={"S3Object": {"Bucket": bucket, "Name": key}})
    return response

#LINEへファイルとメッセージを通知する
def line(image, message):
   url = "https://notify-api.line.me/api/notify"
   token = ""
   headers = {"Authorization" : "Bearer "+ token}
   payload = {"message" :  message}
   files = {"imageFile": open(image, "rb")}
   r = requests.post(url, headers = headers, params=payload, files=files)
   print(r.text) 

#----メイン処理----
def lambda_handler(event, context):
    #トリガーからオブジェクト（撮影した写真）を取得
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'], encoding='utf8')
    file_path = '/tmp/' + datetime.now().strftime('%Y-%m-%d-%H-%M-%S-') + str(random.randint(0,999999))

    try:
        #撮影した写真をRekognitionで解析
        response = detect_labels(bucket, key)
        #解析結果をコンソールに表示
        print(response)
        #撮影した写真を取得
        bucket = s3.Bucket(bucket)
        bucket.download_file(key, file_path)
        print(subprocess.run(["ls", "-l", "/tmp"], stdout=subprocess.PIPE))
        for label in response['Labels']:
            #print(label['Name'])
            conf_most = ''
            if label['Name'] == 'Bird':
                for index,ins in enumerate(label['Instances']):
                    if index == 0:
                        width_most = ins['BoundingBox']['Width']
                        height_most = ins['BoundingBox']['Height']
                        conf_most = ins['Confidence']
                    else:
                        if ins['Confidence'] > conf_most:
                            width_most = ins['BoundingBox']['Width']
                            height_most = ins['BoundingBox']['Height']
                            conf_most = ins['Confidence']
                if width_most < 0.24:                     
                    message = 'いつもの位置かな？(スコア:{}点)'.format(int(conf_most))  p
                    pint(message)
                elif conf_most >= 98:
                    message = 'ベストショット!(スコア:{}点)'.format(int(conf_most))
                    print(message)
                elif conf_most >= 95:
                    message = 'ナイスショット!(スコア:{}点)'.format(int(conf_most))
                    print(message)
                else:
                    message = '写真を撮りました！(スコア:{}点)'.format(int(conf_most))
                    print(message)
                break
        if not conf_most:
            message = 'ぴよちゃんどこかな～？'
            print(message)
        line(file_path, message)
        return response
    except Exception as e:
        print(e)
        print("Error processing object {} from bucket {}. ".format(key, bucket) +
              "Make sure your object and bucket exist and your bucket is in the same region as this function.")
        raise e