from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Email, Length
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, PasswordField, SubmitField
from wtforms.validators import DataRequired


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
    title = StringField("Title", validators=[DataRequired()])
    short_description = StringField("Short Description", validators=[DataRequired()])
    long_description = TextAreaField("Full Description")
    image_path = StringField("Image Path")
    skills = StringField("Skills")
    submit = SubmitField("Save")


class CertificateForm(FlaskForm):
    title = StringField("Title", validators=[DataRequired()])
    issuer = StringField("Issuer", validators=[DataRequired()])
    image_path = StringField("Image Path")
    submit = SubmitField("Save")
