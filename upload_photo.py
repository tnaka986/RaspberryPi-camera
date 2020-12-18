#使用モジュール読み込み
import subprocess, os, sys, re
from datetime import datetime
import time
import json
import boto3
import shutil

#変数定義
now = datetime.now()
dir_name = now.strftime('%Y%m')
dir_path = '/home/pi/camera/tmp/' + dir_name + '/'
file_name= now.strftime('%d%H%M') + '.jpg'

#撮影したファイルをfnameとして保存
def camera():
    fname    = dir_path + file_name
    try:
        os.mkdir(dir_path)
    except OSError:
        print('Date dir already exists')
    os.system('raspistill -vf -hf -fp -t 1 -w 800 -h 600 -o ' + fname)
    return fname 

#保存した写真をS3にアップロード
def s3(fname):
    bucket_name = "pi-photo-piyo"
    s3 = boto3.resource('s3')
    s3_file_path = dir_name + '/' + dir_name + file_name 
    s3.Bucket(bucket_name).upload_file(fname, s3_file_path)

#保存した写真を削除
def delete():
    shutil.rmtree('/home/pi/camera/tmp/')
    os.mkdir('/home/pi/camera/tmp/')

#メイン処理
def main(image=""):
    if image == "":
        fname = camera()
    else:
        fname = image
    if fname:
      s3(fname)
      delete()       

if name == 'main':
    main() 