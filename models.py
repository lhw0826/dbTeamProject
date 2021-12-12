from flask_sqlalchemy import SQLAlchemy

db=SQLAlchemy()

class UserData(db.Model):
    __tablename__ = 'userdata'
    userNum = db.Column(db.Integer, primary_key=True, autoincrement=True)
    userId = db.Column(db.String(32))
    userPw = db.Column(db.String(255))
    userMajor = db.Column(db.String(32))
    userLang = db.Column(db.String(32))

    conditiondatas = db.relationship('ConditionData', backref='user')
    doneteamdatas = db.relationship('DoneTeamData', backref='userid')

class WaitTeamData(db.Model):
    __tablename__ = 'waitteamdata'
    teamCode = db.Column(db.Integer, primary_key = True, autoincrement=True)
    teamName = db.Column(db.String(32))
    teamIntro = db.Column(db.String(128))
    teamTo = db.Column(db.String(32))
    teamRecNum = db.Column(db.Integer)
    teamNumGoal = db.Column(db.Integer)

    doneteamdatas= db.relationship('DoneTeamData', backref='teamcode', lazy=True)
    contactdatas = db.relationship('ContactData', backref='teamcode', uselist=False)

class DoneTeamData(db.Model):
    __tablename__ = 'doneteamdata'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    teamCode = db.Column(db.Integer, db.ForeignKey('waitteamdata.teamCode'))
    userNum = db.Column(db.Integer, db.ForeignKey('userdata.userNum'))
    userSat = db.Column(db.String(32))



class ContactData(db.Model):
    __tablename__ = 'contactdata'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    teamCode = db.Column(db.Integer, db.ForeignKey('waitteamdata.teamCode'))
    teamAddress = db.Column(db.String(128))

class NeedLangData(db.Model):
    __tablename__ = 'needlangdata'
    countryName = db.Column(db.String(32))
    countryCode = db.Column(db.Integer, primary_key=True, autoincrement=True)
    countryLang = db.Column(db.String(32))


class ConditionData(db.Model):
    __tablename__ = 'conditiondata'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    userNum = db.Column(db.Integer, db.ForeignKey('userdata.userNum'))
    travelDes = db.Column(db.String(32))
    travelNum = db.Column(db.Integer)
    travelLang = db.Column(db.String(32))