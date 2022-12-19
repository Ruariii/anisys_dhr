from flask import Flask, render_template, flash, request, redirect, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, SelectField
from wtforms.validators import DataRequired
from flask import appcontext_pushed, appcontext_popped, Flask
from sqlalchemy import Table, create_engine
import mysql.connector
from sqlalchemy.orm import sessionmaker, relationship
from datetime import date, datetime, timedelta
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from werkzeug.security import check_password_hash, generate_password_hash
import os
import re
import pandas as pd

app = Flask(__name__)
app_ctx = app.app_context()
engine = create_engine('mysql://root:jqtnnhj2@localhost/DHR_834_1190', pool_pre_ping=True)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:jqtnnhj2@localhost/DHR_834_1190'
app.config['SECRET_KEY'] = os.urandom(12)
db = SQLAlchemy()
db.init_app(app)

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
app_ctx.push()
db.create_all()
app_ctx.pop()
class input_1111(FlaskForm):
    customerPO = StringField('Customer purchase order')
    internalMFR = StringField('Internal MFR order', validators=[DataRequired()])
    productREF = StringField('Product REF including revision', validators=[DataRequired()])
    totalQTY = StringField('Total QTY ordered', validators=[DataRequired()])
    manufacturingVER = StringField('Manufacturing Verification ref.', validators=[DataRequired()])
    manufacturedBY = StringField('Manufactured by', validators=[DataRequired()])
    approvedBY = StringField('Approved by', validators=[DataRequired()])
    comments = StringField('Comments')
    manufactureDATE = StringField('Manufacture Date', validators=[DataRequired()])
    LOTno = StringField('LOT no', validators=[DataRequired()])
    submit = SubmitField('Add to database')

@app.route('/', methods=['GET', 'POST'])
def form():
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
        expDate = f'{manDate[0]}{threeYears}-{manDate[3]}{manDate[4]}-{manDate[6]}{manDate[7]}'
        expDateUDI = expDate[0]+expDate[1]+expDate[3]+expDate[4]+expDate[6]+expDate[7]
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
        return redirect(url_for('form'))

    return render_template('1111.html', form=form, items=items, appCodeList=appCodeList, lastID=int(lastID.id))

@app.route('/delete_record/<record_id>', methods=['GET', 'DELETE'])
def delete_record(record_id):
    #connect to database
    connection = mysql.connector.connect(user='root', password='jqtnnhj2', host='localhost', database='DHR_834_1190')
    cursor = connection.cursor()
    sql_delete_query = """DELETE FROM dhr_asm_834_1111 WHERE id = %s"""
    cursor.execute(sql_delete_query, (record_id, ))
    connection.commit()
    connection.close()
    return redirect(url_for('form'))

if __name__ == '__main__':
    app.run(debug=True)