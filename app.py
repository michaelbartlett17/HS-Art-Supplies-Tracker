from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_basicauth import BasicAuth
from email_send import *
from time import strftime
import random
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///supplies.db'
app.config['BASIC_AUTH_USERNAME'] = 'teacher'
app.config['BASIC_AUTH_PASSWORD'] = 'teacherpassword'
db = SQLAlchemy(app)
basic_auth = BasicAuth(app)


# Database Init
class Supplies(db.Model):
    __tablename__ = "available"
    id = db.Column('id', db.Integer, primary_key=True)
    supply = db.Column('supply', db.String)
    qty = db.Column('qty', db.Integer)


class SignedOut(db.Model):
    __tablename__ = "signed_out"
    id = db.Column('id', db.Integer, primary_key=True)
    name = db.Column('name', db.String)
    supply = db.Column('supply', db.String)
    qty = db.Column('qty', db.Integer)
    time = db.Column('time', db.String)
    status = db.Column('status', db.String)
    email = db.Column('email',db.String)
    pin = db.Column('pin',db.Integer)

@app.route("/", methods=['GET', 'POST', 'PUT'])
def home():
    available = Supplies.query.all()
    signed_out = SignedOut.query.all()
    return render_template('index.html', available=available, signed_out=signed_out)

@app.route("/signoutform", methods=['GET', 'POST', 'PUT'])
def signoutform():
    available = Supplies.query.all()
    signed_out = SignedOut.query.all()
    error = request.args.get('error')
    if error:
        return render_template('SignOutForm.html', available=available, signed_out=signed_out, error = True)
    return render_template('SignOutForm.html', available=available, signed_out=signed_out,error = False)

@app.route("/post", methods=['POST'])
def post():
    signedout_item = SignedOut(name=request.form['name'], supply = request.form['supply'], qty = request.form['qty'], time = strftime("%m/%d/%y - %H:%M"), status="Pending", email = request.form['email'], pin = random.randint(1000,9999))
    update_item = Supplies.query.filter(Supplies.supply == signedout_item.supply).first()
    if int(signedout_item.qty) > update_item.qty:
        return redirect(url_for('signoutform', error = True))
    else:
        update_item.qty -= int(signedout_item.qty)
        db.session.add(signedout_item)
        db.session.commit()
        return redirect(url_for('home'))

@app.route("/teacher", methods=['GET', 'POST', 'PUT'])
@basic_auth.required
def teacher():
    signed_out = SignedOut.query.all()
    available = Supplies.query.all()
    return render_template('teacher.html', signed_out=signed_out, available = available)

@app.route("/approve", methods=['GET', 'POST'])
def approve():
    approve_item = SignedOut.query.filter(SignedOut.id == request.form['approve']).first()
    approve_item.status = "Approved"
    email = Email(approve_item.email, approve_item.supply, approve_item.qty, approve_item.pin)
    email.email_send()
    db.session.commit()
    return redirect(url_for('teacher'))

@app.route("/signinform", methods=['GET', 'POST'])
def signinform():
    available = Supplies.query.all()
    signed_out = SignedOut.query.all()
    pin_error = request.args.get('pin_error')
    qty_error = request.args.get('qty_error')
    signin_msg = request.args.get('signin_msg')
    if pin_error:
        return render_template('SignInForm.html', available=available, signed_out=signed_out, pin_error = True)
    elif qty_error:
        return render_template('SignInForm.html', available=available, signed_out=signed_out, qty_error = True)
    if signin_msg:
        return render_template('SignInForm.html', available=available, signed_out=signed_out, signin_msg = True)
    else:
        return render_template('SignInForm.html', available=available, signed_out=signed_out, pin_error = False, qty_error = False, signin_msg = False)

@app.route("/signinpost", methods=['POST'])
def signinpost():
    qty = request.form['qty']
    pin = request.form['pin']
    signedout_item = SignedOut.query.filter(SignedOut.id == request.form['signedOutSupply']).first()
    update_item = Supplies.query.filter(Supplies.supply == signedout_item.supply).first()
    if int(signedout_item.pin) != int(pin):
        app.logger.info(f'The signed out item pin is: {signedout_item.pin} and the entered pin is: {pin}')
        return redirect(url_for('signinform', pin_error = True))
    else:
        update_item.qty += int(qty)
        if int(qty) < signedout_item.qty:
            signedout_item.qty -= int(qty)
        elif int(qty) == signedout_item.qty:
            db.session.delete(signedout_item)
        else:
            return redirect(url_for('signinform', qty_error = True))
        db.session.commit()
        return redirect(url_for('signinform', signin_msg = True))


if __name__ == '__main__':
    app.run(host='0.0.0.0',port=int(os.getenv('PORT', 8080)))
