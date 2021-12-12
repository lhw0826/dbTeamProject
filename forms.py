# 데이터 수집을 위한 형식
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, IntegerField, TextAreaField, SelectField, BooleanField
from wtforms.validators import DataRequired, EqualTo


class SignUp(FlaskForm):    #회원가입 폼
    userId = StringField('userId', validators=[DataRequired(message='필숫값입니다.')])    # 유저의 아이디를 String 형태로 받음
    userPw = PasswordField('userPw', validators=[DataRequired(message='필숫값입니다.')])  # 유저의 비밀번호를 Stirng 형태로 받음 (PasswordField를 사용하여 표시가 안 되도록 함)
    repassword = PasswordField('repassword', validators=[DataRequired(message='비밀번호를 재입력하세요'), EqualTo('userPw')])  # 앞서 작성한 userPw와의 일치 여부 확인
    userMajor = StringField('useMajor', validators=[DataRequired(message='필숫값입니다.')])   # 유저의 전공 정보를 String 형태로 받음
    userLang = StringField('userLang', validators=[DataRequired(message='필숫값입니다.')])    # 유저의 특기 언어 정보를 String 형태로 받음


class Login(FlaskForm): #로그인 폼
    userId = StringField('userId', validators=[DataRequired()]) # 유저의 아이디를 String 형태로 받음
    userPw = PasswordField('userPw', validators=[DataRequired()])   # 유저의 비밀번호를 Stirng 형태로 받음 (PasswordField를 사용하여 표시가 안 되도록 함)

class Condition(FlaskForm): # 매칭 조건 폼
    travelDes = SelectField('travelDes', validators=[DataRequired()])   # 유저가 주어진 여행지 중 하나를 선택하게 함
    travelNum = SelectField('travelNum', validators=[DataRequired()], choices=[])   # 유저가 주어진 팀 인원 중 하나를 선택하게 함
    travelLang = SelectField('travelLang', validators=[DataRequired()]) # 유저가 특기 언어 중 하나를 선택하게 함

class CreateTeam(FlaskForm):
    userNum = SelectField('userNum', validators=[DataRequired()])   # 유저가 주어진 자신의 유저 식별 번호를 선택하게 함
    teamName = StringField('teamNum', validators=[DataRequired()])  # 팀 이름을 String 형태로 받음
    teamIntro = TextAreaField('teamIntro', validators=[DataRequired()]) # 팀 소개문을 String 형태로 받음
    teamTo = SelectField('teamTo', validators=[DataRequired()]) # 유저가 주어진 여행지 중 하나를 선택하게 함
    teamNumGoal = SelectField('teamNumGoal', validators=[DataRequired()], choices=[]) # 유저가 주어진 팀 인원 중 하나를 선택하게 함
    teamAddress = StringField('teamAddress', validators=[DataRequired()])   # 팀 연락처 정보를 String 형태로 받음


class Satisfy(FlaskForm):   # 만족 여부 폼
    input_sat = SelectField('userSat', validators=[DataRequired()], choices=[]) #유저가 만족 여부를 선택하게 함
