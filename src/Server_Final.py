import os.path
from io import StringIO
from werkzeug.wrappers import Response
from flask import Flask, current_app, request, render_template, jsonify, redirect

from src.Database_Final import *
from sqlalchemy import exc

APP = Flask(__name__)
# with APP.app_context(): #추가
#     print(current_app.name)

APP.secret_key = "secretKey"

Data_Admin = None
Data_Operate = None
CurrentContentConfiguration = ContentConfig()
CurrentUser = UserInformation()
orderString = ""
LeftRight = True
btnhasPushed = False
debugbtn = True


class NRCServer:
    def __init__(self, host: str, port: float):
        global APP
        self.HOST = host
        self.PORT = port
        self.DATABASE_DIRECTORY = os.path.join(os.getcwd(), "Database")
        if not os.path.isdir(self.DATABASE_DIRECTORY):
            os.mkdir(self.DATABASE_DIRECTORY)
        APP.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:///' + userDBPath
        APP.config["SQLALCHEMY_BINDS"] = {
            "user": 'sqlite:///' + userDBPath,
            "result": "sqlite:///" + resultDBPath
        }
        APP.config["SQLALCHEMY_COMMIT_ON_TEARDOWN"] = True
        APP.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
        APP.config["JSON_AS_ASCII"] = False
        DB.init_app(APP)
        DB.app = APP
        DB.create_all()


    def Start(self):
        global APP
        print(self.HOST)
        APP.run(host=self.HOST, port=self.PORT, threaded=True, debug=False)

@APP.route("/", methods=["GET"])
def GetMainPage():
    if request.method == "GET":
        return render_template("MainPage.html")


@APP.route("/admin", methods=["POST"])
def GetAdminPage():
    return render_template("AdminMode.html")

@APP.route("/admin/config", methods=["POST"])
def ContentConfigByAdmin():
    global CurrentContentConfiguration
    CurrentContentConfiguration.stride = int(request.form["patient_stride"]) if request.form["patient_stride"] != "" else 0
    CurrentContentConfiguration.width = int(request.form["patient_width"]) if request.form["patient_width"] != "" else 0
    CurrentContentConfiguration.difficulty = int(request.form.get("difficulty"))
    CurrentContentConfiguration.distance = int(request.form.get("distance"))
    CurrentContentConfiguration.type = int(request.form.get("chk_info")) if request.form.get("chk_info") is not None else 0
    if CurrentContentConfiguration.isEmpty():
        print("콘텐츠 정보 : " + CurrentContentConfiguration.ToString())
        CurrentContentConfiguration.clear()
        return "콘텐츠 관련 항목이 비었습니다"

    print("콘텐츠 정보 : " + CurrentContentConfiguration.ToString())

    global DB
    global CurrentUser
    user_name = request.form["patient_name"]
    user_sex = int(request.form.get("sex"))
    user_size = int(request.form["foot_size"]) if request.form["foot_size"] !="" else 0
    user_severe = int(request.form.get("severe"))
    user_age = int(request.form.get("patient_age"))

    _currentUser = User(user_name, user_sex, user_size, user_severe, user_age)

    if(_currentUser.isEmptry()):
        CurrentContentConfiguration.clear()
        return "보행자 관련 항목이 비었습니다"

    else:
        try:
            DB.session.add(_currentUser)
            DB.session.commit()
        except exc.InvalidRequestError as e:
            DB.session.rollback()
            return "잘못된 값"
        except exc.IntegrityError as e:
            DB.session.rollback()
            _currentUser = User.query.filter_by(name=user_name, sex=user_sex, size=user_size, severe=user_severe, age=user_age).first()
            print("중복된 값 : 기존에 등록된 사용자 사용")
    CurrentUser = UserInformation(_currentUser.name, _currentUser.sex, _currentUser.size, _currentUser.severe, _currentUser.age)

    return redirect("/")


@APP.route("/content/reset", methods=["POST"])
def ResetContent():
    global orderString
    orderString = "order"
    return redirect("/") #추가

@APP.route("/content/resetfinish", methods=["POST"])
def ResetContentFinish():
    global CurrentContentConfiguration
    global orderString
    CurrentContentConfiguration.clear()
    orderString = ""
    print("order has ordered")
    return redirect("/")

@APP.route("/content/order", methods=["POST"])
def GetContentType():
    global orderString
    return str(orderString)

@APP.route("/content/information", methods=["POST"])
def GetContentInformation():
    global CurrentContentConfiguration
    print("콘텐츠 정보: " + CurrentContentConfiguration.ToString())
    if not CurrentContentConfiguration.isEmpty() and not CurrentContentConfiguration.isContentReset():
        return jsonify(CurrentContentConfiguration.serialize())
    return "Empty"

@APP.route("/content/finish", methods=["POST"])
def SaveResult():
    global CurrentContentConfiguration
    global CurrentUser
    try:
        l_success_cnt = int(request.form["L_Success_Cnt"])
        r_success_cnt = int(request.form["R_Success_Cnt"])
        l_total_cnt = int(request.form["L_Total_Cnt"])
        r_total_cnt = int(request.form["R_Total_Cnt"])
        time_train = request.form["Training_Time"]
        info_1 = request.form["Info1"]
        info_2 = request.form["Info2"]
        info_3 = request.form["Info3"]

        _currentUser = User.query.filter_by(name=CurrentUser.name, sex=CurrentUser.sex,
                                            size=CurrentUser.size, severe=CurrentUser.severe, age=CurrentUser.age).first()
        result = ContentResult(_currentUser, CurrentContentConfiguration, time_train,
                               l_success_cnt, l_total_cnt, r_success_cnt, r_total_cnt, info_1, info_2, info_3)

        CurrentContentConfiguration.clear()

        try:
            DB.session.add(result)
            DB.session.commit()
        except exc.InvalidRequestError as e:
            DB.session.rollback()
            return "잘못된 값"
        except exc.IntegrityError as e:
            DB.session.rollback()
            print("중복된 값")
        return "True"
    except Exception as e:
        print(str(e))
        return "False"

@APP.route("/data", methods=["POST"])
def GetDataConfigPage():
    user_list = User.query.all()
    user_name_list = []
    index = int(request.form["user_index"])
    selectedUser = None
    for user in user_list:
        user_name = "{0}:{1}".format(user.id, user.name)
        user_name_list.append((user_name))
        if user.id == index:
            selectedUser = user
    content_result_list = ContentResult.query.filter_by(user=selectedUser).all()
    result_list = []
    for content_result in content_result_list:
        result_list.append((content_result.convertToTable()))
    user_info = (selectedUser.id, selectedUser.name, "Male" if selectedUser.sex == 1 else "Female",
        selectedUser.size, selectedUser.severe, selectedUser.age)
    return render_template("DataConfig.html", user_name_list=user_name_list, selected_index=index, result_list=result_list, user_info=user_info)


@APP.route("/LoadSettings", methods=["POST"])
def GetSetting():
    user_list = User.query.all()
    user_name_list = []
    index = int(request.form["user_index"])
    selectedUser = None
    for user in user_list:
        user_name = "{0}:{1}".format(user.id, user.name)
        user_name_list.append((user_name))
        if user.id == index:
            selectedUser = user
    content_result_list = ContentResult.query.filter_by(user=selectedUser).all()
    result_list = []
    for content_result in content_result_list:
        result_list.append((content_result.convertToTable()))
    user_info = (selectedUser.id, selectedUser.name, "Male" if selectedUser.sex == 1 else "Female",
        selectedUser.size, selectedUser.severe, selectedUser.age)
    #print(' '.join(str(e) for e in result_list))
    return render_template("LoadSetting.html", user_name_list=user_name_list, selected_index=index, result_list=result_list, user_info=user_info)

@APP.route("/LoadSettings/config", methods=["POST"])
def SettingConfigFinish():
    # 콘텐츠 관리 모드 파트
    global CurrentContentConfiguration
    CurrentContentConfiguration.stride = int(request.form["patient_stride1"]) if request.form["patient_stride1"] != "" else 0
    CurrentContentConfiguration.width = int(request.form["patient_width1"]) if request.form["patient_width1"] != "" else 0
    CurrentContentConfiguration.difficulty = int(request.form.get("difficulty1"))
    CurrentContentConfiguration.distance = int(request.form.get("distance1"))
    if CurrentContentConfiguration.isEmpty():
        CurrentContentConfiguration.clear()
        return "콘텐츠 관련 항목이 비었습니다"
    print("콘텐츠 정보(load) : " + CurrentContentConfiguration.ToString())

    # 콘텐츠 운영 모드 파트
    global DB
    global CurrentUser
    CurrentContentConfiguration.type = int(request.form.get("chk_info1")) if request.form.get("chk_info1") is not None else 0
    user_name = request.form["patient_name1"]

    # user_sex = int(request.form.get("sex"))
    if request.form.get("sex1") =="Male":
        user_sex = 1
    else:
        user_sex = 0

    user_size = int(request.form["foot_size1"]) if request.form["foot_size1"] != "" else 0

    #user_severe = int(request.form.get("severe"))
    # if request.form.get("severe1") =="X":
    #     user_severe = 0
    # else:
    #     user_severe = 1

    user_severe = request.form.get("severe1")
    user_age = request.form["patient_age1"]

    _currentUser = User(user_name, user_sex, user_size, user_severe, user_age)

    if (_currentUser.isEmptry()):
        return "사용자 관련 항목이 비었습니다"

    else:
        try:
            DB.session.add(_currentUser)
            DB.session.commit()
        except exc.InvalidRequestError as e:
            DB.session.rollback()
            return "잘못된 값"
        except exc.IntegrityError as e:
            DB.session.rollback()
            _currentUser = User.query.filter_by(name=user_name, sex=user_sex, size=user_size, severe=user_severe, age=user_age).first()
            print("중복된 값: 기존에 등록된 사용자 사용")

    CurrentUser = UserInformation(_currentUser.name, _currentUser.sex, _currentUser.size, _currentUser.severe, _currentUser.age)
    print("사용자 정보(severe, load) : " + str(_currentUser.severe))
    return redirect("/")


@APP.route("/data/download", methods=["POST"])
def GetDataFile():
    index = int(request.form["user_index"])
    user = User.query.filter_by(id=index).first()
    result_list = []
    content_result_list = ContentResult.query.filter_by(user=user).all()
    result_list.append("ID,{0}\n이름,{1}\n성별,{2}\n발사이즈,{3}\n중증도,{4}\n나이,{5}".format(
            user.id, user.name, "Male" if user.sex == 1 else "Female",
            user.size, user.severe, user.age))
    for content_result in content_result_list:
        tempTable = list(content_result.convertToTable())
        for index in range(len(tempTable)):
            tempTable[index] = str(tempTable[index])
        result_list.append(','.join(tempTable))
    response = Response(
        StringIO('\n'.join(result_list)),
        mimetype='text/csv', 
        content_type='application/octet-stream',
    )
    response.headers["Content-Disposition"] = "attachment; filename=train_data.csv"
    return response

@APP.route("/content/changebtn", methods=["POST"])
def ChangeButton():
    global btnhasPushed
    btnhasPushed = not btnhasPushed
    print("btnhasPushed: " + str(btnhasPushed))
    return render_template("MainPage.html", btnhasPushed=btnhasPushed)

@APP.route("/content/changebtn_fromUnity", methods=["POST"])
def ChangeButton_FromUnity():
    global btnhasPushed
    return str(btnhasPushed)

@APP.route("/debugmode", methods=["POST"])
def DebugMode_changebtn():
    global debugbtn
    debugbtn = not debugbtn
    return render_template("AdminMode.html", debugbtn=debugbtn)
@APP.route("/debugmode_fromUnity", methods=["POST"])
def DebugMode_FromUnity():
    global debugbtn
    return str(debugbtn)