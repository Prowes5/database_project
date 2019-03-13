# -*- coding: utf-8 -*-
from flask import Flask,render_template,request,redirect,url_for
from flask_sqlalchemy import SQLAlchemy
from flask import session
import re
import config
import hashlib

app = Flask(__name__)
app.config.from_object(config)

db = SQLAlchemy(app)

global Stu_no_sel
global Tea_no_sel

class lesson_stu(db.Model):
    __tablename__ = 'lesson_stu'
    stu_no = db.Column('stu_no', db.String(10), db.ForeignKey('student.StuNo'), primary_key=True)
    lesson_no = db.Column('lesson_no', db.String(5), db.ForeignKey('lesson.LessonNo'), primary_key=True)
    score = db.Column('score', db.Integer)
    Lessons = db.relationship('Lesson',backref=db.backref('Stus'))
    Stus = db.relationship('Stu', backref=db.backref('Lessons'))

class Course:
    def __init__(self,stu_no,stu_name,lesson_no,lesson_name,score):
        self.stu_no = stu_no
        self.stu_name = stu_name
        self.lesson_no = lesson_no
        self.lesson_name = lesson_name
        self.score = score

class Cscore:
    def __init__(self,lesson_no,lesson_name,lesson_credit,score):
        self.lesson_no = lesson_no
        self.lesson_name = lesson_name
        self.lesson_credit = lesson_credit
        self.score = score

class Stu(db.Model):
    __tablename__ = 'student'
    StuNo = db.Column(db.String(10),primary_key=True)   #学号
    StuName = db.Column(db.String(30),nullable=False)   #姓名
    StuPass = db.Column(db.String(32),nullable=False)   #密码
    StuGen = db.Column(db.String(4),nullable=False)     #性别
    StuGrade = db.Column(db.Integer, nullable=False)    #年级
    StuPro = db.Column(db.String(20), nullable=False)   #专业
    StuYear = db.Column(db.Integer,nullable=False)      #学制
    StuAddr = db.Column(db.String(50),nullable=False)   #地区
    StuAge = db.Column(db.Integer,nullable=False)       #年龄
    StuPol = db.Column(db.String(20),nullable=False)    #政治面貌
    StuNation = db.Column(db.String(10),nullable=False) #民族
    StuRec = db.Column(db.Text)                         #奖惩记录
    StuFlag = db.Column(db.String(100))                 #修复转退标记

class Manage(db.Model):
    __tablename__ = 'manager'
    username = db.Column(db.String(10),primary_key=True) #管理员用户名
    password = db.Column(db.String(32),nullable=False)  #管理员密码



class Lesson(db.Model):
    __tablename__ = 'lesson'
    LessonNo = db.Column(db.String(5),primary_key=True)
    LessonName = db.Column(db.String(20),nullable=False)
    LessonCredits = db.Column(db.Integer,nullable=False)
    Tea_No = db.Column(db.String(8), db.ForeignKey('teacher.TeaNo'))
    Tea = db.relationship('Tea',backref = db.backref('lessons'))


class Tea(db.Model):
    __tablename__ = 'teacher'
    TeaNo = db.Column(db.String(8),primary_key=True)
    TeaName = db.Column(db.String(30),nullable=False)
    TeaPass = db.Column(db.String(32),nullable=False)

db.create_all()


#跳转到登录页面
@app.route('/')
def hello_world():
    return redirect(url_for('login'))


#登录
@app.route('/login/',methods=['GET','POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    else:
        No = request.form.get('No')
        if len(No)==8:
            TeaNo = No
            password = Md5(request.form.get('password'))
            user = Tea.query.filter(Tea.TeaNo == TeaNo,Tea.TeaPass==password).first()
            if user:
                session['user_No'] = user.TeaNo
                session.permanent = True
                return redirect(url_for('Tindex'))
            else:
                return '<script>' \
                'alert("登录失败，请重新登录。");' \
                'window.history.back(-1);' \
                '</script>'
        elif len(No) == 10:
            StuNo = No
            password = Md5(request.form.get('password'))
            user = Stu.query.filter(Stu.StuNo == StuNo,Stu.StuPass==password).first()
            if user:
                session['user_No'] = user.StuNo
                session.permanent = True
                return redirect(url_for('Sindex'))
            else:
                return '<script>' \
                'alert("登录失败，请重新登录。");' \
                'window.history.back(-1);' \
                '</script>'
        elif len(No) == 5:
            username = No
            password = Md5(request.form.get('password'))
            user = Manage.query.filter(Manage.username == username,Manage.password == password).first()
            if user:
                session['user_No'] = user.username
                session.permanent = True
                return redirect(url_for('Mindex'))
            else:
                return '<script>' \
                'alert("登录失败，请重新登录。");' \
                'window.history.back(-1);' \
                '</script>'

        else:
            return '<script>' \
                    'alert("登录失败，请重新登录。");' \
                    'window.history.back(-1);' \
                    '</script>'


#教师首页
@app.route('/teacher/index/')
def Tindex():
    addrs = []
    nations = []
    pols = []
    ages = []
    dic1 = {}
    dic2 = {}
    dic3 = {}
    dic4 = {}
    stus = Stu.query.filter().all()
    for stu in stus:
        addrs.append(stu.StuAddr[0:2])
        nations.append(stu.StuNation)
        pols.append(stu.StuPol)
        ages.append(stu.StuAge)
    # 统计学生地区
    for addr in addrs:
        d = dic1.get(addr)
        if d == None:
            dic1[addr] = 1
        else:
            dic1[addr] = dic1[addr] + 1
    for dic in dic1:
        dic1[dic] = dic1[dic] / len(stus) * 100
    # 统计学生民族
    for nation in nations:
        d = dic2.get(nation)
        if d == None:
            dic2[nation] = 1
        else:
            dic2[nation] = dic2[nation] + 1
    for dic in dic2:
        dic2[dic] = dic2[dic] / len(stus) * 100
    # 统计学生的政治面貌
    for pol in pols:
        d = dic3.get(pol)
        if d == None:
            dic3[pol] = 1
        else:
            dic3[pol] = dic3[pol] + 1
    for dic in dic3:
        dic3[dic] = dic3[dic] / len(stus) * 100
    # 统计学生的年龄
    for age in ages:
        d = dic4.get(age)
        if d == None:
            dic4[age] = 1
        else:
            dic4[age] = dic4[age] + 1
    for dic in dic4:
        dic4[dic] = dic4[dic] / len(stus) * 100
    lss = lesson_stu.query.filter().all()
    dic5 = {}
    scores = []
    for ls in lss:
        scores.append(ls.score)
    for score in scores:
        if score == None:
            score = '无成绩'
        elif score < 60 and score >= 0:
            score = '不及格'
        elif score >= 60 and score < 70:
            score = '及格'
        elif score < 80 and score >= 70:
            score = '中等'
        elif score < 90 and score >= 80:
            score = '良好'
        elif score <= 100 and score >= 90:
            score = '优秀'
        else:
            score = '无成绩'
        d = dic5.get(score)
        if d == None:
            dic5[score] = 1
        else:
            dic5[score] = dic5[score] + 1
    for dic in dic5:
        dic5[dic] = dic5[dic] / len(lss) * 100
        dic5[dic] = round(dic5[dic], 1)
    return render_template('Tindex.html', dic1=dic1, dic2=dic2, dic3=dic3, dic4=dic4, dic5=dic5)

#学生首页
@app.route('/student/index/')
def Sindex():
    addrs = []
    nations = []
    pols = []
    ages = []
    dic1 = {}
    dic2 = {}
    dic3 = {}
    dic4 = {}
    stus = Stu.query.filter().all()
    for stu in stus:
        addrs.append(stu.StuAddr[0:2])
        nations.append(stu.StuNation)
        pols.append(stu.StuPol)
        ages.append(stu.StuAge)
    # 统计学生地区
    for addr in addrs:
        d = dic1.get(addr)
        if d == None:
            dic1[addr] = 1
        else:
            dic1[addr] = dic1[addr] + 1
    for dic in dic1:
        dic1[dic] = dic1[dic] / len(stus) * 100
    # 统计学生民族
    for nation in nations:
        d = dic2.get(nation)
        if d == None:
            dic2[nation] = 1
        else:
            dic2[nation] = dic2[nation] + 1
    for dic in dic2:
        dic2[dic] = dic2[dic] / len(stus) * 100
    # 统计学生的政治面貌
    for pol in pols:
        d = dic3.get(pol)
        if d == None:
            dic3[pol] = 1
        else:
            dic3[pol] = dic3[pol] + 1
    for dic in dic3:
        dic3[dic] = dic3[dic] / len(stus) * 100
    # 统计学生的年龄
    for age in ages:
        d = dic4.get(age)
        if d == None:
            dic4[age] = 1
        else:
            dic4[age] = dic4[age] + 1
    for dic in dic4:
        dic4[dic] = dic4[dic] / len(stus) * 100
    lss = lesson_stu.query.filter().all()
    dic5 = {}
    scores = []
    for ls in lss:
        scores.append(ls.score)
    for score in scores:
        if score == None:
            score = '无成绩'
        elif score < 60 and score >= 0:
            score = '不及格'
        elif score >= 60 and score < 70:
            score = '及格'
        elif score < 80 and score >= 70:
            score = '中等'
        elif score < 90 and score >= 80:
            score = '良好'
        elif score <= 100 and score >= 90:
            score = '优秀'
        else:
            score = '无成绩'
        d = dic5.get(score)
        if d == None:
            dic5[score] = 1
        else:
            dic5[score] = dic5[score] + 1
    for dic in dic5:
        dic5[dic] = dic5[dic] / len(lss) * 100
        dic5[dic] = round(dic5[dic], 1)
    return render_template('Sindex.html', dic1=dic1, dic2=dic2, dic3=dic3, dic4=dic4, dic5=dic5)


#教师管理学生
@app.route('/teacher/chart/')
def Tchart():
    return render_template('Tchart.html')


@app.route('/teacher/form/')
def Tform():
    return render_template('Tform.html')


#学生查询成绩
@app.route('/student/form/')
def Sform():
    ssc = []
    Stu_no = session.get('user_No')
    ls = lesson_stu.query.filter(lesson_stu.stu_no == Stu_no).all()
    for l in ls:
        score = l.score
        lesson = Lesson.query.filter(Lesson.LessonNo == l.lesson_no).first()
        lesson_no = lesson.LessonNo
        lesson_name = lesson.LessonName
        lesson_credit = lesson.LessonCredits
        cssore = Cscore(lesson_no=lesson_no,lesson_name=lesson_name,lesson_credit=lesson_credit,score=score)
        ssc.append(cssore)

    return render_template('Sform.html',ssc=ssc)


#教师管理学生成绩
@app.route('/teacher/tab_panel/',methods=['GET','POST'])
def Ttab_panel():
    if request.method == 'GET':
        courses = []
        Tea_No = session.get('user_No')
        tea = Tea.query.filter(Tea.TeaNo == Tea_No).first()
        for lesson in tea.lessons:
            stus = lesson_stu.query.filter(lesson_stu.lesson_no == lesson.LessonNo).all()
            for stu in lesson.Stus:
                stud = Stu.query.filter(Stu.StuNo == stu.stu_no).first()
                les = Lesson.query.filter(Lesson.LessonNo == stu.lesson_no).first()
                stu_no = stu.stu_no
                stu_name = stud.StuName
                lesson_no = stu.lesson_no
                lesson_name = les.LessonName
                score = stu.score
                course = Course(stu_no=stu_no,stu_name=stu_name,lesson_no=lesson_no,lesson_name=lesson_name,score=score)
                courses.append(course)

        return render_template('Ttab-panel.html', courses=courses)
    else:
        if request.form.get('lesson_no'):
            lesson_no = request.form.get('lesson_no')
            stu_no = request.form.get('stu_no')
            score = request.form.get('score')
            temp1 = re.search("\\D+",lesson_no)
            if temp1:
                return '<script>' \
                       'alert("课程号不合法，请重新输入");' \
                       'window.history.back(-1);' \
                       '</script>'
            temp2 = re.search("\\D+",stu_no)
            if temp2:
                return '<script>' \
                       'alert("学号不合法，请重新输入");' \
                       'window.history.back(-1);' \
                       '</script>'
            temp3 = re.search("\\D+",score)
            if temp3:
                return '<script>' \
                       'alert("输入的成绩不合法，请重新输入");' \
                       'window.history.back(-1);' \
                       '</script>'
            if len(lesson_no) == 5 and len(stu_no) == 10:
                score = int(score)
                ls = lesson_stu.query.filter(lesson_stu.lesson_no==lesson_no,lesson_stu.stu_no==stu_no).first()
                if ls==None:
                    return '<script>' \
                       'alert("没有这个学生或课程或这个学生没有选这个课程");' \
                       'window.history.back(-1);' \
                       '</script>'
                if ls.score:
                    return '<script>' \
                       'alert("这个课程已经有成绩了，如果想要修改请到修改模块");' \
                       'window.history.back(-1);' \
                       '</script>'
                ls.score = score
                db.session.commit()
                return redirect(url_for('Ttab_panel'))
            else:
                return '<script>' \
                       'alert("课程号或学号不合法，请重新输入");' \
                       'window.history.back(-1);' \
                       '</script>'

        if request.form.get('lesson_no_last'):
            lesson_no = request.form.get('lesson_no_last')
            stu_no = request.form.get('stu_no_last')
            score = request.form.get('score_last')
            temp1 = re.search("\\D+", lesson_no)
            if temp1:
                return '<script>' \
                       'alert("课程号不合法，请重新输入");' \
                       'window.history.back(-1);' \
                       '</script>'
            temp2 = re.search("\\D+", stu_no)
            if temp2:
                return '<script>' \
                       'alert("学号不合法，请重新输入");' \
                       'window.history.back(-1);' \
                       '</script>'
            temp3 = re.search("\\D+", score)
            if temp3:
                return '<script>' \
                       'alert("输入的成绩不合法，请重新输入");' \
                       'window.history.back(-1);' \
                       '</script>'
            if len(lesson_no) == 5 and len(stu_no) == 10:
                if score == '':
                    return '<script>' \
                       'alert("请输入你想要修改后的成绩，请重新输入");' \
                       'window.history.back(-1);' \
                       '</script>'
                score = int(score)
                ls = lesson_stu.query.filter(lesson_stu.lesson_no == lesson_no, lesson_stu.stu_no == stu_no).first()
                if ls.score:
                    ls.score = score
                    db.session.commit()
                    return redirect(url_for('Ttab_panel'))
                else:
                    return '<script>' \
                           'alert("这个课程已经还没有成绩，如果想要添加请到添加模块");' \
                           'window.history.back(-1);' \
                           '</script>'
            else:
                return '<script>' \
                       'alert("课程号或学号不合法，请重新输入");' \
                       'window.history.back(-1);' \
                       '</script>'

        if request.form.get('lesson_no_de'):
            lesson_no = request.form.get('lesson_no_de')
            stu_no = request.form.get('stu_no_de')
            temp1 = re.search("\\D+",lesson_no)
            temp2 = re.search("\\D+",stu_no)
            if temp1:
                return '<script>' \
                       'alert("课程号不合法，请重新输入");' \
                       'window.history.back(-1);' \
                       '</script>'
            if temp2:
                return '<script>' \
                       'alert("学号不合法，请重新输入");' \
                       'window.history.back(-1);' \
                       '</script>'
            if len(lesson_no) == 5 and len(stu_no) == 10:
                ls = lesson_stu.query.filter(lesson_stu.lesson_no ==lesson_no,lesson_stu.stu_no == stu_no).first()
                if ls.score:
                    ls.score = None
                    db.session.commit()
                else:
                    return '<script>' \
                       'alert("这里本来就没有成绩，删除失败");' \
                       'window.history.back(-1);' \
                       '</script>'
            else:
                return '<script>' \
                       'alert("课程号或学号不合法，请重新输入");' \
                       'window.history.back(-1);' \
                       '</script>'

    return redirect(url_for('Ttab_panel'))



#老师查询学生简历
@app.route('/teacher/table/')
def Ttable():
    stus = Stu.query.filter().all()
    return render_template('Ttable.html',stus = stus)


#学生个人简历
@app.route('/student/table')
def Stable():
    return render_template('Stable.html')


#老师课程管理
@app.route('/teacher/ui_elements/',methods=['GET','POST'])
def Tui_elements():
    if request.method == 'GET':
        return render_template('Tui-elements.html')
    else:
        lesson_no = request.form.get('lesson_no')
        if lesson_no:
            lesson_name = request.form.get('lesson_name')
            lesson_credits = request.form.get('lesson_credits')
            if lesson_no == '' or lesson_name == '' or lesson_credits == '':
                return '<script>' \
            'alert("课程号、课程名称和学分都需要添加，请重新输入");' \
            'window.history.back(-1);' \
            '</script>'
            fff = re.search("\\D+",lesson_credits)
            if fff:
                return '<script>' \
            'alert("您输入了非法的学分，请重新输入");' \
            'window.history.back(-1);' \
            '</script>'
            else:
                lesson_credits = int(lesson_credits)
            flag = re.search("\\D+",lesson_no)
            if flag:
                return '<script>' \
            'alert("您输入了非法的课程号，请重新输入");' \
            'window.history.back(-1);' \
            '</script>'
            else:
                if len(lesson_no) == 5:
                    lesson = Lesson.query.filter(Lesson.LessonNo == lesson_no).first()
                    print(lesson_no)
                    print(lesson)
                    if lesson:
                        if lesson.Tea_No:
                            return '<script>' \
                           'alert("此课程号以存在，添加失败，请重新输入");' \
                           'window.history.back(-1);' \
                           '</script>'
                        else:
                            lesson.Tea = Tea.query.filter(Tea.TeaNo == session.get('user_No')).first()
                            db.session.commit()
                            return redirect(url_for('Tui_elements'))
                    else:
                        if lesson_credits <=10 and lesson_credits > 0:
                            lesson = Lesson(LessonNo=lesson_no,LessonName=lesson_name,LessonCredits=lesson_credits)
                            lesson.Tea = Tea.query.filter(Tea.TeaNo == session.get('user_No')).first()
                            db.session.add(lesson)
                            db.session.commit()
                            return render_template('Tui-elements.html')
                        else:
                            return '<script>' \
                           'alert("您输入了非法的学分，请重新输入");' \
                           'window.history.back(-1);' \
                           '</script>'
                else:
                    return '<script>' \
                       'alert("您输入了非法的课程号，请重新输入");' \
                       'window.history.back(-1);' \
                       '</script>'
        lesson_no_last = request.form.get('lesson_no_last')
        if lesson_no_last:
            lesson_name_last = request.form.get('lesson_name_last')
            lesson_credits_last = request.form.get('lesson_credits_last')
            if lesson_no_last == '' or lesson_name_last == '' or lesson_credits_last == '':
                return '<script>' \
                       'alert("课程名称和学分都需要重新修改，请重新输入");' \
                       'window.history.back(-1);' \
                       '</script>'
            fff = re.search('\\D+', lesson_credits_last)
            if fff:
                return '<script>' \
                       'alert("您输入了非法的学分，请重新输入");' \
                       'window.history.back(-1);' \
                       '</script>'
            else:
                lesson_credits_last = int(lesson_credits_last)
            flag = re.search('\\D+', lesson_no_last)
            if flag:
                return '<script>' \
                       'alert("不存在此课程号，请重新输入");' \
                       'window.history.back(-1);' \
                       '</script>'
            else:
                if len(lesson_no_last) == 5:
                    if lesson_credits_last <= 10 and lesson_credits_last > 0:
                        lesson = Lesson.query.filter(Lesson.LessonNo == lesson_no_last).first()
                        if lesson:
                            lesson.LessonName = lesson_name_last
                            lesson.LessonCredits = lesson_credits_last
                            db.session.commit()
                            return render_template('Tui-elements.html')
                        else:
                            return '<script>' \
                           'alert("不存在此课程号，请重新输入");' \
                           'window.history.back(-1);' \
                           '</script>'
                    else:
                        return '<script>' \
                               'alert("您输入了非法的学分，请重新输入");' \
                               'window.history.back(-1);' \
                               '</script>'
                else:
                    return '<script>' \
                           'alert("不存在此课程号，请重新输入");' \
                           'window.history.back(-1);' \
                           '</script>'
        lesson_no_de = request.form.get('lesson_no_de')
        if lesson_no_de:
            if lesson_no_de == '':
                return '<script>' \
                       'alert("需要添加课程号，请重新输入");' \
                       'window.history.back(-1);' \
                       '</script>'
            if len(lesson_no_de) == 5:
                lesson = Lesson.query.filter(Lesson.LessonNo == lesson_no_de).first()
                if lesson:
                    db.session.delete(lesson)
                    db.session.commit()
                    return render_template('Tui-elements.html')
                else:
                    return '<script>' \
                       'alert("不存在的课程，请重新输入");' \
                       'window.history.back(-1);' \
                       '</script>'
            else:
                return '<script>' \
                       'alert("不存在的课程，请重新输入");' \
                       'window.history.back(-1);' \
                       '</script>'
        else:
            return '<script>' \
                       'alert("课程号、课程名称和学分都需要添加，请重新输入");' \
                       'window.history.back(-1);' \
                       '</script>'


#学生选课
@app.route('/student/ui_elements',methods=['GET','POST'])
def Sui_elements():
    if request.method == 'GET':
        scs = []
        #得到session中的学号
        stu_no = session.get('user_No')
        #找到该学生
        stu = Stu.query.filter(Stu.StuNo == stu_no).first()
        #找到学生相联系的课程
        for lesson in stu.Lessons:
            Lessons = lesson_stu.query.filter(lesson_stu.stu_no == stu_no).all()
            for lessonl in Lessons:
                sc = Lesson.query.filter(Lesson.LessonNo == lessonl.lesson_no).first()
                scs.append(sc)

        scs = list(set(scs))
        scs_no = []
        notscs = []
        for sc in scs:
            scs_no.append(sc.LessonNo)


        Lessons = Lesson.query.filter().all()
        for lesson in Lessons:
            if lesson.LessonNo not in scs_no:
                notscs.append(lesson)

        return render_template('Sui-elements.html',scs=scs,notscs=notscs)
    else:
        scs = []
        stu_no = session.get('user_No')
        # 找到该学生
        stu = Stu.query.filter(Stu.StuNo == stu_no).first()
        # 找到学生相联系的课程
        for lesson in stu.Lessons:
            Lessons = lesson_stu.query.filter(lesson_stu.stu_no == stu_no).all()
            for lessonl in Lessons:
                sc = Lesson.query.filter(Lesson.LessonNo == lessonl.lesson_no).first()
                scs.append(sc)

        scs_no = []
        notscs = []
        notscs_no = []
        for sc in scs:
            scs_no.append(sc.LessonNo)

        Lessons = Lesson.query.filter().all()
        for lesson in Lessons:
            if lesson.LessonNo not in scs_no:
                notscs.append(lesson)
                notscs_no.append(lesson.LessonNo)

        #将未选的课程号取出组成列表
        if request.form.get('lesson_no'):
            sc = []
            lesson_no = request.form.get('lesson_no')
            temp1 = re.search("\\D+",lesson_no)
            #课程是否

            if temp1:
                return '<script>' \
                       'alert("课程号不合法，请重新输入");' \
                       'window.history.back(-1);' \
                       '</script>'
            if len(lesson_no) == 5:
                # 查找总课表里是否有这个课程
                lesson = Lesson.query.filter(Lesson.LessonNo == lesson_no).first()
                if lesson:
                    # 判断课程是否已选
                    if lesson_no in notscs_no:
                        ls = lesson_stu(stu_no=stu_no, lesson_no=lesson_no)
                        db.session.add(ls)
                        db.session.commit()
                    else:
                        return '<script>' \
                                'alert("这个课程你已经添加过了，请重新输入");' \
                               'window.history.back(-1);' \
                               '</script>'
                else:
                    return '<script>' \
                           'alert("系统中没有这个课程，请重新输入");' \
                           'window.history.back(-1);' \
                           '</script>'
            else:
                return '<script>' \
                       'alert("课程号不合法，请重新输入");' \
                       'window.history.back(-1);' \
                       '</script>'

        #删除已选课程
        if request.form.get('lesson_no_last'):
            lesson_no_last = request.form.get('lesson_no_last')
            temp1 = re.search("\\D+", lesson_no_last)
            if temp1:
                return '<script>' \
                       'alert("课程号不合法，请重新输入");' \
                       'window.history.back(-1);' \
                       '</script>'
            if len(lesson_no_last) == 5:
                ls = lesson_stu.query.filter(lesson_stu.lesson_no == lesson_no_last).first()
                if ls:
                    db.session.delete(ls)
                    db.session.commit()
                else:
                    return '<script>' \
                       'alert("没有添加这个课程，删除失败");' \
                       'window.history.back(-1);' \
                       '</script>'
            else:
                return '<script>' \
                       'alert("没有这个课程，请重新输入");' \
                       'window.history.back(-1);' \
                       '</script>'

        return redirect(url_for('Sui_elements'))

#老师添加学生
@app.route('/teacher/chart/TinsertS/',methods=['GET','POST'])
def T_insert_S():
    if request.method == 'GET':
        return render_template('TinsertS.html')
    else:
        Stu_no = request.form.get('Stu_no')
        Stu_name = request.form.get('Stu_name')
        Stu_pass = request.form.get('Stu_pass')
        Stu_gen = request.form.get('Stu_gen')
        Stu_grade = request.form.get('Stu_grade')
        Stu_pro = request.form.get('Stu_pro')
        Stu_year = request.form.get('Stu_year')
        Stu_addr = request.form.get('Stu_addr')
        Stu_age = request.form.get('Stu_age')
        Stu_nation = request.form.get('Stu_nation')
        Stu_pol = request.form.get('Stu_pol')
        Stu_rec = request.form.get('Stu_rec')
        Stu_flag = request.form.get('Stu_flag')
        temp1 = re.search("\\D+",Stu_no)
        if Stu_no == '' or Stu_name == '' or Stu_gen == '' or Stu_grade == '' or Stu_pro == '' or Stu_year == '' or Stu_addr == '' or Stu_age == '' or Stu_nation == '' or Stu_pol == '' or Stu_pass == '':
            return '<script>' \
                       'alert("学号、姓名、性别、年级、专业、学制、现住址、年龄、民族和政治面貌这些都需要输入，请重新输入");' \
                       'window.history.back(-1);' \
                       '</script>'
        if temp1:
            return '<script>' \
                       'alert("学号不合法，请重新输入");' \
                       'window.history.back(-1);' \
                       '</script>'
        temp2 = re.search("\\D+",Stu_grade)
        if temp2:
            return '<script>' \
                       'alert("年级不合法，请重新输入");' \
                       'window.history.back(-1);' \
                       '</script>'
        temp3 = re.search("\\D+",Stu_year)
        if temp3:
            return '<script>' \
                       'alert("学制不合法，请重新输入");' \
                       'window.history.back(-1);' \
                       '</script>'
        temp4 = re.search("\\D+",Stu_age)
        if temp4:
            return '<script>' \
                       'alert("年龄不合法，请重新输入");' \
                       'window.history.back(-1);' \
                       '</script>'
        if Stu_gen != u'男' and Stu_gen != u'女':
            return '<script>' \
                       'alert("性别输入不合法，请重新输入");' \
                       'window.history.back(-1);' \
                       '</script>'
        Stu_grade = int(Stu_grade)
        Stu_year = int(Stu_year)
        Stu_age = int(Stu_age)
        if Stu_grade <= 1970:
            return '<script>' \
                       'alert("输入的年级不合法，请重新输入");' \
                       'window.history.back(-1);' \
                       '</script>'
        if Stu_year<=0 or Stu_year >= 10:
            return '<script>' \
                       'alert("输入的学制不合法，请重新输入");' \
                       'window.history.back(-1);' \
                       '</script>'
        if Stu_age <=12 or Stu_age >=100:
            return '<script>' \
                       'alert("输入的年龄有点儿离谱，如情况属实，请联系管理员");' \
                       'window.history.back(-1);' \
                       '</script>'
        if len(Stu_no) != 10:
            return '<script>' \
                       'alert("学号不合法，请重新输入");' \
                       'window.history.back(-1);' \
                       '</script>'
        stu = Stu.query.filter(Stu.StuNo == Stu_no).first()
        if stu:
            return '<script>' \
                       'alert("该学生已经存在，请重新输入学号添加");' \
                       'window.history.back(-1);' \
                       '</script>'
        stu = Stu(StuNo=Stu_no,StuName=Stu_name,
                  StuPass=Md5(Stu_pass),StuGen=Stu_gen,
                  StuGrade=Stu_grade,StuPro=Stu_pro,
                  StuYear=Stu_year,StuAddr=Stu_addr,
                  StuAge=Stu_age,StuPol=Stu_pol,
                  StuNation=Stu_nation,StuRec=Stu_rec,
                  StuFlag=Stu_flag
                  )
        db.session.add(stu)
        db.session.commit()
        return redirect(url_for('Tchart'))

#老师修改学生
@app.route('/teacher/chart/TupdateS/',methods=['GET','POST'])
def T_update_S():
    if request.method == 'GET':
        #### 利用全局变量，对用户输入的学号进行查询，并返回到网页上
        global Stu_no_sel
        Stu_no_sel = request.args.get('Stu_no_sel')
        sstu = Stu.query.filter(Stu.StuNo == Stu_no_sel).first()
        return render_template('TupdateS.html',sstu=sstu)
    else:
        Stu_name = request.form.get('Stu_name')
        Stu_gen = request.form.get('Stu_gen')
        Stu_grade = request.form.get('Stu_grade')
        Stu_pro = request.form.get('Stu_pro')
        Stu_year = request.form.get('Stu_year')
        Stu_addr = request.form.get('Stu_addr')
        Stu_age = request.form.get('Stu_age')
        Stu_nation = request.form.get('Stu_nation')
        Stu_pol = request.form.get('Stu_pol')
        Stu_rec = request.form.get('Stu_rec')
        Stu_flag = request.form.get('Stu_flag')
        ### 利用正则表达式和各个条件对输入进行限制
        stu = Stu.query.filter(Stu.StuNo == Stu_no_sel).first()
        ### 如果用户输入为空的话，就看作不改动
        if Stu_name == '':
            Stu_name = stu.StuName
        if Stu_gen == '':
            Stu_gen = stu.StuGen
        if Stu_grade == '':
            Stu_grade = stu.StuGrade
        if Stu_pro == '':
            Stu_pro = stu.StuPro
        if Stu_year == '':
            Stu_year = stu.StuYear
        if Stu_addr == '':
            Stu_addr = stu.StuAddr
        if Stu_age == '':
            Stu_age = stu.StuAge
        if Stu_pol == '':
            Stu_pol = stu.StuPol
        if Stu_nation == '':
            Stu_nation = stu.StuNation
        Stu_grade = str(Stu_grade)
        temp2 = re.search("\\D+", Stu_grade)
        if temp2:
            return '<script>' \
                   'alert("年级不合法，请重新输入");' \
                   'window.history.back(-1);' \
                   '</script>'
        Stu_year = str(Stu_year)
        temp3 = re.search("\\D+", Stu_year)
        if temp3:
            return '<script>' \
                   'alert("学制不合法，请重新输入");' \
                   'window.history.back(-1);' \
                   '</script>'
        Stu_age = str(Stu_age)
        temp4 = re.search("\\D+", Stu_age)
        if temp4:
            return '<script>' \
                   'alert("年龄不合法，请重新输入");' \
                   'window.history.back(-1);' \
                   '</script>'
        if Stu_gen != u'男' and Stu_gen != u'女' and Stu_gen != '':
            return '<script>' \
                   'alert("性别输入不合法，请重新输入");' \
                   'window.history.back(-1);' \
                   '</script>'
        Stu_grade = int(Stu_grade)
        Stu_year = int(Stu_year)
        Stu_age = int(Stu_age)
        if Stu_grade <= 1970:
            return '<script>' \
                   'alert("输入的年级不合法，请重新输入");' \
                   'window.history.back(-1);' \
                   '</script>'
        if Stu_year <= 0 or Stu_year >= 10:
            return '<script>' \
                   'alert("输入的学制不合法，请重新输入");' \
                   'window.history.back(-1);' \
                   '</script>'
        if Stu_age <= 12 or Stu_age >= 100:
            return '<script>' \
                   'alert("输入的年龄有点儿离谱，如情况属实，请联系管理员");' \
                   'window.history.back(-1);' \
                   '</script>'
        if Stu_rec == '':
            Stu_rec = stu.StuRec
        if Stu_flag == '':
            Stu_flag = stu.StuFlag
        stu.StuName = Stu_name
        stu.StuGen = Stu_gen
        stu.StuGrade = Stu_grade
        stu.StuPro = Stu_pro
        stu.StuYear = Stu_year
        stu.StuAddr = Stu_addr
        stu.StuAge = Stu_age
        stu.StuPol = Stu_pol
        stu.StuNation = Stu_nation
        stu.StuRec = Stu_rec
        stu.StuFlag = Stu_flag
        db.session.commit()
        return redirect(url_for('Tchart'))


#老师删除学生
@app.route('/teacher/chart/TdeleteS/',methods=['GET','POST'])
def T_delete_S():
    if request.method == 'GET':
        return render_template('TdeleteS.html')
    else:
        Stu_no_del = request.form.get('Stu_no_del')
        print(Stu_no_del)
        stu = Stu.query.filter(Stu.StuNo == Stu_no_del).first()
        if stu:
            db.session.delete(stu)
            db.session.commit()
            return '<script>' \
                       'alert("删除成功");' \
                       'window.history.go(-2);' \
                       '</script>'
        else:
            return '<script>' \
                       'alert("删除失败，没有这个学生，请重新输入");' \
                       'window.history.back(-1);' \
                       '</script>'

#老师修改密码
@app.route('/teacher/pas/',methods=['GET','POST'])
def Tpass():
    if request.method == 'GET':
        return render_template('Tpass.html')
    else:
        Tea_No = session.get('user_No')
        tea = Tea.query.filter(Tea.TeaNo == Tea_No).first()
        Tea_pass = Md5(request.form.get('beforepassword'))
        if tea.TeaPass == Tea_pass:
            Tea_pass1 = request.form.get('last1password')
            Tea_pass2 = request.form.get('last2password')
            if Tea_pass1 == Tea_pass2:
                tea.TeaPass = Md5(Tea_pass1)
                db.session.commit()
                return redirect(url_for('login'))
            else:
                return '<script>' \
                    'alert("俩次密码输入不同，修改失败。");' \
                    'window.history.back(-1);' \
                    '</script>'
        else:
            return '<script>' \
                    'alert("原密码错误，修改失败。");' \
                    'window.history.back(-1);' \
                    '</script>'

#学生修改密码
@app.route('/student/pas/',methods=['GET','POST'])
def Spass():
    if request.method == 'GET':
        return render_template('Spass.html')
    else:
        Stu_No = session.get('user_No')
        stu = Stu.query.filter(Stu.StuNo == Stu_No).first()
        Stu_pass = Md5(request.form.get('beforepassword'))
        if stu.StuPass == Stu_pass:
            Stu_pass1 = request.form.get('last1password')
            Stu_pass2 = request.form.get('last2password')
            if Stu_pass1 == Stu_pass2:
                stu.StuPass = Md5(Stu_pass1)
                db.session.commit()
                return redirect(url_for('login'))
            else:
                return '<script>' \
                    'alert("俩次密码输入不同，修改失败。");' \
                    'window.history.back(-1);' \
                    '</script>'
        else:
            return '<script>' \
                    'alert("原密码错误，修改失败。");' \
                    'window.history.back(-1);' \
                    '</script>'

#管理员修改密码
@app.route('/manager/passpass',methods=['GET','POST'])
def Mpass():
    if request.method == 'GET':
        return render_template('Mpass.html')
    else:
        username = session.get('user_No')
        user = Manage.query.filter(Manage.username == username).first()
        user_pass = Md5(request.form.get('beforepassword'))
        if user.password == user_pass:
            user_pass1 = request.form.get('last1password')
            user_pass2 = request.form.get('last2password')
            if user_pass1 == user_pass2:
                user.password = Md5(user_pass1)
                db.session.commit()
                return redirect(url_for('login'))
            else:
                return '<script>' \
                    'alert("俩次密码输入不同，修改失败。");' \
                    'window.history.back(-1);' \
                    '</script>'
        else:
            return '<script>' \
                    'alert("原密码错误，修改失败。");' \
                    'window.history.back(-1);' \
                    '</script>'

#管理员首页
@app.route('/manager/indexindex/')
def Mindex():
    addrs = []
    nations = []
    pols = []
    ages = []
    dic1 = {}
    dic2 = {}
    dic3 = {}
    dic4 = {}
    stus = Stu.query.filter().all()
    for stu in stus:
        addrs.append(stu.StuAddr[0:2])
        nations.append(stu.StuNation)
        pols.append(stu.StuPol)
        ages.append(stu.StuAge)
    #统计学生地区
    for addr in addrs:
        d = dic1.get(addr)
        if d == None:
            dic1[addr] = 1
        else:
            dic1[addr] = dic1[addr] + 1
    for dic in dic1:
        dic1[dic] = dic1[dic] / len(stus) * 100
    #统计学生民族
    for nation in nations:
        d = dic2.get(nation)
        if d == None:
            dic2[nation] = 1
        else:
            dic2[nation] = dic2[nation] + 1
    for dic in dic2:
        dic2[dic] = dic2[dic]/len(stus) * 100
    #统计学生的政治面貌
    for pol in pols:
        d = dic3.get(pol)
        if d == None:
            dic3[pol] = 1
        else:
            dic3[pol] = dic3[pol] + 1
    for dic in dic3:
        dic3[dic] = dic3[dic]/len(stus) * 100
    #统计学生的年龄
    for age in ages:
        d = dic4.get(age)
        if d == None:
            dic4[age] = 1
        else:
            dic4[age] = dic4[age] + 1
    for dic in dic4:
        dic4[dic] = dic4[dic]/len(stus) * 100
    lss = lesson_stu.query.filter().all()
    dic5 = {}
    scores = []
    for ls in lss:
        scores.append(ls.score)
    for score in scores:
        if score == None:
            score = '无成绩'
        elif score<60 and score >= 0:
            score = '不及格'
        elif score>=60 and score<70:
            score = '及格'
        elif score<80 and score>=70:
            score = '中等'
        elif score<90 and score>=80:
            score = '良好'
        elif score<=100 and score>=90:
            score = '优秀'
        else:
            score = '无成绩'
        d = dic5.get(score)
        if d == None:
            dic5[score] = 1
        else:
            dic5[score] = dic5[score] + 1
    for dic in dic5:
        dic5[dic] = dic5[dic]/len(lss) * 100
        dic5[dic] = round(dic5[dic],1)
    return render_template('Mindex.html',dic1=dic1,dic2=dic2,dic3=dic3,dic4=dic4,dic5=dic5)

#管理员课程管理
@app.route('/manager/ui_elementsui_elements/',methods=['GET','POST'])
def Mui_elements():
    if request.method == 'GET':
        lessons = Lesson.query.filter().all()
        return render_template('Mui_elements.html',lessons=lessons)
    else:
        lesson_no = request.form.get('lesson_no')
        if lesson_no:
            lesson_name = request.form.get('lesson_name')
            lesson_credits = request.form.get('lesson_credits')
            lesson_teacher = request.form.get('lesson_teacher')
            temp1 = re.search("\\D+",lesson_teacher)
            if temp1:
                return '<script>' \
                       'alert("输入的授课教师工号不合法，请重新输入");' \
                       'window.history.back(-1);' \
                       '</script>'
            if lesson_no == '' or lesson_name == '' or lesson_credits == '':
                return '<script>' \
                       'alert("课程号、课程名称和学分都需要添加，请重新输入");' \
                       'window.history.back(-1);' \
                       '</script>'
            fff = re.search("\\D+", lesson_credits)
            if fff:
                return '<script>' \
                       'alert("您输入了非法的学分，请重新输入");' \
                       'window.history.back(-1);' \
                       '</script>'
            else:
                lesson_credits = int(lesson_credits)
            flag = re.search("\\D+", lesson_no)
            if flag:
                return '<script>' \
                       'alert("您输入了非法的课程号，请重新输入");' \
                       'window.history.back(-1);' \
                       '</script>'
            else:
                if len(lesson_no) == 5:
                    lesson = Lesson.query.filter(Lesson.LessonNo == lesson_no).first()
                    if lesson:
                        return '<script>' \
                               'alert("此课程号以存在，添加失败，请重新输入");' \
                               'window.history.back(-1);' \
                               '</script>'
                    if lesson_credits <= 10 and lesson_credits > 0:
                        lesson = Lesson(LessonNo=lesson_no, LessonName=lesson_name, LessonCredits=lesson_credits)
                        lesson.Tea = Tea.query.filter(Tea.TeaNo == lesson_teacher).first()
                        db.session.add(lesson)
                        db.session.commit()
                        return redirect(url_for('Mui_elements'))
                    else:
                        return '<script>' \
                               'alert("您输入了非法的学分，请重新输入");' \
                               'window.history.back(-1);' \
                               '</script>'
                else:
                    return '<script>' \
                           'alert("您输入了非法的课程号，请重新输入");' \
                           'window.history.back(-1);' \
                           '</script>'
        lesson_no_last = request.form.get('lesson_no_last')
        if lesson_no_last:
            lesson_name_last = request.form.get('lesson_name_last')
            lesson_credits_last = request.form.get('lesson_credits_last')
            lesson_teacher_last = request.form.get('lesson_teacher_last')
            temp1 = re.search("\\D+", lesson_teacher_last)
            if temp1:
                return '<script>' \
                       'alert("输入的授课教师工号不合法，请重新输入");' \
                       'window.history.back(-1);' \
                       '</script>'
            if lesson_no_last == '' or lesson_name_last == '' or lesson_credits_last == '':
                return '<script>' \
                       'alert("课程名称和学分都需要重新修改，请重新输入");' \
                       'window.history.back(-1);' \
                       '</script>'
            fff = re.search('\\D+', lesson_credits_last)
            if fff:
                return '<script>' \
                       'alert("您输入了非法的学分，请重新输入");' \
                       'window.history.back(-1);' \
                       '</script>'
            else:
                lesson_credits_last = int(lesson_credits_last)
            flag = re.search('\\D+', lesson_no_last)
            if flag:
                return '<script>' \
                       'alert("不存在此课程号，请重新输入");' \
                       'window.history.back(-1);' \
                       '</script>'
            else:
                if len(lesson_no_last) == 5:
                    if lesson_credits_last <= 10 and lesson_credits_last > 0:
                        lesson = Lesson.query.filter(Lesson.LessonNo == lesson_no_last).first()
                        if lesson:
                            lesson.LessonName = lesson_name_last
                            lesson.LessonCredits = lesson_credits_last
                            lesson.Tea = Tea.query.filter(Tea.TeaNo == lesson_teacher_last).first()
                            db.session.commit()
                            return redirect(url_for('Mui_elements'))
                        else:
                            return '<script>' \
                                   'alert("不存在此课程号，请重新输入或到添加模块添加");' \
                                   'window.history.back(-1);' \
                                   '</script>'
                    else:
                        return '<script>' \
                               'alert("您输入了非法的学分，请重新输入");' \
                               'window.history.back(-1);' \
                               '</script>'
                else:
                    return '<script>' \
                           'alert("不存在此课程号，请重新输入");' \
                           'window.history.back(-1);' \
                           '</script>'
        lesson_no_de = request.form.get('lesson_no_de')
        if lesson_no_de:
            if lesson_no_de == '':
                return '<script>' \
                       'alert("需要添加课程号，请重新输入");' \
                       'window.history.back(-1);' \
                       '</script>'
            if len(lesson_no_de) == 5:
                lesson = Lesson.query.filter(Lesson.LessonNo == lesson_no_de).first()
                if lesson:
                    db.session.delete(lesson)
                    db.session.commit()
                    return redirect(url_for('Mui_elements'))
                else:
                    return '<script>' \
                           'alert("不存在的课程，请重新输入");' \
                           'window.history.back(-1);' \
                           '</script>'
            else:
                return '<script>' \
                       'alert("不存在的课程，请重新输入");' \
                       'window.history.back(-1);' \
                       '</script>'
        else:
            return '<script>' \
                   'alert("课程号、课程名称和学分都需要添加，请重新输入");' \
                   'window.history.back(-1);' \
                   '</script>'

#管理员管理学生
@app.route('/manager/chartchart/')
def Mchart():
    return render_template('Mchart.html')

#管理员添加学生
@app.route('/manager/chartchart/MinsertSMinsertS/',methods=['GET','POST'])
def M_insert_S():
    if request.method == 'GET':
        return render_template('MinsertS.html')
    else:
        Stu_no = request.form.get('Stu_no')
        Stu_name = request.form.get('Stu_name')
        Stu_pass = request.form.get('Stu_pass')
        Stu_gen = request.form.get('Stu_gen')
        Stu_grade = request.form.get('Stu_grade')
        Stu_pro = request.form.get('Stu_pro')
        Stu_year = request.form.get('Stu_year')
        Stu_addr = request.form.get('Stu_addr')
        Stu_age = request.form.get('Stu_age')
        Stu_nation = request.form.get('Stu_nation')
        Stu_pol = request.form.get('Stu_pol')
        Stu_rec = request.form.get('Stu_rec')
        Stu_flag = request.form.get('Stu_flag')
        temp1 = re.search("\\D+",Stu_no)
        if Stu_no == '' or Stu_name == '' or Stu_gen == '' or Stu_grade == '' or Stu_pro == '' or Stu_year == '' or Stu_addr == '' or Stu_age == '' or Stu_nation == '' or Stu_pol == '' or Stu_pass == '':
            return '<script>' \
                       'alert("学号、姓名、性别、年级、专业、学制、现住址、年龄、民族和政治面貌这些都需要输入，请重新输入");' \
                       'window.history.back(-1);' \
                       '</script>'
        if temp1:
            return '<script>' \
                       'alert("学号不合法，请重新输入");' \
                       'window.history.back(-1);' \
                       '</script>'
        temp2 = re.search("\\D+",Stu_grade)
        if temp2:
            return '<script>' \
                       'alert("年级不合法，请重新输入");' \
                       'window.history.back(-1);' \
                       '</script>'
        temp3 = re.search("\\D+",Stu_year)
        if temp3:
            return '<script>' \
                       'alert("学制不合法，请重新输入");' \
                       'window.history.back(-1);' \
                       '</script>'
        temp4 = re.search("\\D+",Stu_age)
        if temp4:
            return '<script>' \
                       'alert("年龄不合法，请重新输入");' \
                       'window.history.back(-1);' \
                       '</script>'
        if Stu_gen != u'男' and Stu_gen != u'女':
            return '<script>' \
                       'alert("性别输入不合法，请重新输入");' \
                       'window.history.back(-1);' \
                       '</script>'
        Stu_grade = int(Stu_grade)
        Stu_year = int(Stu_year)
        Stu_age = int(Stu_age)
        if Stu_grade <= 1970:
            return '<script>' \
                       'alert("输入的年级不合法，请重新输入");' \
                       'window.history.back(-1);' \
                       '</script>'
        if Stu_year<=0 or Stu_year >= 10:
            return '<script>' \
                       'alert("输入的学制不合法，请重新输入");' \
                       'window.history.back(-1);' \
                       '</script>'
        if Stu_age <=12 or Stu_age >=100:
            return '<script>' \
                       'alert("输入的年龄有点儿离谱，如情况属实，请联系管理员");' \
                       'window.history.back(-1);' \
                       '</script>'
        if len(Stu_no) != 10:
            return '<script>' \
                       'alert("学号不合法，请重新输入");' \
                       'window.history.back(-1);' \
                       '</script>'
        stu = Stu.query.filter(Stu.StuNo == Stu_no).first()
        if stu:
            return '<script>' \
                       'alert("该学生已经存在，请重新输入学号添加");' \
                       'window.history.back(-1);' \
                       '</script>'
        stu = Stu(StuNo=Stu_no,StuName=Stu_name,
                  StuPass=Md5(Stu_pass),StuGen=Stu_gen,
                  StuGrade=Stu_grade,StuPro=Stu_pro,
                  StuYear=Stu_year,StuAddr=Stu_addr,
                  StuAge=Stu_age,StuPol=Stu_pol,
                  StuNation=Stu_nation,StuRec=Stu_rec,
                  StuFlag=Stu_flag
                  )
        db.session.add(stu)
        db.session.commit()
        return redirect(url_for('Mchart'))

#管理员修改学生
@app.route('/manager/chartchart/MupdateSMupdateS/',methods=['GET','POST'])
def M_update_S():
    if request.method == 'GET':
        #### 利用全局变量，对用户输入的学号进行查询，并返回到网页上
        global Stu_no_sel
        Stu_no_sel = request.args.get('Stu_no_sel')
        sstu = Stu.query.filter(Stu.StuNo == Stu_no_sel).first()
        if sstu:
            return render_template('MupdateS.html', sstu=sstu)
        return render_template('MupdateS.html',sstu=None)

    else:
        Stu_name = request.form.get('Stu_name')
        Stu_gen = request.form.get('Stu_gen')
        Stu_grade = request.form.get('Stu_grade')
        Stu_pro = request.form.get('Stu_pro')
        Stu_year = request.form.get('Stu_year')
        Stu_addr = request.form.get('Stu_addr')
        Stu_age = request.form.get('Stu_age')
        Stu_nation = request.form.get('Stu_nation')
        Stu_pol = request.form.get('Stu_pol')
        Stu_rec = request.form.get('Stu_rec')
        Stu_flag = request.form.get('Stu_flag')
        ### 利用正则表达式和各个条件对输入进行限制
        stu = Stu.query.filter(Stu.StuNo == Stu_no_sel).first()
        ### 如果用户输入为空的话，就看作不改动
        if Stu_name == '':
            Stu_name = stu.StuName
        if Stu_gen == '':
            Stu_gen = stu.StuGen
        if Stu_grade == '':
            Stu_grade = stu.StuGrade
        if Stu_pro == '':
            Stu_pro = stu.StuPro
        if Stu_year == '':
            Stu_year = stu.StuYear
        if Stu_addr == '':
            Stu_addr = stu.StuAddr
        if Stu_age == '':
            Stu_age = stu.StuAge
        if Stu_pol == '':
            Stu_pol = stu.StuPol
        if Stu_nation == '':
            Stu_nation = stu.StuNation
        if Stu_rec == '':
            Stu_rec = stu.StuRec
        if Stu_flag == '':
            Stu_flag = stu.StuFlag
        Stu_grade = str(Stu_grade)
        temp2 = re.search("\\D+", Stu_grade)
        if temp2:
            return '<script>' \
                   'alert("年级不合法，请重新输入");' \
                   'window.history.back(-1);' \
                   '</script>'
        Stu_year = str(Stu_year)
        temp3 = re.search("\\D+", Stu_year)
        if temp3:
            return '<script>' \
                   'alert("学制不合法，请重新输入");' \
                   'window.history.back(-1);' \
                   '</script>'
        Stu_age = str(Stu_age)
        temp4 = re.search("\\D+", Stu_age)
        if temp4:
            return '<script>' \
                   'alert("年龄不合法，请重新输入");' \
                   'window.history.back(-1);' \
                   '</script>'
        if Stu_gen != u'男' and Stu_gen != u'女' and Stu_gen != '':
            return '<script>' \
                   'alert("性别输入不合法，请重新输入");' \
                   'window.history.back(-1);' \
                   '</script>'
        Stu_grade = int(Stu_grade)
        Stu_year = int(Stu_year)
        Stu_age = int(Stu_age)
        if Stu_grade <= 1970:
            return '<script>' \
                   'alert("输入的年级不合法，请重新输入");' \
                   'window.history.back(-1);' \
                   '</script>'
        if Stu_year <= 0 or Stu_year >= 10:
            return '<script>' \
                   'alert("输入的学制不合法，请重新输入");' \
                   'window.history.back(-1);' \
                   '</script>'
        if Stu_age <= 12 or Stu_age >= 100:
            return '<script>' \
                   'alert("输入的年龄有点儿离谱，如情况属实，请联系管理员");' \
                   'window.history.back(-1);' \
                   '</script>'
        stu.StuName = Stu_name
        stu.StuGen = Stu_gen
        stu.StuGrade = Stu_grade
        stu.StuPro = Stu_pro
        stu.StuYear = Stu_year
        stu.StuAddr = Stu_addr
        stu.StuAge = Stu_age
        stu.StuPol = Stu_pol
        stu.StuNation = Stu_nation
        stu.StuRec = Stu_rec
        stu.StuFlag = Stu_flag
        db.session.commit()
        return redirect(url_for('Mchart'))

#管理员删除学生
@app.route('/manager/chartchart/MdeleteSMdeleteS/',methods=['GET','POST'])
def M_delete_S():
    if request.method == 'GET':
        return render_template('MdeleteS.html')
    else:
        Stu_no_del = request.form.get('Stu_no_del')
        stu = Stu.query.filter(Stu.StuNo == Stu_no_del).first()
        if stu:
            db.session.delete(stu)
            db.session.commit()
            return '<script>' \
                       'alert("删除成功");' \
                       'window.history.go(-2);' \
                       '</script>'
        else:
            return '<script>' \
                       'alert("删除失败，没有这个学生，请重新输入");' \
                       'window.history.back(-1);' \
                       '</script>'


#管理员管理教师
@app.route('/manager/managemanage/')
def Mmanage():
    return render_template('Mmanage.html')

#管理员添加老师
@app.route('/manager/managemanage/MinsertTMinsertT/',methods=['GET','POST'])
def M_insert_T():
    if request.method == 'GET':
        return render_template('MinsertT.html')
    else:
        Tea_no = request.form.get('Tea_no')
        Tea_name = request.form.get('Tea_name')
        Tea_pass = request.form.get('Tea_pass')
        if Tea_no == '' or Tea_name == '' or Tea_pass == '':
            return '<script>' \
                   'alert("工号、姓名和密码都不可为空！！！");' \
                   'window.history.back(-1);' \
                   '</script>'
        temp1 = re.search("\\D+",Tea_no)
        if temp1:
            return '<script>' \
                   'alert("输入了非法的工号");' \
                   'window.history.back(-1);' \
                   '</script>'
        if len(Tea_no)==8:
            tea = Tea(TeaNo=Tea_no,TeaName=Tea_name,TeaPass=Md5(Tea_pass))
            db.session.add(tea)
            db.session.commit()
        else:
            return '<script>' \
                   'alert("输入了非法的工号");' \
                   'window.history.back(-1);' \
                   '</script>'

        return redirect(url_for('Mmanage'))

#管理员修改老师信息
@app.route('/manager/managemanage/MupdateTMupdateT/',methods=['GET','POST'])
def M_update_T():
    if request.method == 'GET':
        global Tea_no_sel
        Tea_no_sel = request.args.get('Tea_no')
        ttea = Tea.query.filter(Tea.TeaNo == Tea_no_sel).first()
        if ttea:
            return render_template('MupdateT.html', ttea=ttea)
        return render_template('MupdateT.html',ttea=None)
    else:
        Tea_name = request.form.get('Tea_name')
        tea = Tea.query.filter(Tea.TeaNo == Tea_no_sel).first()
        if Tea_name == '':
            Tea_name = tea.TeaName
        tea.TeaName = Tea_name
        db.session.commit()
        return redirect(url_for('Mmanage'))

#管理员删除老师信息
@app.route('/manager/managemanage/MdeleteTMdeleteT/',methods=['GET','POST'])
def M_delete_T():
    if request.method == 'GET':
        return render_template('MdeleteT.html')
    else:
        Tea_no = request.form.get('Tea_no_del')
        print(Tea_no)
        temp1 = re.search("\\D+",Tea_no)
        if temp1:
            return '<script>' \
                   'alert("输入了非法的工号");' \
                   'window.history.back(-1);' \
                   '</script>'
        tea = Tea.query.filter(Tea.TeaNo == Tea_no).first()
        if tea:
            db.session.delete(tea)
            db.session.commit()
            return '<script>' \
               'alert("删除成功");' \
               'window.history.go(-2);' \
               '</script>'
        else:
            return '<script>' \
               'alert("删除失败，没有这个教师，请重新输入");' \
               'window.history.back(-1);' \
               '</script>'

@app.route('/logout/')
def logout():
    session.clear()
    return redirect(url_for('login'))




@app.context_processor
def context_processor():
    user_No = session.get('user_No')
    if user_No:
        if len(user_No)==8:
            tea = Tea.query.filter(Tea.TeaNo == user_No).first()
            if tea:
                return {'tea':tea}
        if len(user_No)==10:
            stu = Stu.query.filter(Stu.StuNo == user_No).first()
            if stu:
                return {'stu': stu}
        if len(user_No)==5:
            manage = Manage.query.filter(Manage.username == user_No).first()
            if manage:
                return {'manage':manage}
    return {'Stu':None}

from flask_script import Manager,Shell

manager = Manager(app)
def make_shell_context():
    return dict(app=app,db=db,Stu=Stu,Lesson=Lesson,lesson_stu=lesson_stu)

manager.add_command("shell",Shell(make_context=make_shell_context))

def Md5(pas):
    hh = hashlib.md5()
    hh.update(pas.encode(encoding = 'utf-8'))
    return hh.hexdigest()


if __name__ == '__main__':
    manager.run()
    #app.run(host='0.0.0.0',port=80)
