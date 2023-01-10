from flask import Flask, render_template, flash, request, redirect, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, SelectField
from wtforms.validators import DataRequired
from flask import appcontext_pushed, appcontext_popped, Flask
import sqlalchemy
from sqlalchemy import Table, create_engine, engine
import mysql.connector
import pymysql
from sqlalchemy.orm import sessionmaker, relationship
from datetime import date, datetime, timedelta
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from werkzeug.security import check_password_hash, generate_password_hash
import os
import re
from typing import Dict
import pandas as pd
from google.cloud.sql.connector import Connector, IPTypes

app = Flask(__name__)

#Local SQL
mysql_user = os.environ['MYSQL_USER']
mysql_password = os.environ['MYSQL_PASSWORD']
mysql_host = os.environ['MYSQL_HOST']
mysql_database = os.environ['MYSQL_DATABASE']
engine = create_engine(f'mysql://{mysql_user}:{mysql_password}@{mysql_host}/{mysql_database}', pool_pre_ping=True)
app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql://{mysql_user}:{mysql_password}@{mysql_host}/{mysql_database}'
app.config['SECRET_KEY'] = os.urandom(12)
app.config['ENV'] = 'development'


#Google cloud SQL

# Python Connector database connection function
def getconn():
    with Connector() as connector:
        conn = connector.connect(
            os.environ['GOOGLESQL_CONNECTION'], # Cloud SQL Instance Connection Name
            "pymysql",
            user=os.environ['GOOGLESQL_USER'],
            password=os.environ['GOOGLESQL_USER_PASSWORD'],
            db=os.environ['GOOGLESQL_DATABASE']
        )
        return conn

#pool = sqlalchemy.create_engine(
    #"mysql+pymysql://",
    #creator=getconn,
    #pool_pre_ping=True
#)


# configure Flask-SQLAlchemy to use Python Connector
#app.config['SQLALCHEMY_DATABASE_URI'] = "mysql+pymysql://"
#app.config["SQLALCHEMY_POOL_RECYCLE"] = 280
#app.config['SQLALCHEMY_POOL_TIMEOUT'] = 10
#app.config['SECRET_KEY'] = os.urandom(12)

#app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql + mysqldb://root:{googlesql_password}@{googlesql_ip}/{googlesql_database}?unix_socket=/cloudsql/{googlesql_project}:{googlesql_instance}'
#uri = f"mysql+pymysql://{os.environ['GOOGLESQL_USER']}:{os.environ['GOOGLESQL_USER_PASSWORD']}@/{os.environ['GOOGLESQL_DATABASE']}?unix_socket={os.environ['GOOGLESQL_UNIX_SOCKET']}"

db = SQLAlchemy(app)


class dhr_asm_834_1111(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customerPO = db.Column(db.VARCHAR(10))
    internalMFR = db.Column(db.VARCHAR(50))
    productREF = db.Column(db.VARCHAR(20))
    totalQTY = db.Column(db.Integer)
    manufacturingVER = db.Column(db.VARCHAR(50))
    manufacturedBY = db.Column(db.VARCHAR(3))
    approvedBY = db.Column(db.VARCHAR(3))
    comments = db.Column(db.VARCHAR(200))
    manufactureDATE = db.Column(db.VARCHAR(10))
    LOTno = db.Column(db.VARCHAR(20))
    SERIALno = db.Column(db.VARCHAR(10))
    appCODE = db.Column(db.VARCHAR(8))
    expiryDATE = db.Column(db.VARCHAR(10))
    GTIN = db.Column(db.VARCHAR(14))
    UDI = db.Column(db.VARCHAR(70))


class dhr_asm_834_1188(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customerPO = db.Column(db.VARCHAR(10))
    internalMFR = db.Column(db.VARCHAR(50))
    productREF = db.Column(db.VARCHAR(20))
    totalQTY = db.Column(db.Integer)
    manufacturingVER = db.Column(db.VARCHAR(50))
    manufacturedBY = db.Column(db.VARCHAR(3))
    approvedBY = db.Column(db.VARCHAR(3))
    comments = db.Column(db.VARCHAR(200))
    manufactureDATE = db.Column(db.VARCHAR(20))
    LOTno = db.Column(db.VARCHAR(20))
    expiryDATE = db.Column(db.VARCHAR(20))
    GTIN = db.Column(db.VARCHAR(14))
    UDI = db.Column(db.VARCHAR(70))

class dhr_asm_834_1190(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customerPO = db.Column(db.VARCHAR(10))
    internalMFR = db.Column(db.VARCHAR(50))
    productREF = db.Column(db.VARCHAR(20))
    totalQTY = db.Column(db.Integer)
    manufacturingVER = db.Column(db.VARCHAR(50))
    manufacturedBY = db.Column(db.VARCHAR(3))
    approvedBY = db.Column(db.VARCHAR(3))
    comments = db.Column(db.VARCHAR(200))
    manufactureDATE = db.Column(db.VARCHAR(20))
    LOTno = db.Column(db.VARCHAR(20))
    expiryDATE = db.Column(db.VARCHAR(20))
    GTIN = db.Column(db.VARCHAR(14))
    UDI = db.Column(db.VARCHAR(70))


class input_1111(FlaskForm):
    customerPO = StringField('Customer purchase order')
    internalMFR = StringField('Internal MFR order', validators=[DataRequired()])
    productREF = StringField('Product REF including revision', validators=[DataRequired()])
    totalQTY = StringField('Total QTY ordered', validators=[DataRequired()])
    manufacturingVER = StringField('Manufacturing Verification ref.', validators=[DataRequired()])
    manufacturedBY = StringField('Manufactured by', validators=[DataRequired()])
    approvedBY = StringField('Approved by', validators=[DataRequired()])
    comments = StringField('Comments')
    manufactureDATE = StringField('Manufacture Date (YYMDD)', validators=[DataRequired()])
    LOTno = StringField('LOT no', validators=[DataRequired()])
    submit = SubmitField('Add to database')


@app.route('/')
def home():
    last1111 = str(db.session.query(dhr_asm_834_1111.manufactureDATE).order_by(dhr_asm_834_1111.id.desc()).first())
    last1111str = f'{last1111[2]}{last1111[3]}-{last1111[4]}{last1111[5]}-{last1111[6]}{last1111[7]}'
    last1188 = str(db.session.query(dhr_asm_834_1188.manufactureDATE).order_by(dhr_asm_834_1188.id.desc()).first())
    last1188str = f'{last1188[2]}{last1188[3]}-{last1188[4]}{last1188[5]}-{last1188[6]}{last1188[7]}'
    last1190 = str(db.session.query(dhr_asm_834_1190.manufactureDATE).order_by(dhr_asm_834_1190.id.desc()).first())
    last1190str = f'{last1190[2]}{last1190[3]}-{last1190[4]}{last1190[5]}-{last1190[6]}{last1190[7]}'
    return render_template('home.html', last1190=last1190str, last1111=last1111str, last1188=last1188str)

@app.route('/1111', methods=['GET', 'POST'])
def form1111():
    form = input_1111()
    items = db.session.query(dhr_asm_834_1111).order_by(dhr_asm_834_1111.id.desc()).all()
    appCodes = pd.read_csv('sheath_app_codes.csv')
    appCodeList = [i for i in appCodes['code']]
    lastID = db.session.query(dhr_asm_834_1111.id) \
        .order_by(dhr_asm_834_1111.id.desc()).limit(1).first()
    nextID = int(lastID.id)+1
    if form.validate_on_submit():
        # Create a new protect_pro_sheaths object and set its attributes
        # to the form data
        item = dhr_asm_834_1111(
            customerPO=form.customerPO.data,
            internalMFR=form.internalMFR.data,
            productREF=form.productREF.data,
            totalQTY=form.totalQTY.data,
            manufacturingVER=form.manufacturingVER.data,
            manufacturedBY=form.manufacturedBY.data,
            approvedBY=form.approvedBY.data,
            comments=form.comments.data,
            manufactureDATE=form.manufactureDATE.data,
            LOTno=form.LOTno.data
        )
        batch = int(item.totalQTY)
        lot = item.LOTno
        manDate = item.manufactureDATE
        mdY = int(manDate[1])
        threeYears = mdY+3
        expDate = f'{manDate[0]}{threeYears}{manDate[2]}{manDate[3]}{manDate[4]}{manDate[5]}'
        expDateUDI = expDate[0]+expDate[1]+expDate[2]+expDate[3]+expDate[4]+expDate[5]
        gtin = '05060710360042'

        for i in range(0,batch):
            dbID = nextID+i
            serial = dbID + 65
            appcode = appCodeList[dbID]
            udi = f'(01){gtin}(10){lot}(17){expDateUDI}(21)000{serial}(240){appcode}'
            item_info = {
                'id': dbID,
                'customerPO': request.form['customerPO'],
                'internalMFR': request.form['internalMFR'],
                'productREF': request.form['productREF'],
                'totalQTY': batch,
                'manufacturingVER': request.form['manufacturingVER'],
                'manufacturedBY': request.form['manufacturedBY'],
                'approvedBY': request.form['approvedBY'],
                'comments': request.form['comments'],
                'manufactureDATE': request.form['manufactureDATE'],
                'LOTno': request.form['LOTno'],
                'SERIALno': f'000{serial}',
                'appCODE': appcode,
                'expiryDATE': expDate,
                'GTIN': gtin,
                'UDI': udi,
            }
            item_obj = dhr_asm_834_1111(**item_info)
            # Add the item to the database
            db.session.add(item_obj)
        db.session.commit()

        # Redirect to the form page
        return redirect(url_for('form1111'))

    return render_template('1111.html', form=form, items=items, appCodeList=appCodeList, lastID=int(lastID.id))

@app.route('/delete_record1111/<record_id>', methods=['GET', 'DELETE'])
def delete_record1111(record_id):
    #connect to database
    connection = mysql.connector.connect(user='root', password='jqtnnhj2', host='localhost', database='DHR_834_1190')
    cursor = connection.cursor()
    sql_delete_query = """DELETE FROM dhr_asm_834_1111 WHERE id = %s"""
    cursor.execute(sql_delete_query, (record_id, ))
    connection.commit()
    connection.close()
    return redirect(url_for('form1111'))

@app.route('/1188', methods=['GET', 'POST'])
def form1188():
    form = input_1111()
    items = db.session.query(dhr_asm_834_1188).order_by(dhr_asm_834_1188.id.desc()).all()
    lastID = db.session.query(dhr_asm_834_1188.id) \
        .order_by(dhr_asm_834_1188.id.desc()).limit(1).first()
    nextID = int(lastID.id)+1
    if form.validate_on_submit():
        # Create a new protect_pro_sheaths object and set its attributes
        # to the form data
        item = dhr_asm_834_1188(
            customerPO=form.customerPO.data,
            internalMFR=form.internalMFR.data,
            productREF=form.productREF.data,
            totalQTY=form.totalQTY.data,
            manufacturingVER=form.manufacturingVER.data,
            manufacturedBY=form.manufacturedBY.data,
            approvedBY=form.approvedBY.data,
            comments=form.comments.data,
            manufactureDATE=form.manufactureDATE.data,
            LOTno=form.LOTno.data
        )
        batch = int(item.totalQTY)
        lot = item.LOTno
        manDate = item.manufactureDATE
        mdY = int(manDate[1])
        threeYears = mdY+3
        expDate = f'{manDate[0]}{threeYears}{manDate[2]}{manDate[3]}{manDate[4]}{manDate[5]}'
        expDateUDI = expDate[0] + expDate[1] + expDate[2] + expDate[3] + expDate[4] + expDate[5]
        gtin = '05060710360011'

        for i in range(0,batch):
            dbID = nextID + i
            udi = f'(01){gtin}(10){lot}(17){expDateUDI}'
            item_info = {
                'id': dbID,
                'customerPO': request.form['customerPO'],
                'internalMFR': request.form['internalMFR'],
                'productREF': request.form['productREF'],
                'totalQTY': batch,
                'manufacturingVER': request.form['manufacturingVER'],
                'manufacturedBY': request.form['manufacturedBY'],
                'approvedBY': request.form['approvedBY'],
                'comments': request.form['comments'],
                'manufactureDATE': request.form['manufactureDATE'],
                'LOTno': request.form['LOTno'],
                'expiryDATE': expDate,
                'GTIN': gtin,
                'UDI': udi,
            }
            item_obj = dhr_asm_834_1188(**item_info)
            # Add the item to the database
            db.session.add(item_obj)
        db.session.commit()

        # Redirect to the form page
        return redirect(url_for('form1188'))

    return render_template('1188.html', form=form, items=items, lastID=int(lastID.id))

@app.route('/delete_record1188/<record_id>', methods=['GET', 'DELETE'])
def delete_record1188(record_id):
    #connect to database
    connection = mysql.connector.connect(user='root', password='jqtnnhj2', host='localhost', database='DHR_834_1190')
    cursor = connection.cursor()
    sql_delete_query = """DELETE FROM dhr_asm_834_1188 WHERE id = %s"""
    cursor.execute(sql_delete_query, (record_id, ))
    connection.commit()
    connection.close()
    return redirect(url_for('form1188'))

@app.route('/1190', methods=['GET', 'POST'])
def form1190():
    form = input_1111()
    items = db.session.query(dhr_asm_834_1190).order_by(dhr_asm_834_1190.id.desc()).all()
    lastID = db.session.query(dhr_asm_834_1190.id) \
        .order_by(dhr_asm_834_1190.id.desc()).limit(1).first()
    nextID = int(lastID.id)+1
    if form.validate_on_submit():
        # Create a new protect_pro_sheaths object and set its attributes
        # to the form data
        item = dhr_asm_834_1190(
            customerPO=form.customerPO.data,
            internalMFR=form.internalMFR.data,
            productREF=form.productREF.data,
            totalQTY=form.totalQTY.data,
            manufacturingVER=form.manufacturingVER.data,
            manufacturedBY=form.manufacturedBY.data,
            approvedBY=form.approvedBY.data,
            comments=form.comments.data,
            manufactureDATE=form.manufactureDATE.data,
            LOTno=form.LOTno.data
        )
        batch = int(item.totalQTY)
        lot = item.LOTno
        manDate = item.manufactureDATE
        mdY = int(manDate[1])
        threeYears = mdY+3
        expDate = f'{manDate[0]}{threeYears}{manDate[2]}{manDate[3]}{manDate[4]}{manDate[5]}'
        expDateUDI = expDate[0] + expDate[1] + expDate[2] + expDate[3] + expDate[4] + expDate[5]
        gtin = '05060710360059'

        for i in range(0,batch):
            dbID = nextID+i
            udi = f'(01){gtin}(10){lot}(17){expDateUDI}'
            item_info = {
                'id': dbID,
                'customerPO': request.form['customerPO'],
                'internalMFR': request.form['internalMFR'],
                'productREF': request.form['productREF'],
                'totalQTY': batch,
                'manufacturingVER': request.form['manufacturingVER'],
                'manufacturedBY': request.form['manufacturedBY'],
                'approvedBY': request.form['approvedBY'],
                'comments': request.form['comments'],
                'manufactureDATE': request.form['manufactureDATE'],
                'LOTno': request.form['LOTno'],
                'expiryDATE': expDate,
                'GTIN': gtin,
                'UDI': udi,
            }
            item_obj = dhr_asm_834_1190(**item_info)
            # Add the item to the database
            db.session.add(item_obj)
        db.session.commit()

        # Redirect to the form page
        return redirect(url_for('form1190'))

    return render_template('1190.html', form=form, items=items, lastID=int(lastID.id))

@app.route('/delete_record1190/<record_id>', methods=['GET', 'DELETE'])
def delete_record1190(record_id):
    #connect to database
    connection = mysql.connector.connect(user='root', password='jqtnnhj2', host='localhost', database='DHR_834_1190')
    cursor = connection.cursor()
    sql_delete_query = """DELETE FROM dhr_asm_834_1190 WHERE id = %s"""
    cursor.execute(sql_delete_query, (record_id, ))
    connection.commit()
    connection.close()
    return redirect(url_for('form1190'))

if __name__ == '__main__':
    app.run(host="127.0.0.1", port="8080", debug=True)