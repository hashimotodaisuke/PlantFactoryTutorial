import hashlib
import datetime

from flask import *

from sqlalchemy import create_engine, Column, String, Integer, DATETIME
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session

app = Flask(__name__)
engine = create_engine('sqlite:///app.db')
Base = declarative_base()


class User(Base):
    __tablename__ = 'users'
    name = Column(String, primary_key=True, unique=True)
    passw = Column(String)

    def __repr__(self):
        return "User<{}, {}, {}>".format(self.name)


class Content(Base):
    __tablename__ = 'contents'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    content = Column(String)
    timestamp = Column(DATETIME)

    def __repr__(self):
        return "Content<{}, {}, {}, {}>".format(self.id, self.name, self.content, self.timestamp)


Base.metadata.create_all(engine)
SessionMaker = sessionmaker(bind=engine)
session = scoped_session(SessionMaker)


@app.route("/", methods=["GET", "POST"])
def main_page():
    cont = session.query(Content).all()
    if request.method == "GET":
        return render_template("mainpage.html", cont=cont)
    else: #request.method == "POST":
        # 同一ユーザーいるかチェック
        user = session.query(User).get(request.form["name"].strip())
        if user:
            # 同一ユーザー入ればパスワードチェック
            if user.passw != str(hashlib.sha256(request.form["pass"].strip().encode("utf-8")).digest()):
                # パスワード一致しないならそのままcontentsテーブルを返す 
                return render_template("mainpage.html", cont=cont)
                # パスワード一致するならcontentsテーブルを追加
        else:
            # 同一ユーザーいなければuserテーブルに新規登録し、contentsテーブルを追加
            user = User(name=request.form["name"], passw=str(hashlib.sha256(request.form["pass"].strip().encode("utf-8")).digest()))
            session.add(user)
        mess = Content(name=request.form["name"], content=request.form["content"], timestamp=datetime.datetime.now())
        session.add(mess)
        # コミットし各テーブルを更新
        session.commit()
        cont = session.query(Content).all()
        # contentsテーブル全てを引き渡しmainpage.htmlをリクエスト
        return render_template("mainpage.html", cont=cont)


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000, threaded=True)
