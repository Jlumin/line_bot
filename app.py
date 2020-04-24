import re
from flask import Flask, request, abort
import urllib.request
import pyimgur
import requests
from urllib.request import urlopen
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator
from time import gmtime, strftime
from datetime import timedelta
import datetime
import os
from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage, ImageSendMessage
)


app = Flask(__name__)

# Channel Access Token
line_bot_api = LineBotApi('your Line access token')

# Channel Secret
handler = WebhookHandler('your Line Secret')

#imgur
client_id = 
client_secret = 
access_token = 
refresh_token = 


        



# 監聽所有來自 /callback 的 Post Request
@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'

def graphrg(test_x,test_y):
    fig = plt.figure()
    ax2 = fig.add_subplot()
    ax2.set_ylim([0, max(test_y)])
    ax2.set_yticks(np.arange(min(test_y), max(test_y)+1, 0.5))
    bar=ax2.bar(test_x, test_y, width=0.007, color='red', label='rainfall')
    ax2.xaxis.set_major_locator(mdates.HourLocator(interval=2))
    ax2.xaxis.set_major_formatter(mdates.DateFormatter('%D %H:00'))
    ax2.set_xlim([min(test_x),max(test_x)])
    ax2.grid()
    plt.setp(ax2.get_xticklabels(), rotation=70, horizontalalignment='right')
    ax2.set_xlabel(r'time',fontdict={'fontsize':12})
    ax2.set_ylabel(r'mm/hour',fontdict={'fontsize':12})
    minorLocator = MultipleLocator(0.5)
    ax2.xaxis.set_minor_locator(minorLocator)
    plt.savefig(name[0]+'(Rainfall)'+'.png')
    im = pyimgur.Imgur(client_id)
    path=name[0]+'(Rainfall)'+'.png'
    upload=im.upload_image(name[0]+'(Rainfall)'+'.png', title='test')
    return upload.link 


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    message = TextSendMessage(text=event.message.text)
#    message = TextSendMessage(text="歡迎來到STORY!")
#    ll = ['測站一','測站二','測站三']
#    line_bot_api.reply_message(event.reply_token,TextSendMessage(text='Lets Go!'))
    if 'test' in message.text:
        xt=datetime.datetime.now().strftime('%Y%m%d')
        loc_wl = "AWS_website"+xt
        response = urllib.request.urlopen(loc_wl)
        html = response.readlines()
        html = str(html)
        aa = re.split('<br>|b\'|,| = ',html)
        aa = aa[1:-1]
        while '' in aa:
            aa.remove('')
        time = []
        depth = []
        for i in range(len(aa)):
            if aa[i] == 'time':
                time.append(aa[i+1])
            elif aa[i] == 'depth':
                depth.append(aa[i+1])
        column = ['time','depth']
        wl_data = pd.DataFrame(columns=column)
        wl_data['time']=pd.to_datetime(pd.Series(time),format='%Y%m%d%H%M%S')
        wl_data['depth'] = pd.Series(depth).values.astype(float)
        wl_data = wl_data.set_index('time')
        wl_data.plot()
        plt.savefig('ddd.png')
        plt.close()
        path = 'ddd.png' 
        im = pyimgur.Imgur(client_id)
        upload=im.upload_image(path, title='test')
        imgurl = upload.link
        line_bot_api.reply_message(event.reply_token,ImageSendMessage(original_content_url=imgurl,preview_image_url=imgurl))

    if 'bbb' in message.text:
        xt=datetime.datetime.now().strftime('%Y%m%d')
        loc_rg = "AWS_website"+xt
        response = urllib.request.urlopen(loc_rg)
        html = response.readlines()
        html = str(html)
        aa = re.split('<br>|b\'|,| = ',html)
        aa = aa[1:-1]
        while '' in aa:
            aa.remove('')
        time=[]
        rain_5mva=[]
        for i in range(len(aa)):
            if aa[i]=='time':
                time.append(aa[i+1])
            elif aa[i]=='weather':
                try:
                    rain_5mva.append(float(aa[i+5]))
                except:
                    rain_5mva.append('0.0')
        column=['time','rainvalue']
        rg_data=pd.DataFrame(columns=column)
        rg_data['time']=pd.to_datetime(pd.Series(time),format='%Y%m%d%H%M%S')
        rg_data['rainvalue']=pd.Series(rain_5mva).values.astype(float)
        rg_data['Hour'] = rg_data['time'].dt.hour
        rg_data = rg_data.set_index('time')
        rg_data['hour_value'] = rg_data['rainvalue'].groupby(rg_data['Hour']).transform('sum')
        del rg_data['Hour']
        del rg_data['rainvalue']
        rg_data = rg_data.drop_duplicates(subset = None, keep = 'first', inplace = False)
        rg_data.plot.bar(width=0.007, color='red')
        plt.savefig('ccc.png')
        plt.close()
        path_rg = 'ccc.png'      
        im = pyimgur.Imgur(client_id)
        upload_rg=im.upload_image(path_rg, title='test')
        imgurl_rg = upload_rg.link
        line_bot_api.reply_message(event.reply_token,ImageSendMessage(original_content_url=imgurl_rg,preview_image_url=imgurl_rg))        
    if '介壽村' in message.text:
        loc1 = 'AWS_website'
        response = urllib.request.urlopen(loc1)
        html = response.read()
        html = str(html)
        aa = re.split('<br>|b\'',html)
        aa1 = aa[1].replace(',',' ')
        ddl1 = re.split('=',aa1)
        ddtemp1 = re.split(' ',ddl1[3])
        dd1 = ddtemp1[1]
        if float(dd1) < 0:
            dd1 = '0.0'
        tttemp1 = re.split(' ',ddl1[2])
        ttq1 = tttemp1[1]
        tt1 = ttq1[0:12]
        wmgs = '介壽村道路淹水感知查詢資訊\n--------------------------------\n目前水位'+dd1+'公分\n(地表高程起算以上)\n最後更新時間：'+tt1
        line_bot_api.reply_message(event.reply_token,TextSendMessage(text=wmgs))
    if '復興村' in message.text:
        loc2 = 'AWS_website'
        response = urllib.request.urlopen(loc2)
        html = response.read()
        html = str(html)
        aa = re.split('<br>|b\'',html)
        aa2 = aa[1].replace(',',' ')
        ddl2 = re.split('=',aa2)
        ddtemp2 = re.split(' ',ddl2[3])
        dd2 = ddtemp2[1]
        if float(dd2) < 0:
            dd2 = '0.0'
        tttemp2 = re.split(' ',ddl2[2])
        ttq2 = tttemp2[1]
        tt2 = ttq2[0:12]
        wmgs = '復興村道路淹水感知查詢資訊\n--------------------------------\n目前水位'+dd2+'公分\n(地表高程起算以上)\n最後更新時間：'+tt2
        line_bot_api.reply_message(event.reply_token,TextSendMessage(text=wmgs))
    if '珠螺村' in message.text:
        loc3 = 'AWS_website'
        response = urllib.request.urlopen(loc3)
        html = response.read()
        html = str(html)
        aa = re.split('<br>|b\'',html)
        aa3 = aa[1].replace(',',' ')
        ddl3 = re.split('=',aa3)
        ddtemp3 = re.split(' ',ddl3[3])
        dd3 = ddtemp3[1]
        if float(dd3) < 0:
            dd3 = '0.0'
        tttemp3 = re.split(' ',ddl3[2])
        ttq3 = tttemp3[1]
        tt3 = ttq3[0:12]
        wmgs = '珠螺村道路淹水感知查詢資訊\n--------------------------------\n目前水位'+dd3+'公分\n(地表高程起算以上)\n最後更新時間：'+tt3
        line_bot_api.reply_message(event.reply_token,TextSendMessage(text=wmgs))
    if '漁會' in message.text:
        xt=datetime.datetime.now().strftime('%Y%m%d')
        loc2 = 'AWS_website'+xt
        response = urllib.request.urlopen(loc2)
        html = response.readlines()
        html = str(html)
        aa = re.split('<br>|b\'',html)
        aa2 = aa[-2].replace(',',' ')
        ddl2 = re.split('=',aa2)
        ddtemp2 = re.split(' ',ddl2[3])
        dd2 = ddtemp2[1]
        if float(dd2) < 0:
            dd2 = '0.0'
        tttemp2 = re.split(' ',ddl2[2])
        ttq2 = tttemp2[1]
        tt2 = ttq2[0:12]
        wmgs = '漁會道路淹水感知查詢資訊\n--------------------------------\n目前水位'+dd2+'公分\n(地表高程起算以上)\n最後更新時間：'+tt2
        line_bot_api.reply_message(event.reply_token,TextSendMessage(text=wmgs))
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)