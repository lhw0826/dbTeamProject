import os
import hashlib
from forms import SignUp, Login, Condition, CreateTeam, Satisfy
from flask import Flask, request, render_template, redirect, session
from models import db, UserData, ConditionData, WaitTeamData, DoneTeamData, NeedLangData
from sqlalchemy.sql import exists


app = Flask(__name__)

@app.route('/', methods=['GET'])
def home():
    userid = session.get('userId', None)
    return render_template('base.html', userId=userid)


@app.route('/login', methods=['GET', 'POST'])
def checkValid():
    form = Login()
    if form.validate_on_submit():
        userid = form['userId'].data
        password = form['userPw'].data
        userdata = UserData.query.filter(UserData.userId == userid).first()
        if not userdata:
            form.userId.errors.append('잘못된 아이디입니다.')
            return render_template('index.html', form=form)
        elif userdata.userPw != password:
            form.userPw.errors.append("잘못된 비밀번호 입니다.")
            return render_template('index.html', form=form)
        else:
            done_user = DoneTeamData.query.join(UserData, UserData.userNum == DoneTeamData.userNum)
            if done_user is exists:
                return redirect("/satisfy")
            else:
                session['userId'] = userid
                return redirect("/condition")

    return render_template('index.html', form=form)



@app.route('/logout', methods=['GET'])
def logout():
    session.pop('userId', None)
    return redirect('/')


@app.route('/register', methods=['GET', 'POST'])
def insertUserData():
    form = SignUp()
    if form.validate_on_submit():
        userid = UserData.query.filter(UserData.userId == form.userId.data).first()
        if userid:
            form.userId.errors.append('이미 가입된 아이디입니다.')
        if form.userId.errors:
            return render_template('/register.html', form=form)

        userdata = UserData()
        userdata.userId = form.data.get('userId')
        userdata.userPw = form.data.get('userPw')
        userdata.userMajor = form.data.get('userMajor')
        userdata.userLang = form.data.get('userLang')

        db.session.add(userdata)
        db.session.commit()

        return redirect('/')
    return render_template('register.html', form=form)

@app.route('/condition', methods=['GET', 'POST'])
def sendCondition():
    form = Condition()
    form.travelDes.choices = [(a.countryName) for a in NeedLangData.query.order_by(NeedLangData.countryName)]
    form.travelLang.choices = [(a.countryLang) for a in NeedLangData.query.order_by(NeedLangData.countryName)]

    travelNum = {'2명': 2, '3명':3, '4명':4}
    for key in travelNum.keys():
        form.travelNum.choices.append(travelNum[key])

    if form.validate_on_submit():
        #waitteamdata에 조건에 맞는 팀이 있는지 탐색 / 있으면 waitteamlist 없으면 teamcreate
        return render_template('condition.html', form=form, result='저장했습니다.') #왼쪽코드는 임시코드
    return render_template('condition.html', form=form)

@app.route('/createteam', methods=['GET', 'POST'])
def insertWaitTeamData():
    userid = session.get('userId', None)
    form = CreateTeam()
    if form.validate_on_submit():
        doneteamdata = DoneTeamData()
        doneteamdata.teamName = form.data.get('teamName')
        doneteamdata.teamIntro = form.data.get('teamIntro')
        doneteamdata.teamTo = form.data.get('teamTo')
        doneteamdata.teamNumGoal = form.data.get('teamNumGoal')

        db.session.add(doneteamdata)
        db.session.commit()

        return redirect('/condition')
    return render_template('/createteam.html', form=form)

@app.route('/waitteamlist', methods=['GET', 'POST'])
def findTeam():
    WaitTeamData.query.all()




basedir = os.path.abspath(os.path.dirname(__file__))
dbfile = os.path.join(basedir, 'db.sqlite')

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + dbfile
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'jawelfusidufhxkcljvhwiul'

db.init_app(app)
db.app = app
db.create_all()

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)