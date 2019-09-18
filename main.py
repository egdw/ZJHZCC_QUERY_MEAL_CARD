import requests
from bs4 import BeautifulSoup
import redis
from flask import Flask
from flask_cors import CORS
import json
pool = redis.ConnectionPool(host='localhost', port=6379,db=1)
red = redis.Redis(connection_pool=pool)
app = Flask(__name__)


__Author__ = "洪德衍";

# 设置当月历史消费记录
def setMonth(year,month,session_id):
    session_id = "ASP.NET_SessionId="+session_id;
    payload = {'ImageButton1.y': 10,'ImageButton1.x': 33,'txtMonth': month,'ddlMonth': month,'ddlYear': year, '__VIEWSTATE': '/wEPDwULLTEyNzY5MzAyODYPZBYCAgEPZBYGAgkPEA9kFgIeCG9uY2hhbmdlBTdqYXZhc2NyaXB0OmRkbFNlbGVjdGVkKHRoaXMub3B0aW9ucy5zZWxlY3RlZEluZGV4LDMsOSk7EBUBBDIwMTkVAQQyMDE5FCsDAWcWAWZkAgsPEGQQFQYBOQE4ATcBNgE1ATQVBgE5ATgBNwE2ATUBNBQrAwZnZ2dnZ2dkZAINDw9kFgIeB29uY2xpY2sFHmphdmFzY3JpcHQ6R2V0ZGRsTW9udGhWYWx1ZSgpO2QYAQUeX19Db250cm9sc1JlcXVpcmVQb3N0QmFja0tleV9fFgEFDEltYWdlQnV0dG9uMTyntTQAoXdlCsx/vyOxh5M1bdZJfc6uJIedUHWBe9NX'}
    get = requests.post("http://ykt.zjhzcc.edu.cn/Cardholder/Queryhistory.aspx",headers={"Cookie":session_id},data=payload)
    if get.ok:
        return True
    else:
        return False

# 查询当月历史消费记录
def getHisotoryRecord(session_id):
    session_id = "ASP.NET_SessionId="+session_id;
    get = requests.get("http://ykt.zjhzcc.edu.cn/Cardholder/QueryhistoryDetailFrame.aspx",headers={"Cookie":session_id});
    #开始解析
    if get.ok:
        soup = BeautifulSoup(get.text, "html.parser")
        try:
            table = soup.select("table#dgShow")[0];
        except IndexError:
            print("token失效!请重新登录");
            return None;
        list = [];
        first = False;
        for tr in table.find_all("tr"):
            if first:
                tds = tr.find_all("td")
                ret = {"id":tds[0].text,"account":tds[1].text,"card_type":tds[2].text,"shop_type":tds[3].text,"store":tds[4].text,"station":tds[5].text,"final_id":tds[6].text,"use_money":tds[7].text,"time":tds[8].text,"package_name":tds[9].text,"money":tds[10].text};
                list.append(ret);
            first = True;
        return json.dumps(list);
    else:
        return None;
    
# 查询当日历史消费记录
def getToday(session_id):
    session_id = "ASP.NET_SessionId="+session_id;
    get = requests.get("http://ykt.zjhzcc.edu.cn/Cardholder/QueryCurrDetailFrame.aspx",headers={"Cookie":session_id});
    #开始解析
    if get.ok:
        soup = BeautifulSoup(get.text, "html.parser")
        try:
            table = soup.select("table#dgShow")[0];
        except IndexError:
            print("token失效!请重新登录");
            return None;
        list = [];
        first = False;
        for tr in table.find_all("tr"):
            if first:
                tds = tr.find_all("td")
                ret = {"id":tds[0].text,"account":tds[1].text,"card_type":tds[2].text,"shop_type":tds[3].text,"store":tds[4].text,"station":tds[5].text,"final_id":tds[6].text,"use_money":tds[7].text,"time":tds[8].text,"package_name":tds[9].text,"money":tds[10].text};
                list.append(ret);
            first = True;
        return json.dumps(list);
    else:
        return None;

# 查询余额和一些其他的个人信息
def getRemainMoneyAndOtherInfo(session_id):
    session_id = "ASP.NET_SessionId="+session_id;
    get = requests.get("http://ykt.zjhzcc.edu.cn/Cardholder/AccBalance.aspx",headers={"Cookie":session_id});
    if get.ok: 
        soup = BeautifulSoup(get.text, "html.parser")
        #获取账户余额
        money = soup.select("span#lblOne0")[0].text;
        lblPerCode0 = soup.select("span#lblPerCode0")[0].text;
        lblCardNum0 = soup.select("span#lblCardNum0")[0].text;
        lblName0 = soup.select("span#lblName0")[0].text;
        ret = {"id":lblPerCode0,"card_id":lblCardNum0,"name:":lblName0,"money":money};
        return json.dumps(ret);
    else:
        return None;

# 查询可以查询的月份和年份
def getCouldQueryYearAndMonths(session_id):
    session_id = "ASP.NET_SessionId="+session_id;
    get = requests.get("http://ykt.zjhzcc.edu.cn/Cardholder/Queryhistory.aspx",headers={"Cookie":session_id});
    if get.ok:
        soup = BeautifulSoup(get.text, "html.parser")
        years = soup.select("select#ddlYear")[0].select("option");
        months = soup.select("select#ddlMonth")[0].select("option")
        m = [];
        for i in months:
            m.append(i.text);
        y = [];
        for i in years:
            y.append(i.text)
        ret = {"year":y,"months":m};
        return ret;
    else:
        return None;
    
def getCookieId(username,password):
    request = requests.session()
    get = request.get("http://ykt.zjhzcc.edu.cn/default.aspx")
    if get.ok:
        #获取__VIEWSTATE
        soup = BeautifulSoup(get.text, "html.parser")
        viewstate = soup.select("input#__VIEWSTATE")[0].get("value");
        EVENTVALIDATION = soup.select("input#__EVENTVALIDATION")[0].get("value");
        #获取验证码
        UserLogin_ImgFirst = soup.select("img#UserLogin_ImgFirst")[0].get("src")[7:8];
        UserLogin_imgSecond = soup.select("img#UserLogin_imgSecond")[0].get("src")[7:8];
        UserLogin_imgThird = soup.select("img#UserLogin_imgThird")[0].get("src")[7:8];
        UserLogin_imgFour = soup.select("img#UserLogin_imgFour")[0].get("src")[7:8];
        code = UserLogin_ImgFirst+UserLogin_imgSecond+UserLogin_imgThird+UserLogin_imgFour;
        payload = {'__EVENTVALIDATION':EVENTVALIDATION,'__EVENTARGUMENT':'','__EVENTTARGET':'','__LASTFOCUS':'','UserLogin:txtUser': username,'UserLogin:txtPwd': password,'UserLogin:ddlPerson': "卡户".encode("gb2312"),'UserLogin:txtSure': code,'UserLogin:ImageButton1.x': 52,"UserLogin:ImageButton1.y": 12,'__VIEWSTATE': viewstate}
        get = request.post("http://ykt.zjhzcc.edu.cn/default.aspx",data=payload)
        if "领导" in get.text:
            return None;
        cookie = str(request.cookies["ASP.NET_SessionId"]);
        return cookie;
    else :
        return None;
    
        
# flask 相关
@app.route('/login/<username>/<password>')
def login(username,password):
    cookie = red.get("card_"+username)
    if cookie==None:
        cookie = getCookieId(username,password)
        print("获取到的cookie为:%s"%(cookie));
        if cookie != None:
            red.setex("card_"+username,60*10,cookie)
            return '{"info":1}'
        else:
            return '{"info":0}';
    return '{"info":1}'


@app.route('/getHistoryRecord/<username>/<year>/<month>')
def getHistoryRecordForWeb(username,year,month):
    cookie = red.get("card_"+username)
    if cookie!=None:
        cookie = str(cookie,encoding="utf-8")
        setMonth(year,month,cookie)
        ret = getHisotoryRecord(cookie);
        if ret == None:
#             red.delete("card_"+username);
            return "";
        else:
            return ret;
    else:
        return "";
    
@app.route('/today/<username>')
def getTodayRecord(username):
    cookie = red.get("card_"+username)
    if cookie!=None:
        cookie = str(cookie,encoding="utf-8")
        ret = getToday(cookie);
        if ret == None:
            return "";
        else:
            return ret;
    else:
        return "";

@app.route('/getUserInfo/<username>')
def getUserInfo(username):
    cookie = red.get("card_"+username)
    if cookie!=None:
        cookie = str(cookie,encoding="utf-8")
        ret = getRemainMoneyAndOtherInfo(cookie)
        if ret == None:
            return "";
        else:
            return ret;
    else:
        return "";

@app.route('/getYearAndMonth/<username>')
def getYearAndMonth(username):
    cookie = red.get("card_"+username)
    if cookie!=None:
        cookie = str(cookie,encoding="utf-8")
        ret = getCouldQueryYearAndMonths(cookie)
        if ret == None:
            return "";
        else:
            return ret;
    else:
        return "";
    
if __name__ == '__main__':
    CORS(app, supports_credentials=True)
    app.run()



# getCookieId("1841920344","094110");
# setMonth(2019,4,"wafhf4ru3yyend1ghxowmw2t")
# ret = getHisotoryRecord("wafhf4ru3yyend1ghxowmw2t");
# print("jieguo:"+ret);
# getRemainMoneyAndOtherInfo("oqhtiwswfcgltjxouwe20bhq");
# print(getToday("oqhtiwswfcgltjxouwe20bhq"));
# print(getCouldQueryYearAndMonths("oqhtiwswfcgltjxouwe20bhq"));
