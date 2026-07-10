from datetime import datetime
import os
import secrets

from flask import Blueprint, current_app, flash, redirect, render_template, request, session, url_for
from flask_jwt_extended import create_access_token, set_access_cookies, unset_jwt_cookies
from werkzeug.security import check_password_hash, generate_password_hash

from app.models import Patient, Role, User, db

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")
        full_name = request.form.get("full_name", "").strip()
        phone = request.form.get("phone", "").strip()
        if not all([username, email, password, full_name]):
            flash("Please fill in all required fields.", "danger")
            return redirect(url_for("auth.register"))
        if User.query.filter((User.username == username) | (User.email == email)).first():
            flash("A user with that username or email already exists.", "danger")
            return redirect(url_for("auth.register"))
        patient_role = Role.query.filter_by(name="patient").first()
        if not patient_role:
            flash("Patient role not found.", "danger")
            return redirect(url_for("auth.register"))
        user = User(username=username, email=email, password_hash=generate_password_hash(password), full_name=full_name, phone=phone, role_id=patient_role.id)
        db.session.add(user)
        db.session.flush()

        patient = Patient(
        user_id=user.id,
            gender=request.form.get("gender","")
    )

        db.session.add(patient)
        
        db.session.commit()
        flash("Registration successful. Please sign in.", "success")
        return redirect(url_for("auth.login"))
    return render_template("register.html")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")
        user = User.query.filter_by(email=email).first()
        if not user or not check_password_hash(user.password_hash, password):
            flash("Invalid email or password.", "danger")
            return redirect(url_for("auth.login"))
        if not user.is_active:
            flash("Account is disabled.", "warning")
            return redirect(url_for("auth.login"))
        token = create_access_token(identity=str(user.id))
        print(token) 
        response = redirect(url_for("main.dashboard"))
        set_access_cookies(response, token)
        print(response.headers)
        flash("Welcome back, MediAI user.", "success")
        return response
    return render_template("login.html")


@auth_bp.route("/logout")
def logout():
    response = redirect(url_for("main.home"))
    unset_jwt_cookies(response)
    return response


@auth_bp.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        user = User.query.filter_by(email=email).first()
        if user:
            token = secrets.token_urlsafe(16)
            current_app.config.setdefault("PASSWORD_RESET_TOKENS", {})[token] = user.id
            print(f"Reset link: {url_for('auth.reset_password', token=token, _external=True)}")
            flash("Password reset instructions were sent (shown in server log).", "success")
        else:
            flash("No account found for that email.", "warning")
        return redirect(url_for("auth.login"))
    return render_template("forgot_password.html")


@auth_bp.route("/reset-password/<token>", methods=["GET", "POST"])
def reset_password(token):
    if request.method == "POST":
        new_password = request.form.get("password", "")
        if len(new_password) < 6:
            flash("Password must be at least 6 characters.", "warning")
            return redirect(url_for("auth.reset_password", token=token))
        user_id = current_app.config.get("PASSWORD_RESET_TOKENS", {}).pop(token, None)
        if not user_id:
            flash("Invalid or expired reset token.", "danger")
            return redirect(url_for("auth.login"))
        user = User.query.get(user_id)
        if user:
            user.password_hash = generate_password_hash(new_password)
            db.session.commit()
            flash("Password updated successfully.", "success")
        return redirect(url_for("auth.login"))
    return render_template("reset_password.html", token=token)
