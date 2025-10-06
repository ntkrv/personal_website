from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, PasswordField, SubmitField, SelectField
from wtforms.validators import DataRequired, Email, Length, Optional, URL, EqualTo


class ContactForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired(), Length(max=50)])
    email = StringField("Email", validators=[DataRequired(), Email()])
    message = TextAreaField("Message", validators=[DataRequired()])
    submit = SubmitField("Send")


class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Login")


class ProjectForm(FlaskForm):
    title = StringField("Title", validators=[DataRequired(), Length(max=150)])
    short_description = StringField(
        "Short Description", validators=[DataRequired(), Length(max=300)]
    )
    long_description = TextAreaField("Full Description", validators=[DataRequired()])
    image_path = StringField("Image Path", validators=[Optional(), Length(max=120)])
    stack = StringField("Stack", validators=[Optional(), Length(max=200)])

    git_link = StringField("Link", validators=[Optional(), URL(), Length(max=255)])
    link_type = SelectField(
        "Link Type",
        choices=[("github", "GitHub"), ("gdrive", "Google Drive")],
        validators=[DataRequired()],
    )


class CertificateForm(FlaskForm):
    title = StringField("Title", validators=[DataRequired(), Length(max=150)])
    issuer = StringField("Issuer", validators=[DataRequired(), Length(max=100)])
    skills = StringField("Skills", validators=[Optional(), Length(max=200)])
    link = StringField(
        "Certificate Link", validators=[Optional(), URL(), Length(max=255)]
    )


class ResetPasswordForm(FlaskForm):
    new_password = PasswordField("New Password", validators=[DataRequired()])
    confirm_password = PasswordField(
        "Confirm Password", validators=[DataRequired(), EqualTo("new_password")]
    )
    submit = SubmitField("Reset Password")
