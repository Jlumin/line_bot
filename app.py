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
from time import gmtime, strftime, strptime
from datetime import  datetime, timezone, timedelta

import os
from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage, ImageSendMessage, ConfirmTemplate,
    TemplateSendMessage, MessageAction, ButtonsTemplate, PostbackAction,DatetimePickerTemplateAction,
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

def Test(id,time):
    global html
    ids = str(id)
    stime = str(time)[:-4]
    #rg = {'7504':'3040', '7505':'3040', '7506':'3039', '7507':'2026'}
    #rg_id = rg[ids]
    ltime = datetime.strptime(stime,'%Y%m%d') + timedelta(-1)
    ltime = ltime.strftime('%Y%m%d')
    htime = str(time)[-4:-2]
    if htime == '00':
        lhtime = '23'
    else:
        lhtime = str(int(htime) + 1)
    global ldhtime
    global tdhtime
    ldhtime = ltime + htime
    tdhtime = stime + htime
    if ids in ['7507','3038','3039', '3040', '2026']:
        loct = "http://AWS.amazonaws.com/data".format(ids,stime)
        locy = "http://AWS.amazonaws.com/data".format(ids,ltime)
    else:
        loct = "http://AWS.amazonaws.com/data".format(ids,stime)
        locy = "http://AWS.amazonaws.com/data".format(ids,ltime)
    
    responset = urllib.request.urlopen(loct)
    responsey = urllib.request.urlopen(locy)
    htmlt = responset.readlines()
    htmlt = str(htmlt)
    htmly = responsey.readlines()
    htmly = str(htmly)
    html = htmlt + htmly
    if ("No" in html) & ("results" in html):
        #print()
        #print('執行程序1')
        if ids in ['7507','3038','3039', '3040', '2026']:
            loct = "http://AWS.amazonaws.com/data".format(ids,stime[:-2])
        else:
            #print('執行程序2')
            loct = "http://AWS.amazonaws.com/data".format(ids,stime[:-2])
        responset = urllib.request.urlopen(loct)
        responsey = urllib.request.urlopen(locy)
        htmlt = responset.readlines()
        htmlt = str(htmlt)
        html = htmlt
        if ("No" in html) & ("results" in html):
            global wl
            wl = '儀器故障，超過一個月!' 
            return html + wl
        else:
            return html+'今天沒有資料'
    else:
        return html
            #print(wl)
def Gwl_data():
    global aa
    aa = re.split('<br>|b\'|,| = ',html)
    aa = aa[1:-1]
    while '' in aa:
        aa.remove('')
    global ggtime 
    ggtime = []
    global depth
    depth = []
    for i in range(len(aa)):
        try:
            if aa[i] == 'time':
                ggtime.append(aa[i+1])
            if aa[i] == 'depth':
                depth.append(aa[i+1])
        except:
            pass
    global wl_data
    column = ['time','depth']
    wl_data = pd.DataFrame(columns=column)
    wl_data['time']=pd.to_datetime(pd.Series(ggtime))
    wl_data['depth'] = pd.Series(depth).values.astype(float)
    wl_data = wl_data.sort_values('time')
    wl_data = wl_data.reset_index()
    wl_data['num'] = pd.Series(wl_data.index.values)
    wl_data['ser'] = wl_data['time'].dt.strftime('%m%d%H')
    del wl_data['index']
    #wl_data = wl_data.set_index('time')
    wl_data.sort_values(by=['time'])
    return wl_data
def Wl24f():
    global wl24
    wl24 = wl_data[wl_data['ser'].between(ldhtime[4:],tdhtime[4:])]
    del wl_data['num']
    del wl_data['ser']
    del wl24['ser']
    del wl24['num']
    return wl24
def Rg_data():
    global aa
    aa = re.split('<br>|b\'|,| = ',html)
    aa = aa[1:-1]
    while '' in aa:
        aa.remove('')
    global ggtime 
    ggtime = []
    global rain_5mva
    rain_5mva=[]
    for i in range(len(aa)):
        if aa[i]=='time':
            ggtime.append(aa[i+1])
        elif aa[i]=='weather':
            try:
                rain_5mva.append(float(aa[i+5]))
            except:
                rain_5mva.append('0.0')
    global rg_data
    column=['time','rainvalue']
    rg_data=pd.DataFrame(columns=column)
    rg_data['time']=pd.to_datetime(pd.Series(ggtime),format='%Y%m%d%H%M%S')
    rg_data['rainvalue']=pd.Series(rain_5mva).astype(float)
    rg_data['Hour'] = rg_data['time'].dt.strftime('%m%d%H')
    #rg_data = rg_data.set_index('time')
    #rg_data = rg_data.sort_index(ascending=True)
    rg_data.sort_values(by=['time'])
    rg_data['hour_value'] = rg_data['rainvalue'].groupby(rg_data['Hour']).transform('sum')
    del rg_data['rainvalue']
    rg_data = rg_data.drop_duplicates(subset = 'Hour', keep = 'first', inplace = False)
    return rg_data
def Rg24f():
    global rg24
    rg24 = rg_data[rg_data['Hour'].between(ldhtime[4:],tdhtime[4:])]    
    del rg24['Hour']
    return rg24
def Produce_wl(wl_data):
    if len(wl_data) == 1:
        end=max(wl_data['time'])
        start= end + timedelta(-1)
    else:
        end=max(wl_data['time'])
        start= end + timedelta(-1)
    wl_data =wl_data.reset_index()
    t_index = pd.date_range(start,end, freq='30T')
    T_df = pd.DataFrame(t_index, columns=['time'])
    T_df = pd.to_datetime(T_df['time'], format="%Y%m%d%H%M%S")
    T_df = T_df.to_frame()
    wl_data = pd.concat([wl_data,T_df],join='outer')
    wl_data = wl_data.drop_duplicates(subset = 'time', keep = 'first', inplace = False)
    wl_data.sort_values(by=['time'])
    #wl_data = result.set_index('time')
    #wl_data = result.sort_index(ascending=True)
    return wl_data
def Produce_rg(rg_data):
    if len(rg_data['Hour'])<2:
        end=max(rg_data['time'])
        start= end + timedelta(-1)
    else:
        end=max(rg_data['time'])
        start= end + timedelta(-1)
    rg_data =rg_data.reset_index()
    t_index = pd.date_range(start,end, freq='10T')
    T_df = pd.DataFrame(t_index, columns=['time'])
    T_df = pd.to_datetime(T_df['time'], format="%Y%m%d%H%M%S")
    T_df = T_df.to_frame()
    rg_data = pd.concat([rg_data,T_df],join='outer')
    rg_data = rg_data.drop_duplicates(subset = 'time', keep = 'first', inplace = False)
    rg_data.sort_values(by=['time'])
    #rg_data = rg_data.set_index('time')
    #rg_data = rg_data.sort_index(ascending=True)
    return rg_data


    
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
                PostbackAction(label='今日水位及雨量圖', data = '今日水位及雨量'),
                PostbackAction(label='歷史水位及雨量圖', data = '歷史水位及雨量', text='資料處理中請稍候')            
            ])
        template_mesg = TemplateSendMessage(alt_text = 'the Menu button', template = buttons_template)
        line_bot_api.reply_message(event.reply_token, template_mesg)

    if '介壽村' == message.text:
        buttons_template = ButtonsTemplate(
            text ='歡迎來到介壽村，今天過得好嗎？', 
            actions=[
                PostbackAction(label='當下水位', data = '當下水位1', text='介壽村，水位資料處理中請稍候'), 
                PostbackAction(label='今日水位及雨量圖', data = '今日水位及雨量1'),
                PostbackAction(label='歷史水位及雨量圖', data = '歷史1')                      
            ])
        template_mesg = TemplateSendMessage(alt_text = 'the Menu button', template = buttons_template)
        line_bot_api.reply_message(event.reply_token, template_mesg)

    if '復興村' == message.text:
        buttons_template = ButtonsTemplate(
            text ='歡迎來到復興村，今天過得好嗎？', 
            actions=[
                PostbackAction(label='當下水位', data = '當下水位2', text='復興村，水位資料處理中請稍候'), 
                PostbackAction(label='今日水位及雨量圖', data = '今日水位及雨量2'),
                PostbackAction(label='歷史水位及雨量圖', data = '歷史2')                        
            ])
        template_mesg = TemplateSendMessage(alt_text = 'the Menu button', template = buttons_template)
        line_bot_api.reply_message(event.reply_token, template_mesg)

    if '珠螺村' == message.text:
        buttons_template = ButtonsTemplate(
            text ='歡迎來到珠螺村，今天過得好嗎？', 
            actions=[
                PostbackAction(label='當下水位', data = '當下水位3', text='珠螺村，水位資料處理中請稍候'), 
                PostbackAction(label='今日水位及雨量圖', data = '今日水位及雨量3'),
                PostbackAction(label='歷史水位及雨量圖', data = '歷史3')                        
            ])
        template_mesg = TemplateSendMessage(alt_text = 'the Menu button', template = buttons_template)
        line_bot_api.reply_message(event.reply_token, template_mesg)

    if '港口' == message.text:
        buttons_template = ButtonsTemplate(
            text ='歡迎來到港口，今天過得好嗎？', 
            actions=[
                PostbackAction(label='當下水位', data = '當下水位4', text='港口，水位資料處理中請稍候'), 
                PostbackAction(label='今日水位及雨量圖', data = '今日水位及雨量4'),
                PostbackAction(label='歷史水位及雨量圖', data = '歷史4')            
                            
            ])
        template_mesg = TemplateSendMessage(alt_text = 'the Menu button', template = buttons_template)
        line_bot_api.reply_message(event.reply_token, template_mesg)
@handler.add(PostbackEvent)
def handle_postback(event):
    if isinstance(event, PostbackEvent):
        backdata = event.postback.data
        if backdata == '今日水位及雨量':
            buttons_template = ButtonsTemplate(
                text ='嗨! 今天過得好嗎？', 
                actions=[ 
                    PostbackAction(label='今日水位圖', data = '今日水位', text='水位資料處理中請稍候'),
                    PostbackAction(label='今日雨量圖', data = '今日雨量', text='雨量資料處理中請稍候')            
                ])
            template_mesg = TemplateSendMessage(alt_text = 'the Menu button', template = buttons_template)
            line_bot_api.reply_message(event.reply_token, template_mesg)
        if backdata == '今日水位及雨量1':
            buttons_template = ButtonsTemplate(
                text ='嗨!介壽村，今天過得好嗎？', 
                actions=[ 
                    PostbackAction(label='今日水位圖', data = '今日水位1', text='水位資料處理中請稍候'),
                    PostbackAction(label='今日雨量圖', data = '今日雨量1', text='雨量資料處理中請稍候')            
                ])
            template_mesg = TemplateSendMessage(alt_text = 'the Menu button', template = buttons_template)
            line_bot_api.reply_message(event.reply_token, template_mesg)
        if backdata == '今日水位及雨量2':
            buttons_template = ButtonsTemplate(
                text ='嗨!復興村，今天過得好嗎？', 
                actions=[ 
                    PostbackAction(label='今日水位圖', data = '今日水位2', text='水位資料處理中請稍候'),
                    PostbackAction(label='今日雨量圖', data = '今日雨量2', text='雨量資料處理中請稍候')            
                ])
            template_mesg = TemplateSendMessage(alt_text = 'the Menu button', template = buttons_template)
            line_bot_api.reply_message(event.reply_token, template_mesg)
        if backdata == '今日水位及雨量3':
            buttons_template = ButtonsTemplate(
                text ='嗨!珠螺村，今天過得好嗎？', 
                actions=[ 
                    PostbackAction(label='今日水位圖', data = '今日水位3', text='水位資料處理中請稍候'),
                    PostbackAction(label='今日雨量圖', data = '今日雨量3', text='雨量資料處理中請稍候')            
                ])
            template_mesg = TemplateSendMessage(alt_text = 'the Menu button', template = buttons_template)
            line_bot_api.reply_message(event.reply_token, template_mesg)
        if backdata == '今日水位及雨量4':
            buttons_template = ButtonsTemplate(
                text ='嗨!港口，今天過得好嗎？', 
                actions=[ 
                    PostbackAction(label='今日水位圖', data = '今日水位4', text='水位資料處理中請稍候'),
                    PostbackAction(label='今日雨量圖', data = '今日雨量4', text='雨量資料處理中請稍候')            
                ])
            template_mesg = TemplateSendMessage(alt_text = 'the Menu button', template = buttons_template)
            line_bot_api.reply_message(event.reply_token, template_mesg)

        if backdata == '歷史1':
            buttons_template = ButtonsTemplate(
                text ='嗨!介壽村，今天過得好嗎？', 
                actions=[ 
                    PostbackAction(label='歷史水位圖', data = '歷史水位1', text='水位資料處理中請稍候'),
                    PostbackAction(label='歷史雨量圖', data = '歷史雨量1', text='雨量資料處理中請稍候')            
                ])
            template_mesg = TemplateSendMessage(alt_text = 'the Menu button', template = buttons_template)
            line_bot_api.reply_message(event.reply_token, template_mesg)
        if backdata == '歷史2':
            buttons_template = ButtonsTemplate(
                text ='嗨!復興村，今天過得好嗎？', 
                actions=[ 
                    PostbackAction(label='歷史水位圖', data = '歷史水位2', text='水位資料處理中請稍候'),
                    PostbackAction(label='歷史雨量圖', data = '歷史雨量2', text='雨量資料處理中請稍候')            
                ])
            template_mesg = TemplateSendMessage(alt_text = 'the Menu button', template = buttons_template)
            line_bot_api.reply_message(event.reply_token, template_mesg)
        if backdata == '歷史3':
            buttons_template = ButtonsTemplate(
                text ='嗨!珠螺村，今天過得好嗎？', 
                actions=[ 
                    PostbackAction(label='歷史水位圖', data = '歷史水位3', text='水位資料處理中請稍候'),
                    PostbackAction(label='歷史雨量圖', data = '歷史雨量3', text='雨量資料處理中請稍候')            
                ])
            template_mesg = TemplateSendMessage(alt_text = 'the Menu button', template = buttons_template)
            line_bot_api.reply_message(event.reply_token, template_mesg)
        if backdata == '歷史4':
            buttons_template = ButtonsTemplate(
                text ='嗨!港口，今天過得好嗎？', 
                actions=[ 
                    PostbackAction(label='歷史水位圖', data = '歷史水位4', text='水位資料處理中請稍候'),
                    PostbackAction(label='歷史雨量圖', data = '歷史雨量4', text='雨量資料處理中請稍候')            
                ])
            template_mesg = TemplateSendMessage(alt_text = 'the Menu button', template = buttons_template)
            line_bot_api.reply_message(event.reply_token, template_mesg)

        if backdata == '歷史水位1':
            message = TemplateSendMessage(
                alt_text = '日期時間選擇',
                template = ButtonsTemplate(
                    title = '請選擇查詢時間',
                    text = '請選擇：',
                    actions = [DatetimePickerTemplateAction(
                        label='選擇日期',
                        data = '歷史水位圖1',
                        mode = 'datetime',
                        initial = '2020-04-01T00:00',
                        min = '2020-01-01T00:00',
                        max = '2030-12-31T23:59' )]))
            line_bot_api.reply_message(event.reply_token,message)
        if backdata == '歷史水位2':
            message = TemplateSendMessage(
                alt_text = '日期時間選擇',
                template = ButtonsTemplate(
                    title = '請選擇查詢時間',
                    text = '請選擇：',
                    actions = [DatetimePickerTemplateAction(
                        label='選擇日期',
                        data = '歷史水位圖2',
                        mode = 'datetime',
                        initial = '2020-04-01T00:00',
                        min = '2020-01-01T00:00',
                        max = '2030-12-31T23:59'    )]  ) )
            line_bot_api.reply_message(event.reply_token,message)
        if backdata == '歷史水位3':
            message = TemplateSendMessage(
                alt_text = '日期時間選擇',
                template = ButtonsTemplate(
                    title = '請選擇查詢時間',
                    text = '請選擇：',
                    actions = [DatetimePickerTemplateAction(
                        label='選擇日期',
                        data = '歷史水位圖3',
                        mode = 'datetime',
                        initial = '2020-04-01T00:00',
                        min = '2020-01-01T00:00',
                        max = '2030-12-31T23:59'             )]       )      )
            line_bot_api.reply_message(event.reply_token,message)
        if backdata == '歷史水位4':
            message = TemplateSendMessage(
                alt_text = '日期時間選擇',
                template = ButtonsTemplate(
                    title = '請選擇查詢時間',
                    text = '請選擇：',
                    actions = [DatetimePickerTemplateAction(
                        label='選擇日期',
                        data = '歷史水位圖4',
                        mode = 'datetime',
                        initial = '2020-04-01T00:00',
                        min = '2020-01-01T00:00',
                        max = '2030-12-31T23:59')]  )          )
            line_bot_api.reply_message(event.reply_token,message)
        if backdata == '歷史雨量1':
            message = TemplateSendMessage(
                alt_text = '日期時間選擇',
                template = ButtonsTemplate(
                    title = '請選擇查詢時間',
                    text = '請選擇：',
                    actions = [DatetimePickerTemplateAction(
                        label='選擇日期',
                        data = '歷史雨量圖1',
                        mode = 'datetime',
                        initial = '2020-04-01T00:00',
                        min = '2020-01-01T00:00',
                        max = '2030-12-31T23:59' )]))
            line_bot_api.reply_message(event.reply_token,message)
        if backdata == '歷史雨量2':
            message = TemplateSendMessage(
                alt_text = '日期時間選擇',
                template = ButtonsTemplate(
                    title = '請選擇查詢時間',
                    text = '請選擇：',
                    actions = [DatetimePickerTemplateAction(
                        label='選擇日期',
                        data = '歷史雨量圖2',
                        mode = 'datetime',
                        initial = '2020-04-01T00:00',
                        min = '2020-01-01T00:00',
                        max = '2030-12-31T23:59'    )]  ) )
            line_bot_api.reply_message(event.reply_token,message)
        if backdata == '歷史雨量3':
            message = TemplateSendMessage(
                alt_text = '日期時間選擇',
                template = ButtonsTemplate(
                    title = '請選擇查詢時間',
                    text = '請選擇：',
                    actions = [DatetimePickerTemplateAction(
                        label='選擇日期',
                        data = '歷史雨量圖3',
                        mode = 'datetime',
                        initial = '2020-04-01T00:00',
                        min = '2020-01-01T00:00',
                        max = '2030-12-31T23:59'             )]       )      )
            line_bot_api.reply_message(event.reply_token,message)
        if backdata == '歷史雨量4':
            message = TemplateSendMessage(
                alt_text = '日期時間選擇',
                template = ButtonsTemplate(
                    title = '請選擇查詢時間',
                    text = '請選擇：',
                    actions = [DatetimePickerTemplateAction(
                        label='選擇日期',
                        data = '歷史雨量圖4',
                        mode = 'datetime',
                        initial = '2020-04-01T00:00',
                        min = '2020-01-01T00:00',
                        max = '2030-12-31T23:59')]  )          )
            line_bot_api.reply_message(event.reply_token,message)
#歷史水位
        if backdata == '歷史水位圖1':
            dt = event.postback.params.get('datetime')
            aaa = str(dt)
            ddt = aaa[:4]+aaa[5:7]+aaa[8:10]+aaa[11:13]+aaa[14:]
            html = Test(7504,ddt)
            if '今天沒有資料' in html:
                wl_data = Gwl_data()
                wl24=Produce_wl(wl_data)
                fig = plt.figure(figsize=(9,4))
                ax2 = fig.add_subplot(1,1,1)
                fig.subplots_adjust(bottom=0.3)
                plt.plot(wl24['time'],wl24['depth'])
                plt.title('Water Level Date:'+max(wl24['time']).strftime('%Y-%m-%d'), fontdict={'fontsize':12})
                ax2.set_xlabel(r'time',fontdict={'fontsize':12})
                ax2.set_ylabel(r'cm',fontdict={'fontsize':12})
                plt.grid()
                try:
                    ax2.set_ylim([0, max(wl24['depth'])])
                    ax2.set_yticks(np.arange(min(wl24['depth']), max(wl24['depth'])+1))
                    ax2.set_xlim([min(wl24['time']),max(wl24['time'])])
                    ax2.xaxis.set_major_locator(mdates.HourLocator(interval=1))
                    ax2.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d %H'))
                except:
                    pass
                ax2.xaxis.set_major_locator(mdates.HourLocator(interval=1))
                ax2.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d %H'))
                plt.setp(ax2.get_xticklabels(), rotation=60, horizontalalignment='right')
                plt.savefig('ddd.png')
                plt.close()
                path = 'ddd.png' 
                im = pyimgur.Imgur(client_id)
                upload=im.upload_image(path, title='test')
                imgurl = upload.link
                line_bot_api.reply_message(event.reply_token,ImageSendMessage(original_content_url=imgurl,preview_image_url=imgurl))
            elif '儀器故障，超過一個月!' in html:
                wmgs = '儀器故障，超過一個月!'
                line_bot_api.reply_message(event.reply_token,TextSendMessage(text=wmgs))
            else:
                wl_data = Gwl_data()
                wl24 = Wl24f()
                fig = plt.figure(figsize=(9,4))
                ax2 = fig.add_subplot(1,1,1)
                fig.subplots_adjust(bottom=0.3)
                plt.plot(wl24['time'],wl24['depth'])
                plt.title('Water Level Date:'+ddt, fontdict={'fontsize':12})
                ax2.set_xlabel(r'time',fontdict={'fontsize':12})
                ax2.set_ylabel(r'cm',fontdict={'fontsize':12})
                plt.grid()
                try:
                    ax2.set_ylim([0, max(wl24['depth'])])
                    ax2.set_yticks(np.arange(min(wl24['depth']), max(wl24['depth'])+1))
                    ax2.set_xlim([min(wl24['time']),max(wl24['time'])])
                    ax2.xaxis.set_major_locator(mdates.HourLocator(interval=1))
                    ax2.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d %H'))
                except:
                    pass
                plt.setp(ax2.get_xticklabels(), rotation=60, horizontalalignment='right')
                plt.savefig('ddd.png')
                plt.close()
                path = 'ddd.png' 
                im = pyimgur.Imgur(client_id)
                upload=im.upload_image(path, title='test')
                imgurl = upload.link
                line_bot_api.reply_message(event.reply_token,ImageSendMessage(original_content_url=imgurl,preview_image_url=imgurl))
        if backdata == '歷史水位圖2':
            dt = event.postback.params.get('datetime')
            aaa = str(dt)
            ddt = aaa[:4]+aaa[5:7]+aaa[8:10]+aaa[11:13]+aaa[14:]
            html = Test(7506,ddt)
            if '今天沒有資料' in html:
                wl_data = Gwl_data()
                wl24=Produce_wl(wl_data)
                fig = plt.figure(figsize=(9,4))
                ax2 = fig.add_subplot(1,1,1)
                fig.subplots_adjust(bottom=0.3)
                plt.plot(wl24['time'],wl24['depth'])
                plt.title('Water Level Date:'+max(wl24['time']).strftime('%Y-%m-%d'), fontdict={'fontsize':12})
                ax2.set_xlabel(r'time',fontdict={'fontsize':12})
                ax2.set_ylabel(r'cm',fontdict={'fontsize':12})
                plt.grid()
                try:
                    ax2.set_ylim([0, max(wl24['depth'])])
                    ax2.set_yticks(np.arange(min(wl24['depth']), max(wl24['depth'])+1))
                    ax2.set_xlim([min(wl24['time']),max(wl24['time'])])
                    ax2.xaxis.set_major_locator(mdates.HourLocator(interval=1))
                    ax2.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d %H'))
                except:
                    pass
                ax2.xaxis.set_major_locator(mdates.HourLocator(interval=1))
                ax2.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d %H'))
                plt.setp(ax2.get_xticklabels(), rotation=60, horizontalalignment='right')
                plt.savefig('ddd.png')
                plt.close()
                path = 'ddd.png' 
                im = pyimgur.Imgur(client_id)
                upload=im.upload_image(path, title='test')
                imgurl = upload.link
                line_bot_api.reply_message(event.reply_token,ImageSendMessage(original_content_url=imgurl,preview_image_url=imgurl))
            elif '儀器故障，超過一個月!' in html:
                wmgs = '儀器故障，超過一個月!'
                line_bot_api.reply_message(event.reply_token,TextSendMessage(text=wmgs))
            else:
                wl_data = Gwl_data()
                wl24 = Wl24f()
                fig = plt.figure(figsize=(9,4))
                ax2 = fig.add_subplot(1,1,1)
                fig.subplots_adjust(bottom=0.3)
                plt.plot(wl24['time'],wl24['depth'])
                plt.title('Water Level Date:'+ddt, fontdict={'fontsize':12})
                ax2.set_xlabel(r'time',fontdict={'fontsize':12})
                ax2.set_ylabel(r'cm',fontdict={'fontsize':12})
                plt.grid()
                try:
                    ax2.set_ylim([0, max(wl24['depth'])])
                    ax2.set_yticks(np.arange(min(wl24['depth']), max(wl24['depth'])+1))
                    ax2.set_xlim([min(wl24['time']),max(wl24['time'])])
                    ax2.xaxis.set_major_locator(mdates.HourLocator(interval=1))
                    ax2.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d %H'))
                except:
                    pass
                plt.setp(ax2.get_xticklabels(), rotation=60, horizontalalignment='right')
                plt.savefig('ddd.png')
                plt.close()
                path = 'ddd.png' 
                im = pyimgur.Imgur(client_id)
                upload=im.upload_image(path, title='test')
                imgurl = upload.link
                line_bot_api.reply_message(event.reply_token,ImageSendMessage(original_content_url=imgurl,preview_image_url=imgurl))
        if backdata == '歷史水位圖3':
            dt = event.postback.params.get('datetime')
            aaa = str(dt)
            ddt = aaa[:4]+aaa[5:7]+aaa[8:10]+aaa[11:13]+aaa[14:]
            html = Test(7505,ddt)
            if '今天沒有資料' in html:
                wl_data = Gwl_data()
                wl24=Produce_wl(wl_data)
                fig = plt.figure(figsize=(9,4))
                ax2 = fig.add_subplot(1,1,1)
                fig.subplots_adjust(bottom=0.3)
                plt.plot(wl24['time'],wl24['depth'])
                plt.title('Water Level Date:'+max(wl24['time']).strftime('%Y-%m-%d'), fontdict={'fontsize':12})
                ax2.set_xlabel(r'time',fontdict={'fontsize':12})
                ax2.set_ylabel(r'cm',fontdict={'fontsize':12})
                plt.grid()
                try:
                    ax2.set_ylim([0, max(wl24['depth'])])
                    ax2.set_yticks(np.arange(min(wl24['depth']), max(wl24['depth'])+1))
                    ax2.set_xlim([min(wl24['time']),max(wl24['time'])])
                    ax2.xaxis.set_major_locator(mdates.HourLocator(interval=1))
                    ax2.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d %H'))
                except:
                    pass
                ax2.xaxis.set_major_locator(mdates.HourLocator(interval=1))
                ax2.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d %H'))
                plt.setp(ax2.get_xticklabels(), rotation=60, horizontalalignment='right')
                plt.savefig('ddd.png')
                plt.close()
                path = 'ddd.png' 
                im = pyimgur.Imgur(client_id)
                upload=im.upload_image(path, title='test')
                imgurl = upload.link
                line_bot_api.reply_message(event.reply_token,ImageSendMessage(original_content_url=imgurl,preview_image_url=imgurl))
            elif '儀器故障，超過一個月!' in html:
                wmgs = '儀器故障，超過一個月!'
                line_bot_api.reply_message(event.reply_token,TextSendMessage(text=wmgs))
            else:
                wl_data = Gwl_data()
                wl24 = Wl24f()
                fig = plt.figure(figsize=(9,4))
                ax2 = fig.add_subplot(1,1,1)
                fig.subplots_adjust(bottom=0.3)
                plt.plot(wl24['time'],wl24['depth'])
                plt.title('Water Level Date:'+ddt, fontdict={'fontsize':12})
                ax2.set_xlabel(r'time',fontdict={'fontsize':12})
                ax2.set_ylabel(r'cm',fontdict={'fontsize':12})
                plt.grid()
                try:
                    ax2.set_ylim([0, max(wl24['depth'])])
                    ax2.set_yticks(np.arange(min(wl24['depth']), max(wl24['depth'])+1))
                    ax2.set_xlim([min(wl24['time']),max(wl24['time'])])
                    ax2.xaxis.set_major_locator(mdates.HourLocator(interval=1))
                    ax2.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d %H'))
                except:
                    pass
                plt.setp(ax2.get_xticklabels(), rotation=60, horizontalalignment='right')
                plt.savefig('ddd.png')
                plt.close()
                path = 'ddd.png' 
                im = pyimgur.Imgur(client_id)
                upload=im.upload_image(path, title='test')
                imgurl = upload.link
                line_bot_api.reply_message(event.reply_token,ImageSendMessage(original_content_url=imgurl,preview_image_url=imgurl))
        if backdata == '歷史水位圖4':
            dt = event.postback.params.get('datetime')
            aaa = str(dt)
            ddt = aaa[:4]+aaa[5:7]+aaa[8:10]+aaa[11:13]+aaa[14:]
            html = Test(7507,ddt)
            if '今天沒有資料' in html:
                wl_data = Gwl_data()
                wl24=Produce_wl(wl_data)
                fig = plt.figure(figsize=(9,4))
                ax2 = fig.add_subplot(1,1,1)
                fig.subplots_adjust(bottom=0.3)
                plt.plot(wl24['time'],wl24['depth'])
                plt.title('Water Level Date:'+max(wl24['time']).strftime('%Y-%m-%d'), fontdict={'fontsize':12})
                ax2.set_xlabel(r'time',fontdict={'fontsize':12})
                ax2.set_ylabel(r'cm',fontdict={'fontsize':12})
                plt.grid()
                try:
                    ax2.set_ylim([0, max(wl24['depth'])])
                    ax2.set_yticks(np.arange(min(wl24['depth']), max(wl24['depth'])+1))
                    ax2.set_xlim([min(wl24['time']),max(wl24['time'])])
                    ax2.xaxis.set_major_locator(mdates.HourLocator(interval=1))
                    ax2.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d %H'))
                except:
                    pass
                ax2.xaxis.set_major_locator(mdates.HourLocator(interval=1))
                ax2.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d %H'))
                plt.setp(ax2.get_xticklabels(), rotation=60, horizontalalignment='right')
                plt.savefig('ddd.png')
                plt.close()
                path = 'ddd.png' 
                im = pyimgur.Imgur(client_id)
                upload=im.upload_image(path, title='test')
                imgurl = upload.link
                line_bot_api.reply_message(event.reply_token,ImageSendMessage(original_content_url=imgurl,preview_image_url=imgurl))
            elif '儀器故障，超過一個月!' in html:
                wmgs = '儀器故障，超過一個月!'
                line_bot_api.reply_message(event.reply_token,TextSendMessage(text=wmgs))
            else:
                wl_data = Gwl_data()
                wl24 = Wl24f()
                fig = plt.figure(figsize=(9,4))
                ax2 = fig.add_subplot(1,1,1)
                fig.subplots_adjust(bottom=0.3)
                plt.plot(wl24['time'],wl24['depth'])
                plt.title('Water Level Date:'+ddt, fontdict={'fontsize':12})
                ax2.set_xlabel(r'time',fontdict={'fontsize':12})
                ax2.set_ylabel(r'cm',fontdict={'fontsize':12})
                plt.grid()
                try:
                    ax2.set_ylim([0, max(wl24['depth'])])
                    ax2.set_yticks(np.arange(min(wl24['depth']), max(wl24['depth'])+1))
                    ax2.set_xlim([min(wl24['time']),max(wl24['time'])])
                    ax2.xaxis.set_major_locator(mdates.HourLocator(interval=1))
                    ax2.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d %H'))
                except:
                    pass
                plt.setp(ax2.get_xticklabels(), rotation=60, horizontalalignment='right')
                plt.savefig('ddd.png')
                plt.close()
                path = 'ddd.png' 
                im = pyimgur.Imgur(client_id)
                upload=im.upload_image(path, title='test')
                imgurl = upload.link
                line_bot_api.reply_message(event.reply_token,ImageSendMessage(original_content_url=imgurl,preview_image_url=imgurl))
#歷史雨量
        if backdata == '歷史雨量圖1':
            dt = event.postback.params.get('datetime')
            aaa = str(dt)
            ddt = aaa[:4]+aaa[5:7]+aaa[8:10]+aaa[11:13]+aaa[14:]
            html = Test(3040,ddt)
            if '今天沒有資料' in html:
                rg_data = Rg_data()
                rg24 = Produce_rg(rg_data)
                fig = plt.figure(figsize=(9,4))
                ax2 = fig.add_subplot(1,1,1)
                fig.subplots_adjust(bottom=0.3)
                plt.bar(rg24['time'],rg24['hour_value'],width=0.007, color='red')
                plt.title('Rainfall Date:'+max(rg24['time']).strftime('%Y-%m-%d'), fontdict={'fontsize':12})
                ax2.set_xlabel(r'time',fontdict={'fontsize':12})
                ax2.set_ylabel(r'mm/hr',fontdict={'fontsize':12})
                plt.grid()
                try:
                    ax2.set_ylim([0, max(rg24['hour_value'])])
                    ax2.set_yticks(np.arange(min(rg24['hour_value']), max(rg24['hour_value'])+1))
                except:
                    pass
                ax2.xaxis.set_major_locator(mdates.HourLocator(interval=1))
                ax2.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d %H'))
                plt.setp(ax2.get_xticklabels(), rotation=60, horizontalalignment='right')
                plt.savefig('ddd.png')
                plt.close()
                path = 'ddd.png' 
                im = pyimgur.Imgur(client_id)
                upload=im.upload_image(path, title='test')
                imgurl = upload.link
                line_bot_api.reply_message(event.reply_token,ImageSendMessage(original_content_url=imgurl,preview_image_url=imgurl))
            elif '儀器故障，超過一個月!' in html:
                wmgs = '儀器故障，超過一個月!'
                line_bot_api.reply_message(event.reply_token,TextSendMessage(text=wmgs))
            else:
                rg_data=Rg_data()
                rg24 = Rg24f()
                fig = plt.figure(figsize=(9,4))
                ax2 = fig.add_subplot(1,1,1)
                fig.subplots_adjust(bottom=0.3)
                plt.bar(rg24['time'],rg24['hour_value'],width=0.007, color='red')
                plt.title('Rainfall Date:'+ddt, fontdict={'fontsize':12})
                ax2.set_xlabel(r'time',fontdict={'fontsize':12})
                ax2.set_ylabel(r'mm/hr',fontdict={'fontsize':12})
                plt.grid()
                try:
                    ax2.set_ylim([0, max(rg24['hour_value'])])
                    ax2.set_yticks(np.arange(min(rg24['hour_value']), max(rg24['hour_value'])+1))
                except:
                    pass
                ax2.xaxis.set_major_locator(mdates.HourLocator(interval=1))
                ax2.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d %H'))
                #plt.xlim([min(rg24.index),max(rg24.index)])
                plt.setp(ax2.get_xticklabels(), rotation=60, horizontalalignment='right')
                plt.savefig('ddd.png')
                plt.close()
                path = 'ddd.png' 
                im = pyimgur.Imgur(client_id)
                upload=im.upload_image(path, title='test')
                imgurl = upload.link
                line_bot_api.reply_message(event.reply_token,ImageSendMessage(original_content_url=imgurl,preview_image_url=imgurl))
        if backdata == '歷史雨量圖2':
            dt = event.postback.params.get('datetime')
            aaa = str(dt)
            ddt = aaa[:4]+aaa[5:7]+aaa[8:10]+aaa[11:13]+aaa[14:]
            html = Test(3039,ddt)
            if '今天沒有資料' in html:
                rg_data = Rg_data()
                rg24 = Produce_rg(rg_data)
                fig = plt.figure(figsize=(9,4))
                ax2 = fig.add_subplot(1,1,1)
                fig.subplots_adjust(bottom=0.3)
                plt.bar(rg24['time'],rg24['hour_value'],width=0.007, color='red')
                plt.title('Rainfall Date:'+max(rg24['time']).strftime('%Y-%m-%d'), fontdict={'fontsize':12})
                ax2.set_xlabel(r'time',fontdict={'fontsize':12})
                ax2.set_ylabel(r'mm/hr',fontdict={'fontsize':12})
                plt.grid()
                try:
                    ax2.set_ylim([0, max(rg24['hour_value'])])
                    ax2.set_yticks(np.arange(min(rg24['hour_value']), max(rg24['hour_value'])+1))
                except:
                    pass
                ax2.xaxis.set_major_locator(mdates.HourLocator(interval=1))
                ax2.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d %H'))
                plt.setp(ax2.get_xticklabels(), rotation=60, horizontalalignment='right')
                plt.savefig('ddd.png')
                plt.close()
                path = 'ddd.png' 
                im = pyimgur.Imgur(client_id)
                upload=im.upload_image(path, title='test')
                imgurl = upload.link
                line_bot_api.reply_message(event.reply_token,ImageSendMessage(original_content_url=imgurl,preview_image_url=imgurl))
            elif '儀器故障，超過一個月!' in html:
                wmgs = '儀器故障，超過一個月!'
                line_bot_api.reply_message(event.reply_token,TextSendMessage(text=wmgs))
            else:
                rg_data=Rg_data()
                rg24 = Rg24f()
                fig = plt.figure(figsize=(9,4))
                ax2 = fig.add_subplot(1,1,1)
                fig.subplots_adjust(bottom=0.3)
                plt.bar(rg24['time'],rg24['hour_value'],width=0.007, color='red')
                plt.title('Rainfall Date:'+ddt, fontdict={'fontsize':12})
                ax2.set_xlabel(r'time',fontdict={'fontsize':12})
                ax2.set_ylabel(r'mm/hr',fontdict={'fontsize':12})
                plt.grid()
                try:
                    ax2.set_ylim([0, max(rg24['hour_value'])])
                    ax2.set_yticks(np.arange(min(rg24['hour_value']), max(rg24['hour_value'])+1))
                except:
                    pass
                ax2.xaxis.set_major_locator(mdates.HourLocator(interval=1))
                ax2.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d %H'))
                #plt.xlim([min(rg24.index),max(rg24.index)])
                plt.setp(ax2.get_xticklabels(), rotation=60, horizontalalignment='right')
                plt.savefig('ddd.png')
                plt.close()
                path = 'ddd.png' 
                im = pyimgur.Imgur(client_id)
                upload=im.upload_image(path, title='test')
                imgurl = upload.link
                line_bot_api.reply_message(event.reply_token,ImageSendMessage(original_content_url=imgurl,preview_image_url=imgurl))         
        if backdata == '歷史雨量圖3':
            dt = event.postback.params.get('datetime')
            aaa = str(dt)
            ddt = aaa[:4]+aaa[5:7]+aaa[8:10]+aaa[11:13]+aaa[14:]
            html = Test(3038,ddt)
            if '今天沒有資料' in html:
                rg_data = Rg_data()
                rg24 = Produce_rg(rg_data)
                fig = plt.figure(figsize=(9,4))
                ax2 = fig.add_subplot(1,1,1)
                fig.subplots_adjust(bottom=0.3)
                plt.bar(rg24['time'],rg24['hour_value'],width=0.007, color='red')
                plt.title('Rainfall Date:'+max(rg24['time']).strftime('%Y-%m-%d'), fontdict={'fontsize':12})
                ax2.set_xlabel(r'time',fontdict={'fontsize':12})
                ax2.set_ylabel(r'mm/hr',fontdict={'fontsize':12})
                plt.grid()
                try:
                    ax2.set_ylim([0, max(rg24['hour_value'])])
                    ax2.set_yticks(np.arange(min(rg24['hour_value']), max(rg24['hour_value'])+1))
                except:
                    pass
                ax2.xaxis.set_major_locator(mdates.HourLocator(interval=1))
                ax2.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d %H'))
                plt.setp(ax2.get_xticklabels(), rotation=60, horizontalalignment='right')
                plt.savefig('ddd.png')
                plt.close()
                path = 'ddd.png' 
                im = pyimgur.Imgur(client_id)
                upload=im.upload_image(path, title='test')
                imgurl = upload.link
                line_bot_api.reply_message(event.reply_token,ImageSendMessage(original_content_url=imgurl,preview_image_url=imgurl))
            elif '儀器故障，超過一個月!' in html:
                wmgs = '儀器故障，超過一個月!'
                line_bot_api.reply_message(event.reply_token,TextSendMessage(text=wmgs))
            else:
                rg_data=Rg_data()
                rg24 = Rg24f()
                fig = plt.figure(figsize=(9,4))
                ax2 = fig.add_subplot(1,1,1)
                fig.subplots_adjust(bottom=0.3)
                plt.bar(rg24['time'],rg24['hour_value'],width=0.007, color='red')
                plt.title('Rainfall Date:'+ddt, fontdict={'fontsize':12})
                ax2.set_xlabel(r'time',fontdict={'fontsize':12})
                ax2.set_ylabel(r'mm/hr',fontdict={'fontsize':12})
                plt.grid()
                try:
                    ax2.set_ylim([0, max(rg24['hour_value'])])
                    ax2.set_yticks(np.arange(min(rg24['hour_value']), max(rg24['hour_value'])+1))
                except:
                    pass
                ax2.xaxis.set_major_locator(mdates.HourLocator(interval=1))
                ax2.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d %H'))
                #plt.xlim([min(rg24.index),max(rg24.index)])
                plt.setp(ax2.get_xticklabels(), rotation=60, horizontalalignment='right')
                plt.savefig('ddd.png')
                plt.close()
                path = 'ddd.png' 
                im = pyimgur.Imgur(client_id)
                upload=im.upload_image(path, title='test')
                imgurl = upload.link
                line_bot_api.reply_message(event.reply_token,ImageSendMessage(original_content_url=imgurl,preview_image_url=imgurl))
        if backdata == '歷史雨量圖4':
            dt = event.postback.params.get('datetime')
            aaa = str(dt)
            ddt = aaa[:4]+aaa[5:7]+aaa[8:10]+aaa[11:13]+aaa[14:]
            html = Test(2026,ddt)
            if '今天沒有資料' in html:
                rg_data = Rg_data()
                rg24 = Produce_rg(rg_data)
                fig = plt.figure(figsize=(9,4))
                ax2 = fig.add_subplot(1,1,1)
                fig.subplots_adjust(bottom=0.3)
                plt.bar(rg24['time'],rg24['hour_value'],width=0.007, color='red')
                plt.title('Rainfall Date:'+max(rg24['time']).strftime('%Y-%m-%d'), fontdict={'fontsize':12})
                ax2.set_xlabel(r'time',fontdict={'fontsize':12})
                ax2.set_ylabel(r'mm/hr',fontdict={'fontsize':12})
                plt.grid()
                try:
                    ax2.set_ylim([0, max(rg24['hour_value'])])
                    ax2.set_yticks(np.arange(min(rg24['hour_value']), max(rg24['hour_value'])+1))
                except:
                    pass
                ax2.xaxis.set_major_locator(mdates.HourLocator(interval=1))
                ax2.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d %H'))
                plt.setp(ax2.get_xticklabels(), rotation=60, horizontalalignment='right')
                plt.savefig('ddd.png')
                plt.close()
                path = 'ddd.png' 
                im = pyimgur.Imgur(client_id)
                upload=im.upload_image(path, title='test')
                imgurl = upload.link
                line_bot_api.reply_message(event.reply_token,ImageSendMessage(original_content_url=imgurl,preview_image_url=imgurl))
            elif '儀器故障，超過一個月!' in html:
                wmgs = '儀器故障，超過一個月!'
                line_bot_api.reply_message(event.reply_token,TextSendMessage(text=wmgs))
            else:
                rg_data=Rg_data()
                rg24 = Rg24f()
                fig = plt.figure(figsize=(9,4))
                ax2 = fig.add_subplot(1,1,1)
                fig.subplots_adjust(bottom=0.3)
                plt.bar(rg24['time'],rg24['hour_value'],width=0.007, color='red')
                plt.title('Rainfall Date:'+ddt, fontdict={'fontsize':12})
                ax2.set_xlabel(r'time',fontdict={'fontsize':12})
                ax2.set_ylabel(r'mm/hr',fontdict={'fontsize':12})
                plt.grid()
                try:
                    ax2.set_ylim([0, max(rg24['hour_value'])])
                    ax2.set_yticks(np.arange(min(rg24['hour_value']), max(rg24['hour_value'])+1))
                except:
                    pass
                ax2.xaxis.set_major_locator(mdates.HourLocator(interval=1))
                ax2.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d %H'))
                #plt.xlim([min(rg24.index),max(rg24.index)])
                plt.setp(ax2.get_xticklabels(), rotation=60, horizontalalignment='right')
                plt.savefig('ddd.png')
                plt.close()
                path = 'ddd.png' 
                im = pyimgur.Imgur(client_id)
                upload=im.upload_image(path, title='test')
                imgurl = upload.link
                line_bot_api.reply_message(event.reply_token,ImageSendMessage(original_content_url=imgurl,preview_image_url=imgurl))
#test
        if backdata == '當下水位':  
            Test(7507,)
            tt1 = ttq1[0:12]
            wmgs = '介壽村道路淹水感知查詢資訊\n--------------------------------\n目前水位'+dd1+'公分\n(地表高程起算以上)\n最後更新時間：'+tt1
            line_bot_api.reply_message(event.reply_token,TextSendMessage(text=wmgs)) 
        if backdata == '今日水位':
            tz = timezone(timedelta(hours=+8))
            xt = datetime.now(tz).strftime('%Y%m%d%H%M')
            xtt = datetime.now(tz).strftime('%Y-%m-%d')
            Gwl_data(7507,xt)
            wl24.plot()
            fig = plt.figure(figsize=(9,4))
            ax2 = fig.add_subplot(1,1,1)
            fig.subplots_adjust(bottom=0.3)
            plt.plot(wl24.index,wl24['depth'])
            plt.title('Water Level Date:'+xtt, fontdict={'fontsize':12})
            ax2.set_xlabel(r'time',fontdict={'fontsize':12})
            ax2.set_ylabel(r'cm',fontdict={'fontsize':12})
            plt.grid()
            ax2.set_ylim([0, max(wl24['depth'])])
            ax2.set_yticks(np.arange(min(wl24['depth']), max(wl24['depth'])+1, 0.5))
            ax2.xaxis.set_major_locator(mdates.HourLocator(interval=1))
            ax2.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d %H'))
            ax2.set_xlim([min(wl24.index),max(wl24.index)])
            plt.setp(ax2.get_xticklabels(), rotation=60, horizontalalignment='right')
            plt.savefig('ddd.png')
            plt.close()
            path = 'ddd.png' 
            im = pyimgur.Imgur(client_id)
            upload=im.upload_image(path, title='test')
            imgurl = upload.link
            line_bot_api.reply_message(event.reply_token,ImageSendMessage(original_content_url=imgurl,preview_image_url=imgurl))
        if backdata == '今日雨量':
            tz = timezone(timedelta(hours=+8))
            xt = datetime.now(tz).strftime('%Y%m%d%H%M')
            xtt = datetime.now(tz).strftime('%Y-%m-%d')
            Rg_data(3040,xt)
            fig = plt.figure(figsize=(9,4))
            ax2 = fig.add_subplot(1,1,1)
            fig.subplots_adjust(bottom=0.3)
            plt.bar(rg24.index,rg24['hour_value'],width=0.007, color='red')
            plt.title('Rainfall Date:'+xtt, fontdict={'fontsize':12})
            ax2.set_xlabel(r'time',fontdict={'fontsize':12})
            ax2.set_ylabel(r'mm/hr',fontdict={'fontsize':12})
            plt.grid()
            ax2.set_ylim([0, max(rg24['hour_value'])])
            ax2.set_yticks(np.arange(min(rg24['hour_value']), max(rg24['hour_value'])+1, 0.5))
            ax2.xaxis.set_major_locator(mdates.HourLocator(interval=1))
            ax2.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d %H'))
            #plt.xlim([min(rg24.index),max(rg24.index)])
            plt.setp(ax2.get_xticklabels(), rotation=60, horizontalalignment='right')
            plt.savefig('ddd.png')
            plt.close()
            path = 'ddd.png' 
            im = pyimgur.Imgur(client_id)
            upload=im.upload_image(path, title='test')
            imgurl = upload.link
            line_bot_api.reply_message(event.reply_token,ImageSendMessage(original_content_url=imgurl,preview_image_url=imgurl))
#介壽村
        if backdata == '當下水位1':        
            loc1 = 'http://AWS.amazonaws.com/data'
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
        if backdata == '今日水位1':
            tz = timezone(timedelta(hours=+8))
            xt = datetime.now(tz).strftime('%Y%m%d%H%M')
            xtt = datetime.now(tz).strftime('%Y-%m-%d')
            html = Test(7504,xt)
            if '今天沒有資料' in html:
                wl_data = Gwl_data()
                wl24=Produce_wl(wl_data)
                fig = plt.figure(figsize=(9,4))
                ax2 = fig.add_subplot(1,1,1)
                fig.subplots_adjust(bottom=0.3)
                plt.plot(wl24['time'],wl24['depth'])
                plt.title('Water Level Date:'+max(wl24['time']).strftime('%Y-%m-%d'), fontdict={'fontsize':12})
                ax2.set_xlabel(r'time',fontdict={'fontsize':12})
                ax2.set_ylabel(r'cm',fontdict={'fontsize':12})
                plt.grid()
                try:
                    ax2.set_ylim([0, max(wl24['depth'])])
                    ax2.set_yticks(np.arange(min(wl24['depth']), max(wl24['depth'])+1))
                    ax2.set_xlim([min(wl24['time']),max(wl24['time'])])
                    ax2.xaxis.set_major_locator(mdates.HourLocator(interval=1))
                    ax2.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d %H'))
                except:
                    pass
                ax2.xaxis.set_major_locator(mdates.HourLocator(interval=1))
                ax2.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d %H'))
                plt.setp(ax2.get_xticklabels(), rotation=60, horizontalalignment='right')
                plt.savefig('ddd.png')
                plt.close()
                path = 'ddd.png' 
                im = pyimgur.Imgur(client_id)
                upload=im.upload_image(path, title='test')
                imgurl = upload.link
                line_bot_api.reply_message(event.reply_token,ImageSendMessage(original_content_url=imgurl,preview_image_url=imgurl))
            elif '儀器故障，超過一個月!' in html:
                wmgs = '儀器故障，超過一個月!'
                line_bot_api.reply_message(event.reply_token,TextSendMessage(text=wmgs))
            else:
                wl_data = Gwl_data()
                wl24 = Wl24f()
                fig = plt.figure(figsize=(9,4))
                ax2 = fig.add_subplot(1,1,1)
                fig.subplots_adjust(bottom=0.3)
                plt.plot(wl24['time'],wl24['depth'])
                plt.title('Water Level Date:'+xtt, fontdict={'fontsize':12})
                ax2.set_xlabel(r'time',fontdict={'fontsize':12})
                ax2.set_ylabel(r'cm',fontdict={'fontsize':12})
                plt.grid()
                try:
                    ax2.set_ylim([0, max(wl24['depth'])])
                    ax2.set_yticks(np.arange(min(wl24['depth']), max(wl24['depth'])+1))
                    ax2.set_xlim([min(wl24['time']),max(wl24['time'])])
                    ax2.xaxis.set_major_locator(mdates.HourLocator(interval=1))
                    ax2.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d %H'))
                except:
                    pass
                plt.setp(ax2.get_xticklabels(), rotation=60, horizontalalignment='right')
                plt.savefig('ddd.png')
                plt.close()
                path = 'ddd.png' 
                im = pyimgur.Imgur(client_id)
                upload=im.upload_image(path, title='test')
                imgurl = upload.link
                line_bot_api.reply_message(event.reply_token,ImageSendMessage(original_content_url=imgurl,preview_image_url=imgurl))
        if backdata == '今日雨量1':
            tz = timezone(timedelta(hours=+8))
            xt = datetime.now(tz).strftime('%Y%m%d%H%M')
            xtt = datetime.now(tz).strftime('%Y-%m-%d')
            html = Test(3040,xt)
            if '今天沒有資料' in html:
                rg_data = Rg_data()
                rg24 = Produce_rg(rg_data)
                fig = plt.figure(figsize=(9,4))
                ax2 = fig.add_subplot(1,1,1)
                fig.subplots_adjust(bottom=0.3)
                plt.bar(rg24['time'],rg24['hour_value'],width=0.007, color='red')
                plt.title('Rainfall Date:'+max(rg24['time']).strftime('%Y-%m-%d'), fontdict={'fontsize':12})
                ax2.set_xlabel(r'time',fontdict={'fontsize':12})
                ax2.set_ylabel(r'mm/hr',fontdict={'fontsize':12})
                plt.grid()
                try:
                    ax2.set_ylim([0, max(rg24['hour_value'])])
                    ax2.set_yticks(np.arange(min(rg24['hour_value']), max(rg24['hour_value'])+1))
                except:
                    pass
                ax2.xaxis.set_major_locator(mdates.HourLocator(interval=1))
                ax2.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d %H'))
                plt.setp(ax2.get_xticklabels(), rotation=60, horizontalalignment='right')
                plt.savefig('ddd.png')
                plt.close()
                path = 'ddd.png' 
                im = pyimgur.Imgur(client_id)
                upload=im.upload_image(path, title='test')
                imgurl = upload.link
                line_bot_api.reply_message(event.reply_token,ImageSendMessage(original_content_url=imgurl,preview_image_url=imgurl))
            elif '儀器故障，超過一個月!' in html:
                wmgs = '儀器故障，超過一個月!'
                line_bot_api.reply_message(event.reply_token,TextSendMessage(text=wmgs))
            else:
                rg_data=Rg_data()
                rg24 = Rg24f()
                fig = plt.figure(figsize=(9,4))
                ax2 = fig.add_subplot(1,1,1)
                fig.subplots_adjust(bottom=0.3)
                plt.bar(rg24['time'],rg24['hour_value'],width=0.007, color='red')
                plt.title('Rainfall Date:'+xtt, fontdict={'fontsize':12})
                ax2.set_xlabel(r'time',fontdict={'fontsize':12})
                ax2.set_ylabel(r'mm/hr',fontdict={'fontsize':12})
                plt.grid()
                try:
                    ax2.set_ylim([0, max(rg24['hour_value'])])
                    ax2.set_yticks(np.arange(min(rg24['hour_value']), max(rg24['hour_value'])+1))
                except:
                    pass
                ax2.xaxis.set_major_locator(mdates.HourLocator(interval=1))
                ax2.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d %H'))
                #plt.xlim([min(rg24.index),max(rg24.index)])
                plt.setp(ax2.get_xticklabels(), rotation=60, horizontalalignment='right')
                plt.savefig('ddd.png')
                plt.close()
                path = 'ddd.png' 
                im = pyimgur.Imgur(client_id)
                upload=im.upload_image(path, title='test')
                imgurl = upload.link
                line_bot_api.reply_message(event.reply_token,ImageSendMessage(original_content_url=imgurl,preview_image_url=imgurl))
#復興村
        if backdata == '當下水位2':        
            loc1 = 'http://AWS.amazonaws.com/data'
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
        if backdata == '今日水位2':
            tz = timezone(timedelta(hours=+8))
            xt = datetime.now(tz).strftime('%Y%m%d%H%M')
            xtt = datetime.now(tz).strftime('%Y-%m-%d')
            html = Test(7506,xt)
            if '今天沒有資料' in html:
                wl_data = Gwl_data()
                wl24=Produce_wl(wl_data)
                fig = plt.figure(figsize=(9,4))
                ax2 = fig.add_subplot(1,1,1)
                fig.subplots_adjust(bottom=0.3)
                plt.plot(wl24['time'],wl24['depth'])
                plt.title('Water Level Date:'+max(wl24['time']).strftime('%Y-%m-%d'), fontdict={'fontsize':12})
                ax2.set_xlabel(r'time',fontdict={'fontsize':12})
                ax2.set_ylabel(r'cm',fontdict={'fontsize':12})
                plt.grid()
                try:
                    ax2.set_ylim([0, max(wl24['depth'])])
                    ax2.set_yticks(np.arange(min(wl24['depth']), max(wl24['depth'])+1))
                    ax2.set_xlim([min(wl24['time']),max(wl24['time'])])
                    ax2.xaxis.set_major_locator(mdates.HourLocator(interval=1))
                    ax2.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d %H'))
                except:
                    pass
                ax2.xaxis.set_major_locator(mdates.HourLocator(interval=1))
                ax2.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d %H'))
                plt.setp(ax2.get_xticklabels(), rotation=60, horizontalalignment='right')
                plt.savefig('ddd.png')
                plt.close()
                path = 'ddd.png' 
                im = pyimgur.Imgur(client_id)
                upload=im.upload_image(path, title='test')
                imgurl = upload.link
                line_bot_api.reply_message(event.reply_token,ImageSendMessage(original_content_url=imgurl,preview_image_url=imgurl))
            elif '儀器故障，超過一個月!' in html:
                wmgs = '儀器故障，超過一個月!'
                line_bot_api.reply_message(event.reply_token,TextSendMessage(text=wmgs))
            else:
                wl_data = Gwl_data()
                wl24 = Wl24f()
                fig = plt.figure(figsize=(9,4))
                ax2 = fig.add_subplot(1,1,1)
                fig.subplots_adjust(bottom=0.3)
                plt.plot(wl24['time'],wl24['depth'])
                plt.title('Water Level Date:'+xtt, fontdict={'fontsize':12})
                ax2.set_xlabel(r'time',fontdict={'fontsize':12})
                ax2.set_ylabel(r'cm',fontdict={'fontsize':12})
                plt.grid()
                try:
                    ax2.set_ylim([0, max(wl24['depth'])])
                    ax2.set_yticks(np.arange(min(wl24['depth']), max(wl24['depth'])+1))
                    ax2.set_xlim([min(wl24['time']),max(wl24['time'])])
                    ax2.xaxis.set_major_locator(mdates.HourLocator(interval=1))
                    ax2.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d %H'))
                except:
                    pass
                plt.setp(ax2.get_xticklabels(), rotation=60, horizontalalignment='right')
                plt.savefig('ddd.png')
                plt.close()
                path = 'ddd.png' 
                im = pyimgur.Imgur(client_id)
                upload=im.upload_image(path, title='test')
                imgurl = upload.link
                line_bot_api.reply_message(event.reply_token,ImageSendMessage(original_content_url=imgurl,preview_image_url=imgurl))
        if backdata == '今日雨量2':
            tz = timezone(timedelta(hours=+8))
            xt = datetime.now(tz).strftime('%Y%m%d%H%M')
            xtt = datetime.now(tz).strftime('%Y-%m-%d')
            html = Test(3039,xt)
            if '今天沒有資料' in html:
                rg_data = Rg_data()
                rg24 = Produce_rg(rg_data)
                fig = plt.figure(figsize=(9,4))
                ax2 = fig.add_subplot(1,1,1)
                fig.subplots_adjust(bottom=0.3)
                plt.bar(rg24['time'],rg24['hour_value'],width=0.007, color='red')
                plt.title('Rainfall Date:'+max(rg24['time']).strftime('%Y-%m-%d'), fontdict={'fontsize':12})
                ax2.set_xlabel(r'time',fontdict={'fontsize':12})
                ax2.set_ylabel(r'mm/hr',fontdict={'fontsize':12})
                plt.grid()
                try:
                    ax2.set_ylim([0, max(rg24['hour_value'])])
                    ax2.set_yticks(np.arange(min(rg24['hour_value']), max(rg24['hour_value'])+1))
                except:
                    pass
                ax2.xaxis.set_major_locator(mdates.HourLocator(interval=1))
                ax2.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d %H'))
                plt.setp(ax2.get_xticklabels(), rotation=60, horizontalalignment='right')
                plt.savefig('ddd.png')
                plt.close()
                path = 'ddd.png' 
                im = pyimgur.Imgur(client_id)
                upload=im.upload_image(path, title='test')
                imgurl = upload.link
                line_bot_api.reply_message(event.reply_token,ImageSendMessage(original_content_url=imgurl,preview_image_url=imgurl))
            elif '儀器故障，超過一個月!' in html:
                wmgs = '儀器故障，超過一個月!'
                line_bot_api.reply_message(event.reply_token,TextSendMessage(text=wmgs))
            else:
                rg_data=Rg_data()
                rg24 = Rg24f()
                fig = plt.figure(figsize=(9,4))
                ax2 = fig.add_subplot(1,1,1)
                fig.subplots_adjust(bottom=0.3)
                plt.bar(rg24['time'],rg24['hour_value'],width=0.007, color='red')
                plt.title('Rainfall Date:'+xtt, fontdict={'fontsize':12})
                ax2.set_xlabel(r'time',fontdict={'fontsize':12})
                ax2.set_ylabel(r'mm/hr',fontdict={'fontsize':12})
                plt.grid()
                try:
                    ax2.set_ylim([0, max(rg24['hour_value'])])
                    ax2.set_yticks(np.arange(min(rg24['hour_value']), max(rg24['hour_value'])+1))
                except:
                    pass
                ax2.xaxis.set_major_locator(mdates.HourLocator(interval=1))
                ax2.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d %H'))
                #plt.xlim([min(rg24.index),max(rg24.index)])
                plt.setp(ax2.get_xticklabels(), rotation=60, horizontalalignment='right')
                plt.savefig('ddd.png')
                plt.close()
                path = 'ddd.png' 
                im = pyimgur.Imgur(client_id)
                upload=im.upload_image(path, title='test')
                imgurl = upload.link
                line_bot_api.reply_message(event.reply_token,ImageSendMessage(original_content_url=imgurl,preview_image_url=imgurl))
#珠螺村
        if backdata == '當下水位3':        
            loc1 = 'http://AWS.amazonaws.com/data'
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
        if backdata == '今日水位3':
            tz = timezone(timedelta(hours=+8))
            xt = datetime.now(tz).strftime('%Y%m%d%H%M')
            xtt = datetime.now(tz).strftime('%Y-%m-%d')
            html = Test(7505,xt)
            if '今天沒有資料' in html:
                wl_data = Gwl_data()
                wl24=Produce_wl(wl_data)
                fig = plt.figure(figsize=(9,4))
                ax2 = fig.add_subplot(1,1,1)
                fig.subplots_adjust(bottom=0.3)
                plt.plot(wl24['time'],wl24['depth'])
                plt.title('Water Level Date:'+max(wl24['time']).strftime('%Y-%m-%d'), fontdict={'fontsize':12})
                ax2.set_xlabel(r'time',fontdict={'fontsize':12})
                ax2.set_ylabel(r'cm',fontdict={'fontsize':12})
                plt.grid()
                try:
                    ax2.set_ylim([0, max(wl24['depth'])])
                    ax2.set_yticks(np.arange(min(wl24['depth']), max(wl24['depth'])+1))
                    ax2.set_xlim([min(wl24['time']),max(wl24['time'])])
                    ax2.xaxis.set_major_locator(mdates.HourLocator(interval=1))
                    ax2.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d %H'))
                except:
                    pass
                ax2.xaxis.set_major_locator(mdates.HourLocator(interval=1))
                ax2.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d %H'))
                plt.setp(ax2.get_xticklabels(), rotation=60, horizontalalignment='right')
                plt.savefig('ddd.png')
                plt.close()
                path = 'ddd.png' 
                im = pyimgur.Imgur(client_id)
                upload=im.upload_image(path, title='test')
                imgurl = upload.link
                line_bot_api.reply_message(event.reply_token,ImageSendMessage(original_content_url=imgurl,preview_image_url=imgurl))
            elif '儀器故障，超過一個月!' in html:
                wmgs = '儀器故障，超過一個月!'
                line_bot_api.reply_message(event.reply_token,TextSendMessage(text=wmgs))
            else:
                wl_data = Gwl_data()
                wl24 = Wl24f()
                fig = plt.figure(figsize=(9,4))
                ax2 = fig.add_subplot(1,1,1)
                fig.subplots_adjust(bottom=0.3)
                plt.plot(wl24['time'],wl24['depth'])
                plt.title('Water Level Date:'+xtt, fontdict={'fontsize':12})
                ax2.set_xlabel(r'time',fontdict={'fontsize':12})
                ax2.set_ylabel(r'cm',fontdict={'fontsize':12})
                plt.grid()
                try:
                    ax2.set_ylim([0, max(wl24['depth'])])
                    ax2.set_yticks(np.arange(min(wl24['depth']), max(wl24['depth'])+1))
                    ax2.set_xlim([min(wl24['time']),max(wl24['time'])])
                    ax2.xaxis.set_major_locator(mdates.HourLocator(interval=1))
                    ax2.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d %H'))
                except:
                    pass
                plt.setp(ax2.get_xticklabels(), rotation=60, horizontalalignment='right')
                plt.savefig('ddd.png')
                plt.close()
                path = 'ddd.png' 
                im = pyimgur.Imgur(client_id)
                upload=im.upload_image(path, title='test')
                imgurl = upload.link
                line_bot_api.reply_message(event.reply_token,ImageSendMessage(original_content_url=imgurl,preview_image_url=imgurl))
        if backdata == '今日雨量3':
            tz = timezone(timedelta(hours=+8))
            xt = datetime.now(tz).strftime('%Y%m%d%H%M')
            xtt = datetime.now(tz).strftime('%Y-%m-%d')
            html = Test(3038,xt)
            if '今天沒有資料' in html:
                rg_data = Rg_data()
                rg24 = Produce_rg(rg_data)
                fig = plt.figure(figsize=(9,4))
                ax2 = fig.add_subplot(1,1,1)
                fig.subplots_adjust(bottom=0.3)
                plt.bar(rg24['time'],rg24['hour_value'],width=0.007, color='red')
                plt.title('Rainfall Date:'+max(rg24['time']).strftime('%Y-%m-%d'), fontdict={'fontsize':12})
                ax2.set_xlabel(r'time',fontdict={'fontsize':12})
                ax2.set_ylabel(r'mm/hr',fontdict={'fontsize':12})
                plt.grid()
                try:
                    ax2.set_ylim([0, max(rg24['hour_value'])])
                    ax2.set_yticks(np.arange(min(rg24['hour_value']), max(rg24['hour_value'])+1))
                except:
                    pass
                ax2.xaxis.set_major_locator(mdates.HourLocator(interval=1))
                ax2.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d %H'))
                plt.setp(ax2.get_xticklabels(), rotation=60, horizontalalignment='right')
                plt.savefig('ddd.png')
                plt.close()
                path = 'ddd.png' 
                im = pyimgur.Imgur(client_id)
                upload=im.upload_image(path, title='test')
                imgurl = upload.link
                line_bot_api.reply_message(event.reply_token,ImageSendMessage(original_content_url=imgurl,preview_image_url=imgurl))
            elif '儀器故障，超過一個月!' in html:
                wmgs = '儀器故障，超過一個月!'
                line_bot_api.reply_message(event.reply_token,TextSendMessage(text=wmgs))
            else:
                rg_data=Rg_data()
                rg24 = Rg24f()
                fig = plt.figure(figsize=(9,4))
                ax2 = fig.add_subplot(1,1,1)
                fig.subplots_adjust(bottom=0.3)
                plt.bar(rg24['time'],rg24['hour_value'],width=0.007, color='red')
                plt.title('Rainfall Date:'+xtt, fontdict={'fontsize':12})
                ax2.set_xlabel(r'time',fontdict={'fontsize':12})
                ax2.set_ylabel(r'mm/hr',fontdict={'fontsize':12})
                plt.grid()
                try:
                    ax2.set_ylim([0, max(rg24['hour_value'])])
                    ax2.set_yticks(np.arange(min(rg24['hour_value']), max(rg24['hour_value'])+1))
                except:
                    pass
                ax2.xaxis.set_major_locator(mdates.HourLocator(interval=1))
                ax2.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d %H'))
                #plt.xlim([min(rg24.index),max(rg24.index)])
                plt.setp(ax2.get_xticklabels(), rotation=60, horizontalalignment='right')
                plt.savefig('ddd.png')
                plt.close()
                path = 'ddd.png' 
                im = pyimgur.Imgur(client_id)
                upload=im.upload_image(path, title='test')
                imgurl = upload.link
                line_bot_api.reply_message(event.reply_token,ImageSendMessage(original_content_url=imgurl,preview_image_url=imgurl))
#港口
        if backdata == '當下水位4':        
            tz = timezone(timedelta(hours=+8))
            xt = datetime.now(tz).strftime('%Y%m%d')
            loc2 = 'http://AWS.amazonaws.com/data'+xt
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
            wmgs = '港口道路淹水感知查詢資訊\n--------------------------------\n目前水位'+dd2+'公分\n(地表高程起算以上)\n最後更新時間：'+tt2
            line_bot_api.reply_message(event.reply_token,TextSendMessage(text=wmgs))
        if backdata == '今日水位4':
            tz = timezone(timedelta(hours=+8))
            xt = datetime.now(tz).strftime('%Y%m%d%H%M')
            xtt = datetime.now(tz).strftime('%Y-%m-%d')
            html = Test(7507,xt)
            if '今天沒有資料' in html:
                wl_data = Gwl_data()
                wl24=Produce_wl(wl_data)
                fig = plt.figure(figsize=(9,4))
                ax2 = fig.add_subplot(1,1,1)
                fig.subplots_adjust(bottom=0.3)
                plt.plot(wl24['time'],wl24['depth'])
                plt.title('Water Level Date:'+max(wl24['time']).strftime('%Y-%m-%d'), fontdict={'fontsize':12})
                ax2.set_xlabel(r'time',fontdict={'fontsize':12})
                ax2.set_ylabel(r'cm',fontdict={'fontsize':12})
                plt.grid()
                try:
                    ax2.set_ylim([0, max(wl24['depth'])])
                    ax2.set_yticks(np.arange(min(wl24['depth']), max(wl24['depth'])+1))
                    ax2.set_xlim([min(wl24['time']),max(wl24['time'])])
                    ax2.xaxis.set_major_locator(mdates.HourLocator(interval=1))
                    ax2.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d %H'))
                except:
                    pass
                ax2.xaxis.set_major_locator(mdates.HourLocator(interval=1))
                ax2.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d %H'))
                plt.setp(ax2.get_xticklabels(), rotation=60, horizontalalignment='right')
                plt.savefig('ddd.png')
                plt.close()
                path = 'ddd.png' 
                im = pyimgur.Imgur(client_id)
                upload=im.upload_image(path, title='test')
                imgurl = upload.link
                line_bot_api.reply_message(event.reply_token,ImageSendMessage(original_content_url=imgurl,preview_image_url=imgurl))
            elif '儀器故障，超過一個月!' in html:
                wmgs = '儀器故障，超過一個月!'
                line_bot_api.reply_message(event.reply_token,TextSendMessage(text=wmgs))
            else:
                wl_data = Gwl_data()
                wl24 = Wl24f()
                fig = plt.figure(figsize=(9,4))
                ax2 = fig.add_subplot(1,1,1)
                fig.subplots_adjust(bottom=0.3)
                plt.plot(wl24['time'],wl24['depth'])
                plt.title('Water Level Date:'+xtt, fontdict={'fontsize':12})
                ax2.set_xlabel(r'time',fontdict={'fontsize':12})
                ax2.set_ylabel(r'cm',fontdict={'fontsize':12})
                plt.grid()
                try:
                    ax2.set_ylim([0, max(wl24['depth'])])
                    ax2.set_yticks(np.arange(min(wl24['depth']), max(wl24['depth'])+1))
                    ax2.set_xlim([min(wl24['time']),max(wl24['time'])])
                    ax2.xaxis.set_major_locator(mdates.HourLocator(interval=1))
                    ax2.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d %H'))
                except:
                    pass
                plt.setp(ax2.get_xticklabels(), rotation=60, horizontalalignment='right')
                plt.savefig('ddd.png')
                plt.close()
                path = 'ddd.png' 
                im = pyimgur.Imgur(client_id)
                upload=im.upload_image(path, title='test')
                imgurl = upload.link
                line_bot_api.reply_message(event.reply_token,ImageSendMessage(original_content_url=imgurl,preview_image_url=imgurl))
        if backdata == '今日雨量4':
            tz = timezone(timedelta(hours=+8))
            xt = datetime.now(tz).strftime('%Y%m%d%H%M')
            xtt = datetime.now(tz).strftime('%Y-%m-%d')
            html = Test(2026,xt)
            if '今天沒有資料' in html:
                rg_data = Rg_data()
                rg24 = Produce_rg(rg_data)
                fig = plt.figure(figsize=(9,4))
                ax2 = fig.add_subplot(1,1,1)
                fig.subplots_adjust(bottom=0.3)
                plt.bar(rg24['time'],rg24['hour_value'],width=0.007, color='red')
                plt.title('Rainfall Date:'+max(rg24['time']).strftime('%Y-%m-%d'), fontdict={'fontsize':12})
                ax2.set_xlabel(r'time',fontdict={'fontsize':12})
                ax2.set_ylabel(r'mm/hr',fontdict={'fontsize':12})
                plt.grid()
                try:
                    ax2.set_ylim([0, max(rg24['hour_value'])])
                    ax2.set_yticks(np.arange(min(rg24['hour_value']), max(rg24['hour_value'])+1))
                except:
                    pass
                ax2.xaxis.set_major_locator(mdates.HourLocator(interval=1))
                ax2.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d %H'))
                plt.setp(ax2.get_xticklabels(), rotation=60, horizontalalignment='right')
                plt.savefig('ddd.png')
                plt.close()
                path = 'ddd.png' 
                im = pyimgur.Imgur(client_id)
                upload=im.upload_image(path, title='test')
                imgurl = upload.link
                line_bot_api.reply_message(event.reply_token,ImageSendMessage(original_content_url=imgurl,preview_image_url=imgurl))
            elif '儀器故障，超過一個月!' in html:
                wmgs = '儀器故障，超過一個月!'
                line_bot_api.reply_message(event.reply_token,TextSendMessage(text=wmgs))
            else:
                rg_data=Rg_data()
                rg24 = Rg24f()
                fig = plt.figure(figsize=(9,4))
                ax2 = fig.add_subplot(1,1,1)
                fig.subplots_adjust(bottom=0.3)
                plt.bar(rg24['time'],rg24['hour_value'],width=0.007, color='red')
                plt.title('Rainfall Date:'+xtt, fontdict={'fontsize':12})
                ax2.set_xlabel(r'time',fontdict={'fontsize':12})
                ax2.set_ylabel(r'mm/hr',fontdict={'fontsize':12})
                plt.grid()
                try:
                    ax2.set_ylim([0, max(rg24['hour_value'])])
                    ax2.set_yticks(np.arange(min(rg24['hour_value']), max(rg24['hour_value'])+1))
                except:
                    pass
                ax2.xaxis.set_major_locator(mdates.HourLocator(interval=1))
                ax2.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d %H'))
                #plt.xlim([min(rg24.index),max(rg24.index)])
                plt.setp(ax2.get_xticklabels(), rotation=60, horizontalalignment='right')
                plt.savefig('ddd.png')
                plt.close()
                path = 'ddd.png' 
                im = pyimgur.Imgur(client_id)
                upload=im.upload_image(path, title='test')
                imgurl = upload.link
                line_bot_api.reply_message(event.reply_token,ImageSendMessage(original_content_url=imgurl,preview_image_url=imgurl))





if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)