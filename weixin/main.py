from time import time, localtime
import cityinfo
import config
from requests import get, post
from datetime import datetime, date, timedelta


def get_access_token():
    # appId
    app_id = config.app_id
    # appSecret
    app_secret = config.app_secret
    post_url = ("https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={}&secret={}"
                .format(app_id, app_secret))
    access_token = get(post_url).json()['access_token']
    print(access_token)
    return access_token


def get_chp():
    get_url = "https://api.shadiao.pro/chp"
    headers = {
      'Content-Type': 'application/json',
      'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                    'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36'
    }
    chp = get(get_url, headers=headers).json()['data']['text']
    return chp


def get_weather(province, city):
    # 城市id
    city_id = cityinfo.cityInfo[province][city]["AREAID"]
    # city_id = 101280101
    # 毫秒级时间戳
    t = (int(round(time() * 1000)))
    headers = {
      "Referer": "http://www.weather.com.cn/weather1d/{}.shtml".format(city_id),
      'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                    'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36'
    }
    url = "http://d1.weather.com.cn/dingzhi/{}.html?_={}".format(city_id, t)
    response = get(url, headers=headers)
    response.encoding = "utf-8"
    response_data = response.text.split(";")[0].split("=")[-1]
    response_json = eval(response_data)
   # print(response_json)
    weatherinfo = response_json["weatherinfo"]
    # 天气
    weather = weatherinfo["weather"]
    # 最高气温
    temp = weatherinfo["temp"]
    # 最低气温
    tempn = weatherinfo["tempn"]
    return weather, temp, tempn


def get_ciba():
    url = "http://open.iciba.com/dsapi/"
    headers = {
      'Content-Type': 'application/json',
      'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                    'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36'
    }
    r = get(url, headers=headers)
    note_en = r.json()["content"]
    note_ch = r.json()["note"]
    return note_ch, note_en

def calculate_period_cycle():
    history_period_start_date = datetime.strptime(config.last, "%Y-%m-%d").date() #date(2023, 5, 12)
    period_cycle = config.periodd_cycle
    period_days = config.period_days
    # 计算下一次开始时间
    next_period_start_date = history_period_start_date
    current_date = date.today()
    while next_period_start_date <= current_date:
        next_period_start_date += timedelta(days=period_cycle)
        next_period_end_date = next_period_start_date + timedelta(days=period_days)
    # 根据下一次开始的时间计算，上一次开始的时间
    last_period_start_date = next_period_start_date - timedelta(days=period_cycle)
    # 根据上一次开始时间计算上一次结束的时间
    last_period_end_date = last_period_start_date + timedelta(days=period_days)
    # 判断当前是否处在生理期中，并计算还剩几天结束
    if last_period_start_date <= current_date <= last_period_end_date:
        days_left_in_period = (last_period_end_date - current_date).days
        return "还剩" + str(days_left_in_period) + "天，将在" + last_period_end_date.strftime("%Y-%m-%d") + "结束"
    else:
        days_to_next_period_start = (next_period_start_date - current_date).days
        return "开始日期为：" + next_period_start_date.strftime("%Y-%m-%d") + "，离今天还剩" + str(days_to_next_period_start) + "天"

def send_message(to_user, access_token, city_name, weather, max_temperature, min_temperature, note_ch, note_en, chp1, chp2, chp3, chp4, chp5):
    url = "https://api.weixin.qq.com/cgi-bin/message/template/send?access_token={}".format(access_token)
    week_list = ["星期一", "星期二", "星期三", "星期四", "星期五", "星期六","星期日"]
    year = localtime().tm_year
    month = localtime().tm_mon
    day = localtime().tm_mday
    today = datetime.date(datetime(year=year, month=month, day=day))
    #print(today)
    #print(today.isoweekday())
    week = week_list[today.isoweekday()-1]
    #print(week)
    # 获取在一起的日子的日期格式
    love_year = int(config.love_date.split("-")[0])
    love_month = int(config.love_date.split("-")[1])
    love_day = int(config.love_date.split("-")[2])
    love_date = date(love_year, love_month, love_day)
    #计算结婚倒计时日期
    #marry_year = int(config.marry_date.split("-")[0])
    #marry_month = int(config.marry_date.split("-")[1])
    #marry_day = int(config.marry_date.split("-")[2])
    #marry_date = date(marry_year, marry_month, marry_day)
    #marry_days = str(today.__sub__(marry_date)).split(" ")[0]
    # 获取在一起的日期差
    love_days = str(today.__sub__(love_date)).split(" ")[0]
    # 获取生日的月和日
    birthday_month = int(config.birthday.split("-")[1])
    birthday_day = int(config.birthday.split("-")[2])
    # 今年生日
    year_date = date(year, birthday_month, birthday_day)
    # 计算生日年份，如果还没过，按当年减，如果过了需要+1
    if today > year_date:
        birth_date = date((year + 1), birthday_month, birthday_day)
        birth_day = str(birth_date.__sub__(today)).split(" ")[0]
    elif today == year_date:
        birth_day = 0
    else:
        birth_date = year_date
        birth_day = str(birth_date.__sub__(today)).split(" ")[0]
    # 获取航班的月和日
    flight_month = int(config.flight.split("-")[1])
    flight_day = int(config.flight.split("-")[2])
    # 航班信息
    year_date = date(year, flight_month, flight_day)
    # 计算航班时长，还没过，按当年减
    if today > year_date:
        flight_date = date((year + 1), flight_month, flight_day)
        flight_day = str(flight_date.__sub__(today)).split(" ")[0]
    elif today == year_date:
        flight_day = 0
    else:
        flight_date = year_date
        flight_day = str(flight_date.__sub__(today)).split(" ")[0]
    #计算生理期
    period = calculate_period_cycle()
    data = {
        "touser": to_user,
        "template_id": config.template_id,
        "url": "http://weixin.qq.com/download",
        "topcolor": "#FF0000",
        "data": {
            "date": {
                "value": "{} {}".format(today, week),
                "color": "#00FFFF"
            },
            "city": {
                "value": city_name,
                "color": "#808A87"
            },
            "weather": {
                "value": weather,
                "color": "#ED9121"
            },
            "min_temperature": {
                "value": min_temperature,
                "color": "#00FF00"
            },
            "chp1": {
              "value": chp1,
              "color": "#7B68EE"
            },
            "chp2": {
              "value": chp2,
              "color": "#7B68EE"
            },
            "chp3": {
              "value": chp3,
              "color": "#7B68EE"
            },
            "chp4": {
              "value": chp4,
              "color": "#7B68EE"
            },
            "chp5": {
              "value": chp5,
              "color": "#7B68EE"
            },
            "max_temperature": {
              "value": max_temperature,
              "color": "#FF6100"
            },
            "love_day": {
              "value": love_days,
              "color": "#87CEEB"
            },
            "birthday": {
              "value": birth_day,
              "color": "#FF8000"
            },
            "flight": {
              "value": flight_day,
              "color": "#FF8000"
            },
            "period": {
              "value": period,
              "color": "#FF0000"
            },
            "note_en": {
                "value": note_en,
                "color": "#173177"
            },
            "note_ch": {
                "value": note_ch,
                "color": "#173177"
            }
        }
    }
    headers = {
      'Content-Type': 'application/json',
      'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                    'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36'
    }
    response = post(url, headers=headers, json=data)
    #print(response.text)


# 获取accessToken
accessToken = get_access_token()
#print(accessToken)
# 接收的用户
user1 = config.user1
user2 = config.user2
# 传入省份和市获取天气信息
province, city = config.province, config.city
weather, max_temperature, min_temperature = get_weather(province, city)
# 获取词霸每日金句
note_ch, note_en = get_ciba()
# 获取彩虹屁
chp = get_chp() 
print(chp)
#chp = "夜晚倒是安静,连月亮都收紧光亮,只轻轻拂照,就觉得现代科技吵闹,电波传输太虚妄,想教风说话,让它一里一亭地把我的话传到你的边,让所有春风吹过的街道都流传『我喜欢你』的语言。"
max_length = 100  # 最大长度限制
while(len(chp) > max_length):
    chp = get_chp()
chp1 = chp[0:20]
chp2 = chp[20:40]
chp3 = chp[40:60]
chp4 = chp[60:80]
chp5 = chp[80:100]
# 公众号推送消息
send_message(user1, accessToken, city, weather, max_temperature, min_temperature, note_ch, note_en, chp1, chp2, chp3, chp4, chp5)
send_message(user2, accessToken, city, weather, max_temperature, min_temperature, note_ch, note_en, chp1, chp2, chp3, chp4, chp5)

