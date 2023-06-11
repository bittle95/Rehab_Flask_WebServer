import datetime

import os
from flask_sqlalchemy import SQLAlchemy

userDBPath = os.path.join(os.path.join(os.getcwd(),"Database"), "userDB.sqlite")
resultDBPath = os.path.join(os.path.join(os.getcwd(),"Database"), "resultDB.sqlite")

DB = SQLAlchemy()

class UserInformation():
    def __init__(self, name="", sex=0, size=0, severe=0, age = 0):
        self.name = name
        self.sex = sex
        self.size = size
        self.severe = severe
        self.age = age
    def clear(self):
        self.name = ""
        self.sex = 0
        self.size = 0
        self.severe = 0
        self.age = 0

class ContentConfig():
    def __init__(self, type = 0, stride = 0, width = 0, difficulty = 0, distance = 0):
        self.type = type
        self.stride = stride
        self.width = width
        self.difficulty = difficulty
        self.distance = distance


    def isEmpty(self) -> bool:
        if self.stride == 0:
            return True
        if self.width == 0:
            return True
        if self.difficulty == 2: #라디오박스라서 null 일 수가 없음
            return True
        if self.distance == 0:
            return True
        return False
    def contentReset(self):
        self.type = 0
    def isContentReset(self) -> bool:
        return self.type == 0
    def clear(self):
        self.type = 0
        self.stride = 0
        self.width = 0
        self.difficulty = 0
        self.distance = 0
    def ToString(self):
        return str.format("{0},{1},{2},{3},{4}", self.type, self.stride, self.width, self.difficulty, self.distance)
    def serialize(self):
        return {
            "type" : self.type,
            "distance" : self.distance,
            "stride": self.stride,
            "width": self.width,
            "difficulty": self.difficulty
        }

class User(DB.Model):
    __tablename__ = "user_table"
    __bind_key__ = "user"
    id = DB.Column(DB.Integer, primary_key=True)
    name = DB.Column(DB.String(32), nullable=False)
    sex = DB.Column(DB.Integer, nullable=False)
    size = DB.Column(DB.Integer, nullable=False)
    severe = DB.Column(DB.Integer, nullable=False)
    age = DB.Column(DB.Integer, nullable=False)
    DB.UniqueConstraint(name, sex, size, severe, age)
    def __init__(self, name="", sex=0, size=0, severe=0, age = 0):
        self.name = name
        self.sex = sex
        self.size = size
        self.severe = severe
        self.age = age
    def isEmptry(self) -> bool:
        if self.name == "":
            return True
        if self.size == 0:
            return True
        return False
    def serialize(self):
        return {
            "id" : self.id,
            "name" : self.sex,
            "size" : self.size,
            "severe" : self.severe,
            "age" : self.age
        }

class ContentResult(DB.Model):
    __tablename__ = "result_table"
    __bind_key__ = "result"
    id = DB.Column(DB.Integer, primary_key=True)
    user_id = DB.Column(DB.Integer, DB.ForeignKey("user_table.id", ondelete="CASCADE"))
    user_name = DB.Column(DB.String(32), nullable=False)
    type = DB.Column(DB.Integer, nullable=False)
    distance = DB.Column(DB.Integer, nullable=False)
    difficulty = DB.Column(DB.Integer, nullable=False)
    time_date = DB.Column(DB.String(32), unique=True, nullable=False)
    time_train = DB.Column(DB.Float, nullable=False)
    l_success_cnt = DB.Column(DB.Integer, nullable=False)
    r_success_cnt = DB.Column(DB.Integer, nullable=False)
    l_total_cnt = DB.Column(DB.Integer, nullable=False)
    r_total_cnt = DB.Column(DB.Integer, nullable=False)
    Info1 = DB.Column(DB.Float, nullable=False)
    Info2 = DB.Column(DB.Float, nullable=False)
    Info3 = DB.Column(DB.String(32), nullable=False)
    stride = DB.Column(DB.Integer, nullable=False)
    width = DB.Column(DB.Integer, nullable=False)


    user = DB.relationship("User", backref=DB.backref("result_set"))
    def __init__(self, user: User, config: ContentConfig, time_train, l_success, l_total, r_success, r_total, info1, info2, info3):
        self.user = user
        self.user_name = user.name
        self.time_date = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
        self.time_train = time_train
        self.type = config.type
        self.distance = config.distance
        self.difficulty = config.difficulty
        self.l_success_cnt = l_success
        self.l_total_cnt = l_total
        self.r_success_cnt = r_success
        self.r_total_cnt = r_total
        self.Info1 = info1
        self.Info2 = info2
        self.Info3 = info3
        self.stride = config.stride
        self.width = config.width



    def serialize(self):
        return {
            "id" : self.id,
            "type": self.type,
            "date": self.time_date,
            "train_time": self.time_train,
            "name" : self.user.name,
            "sex" : self.user.sex,
            "size" : self.user.size,
            "severe" : self.user.severe,
            "age" : self.user.age,
            "l_success_cnt" : self.l_success_cnt,
            "r_success_cnt" : self.r_success_cnt,
            "l_total_cnt" : self.l_total_cnt,
            "r_total_cnt" : self.r_total_cnt,
            "distance" : self.distance,
            "difficulty": self.difficulty,
            "info1": self.Info1,
            "info2": self.Info2,
            "info3": self.Info3,
            "stride" : self.stride,
            "width" : self.width
        }
    def convertToTable(self):
        total_success = self.l_success_cnt + self.r_success_cnt
        total = self.l_total_cnt + self.r_total_cnt
        if(total != 0 and total_success != 0) :
            return (
                self.time_date,
                self.type,
                self.distance,
                "{0}".format("하" if self.difficulty % 2 == 0 else "상"),
                self.time_train,
                "{0:.2f}".format((total_success / total) * 100), #"{0}/{1}".format(total_success, total),
                "{0:.2f}".format((self.l_success_cnt / self.l_total_cnt) * 100), #"{0}/{1}".format(self.l_success_cnt,self.l_total_cnt),
                "{0:.2f}".format((self.r_success_cnt /self.r_total_cnt) * 100), #"{0}/{1}".format(self.r_success_cnt,self.r_total_cnt),
                "{0:.2f}".format(self.Info1),
                "{0:.2f}".format(self.Info2),
                self.Info3,
                self.stride,
                self.width
        )
        else :
            return (
                self.time_date,
                self.type,
                self.distance,
                "{0}".format("하" if self.difficulty % 2 == 0 else "상"),
                self.time_train,
                "{x}", #"{0}/{1}".format(total_success, total),
                "{x}", #"{0}/{1}".format(self.l_success_cnt,self.l_total_cnt),
                "{x}", #"{0}/{1}".format(self.r_success_cnt,self.r_total_cnt),
                "{0:.2f}".format(self.Info1),
                "{0:.2f}".format(self.Info2),
                self.Info3,
                self.stride,
                self.width
            )