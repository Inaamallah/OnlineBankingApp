from flask import Blueprint, render_template, redirect, url_for, flash, request
from app.forms import LoginForm, RegisterForm, TransferForm, RequestResetForm, ResetPasswordForm
from app.models import User, Transaction
from app.email import send_reset_email
from app import db, bcrypt
from flask_login import login_user, logout_user, login_required, current_user
import random
from app.utils import generate_account_number
acc_no = generate_account_number()
from flask import session


main = Blueprint('main', __name__)

# Login
@main.route('/', methods=['GET', 'POST'])
@main.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user)
            return redirect(url_for('main.dashboard'))
        flash('Invalid email or password', 'danger')
    return render_template('login.html', form=form)

# Register
@main.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        hashed_pw = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        acc_no = ''.join([str(random.randint(0, 9)) for _ in range(10)])
        user = User(full_name=form.full_name.data, cnic=form.cnic.data,
                    email=form.email.data, phone=form.phone.data,
                    password=hashed_pw, account_number=acc_no)
        db.session.add(user)
        db.session.commit()
        flash('Account created! You can now log in.', 'success')
        return redirect(url_for('main.login'))
    return render_template('register.html', form=form)

# Dashboard
@main.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', balance=current_user.balance)

# Transfer Money
@main.route('/transfer', methods=['GET', 'POST'])
@login_required
def transfer():
    form = TransferForm()
    if form.validate_on_submit():
        recipient = User.query.filter_by(account_number=form.recipient_account.data).first()
        if recipient and recipient != current_user:
            amount = form.amount.data
            if current_user.balance >= amount:
                current_user.balance -= amount
                recipient.balance += amount

                # Record transactions
                db.session.add_all([
                    Transaction(sender_account=current_user.account_number, receiver_account=recipient.account_number, amount=amount, type='debit'),
                    Transaction(sender_account=current_user.account_number, receiver_account=recipient.account_number, amount=amount, type='credit')
                ])
                db.session.commit()
                flash('Transfer successful!', 'success')
                return redirect(url_for('main.dashboard'))
            else:
                flash('Insufficient funds', 'danger')
        else:
            flash('Invalid recipient account', 'danger')
    return render_template('transfer.html', form=form, balance=current_user.balance)

# Transaction History
@main.route('/transactions')
@login_required
def transactions():
    tx = Transaction.query.filter(
        (Transaction.sender_account == current_user.account_number) |
        (Transaction.receiver_account == current_user.account_number)
    ).order_by(Transaction.timestamp.desc()).all()
    return render_template('transactions.html', transactions=tx)

# Request Password Reset
@main.route('/reset_password', methods=['GET', 'POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_reset_email(user)
        flash('Check your email for a password reset link.', 'info')
        return redirect(url_for('main.login'))
    return render_template('reset_request.html', form=form)

# Reset Password with Token
@main.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    user = User.verify_reset_token(token)
    if not user:
        flash('That is an invalid or expired token.', 'warning')
        return redirect(url_for('main.reset_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_pw = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_pw
        db.session.commit()
        flash('Your password has been updated! You can now log in.', 'success')
        return redirect(url_for('main.login'))
    return render_template('reset_token.html', form=form)

from flask import request
from flask_login import login_required

@main.route('/deposit', methods=['GET', 'POST'])
@login_required
def deposit():
    if request.method == 'POST':
        amount = request.form.get('amount', type=float)
        if amount and amount > 0:
            current_user.balance += amount
            db.session.commit()
            flash(f'Successfully added ${amount:.2f} to your account.', 'success')
            return redirect(url_for('main.dashboard'))
        else:
            flash('Invalid amount.', 'danger')
    return render_template('deposit.html', balance=current_user.balance)

@main.route('/profile')
@login_required
def profile():
    return render_template('profile.html', user=current_user)

@main.route('/accounts')
@login_required
def accounts():
    transfers = Transaction.query.filter_by(sender_account=current_user.account_number).all()
    recipients = []
    for tx in transfers:
        recipient = User.query.filter_by(account_number=tx.receiver_account).first()
        if recipient:
            recipients.append({
                'name': recipient.full_name,
                'account': recipient.account_number,
                'amount': tx.amount,
                'date': tx.timestamp.strftime("%Y-%m-%d")
            })
    return render_template('accounts.html', recipients=recipients)

@main.route('/logout')
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for('main.login'))

@main.route('/admin')
@login_required
def admin_panel():
    if not current_user.is_admin:
        flash('Unauthorized access!', 'danger')
        return redirect(url_for('main.dashboard'))

    users = User.query.all()
    transactions = Transaction.query.order_by(Transaction.timestamp.desc()).all()
    return render_template('admin_panel.html', users=users, transactions=transactions)
