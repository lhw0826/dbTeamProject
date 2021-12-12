import os  #디렉토리 절대 경로
from forms import SignUp, Login, Condition, CreateTeam, Satisfy
from flask import Flask, request, render_template, redirect, session, flash
from models import db, UserData, ConditionData, WaitTeamData, DoneTeamData, NeedLangData, ContactData



app = Flask(__name__)

@app.route('/', methods=['GET'])
def home():
    # 로그인 세션정보('userid')
    userid = session.get('userId', None)
    return render_template('home.html', userId=userid)  # home.html에서 userId 명시해줌

# login 페이지 접속(GET)처리와, "action=/login" 처리(POST)모두 정의
@app.route('/login', methods=['GET', 'POST'])
def checkValid():
    form = Login()  # 로그인 폼
    if form.validate_on_submit():  # 내용 채우지 않은 항목이 있는지까지 체크
        userid = form['userId'].data  # form에서의 userId의 데이터를 가져와 userid에 저장
        password = form['userPw'].data  # form에서의 userPw의 데이터를 가져와 password에 저장
        userdata = UserData.query.filter(UserData.userId == userid).first() # 가입된 ID가 있는지 조회Query 실행
        if not userdata:  # 가입된 ID가 없을 경우
            form.userId.errors.append('잘못된 아이디입니다.')
            return render_template('login.html', form=form)
        elif userdata.userPw != password:  # 가입한 ID의 PW가 다를 경우
            form.userPw.errors.append("잘못된 비밀번호 입니다.")
            return render_template('login.html', form=form)
        else:  # 쿼리 데이터가 존재할 경우(ID와 PW가 맞을 경우)
            session['userId'] = userid  # userid를 session에 저장한다.
            done_user = db.session.query(DoneTeamData).\
                filter(DoneTeamData.userNum == UserData.userNum, DoneTeamData.userSat == None).\
                filter(UserData.userId==userid).all()  # 만족 여부가 저장되어 있지 않은 회원이 속한 팀 조회Query 실행
            if done_user:  # 쿼리 데이터가 존재할 경우
                return redirect('/satisfy')
            else:  # 회원이 속한 팀이 없거나, 속한 팀에 대한 만족 여부 데이터가 저장되어 있는 경우
                return redirect("/condition")

    return render_template('login.html', form=form)  # login.html에서 form 명시해줌

# satisfy 페이지 접속(GET)처리와, "action=/satisfy" 처리(POST)모두 정의
@app.route('/satisfy', methods=['Get', 'POST'])
def ask_satisfy():
    userid = session.get('userId', None)
    form = Satisfy()  # 만족여부 폼
    input_sat = {'Yes':'네 다른 여행지도 보고 싶습니다.' , 'N0':'아니요 새로운 팀을 원합니다.'}  # 합류한 팀에 대한 만족 여부를 물어봄
    for key in input_sat.keys():
        form.input_sat.choices.append(input_sat[key])

    if form.validate_on_submit():  # 유효할 경우
        usersat = db.session.query(DoneTeamData).filter(DoneTeamData.userNum == UserData.userNum, DoneTeamData.userSat == None).\
            filter(UserData.userId == userid).first()   # 만족 여부가 저장되어 있지 않은 회원이 속한 팀 조회Query 실행
        usersat.userSat = form.data.get('input_sat')  # form에서의 input_sat을 가져와 usersat의 만족 여부에 저장
        db.session.commit()  # 변동사항 저장
        if usersat.userSat == '네 다른 여행지도 보고 싶습니다.':  # 합류한 팀이 만족스러울 경우
            return redirect('/condition')
        else:  # 합류한 팀이 불만족스러울 경우
            doneteamdata = db.session.query(DoneTeamData).filter(DoneTeamData.userSat == '아니요 새로운 팀을 원합니다.').first()  # 만족 여부가 불만족인 팀 조회Query 실행
            recnum = db.session.query(WaitTeamData).filter(WaitTeamData.teamCode == doneteamdata.teamCode).first()  # WaitTeamData에서 doneteamdata 팀 조회Query 실행
            recnum.teamRecNum -= 1  # recnum의 현재 합류한 팀의 인원 수에서 한 명을 뺌
            db.session.delete(doneteamdata)  # DoneTeamData에서 불만족스러운 팀과 회원 매칭 제거
            db.session.commit()  # 변동사함 저장
            WaitTeamData.query.filter_by(teamRecNum=0).delete()  # 만약 팀에 남아 있는 인원이 0명일 경우 WaitTeamData에서 팀 제거
            db.session.commit() # 변동사항 저장
            return redirect('/condition')
    return render_template('satisfy.html', form=form, userid=userid)


@app.route('/logout', methods=['GET'])
def logout():
    session.pop('userId', None)
    return redirect('/')

# register 페이지 접속(GET)처리와, "action=/register" 처리(POST)모두 정의
@app.route('/register', methods=['GET', 'POST'])
def insertUserData():
    form = SignUp()  # 회원가입 폼
    if form.validate_on_submit():  # 유효할 경우
        userid = UserData.query.filter(UserData.userId == form.userId.data).first()  # 중복ID 조회Query 실행
        if userid:  # 중복 ID일 경우
            form.userId.errors.append('이미 가입된 아이디입니다.')
            return render_template('register.html', form=form)

        userdata = UserData()
        userdata.userId = form.data.get('userId')  # form에서의 userId 데이터를 가져와 UserData 클래스의 userId에 저장
        userdata.userPw = form.data.get('userPw')  # form에서의 userPw 데이터를 가져와 UserData 클래스의 userPw 저장
        userdata.userMajor = form.data.get('userMajor')  # form에서의 userMajor 데이터를 가져와 UserData 클래스의 userMajor 저장
        userdata.userLang = form.data.get('userLang')  # form에서의 userLang 데이터를 가져와 UserData 클래스의 userLang 저장

        flash('회원가입이 완료되었습니다.')
        db.session.add(userdata)  # DB저장
        db.session.commit()  # 변동사항 저장

        return redirect('/')
    return render_template('register.html', form=form)

# condition 페이지 접속(GET)처리와, "action=/condition" 처리(POST)모두 정의
@app.route('/condition', methods=['GET', 'POST'])
def sendCondition():
    userid = session.get('userId', None)
    form = Condition()  # 조건선택 폼
    # 여행 목적지 선택
    form.travelDes.choices = [(a.countryName) for a in NeedLangData.query.order_by(NeedLangData.countryName)]
    # 특기 언어 선택
    form.travelLang.choices = [(a.countryLang) for a in NeedLangData.query.group_by(NeedLangData.countryLang)]
    # 원하는 팀 인원 선택
    travelNum = {'2명': 2, '3명':3, '4명':4}
    for key in travelNum.keys():
        form.travelNum.choices.append(travelNum[key])

    if form.validate_on_submit():  # 유효할 경우
        conditiondata = ConditionData()
        conditiondata.travelDes = form.data.get('travelDes')  # form에서의 travelDes 데이터를 가져와 ConditionData 클래스의 travelDes 저장
        conditiondata.travelNum = form.data.get('travelNum') # form에서의 travelNum 데이터를 가져와 ConditionData 클래스의 travelNum 저장
        conditiondata.travelLang = form.data.get('travelLang') # form에서의 travelLang 데이터를 가져와 ConditionData 클래스의 travelLang 저장
        conditiondata.userNum = db.session.query(UserData.userNum).filter(UserData.userId==userid)  # 회원의 회원번호를 ConditionData 클래스의 userNum에 저장

        db.session.add(conditiondata)  # DB저장
        db.session.commit()  # 변동사항 저장
        return redirect('/waitteam')
    return render_template('condition.html', form=form, userid=userid)

# teamcreate 페이지 접속(GET)처리와, "action=/createteam" 처리(POST)모두 정의
@app.route('/teamcreate', methods=['GET', 'POST'])
def insertWaitTeamData():
    userid = session.get('userId', None)
    userdata = UserData.query.filter(UserData.userId == userid).first()
    form = CreateTeam() # 팀 생성 폼
    form.userNum.choices = [userdata.userNum] #현재 접속한 유저의 유저 번호를 선택할 수 있도록 함
    form.teamTo.choices = [(a.countryName) for a in NeedLangData.query.group_by(NeedLangData.countryName)] # NeedLangData 테이블에서 나라 이름을 가져와 그 중 선택할 수 있게 함
    teamNumGoal = {'2명': 2, '3명': 3, '4명': 4} #같이 갈 인원 선택
    for key in teamNumGoal.keys():
        form.teamNumGoal.choices.append(teamNumGoal[key])
    if form.validate_on_submit():   # 유효할 경우
        doneteamdata = DoneTeamData()   # 매칭 완료 폼 생성
        waitteamdata = WaitTeamData()   # 매칭 대기팀 폼 생성
        contactdata = ContactData() #연락처 데이터 폼 생성
        doneteamdata.userNum = db.session.query(UserData.userNum).filter(UserData.userId==userid)   # 현재 접속 중인 userid로 userNum 조회하여 할당
        waitteamdata.teamName = form.data.get('teamName')   # form에서의 teamName 데이터를 가져와 waitteamdata 클래스의 teamName 저장
        waitteamdata.teamIntro = form.data.get('teamIntro')     # form에서의 teamIntro 데이터를 가져와 waitteamdata 클래스의 teamIntro 저장
        waitteamdata.teamTo = form.data.get('teamTo')   # form에서의 teamTo 데이터를 가져와 waitteamdata 클래스의 teamTo 저장
        waitteamdata.teamNumGoal = form.data.get('teamNumGoal') # form에서의 teamNumGoal 데이터를 가져와 waitteamdata 클래스의 teamNumGoal 저장
        contactdata.teamAddress = form.data.get('teamAddress')  # form에서의 teamAddress 데이터를 가져와 contactdata 클래스의 teamAddress 저장
        waitteamdata.teamRecNum = 1    # 새로 생긴 팀이니까 현재 인원 1
        doneteamdata.teamCode = db.session.query(WaitTeamData.teamCode).filter(WaitTeamData.teamName==waitteamdata.teamName)    # WaitTeamData에서 teamName으로 teamCode 쿼리하여 할당 (아래 라인도)
        contactdata.teamCode = db.session.query(WaitTeamData.teamCode).filter(WaitTeamData.teamName==waitteamdata.teamName)
        db.session.add(doneteamdata)
        db.session.add(waitteamdata)
        db.session.add(contactdata) #각각의 데이터들 DB에 저장
        flash('팀생성이 완료되었습니다.')

        db.session.commit() #변동사항 저장
        return redirect('/')
    return render_template('teamcreate.html', form=form, userid=userid)

# condition 페이지 접속(GET)처리
@app.route('/waitteam', methods=['GET'])
def findTeam():
    userid = session.get('userId', None)
    recent_id = db.session.query(ConditionData.id).order_by(ConditionData.id.desc()).first()    # id로 가장 최근 추가된 데이터 조회
    team_list = db.session.query(WaitTeamData).\
        filter(WaitTeamData.teamTo == ConditionData.travelDes, WaitTeamData.teamNumGoal == ConditionData.travelNum, WaitTeamData.teamRecNum < WaitTeamData.teamNumGoal).\
        filter(ConditionData.id == recent_id[0]).all()  # ConditionData의 데이터를 WaitTeamData의 데이터와 비교, 조건에 맞는 팀을 조회하여 팀 리스트 생성

    return render_template('teamlist.html', userid=userid, team_list=team_list)

# condition 페이지 접속(GET)처리
@app.route('/teaminfo/<int:teamCode>', methods=['GET'])
def teaminfo(teamCode):     # findTeam으로 찾은 팀 정보를 보여주는 함수
    userid = session.get('userId', None)
    team = WaitTeamData.query.get_or_404(teamCode)  # teamCode로 WaitTeamData에서 객체 가져옴 없으면 404 반환
    userLang_list = db.session.query(UserData.userLang).\
        filter(UserData.userNum==DoneTeamData.userNum).\
        filter(DoneTeamData.teamCode == teamCode).\
        group_by(UserData.userLang).all()   # 팀에 속한 유저들의 특기 언어 조회
    myteam = db.session.query(DoneTeamData).\
        filter(UserData.userNum == DoneTeamData.userNum, DoneTeamData.teamCode == teamCode). \
        filter(UserData.userId == userid).first()   # 현재 접속한 유저가 소속된 팀인지 확인
    if myteam:
        flash('이미 합류한 팀입니다.')   # 유저가 자신이 속한 팀을 고른 경우
        return render_template('teaminfo.html', team=team, userLang_list=userLang_list, userid=userid, myteam=myteam)

    return render_template('teaminfo.html', team=team, userLang_list=userLang_list, userid=userid)

# condition 페이지 접속(GET)처리
@app.route('/teaminfo/end/<int:teamCode>', methods=['GET'])
def getAddress(teamCode):       # 매칭된 팀의 연락처 정보를 가져오는 함수
    userid = session.get('userId', None)
    team = ContactData.query.get(teamCode)  # teamCode로 ContactData에서 객체 가져옴
    myteam = db.session.query(DoneTeamData).\
        filter(UserData.userNum == DoneTeamData.userNum, DoneTeamData.teamCode == teamCode).\
        filter(UserData.userId==userid).first() # 현재 접속한 유저가 소속된 팀인지 확인

    if not myteam:
        user = DoneTeamData(teamCode=teamCode, userNum=db.session.query(UserData.userNum).filter(UserData.userId==userid))
        recnum = db.session.query(WaitTeamData).filter(WaitTeamData.teamCode == teamCode).first()
        recnum.teamRecNum += 1 # 유저가 속한 팀이 아닌 경우 팀 합류
        db.session.add(user)
        db.session.commit()
        return render_template('end.html', team=team, userid=userid)
    return render_template('end.html', team=team, userid=userid)


# condition 페이지 접속(GET)처리
@app.route('/showteam', methods=['GET'])
def showTeam():
    userid = session.get('userId', None)
    team_list = db.session.query(WaitTeamData). \
        filter(WaitTeamData.teamCode == DoneTeamData.teamCode, DoneTeamData.userNum == UserData.userNum).\
        filter(UserData.userId == userid).all()  # 회원이 속한 팀 리스트 보여주기
    return render_template('myteam.html', userid=userid, team_list=team_list)  # myteam.html에서 team_list 명시해줌



basedir = os.path.abspath(os.path.dirname(__file__)) #현재 파일이 있는 디렉토리 절대 경로
dbfile = os.path.join(basedir, 'db.sqlite') #데이터베이스 파일을 만든다

# 내가 사용할 데이터베이스 URI
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + dbfile
# 사용자 요청이 끝나면 커밋=DB반영 한다
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
# 버전상관없게 처리
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# 해시 값은 임의로 적음
app.config['SECRET_KEY'] = 'jawelfusidufhxkcljvhwiul'

# app 설정값 초기화
db.init_app(app)
# models.py에서 db를 가져와서 db.app에 app을 명시적으로 넣는다
db.app = app
# db 생성
db.create_all()

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)


