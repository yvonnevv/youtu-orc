import base64, hashlib, json, cv2, random, string, time
from urllib import parse, request
from config import APP_ID
from config import API_KEY
from config import ratio
from frame import getPicFrameMain
import time
import os
 
def GetAccessToken(formdata, app_key):
    '''
    获取签名
    :param formdata:请求参数键值对
    :param app_key:应用秘钥
    :return:返回接口调用签名
    '''
    dic = sorted(formdata.items(), key=lambda d: d[0])
    sign = parse.urlencode(dic) + '&app_key=' + app_key
    m = hashlib.md5()
    m.update(sign.encode('utf8'))
    return m.hexdigest().upper()
 
 
def RecogniseGeneral(app_id, time_stamp, nonce_str, image, app_key):
    '''
    腾讯OCR通用接口
    :param app_id:应用标识，正整数
    :param time_stamp:请求时间戳（单位秒），正整数
    :param nonce_str: 随机字符串，非空且长度上限32字节
    :param image:原始图片的base64编码
    :return:
    '''
    host = 'https://api.ai.qq.com/fcgi-bin/ocr/ocr_generalocr'
    formdata = {'app_id': app_id, 'time_stamp': time_stamp, 'nonce_str': nonce_str, 'image': image}
    app_key = app_key
    sign = GetAccessToken(formdata=formdata, app_key=app_key)
    formdata['sign'] = sign
    req = request.Request(method='POST', url=host, data=parse.urlencode(formdata).encode('utf8'))
    response = request.urlopen(req)
    if (response.status == 200):
        json_str = response.read().decode()
        # print(json_str)
        jobj = json.loads(json_str)
        datas = jobj['data']['item_list']
        recognise = {}
        for obj in datas:
            recognise[obj['itemstring']] = obj
        return recognise
 
 
def Recognise(img_path):
    with open(file=img_path, mode='rb') as file:
        base64_data = base64.b64encode(file.read())
    nonce = ''.join(random.sample(string.digits + string.ascii_letters, 32))
    stamp = int(time.time())
    recognise = RecogniseGeneral(app_id=APP_ID, time_stamp=stamp, nonce_str=nonce, image=base64_data,
                                 app_key=API_KEY) # 替换成自己的app_id,app_key
    filterItems = []
    return recognise

def RecogniseAll():
    outputDir, frameOutputDir = getPicFrameMain()
    
    start = int(time.time())
    print('-------------------------------')
    print('Running Start: ' + str(start))
    print('-------------------------------')
    output = open(outputDir + '/' + str(start) + '.txt', 'a')
    imgDir = sorted(os.listdir(frameOutputDir))
    positionData = []
    allWords = []

    for img_name in imgDir:
        img_path = frameOutputDir + '/' + img_name
        recognise_dic = Recognise(img_path)
        im = cv2.imread(img_path)
        height, width = im.shape[:2]
        time.sleep(0.5)

        index = 0

        for k, value in recognise_dic.items():
            keyword_len = len(recognise_dic.items())
            area = 0
            word = ''
            index += 1
            k = k.strip()

            if k == ' ':
                continue

            for v in value['itemcoord']:
                if v['y'] >= height * (1 - ratio) and k not in allWords:
                    # 选面积最大的
                    measure = v['width'] * v['height']
                    if measure > area:
                        area = measure
                        word = k
                    
            if index == keyword_len:
                print('-------- KEYWORD %s --------'%(word))
                allWords.append(word)
                output.write('\n'+word)
                output.flush()

    end = time.time()
    print('-------------------------------')
    print('Running time: ' + str(end - start))
    print('-------------------------------')
    output.close()

if __name__ == '__main__':
    RecogniseAll()
