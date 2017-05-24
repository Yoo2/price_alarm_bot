import sys
import time
import telepot
import pymysql
import threading
from price import getName
from price import getPrice
from telepot.loop import MessageLoop

TOKEN = '397870881:AAHxO_3rs9ONBZPMKPYaVsdGkqKI_mVid7s'
USER = 'tele'
PASSWORD = 'xpffp'
DB = 'price_alarm_bot'

def on_chat_message(msg):
    content_type, chat_type, chat_id = telepot.glance(msg)
    print(content_type, chat_type, chat_id)

    if content_type != 'text':
        return

    command = msg['text'][0].lower()
    if len(msg['text']) > 2 and msg['text'][1] != ' ':
        command = ''

    if command == 'a':
        arr = msg['text'].split()
        if len(arr) != 4 or not arr[2].isdigit():
            addItem(chat_id,'','', '')
            return
        code = arr[1]
        price = arr[2]
        kind = None
        if arr[3] == '매수':
            kind = 0
        elif arr[3] == '매도':
            kind = 1
        elif not arr[3].isdigit():
            addItem(chat_id,'','', '')
            return
        else :
            kind = arr[3]
        addItem(chat_id, code, int(price), int(kind))

    elif command == 'l':
        listItem(chat_id)
    elif command == 'd':
        arr = msg['text'].split()
        if len(arr) != 2 or not arr[1].isdigit():
            deleteItem(chat_id, '')
            return
        deleteItem(chat_id, int(arr[1]))
    else :
        bot.sendMessage(chat_id, 'a 코드 원하는가격 매수(0)/매도(1)' + \
                        '\nl' + '\nd 번호')

def addItem(chat_id, code, price, kind):
    name = getName(code)
    if name == None or not isinstance(price, int) or not (kind == 0 or kind == 1):
        bot.sendMessage(chat_id, '양식을 다시 확인해주세요.\n' + \
                        'a 코드 원하는가격 매수(0)/매도(1)')
        return

    conn = pymysql.connect(host='localhost', user=USER,
                           password=PASSWORD, db=DB, charset='utf8')
    try:
        curs = conn.cursor()
        sql = """insert into item(chat_id, code, name, price, kind)
            values (%s, %s, %s, %s, %s)"""
        curs.execute(sql, (chat_id, code, name, price, kind))
        conn.commit()
        bot.sendMessage(chat_id, '등록되었습니다.')
        listItem(chat_id)
    except Exception as e:
        print(e)
        bot.sendMessage(chat_id, '양식을 다시 확인해주세요.\n' + \
                        'a 코드 원하는가격 매수(0)/매도(1)')
    finally:
        conn.close()

def listItem(chat_id):
    text = ''
    text += '번호, 이름, 코드, 가격, 매수/매도\n\n'

    conn = pymysql.connect(host='localhost', user=USER,
                           password=PASSWORD, db=DB, charset='utf8')
    try:
        curs = conn.cursor(pymysql.cursors.DictCursor)
        sql = """select * from item"""
        curs.execute(sql)
        rows = curs.fetchall()
        for row in rows:
            kind = ''
            if row['kind'] == 0:
                kind = '매수'
            if row['kind'] == 1:
                kind = '매도'
            text += str(row['id']) + ', ' + row['name'] + \
                ', ' + row['code'] + ', ' + str(row['price']) + \
                ', ' + kind + '\n'

        bot.sendMessage(chat_id, text)
    except Exception as e:
        print(e)
        bot.sendMessage(chat_id, '에러')
    finally:
        conn.close()

def deleteItem(chat_id, item_id):
    if not isinstance(item_id, int):
        bot.sendMessage(chat_id, '양식을 다시 확인해주세요.\n' + \
                        'd 번호')
        return

    conn = pymysql.connect(host='localhost', user=USER,
                           password=PASSWORD, db=DB, charset='utf8')
    try:
        curs = conn.cursor()
        sql = """delete from item where id=%s"""
        curs.execute(sql, item_id)
        conn.commit()
        bot.sendMessage(chat_id, '삭제되었습니다.')
        listItem(chat_id)
    except Exception as e:
        print(e)
        bot.sendMessage(chat_id, '양식을 다시 확인해주세요.\n' + \
                        'a 코드 원하는가격 매수(0)/매도(1)')
    finally:
        conn.close()

def checkPrice():
    conn = pymysql.connect(host='localhost', user=USER,
                           password=PASSWORD, db=DB, charset='utf8')
    ids = list()
    try:
        curs = conn.cursor(pymysql.cursors.DictCursor)
        sql = """select * from item"""
        curs.execute(sql)
        rows = curs.fetchall()

        for row in rows:
            if isTrade(row['code'], row['price'], row['kind']):
                kind = ''
                if row['kind'] == 0:
                    kind = '매수'
                if row['kind'] == 1:
                    kind = '매도'

                text = row['name'] + ' ' + str(row['price']) + ' ' + kind + '\n'

                bot.sendMessage(row['chat_id'], text)
                ids.append(row['id'])

        for delId in ids:
            curs = conn.cursor()
            sql = """delete from item where id=%s"""
            curs.execute(sql, delId)
            conn.commit()

    except Exception as e:
        print(e)
    finally:
        conn.close()

def isTrade(code, goal_price, kind):
    current_price = getPrice(code)
    if kind == 0 and goal_price >= current_price:
        return True
    if kind == 1 and goal_price <= current_price:
        return True
    return False

def repeatMinute():
    checkPrice()
    print("repeat")
    threading.Timer(60, repeatMinute).start()

bot = telepot.Bot(TOKEN)
MessageLoop(bot, {'chat': on_chat_message}).run_as_thread()

print ('Listening ...')
repeatMinute()

# Keep the program running.
while 1:
    time.sleep(10)
