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
    MessageEvent, TextMessage, TextSendMessage, ImageSendMessage, ConfirmTemplate,
    TemplateSendMessage, MessageAction, ButtonsTemplate, PostbackAction,
    URIAction, PostbackEvent)


app = Flask(__name__)

# Channel Access Token
line_bot_api = LineBotApi(your line bot access token)

# Channel Secret
handler = WebhookHandler(your line bot channel Secret)

#imgur
client_id = imgur client_idid
client_secret = imgur client_secret
access_token = imgur access_token
refresh_token = imgur refresh_token
    



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


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    message = TextSendMessage(text=event.message.text)
#    message = TextSendMessage(text="歡迎來到STORY!")
#    ll = ['測站一','測站二','測站三']
#    line_bot_api.reply_message(event.reply_token,TextSendMessage(text='Lets Go!'))
    if 'test' == message.text:
        buttons_template = ButtonsTemplate(
            text ='嗨! 今天過得好嗎？', 
            actions=[
                PostbackAction(label='當下水位', data = '當下水位', text='資料處理中請稍候'), 
                PostbackAction(label='今日水位及雨量圖', data = '今日水位及雨量圖', text='資料處理中請稍候')            
            ])
        template_mesg = TemplateSendMessage(alt_text = 'the Menu button', template = buttons_template)
        line_bot_api.reply_message(event.reply_token, template_mesg)

    if '介壽村' == message.text:
        buttons_template = ButtonsTemplate(
            text ='嗨! 今天過得好嗎？', 
            actions=[
                PostbackAction(label='當下水位', data = '當下水位1', text='資料處理中請稍候'), 
                PostbackAction(label='今日水位及雨量圖', data = '今日水位及雨量圖1', text='資料處理中請稍候')            
            ])
        template_mesg = TemplateSendMessage(alt_text = 'the Menu button', template = buttons_template)
        line_bot_api.reply_message(event.reply_token, template_mesg)

    if '復興村' == message.text:
        buttons_template = ButtonsTemplate(
            text ='嗨! 今天過得好嗎？', 
            actions=[
                PostbackAction(label='當下水位', data = '當下水位2', text='資料處理中請稍候'), 
                PostbackAction(label='今日水位及雨量圖', data = '今日水位及雨量圖2', text='資料處理中請稍候')            
            ])
        template_mesg = TemplateSendMessage(alt_text = 'the Menu button', template = buttons_template)
        line_bot_api.reply_message(event.reply_token, template_mesg)

    if '珠螺村' == message.text:
        buttons_template = ButtonsTemplate(
            text ='嗨! 今天過得好嗎？', 
            actions=[
                PostbackAction(label='當下水位', data = '當下水位3', text='資料處理中請稍候'), 
                PostbackAction(label='今日水位及雨量圖', data = '今日水位及雨量圖3', text='資料處理中請稍候')            
            ])
        template_mesg = TemplateSendMessage(alt_text = 'the Menu button', template = buttons_template)
        line_bot_api.reply_message(event.reply_token, template_mesg)

    if '漁會' == message.text:
        buttons_template = ButtonsTemplate(
            text ='嗨! 今天過得好嗎？', 
            actions=[
                PostbackAction(label='當下水位', data = '當下水位4', text='資料處理中請稍候'), 
                PostbackAction(label='今日水位及雨量圖', data = '今日水位及雨量圖4', text='資料處理中請稍候')            
            ])
        template_mesg = TemplateSendMessage(alt_text = 'the Menu button', template = buttons_template)
        line_bot_api.reply_message(event.reply_token, template_mesg)
@handler.add(PostbackEvent)
def handle_postback(event):
    if isinstance(event, PostbackEvent):
        backdata = event.postback.data
        #print("Look at here!B==================>" + str(backdata))
        if backdata == '當下水位':        
            loc1 = 'http://AWS.amazonaws.com/data.'
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
        if backdata == '今日水位及雨量圖':
            xt=datetime.datetime.now().strftime('%Y%m%d')
            loc_wl = "http://AWS.amazonaws.com/data.php"+xt
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
            loc_rg = "http://AWS.amazonaws.com/data.php"+xt
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
            fig, axes = plt.subplots(nrows=2, ncols=1, gridspec_kw={'hspace': 1})
            wl_data.plot(ax=axes[0])
            rg_data.plot.bar(width=0.007, color='red',ax=axes[1])
            axes[0].set_title('水位(Water Level) time:'+xt, fontdict={'fontsize':12})
            axes[0].set_xlabel(r'時間(time)',fontdict={'fontsize':12})
            axes[0].set_ylabel(r'深度(m)',fontdict={'fontsize':12})
            axes[0].grid()
            axes[0].xaxis.set_major_locator(mdates.HourLocator(interval=4))
            axes[0].xaxis.set_major_formatter(mdates.DateFormatter('%H:00'))
            plt.setp(axes[0].get_xticklabels(), rotation=70, horizontalalignment='right')
            axes[1].set_title('雨量(Rainfall) time:'+xt, fontdict={'fontsize':12})
            axes[1].set_xlabel(r'時間(time)',fontdict={'fontsize':12})
            axes[1].set_ylabel(r'時雨量(mm/hour)',fontdict={'fontsize':12})
            axes[1].grid()
            axes[1].xaxis.set_major_locator(mdates.HourLocator(interval=4))
            axes[1].xaxis.set_major_formatter(mdates.DateFormatter('%H:00'))
            plt.setp(axes[1].get_xticklabels(), rotation=70, horizontalalignment='right')
            plt.savefig('ddd.png')
            plt.close()
            path = 'ddd.png' 
            im = pyimgur.Imgur(client_id)
            upload=im.upload_image(path, title='test')
            imgurl = upload.link
            line_bot_api.reply_message(event.reply_token,ImageSendMessage(original_content_url=imgurl,preview_image_url=imgurl))

#介壽村
        if backdata == '當下水位1':        
            loc1 = 'http://AWS.amazonaws.com/data.php'
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
        if backdata == '今日水位及雨量圖1':
            xt=datetime.datetime.now().strftime('%Y%m%d')
            loc_wl = "http://AWS.amazonaws.com/data.php"+xt
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
            loc_rg = "http://AWS.amazonaws.com/data.php"+xt
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
            fig, axes = plt.subplots(nrows=2, ncols=1, gridspec_kw={'hspace': 1})
            wl_data.plot(ax=axes[0])
            rg_data.plot.bar(width=0.007, color='red',ax=axes[1])
            axes[0].set_title('水位(Water Level) time:'+xt, fontdict={'fontsize':12})
            axes[0].set_xlabel(r'時間(time)',fontdict={'fontsize':12})
            axes[0].set_ylabel(r'深度(m)',fontdict={'fontsize':12})
            axes[0].grid()
            axes[0].xaxis.set_major_locator(mdates.HourLocator(interval=4))
            axes[0].xaxis.set_major_formatter(mdates.DateFormatter('%H:00'))
            plt.setp(axes[0].get_xticklabels(), rotation=70, horizontalalignment='right')
            axes[1].set_title('雨量(Rainfall) time:'+xt, fontdict={'fontsize':12})
            axes[1].set_xlabel(r'時間(time)',fontdict={'fontsize':12})
            axes[1].set_ylabel(r'時雨量(mm/hour)',fontdict={'fontsize':12})
            axes[1].grid()
            axes[1].xaxis.set_major_locator(mdates.HourLocator(interval=4))
            axes[1].xaxis.set_major_formatter(mdates.DateFormatter('%H:00'))
            plt.setp(axes[1].get_xticklabels(), rotation=70, horizontalalignment='right')
            plt.savefig('ddd.png')
            plt.close()
            path = 'ddd.png' 
            im = pyimgur.Imgur(client_id)
            upload=im.upload_image(path, title='test')
            imgurl = upload.link
            line_bot_api.reply_message(event.reply_token,ImageSendMessage(original_content_url=imgurl,preview_image_url=imgurl))
#復興村
        if backdata == '當下水位2':        
            loc1 = 'http://AWS.amazonaws.com/data.php'
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
            wmgs = '復興村道路淹水感知查詢資訊\n--------------------------------\n目前水位'+dd1+'公分\n(地表高程起算以上)\n最後更新時間：'+tt1
            line_bot_api.reply_message(event.reply_token,TextSendMessage(text=wmgs)) 
        if backdata == '今日水位及雨量圖2':
            xt=datetime.datetime.now().strftime('%Y%m%d')
            loc_wl = "http://AWS.amazonaws.com/data.php"+xt
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
            loc_rg = "http://AWS.amazonaws.com/data.php"+xt
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
            fig, axes = plt.subplots(nrows=2, ncols=1, gridspec_kw={'hspace': 1})
            wl_data.plot(ax=axes[0])
            rg_data.plot.bar(width=0.007, color='red',ax=axes[1])
            axes[0].set_title('水位(Water Level) time:'+xt, fontdict={'fontsize':12})
            axes[0].set_xlabel(r'時間(time)',fontdict={'fontsize':12})
            axes[0].set_ylabel(r'深度(m)',fontdict={'fontsize':12})
            axes[0].grid()
            axes[0].xaxis.set_major_locator(mdates.HourLocator(interval=4))
            axes[0].xaxis.set_major_formatter(mdates.DateFormatter('%H:00'))
            plt.setp(axes[0].get_xticklabels(), rotation=70, horizontalalignment='right')
            axes[1].set_title('雨量(Rainfall) time:'+xt, fontdict={'fontsize':12})
            axes[1].set_xlabel(r'時間(time)',fontdict={'fontsize':12})
            axes[1].set_ylabel(r'時雨量(mm/hour)',fontdict={'fontsize':12})
            axes[1].grid()
            axes[1].xaxis.set_major_locator(mdates.HourLocator(interval=4))
            axes[1].xaxis.set_major_formatter(mdates.DateFormatter('%H:00'))
            plt.setp(axes[1].get_xticklabels(), rotation=70, horizontalalignment='right')
            plt.savefig('ddd.png')
            plt.close()
            path = 'ddd.png' 
            im = pyimgur.Imgur(client_id)
            upload=im.upload_image(path, title='test')
            imgurl = upload.link
            line_bot_api.reply_message(event.reply_token,ImageSendMessage(original_content_url=imgurl,preview_image_url=imgurl))
#珠螺村
        if backdata == '當下水位3':        
            loc1 = 'http://AWS.amazonaws.com/data.php'
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
            wmgs = '珠螺村道路淹水感知查詢資訊\n--------------------------------\n目前水位'+dd1+'公分\n(地表高程起算以上)\n最後更新時間：'+tt1
            line_bot_api.reply_message(event.reply_token,TextSendMessage(text=wmgs)) 
        if backdata == '今日水位及雨量圖3':
            xt=datetime.datetime.now().strftime('%Y%m%d')
            loc_wl = "http://AWS.amazonaws.com/data.php"+xt
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
            loc_rg = "http://AWS.amazonaws.com/data.php"+xt
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
            fig, axes = plt.subplots(nrows=2, ncols=1, gridspec_kw={'hspace': 1})
            wl_data.plot(ax=axes[0])
            rg_data.plot.bar(width=0.007, color='red',ax=axes[1])
            axes[0].set_title('水位(Water Level) time:'+xt, fontdict={'fontsize':12})
            axes[0].set_xlabel(r'時間(time)',fontdict={'fontsize':12})
            axes[0].set_ylabel(r'深度(m)',fontdict={'fontsize':12})
            axes[0].grid()
            axes[0].xaxis.set_major_locator(mdates.HourLocator(interval=4))
            axes[0].xaxis.set_major_formatter(mdates.DateFormatter('%H:00'))
            plt.setp(axes[0].get_xticklabels(), rotation=70, horizontalalignment='right')
            axes[1].set_title('雨量(Rainfall) time:'+xt, fontdict={'fontsize':12})
            axes[1].set_xlabel(r'時間(time)',fontdict={'fontsize':12})
            axes[1].set_ylabel(r'時雨量(mm/hour)',fontdict={'fontsize':12})
            axes[1].grid()
            axes[1].xaxis.set_major_locator(mdates.HourLocator(interval=4))
            axes[1].xaxis.set_major_formatter(mdates.DateFormatter('%H:00'))
            plt.setp(axes[1].get_xticklabels(), rotation=70, horizontalalignment='right')
            plt.savefig('ddd.png')
            plt.close()
            path = 'ddd.png' 
            im = pyimgur.Imgur(client_id)
            upload=im.upload_image(path, title='test')
            imgurl = upload.link
            line_bot_api.reply_message(event.reply_token,ImageSendMessage(original_content_url=imgurl,preview_image_url=imgurl))
#漁會
        if backdata == '當下水位4':        
            xt=datetime.datetime.now().strftime('%Y%m%d')
            loc2 = 'http://AWS.amazonaws.com/data.php'+xt
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
        if backdata == '今日水位及雨量圖4':
            xt=datetime.datetime.now().strftime('%Y%m%d')
            loc_wl = "http://AWS.amazonaws.com/data.php"+xt
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
            #loc_rg = "http://AWS.amazonaws.com/data.php"+xt
            #response = urllib.request.urlopen(loc_rg)
            #html = response.readlines()
            #html = str(html)
            #aa = re.split('<br>|b\'|,| = ',html)
            #aa = aa[1:-1]
            #while '' in aa:
            #    aa.remove('')
            #time=[]
            #rain_5mva=[]
            #for i in range(len(aa)):
                #if aa[i]=='time':
                 #   time.append(aa[i+1])
                #elif aa[i]=='weather':
                #    try:
               #      except:
             #           rain_5mva.append('0.0')
            #column=['time','rainvalue']
            #rg_data=pd.DataFrame(columns=column)
            #rg_data['time']=pd.to_datetime(pd.Series(time),format='%Y%m%d%H%M%S')
            #rg_data['rainvalue']=pd.Series(rain_5mva).values.astype(float)
            #rg_data['Hour'] = rg_data['time'].dt.hour
            #rg_data = rg_data.set_index('time')
            #rg_data['hour_value'] = rg_data['rainvalue'].groupby(rg_data['Hour']).transform('sum')
            #del rg_data['Hour']
            #del rg_data['rainvalue']
            #rg_data = rg_data.drop_duplicates(subset = None, keep = 'first', inplace = False)
            fig, axes = plt.subplots(nrows=2, ncols=1, gridspec_kw={'hspace': 1})
            wl_data.plot(ax=axes[0])
            #rg_data.plot.bar(width=0.007, color='red',ax=axes[1])
            axes[0].set_title('水位(Water Level) time:'+xt, fontdict={'fontsize':12})
            axes[0].set_xlabel(r'時間(time)',fontdict={'fontsize':12})
            axes[0].set_ylabel(r'深度(m)',fontdict={'fontsize':12})
            axes[0].grid()
            axes[0].xaxis.set_major_locator(mdates.HourLocator(interval=4))
            axes[0].xaxis.set_major_formatter(mdates.DateFormatter('%H:00'))
            plt.setp(axes[0].get_xticklabels(), rotation=70, horizontalalignment='right')
            #axes[1].set_title('雨量(Rainfall) time:'+xt, fontdict={'fontsize':12})
            #axes[1].set_xlabel(r'時間(time)',fontdict={'fontsize':12})
            #axes[1].set_ylabel(r'時雨量(mm/hour)',fontdict={'fontsize':12})
            #axes[1].grid()
            #axes[1].xaxis.set_major_locator(mdates.HourLocator(interval=4))
            #axes[1].xaxis.set_major_formatter(mdates.DateFormatter('%H:00'))
            #plt.setp(axes[1].get_xticklabels(), rotation=70, horizontalalignment='right')
            plt.savefig('ddd.png')
            plt.close()
            path = 'ddd.png' 
            im = pyimgur.Imgur(client_id)
            upload=im.upload_image(path, title='test')
            imgurl = upload.link
            line_bot_api.reply_message(event.reply_token,ImageSendMessage(original_content_url=imgurl,preview_image_url=imgurl))

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)