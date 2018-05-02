"""
reload noti table
"""
import sys, os
sys.path.append(os.path.abspath(os.path.join('..')))
from app.models import Result, Notification, DeviceID
from app import db
from json import loads


def import_noti_from_result():
    user_result_dict = { device_id.device_id: [] for device_id in DeviceID.query.all() }

    for device_id, time_list in user_result_dict.items():
        print("\n{}:".format(device_id))
        for result in Result.query.filter_by(user=device_id).all():
            if not result.date in time_list:
                print("\t<{}>".format(result.date))
                time_list.append(result.date)
                raw = loads(result.raw).get('Notification')
                if raw:
                    for lat, sub_text, app, timestamp, text, lon, title, ticker, send_esm in \
                        zip(raw['latitude_cols'], raw['subText_cols'], raw['app_cols'], raw['timestamps'], \
                            raw['n_text_cols'], raw['longitude_cols'], raw['title_cols'], raw['tickerText_cols'], \
                            raw['sendForm_cols']):
                        if ticker and (app=='com.facebook.orca' or app=='jp.naver.line.android'):
                            new_noti = Notification(
                                timestamp = timestamp,
                                device_id = device_id,
                                latitude = lat,
                                longitude = lon,
                                app = app,
                                title = title,
                                sub_text = sub_text,
                                text = text,
                                ticker_text = ticker,
                                send_esm = True if send_esm == '1' else False)
                            db.session.add(new_noti)
                    try:
                        db.session.commit()
                    except Exception as e:
                        print("WTF")
                        db.session.rollback()
            else:
                print("\t<{}> EXISTS".format(result.date))


def import_noti_from_result_2nd():
    tmp = {}
    for result in Result.query.filter(Result.id >= 11147).all():
        if not result.user in tmp:
            tmp[result.user] = []
        if result.date in tmp[result.user]:
            print("REPEAT", result.user, result.date)
            continue
        tmp[result.user].append(result.date)
        
        print("[{}]".format(result.id))
        noti_dict = loads(result.raw).get('Notification')
        if noti_dict:
            for lat, sub_text, app, timestamp, text, lon, title, ticker, send_esm in \
                zip(noti_dict['latitude_cols'], noti_dict['subText_cols'], noti_dict['app_cols'], noti_dict['timestamps'], \
                    noti_dict['n_text_cols'], noti_dict['longitude_cols'], noti_dict['title_cols'], noti_dict['tickerText_cols'], \
                    noti_dict['sendForm_cols']):
                if Notification.query.filter_by(device_id=result.user).filter_by(timestamp=timestamp).filter_by(ticker_text=ticker).first():
                    print("\t\talready have", timestamp)
                    continue
                elif ticker and (app=='com.facebook.orca' or app=='jp.naver.line.android'):
                    print("\t{}".format(ticker))
                    new_noti = Notification(
                        timestamp = timestamp,
                        device_id = result.user,
                        latitude = lat,
                        longitude = lon,
                        app = app,
                        title = title,
                        sub_text = sub_text,
                        text = text,
                        ticker_text = ticker,
                        send_esm = True if send_esm == '1' else False)
                    db.session.add(new_noti)
            try:
                db.session.commit()
            except Exception as e:
                print("WTF")
                db.session.rollback()


def del_nullticker_or_unwanted_app():
    for noti in Notification.query.filter(Notification.id >= 31258).all():
        if noti.ticker_text and (noti.app=='com.facebook.orca' or noti.app=='jp.naver.line.android'):
            continue
        else:
            print("DEL {}: {}".format(noti.app, noti.ticker_text))
            db.session.delete(noti)
            db.session.commit()


def check_notification_repeat():
    noti_query = Notification.query.filter(Notification.id >= 31258)
    for noti in noti_query.all():
        if noti_query.filter_by(device_id=noti.device_id).filter_by(ticker_text=noti.ticker_text).filter_by(timestamp=noti.timestamp).filter_by(app=noti.app).filter_by(send_esm=noti.send_esm).count() >= 2:
            print(noti.timestamp, noti.device_id, noti.ticker_text)


