from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileSize
from wtforms import StringField, TextAreaField, PasswordField, SubmitField, SelectField
from wtforms.validators import (
    DataRequired,
    Email,
    EqualTo,
    Length,
    Optional,
    URL,
    ValidationError,
)

from utils.uploads import sniff_image_ext


class ContactForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired(), Length(max=50)])
    email = StringField("Email", validators=[DataRequired(), Email()])
    message = TextAreaField("Message", validators=[DataRequired()])
    # Honeypot: hidden field a real user never sees or fills.
    # If a bot submits with anything in it, the route silently drops the
    # request (no flash, no DB write, no email).
    website = StringField("Website", validators=[Optional(), Length(max=200)])
    submit = SubmitField("Send")


class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Login")


ALLOWED_IMAGE_EXTS = ("jpg", "jpeg", "png", "webp")


class ProjectForm(FlaskForm):
    title = StringField("Title", validators=[DataRequired(), Length(max=150)])
    short_description = StringField(
        "Short Description", validators=[DataRequired(), Length(max=300)]
    )
    long_description = TextAreaField("Full Description", validators=[DataRequired()])
    # Upload trumps URL on save. URL is kept as a fallback so legacy
    # external images (Unsplash, etc.) still work without re-uploading.
    image_file = FileField(
        "Upload image (jpg / png / webp, ≤ 4 MB)",
        validators=[
            Optional(),
            FileAllowed(ALLOWED_IMAGE_EXTS, "Images only: jpg, png, or webp."),
            FileSize(max_size=4 * 1024 * 1024, message="Max file size is 4 MB."),
        ],
    )
    image_path = StringField(
        "…or paste an image URL", validators=[Optional(), Length(max=120)]
    )
    stack = StringField("Stack", validators=[Optional(), Length(max=200)])

    git_link = StringField("Link", validators=[Optional(), URL(), Length(max=255)])
    link_type = SelectField(
        "Link Type",
        choices=[("github", "GitHub"), ("gdrive", "Google Drive")],
        validators=[DataRequired()],
    )

    def validate_image_file(self, field):
        # FileAllowed only looks at the filename; check the bytes too.
        if field.data and getattr(field.data, "filename", ""):
            if sniff_image_ext(field.data) is None:
                raise ValidationError(
                    "That file isn't a valid jpg, png, or webp image."
                )


class CertificateForm(FlaskForm):
    title = StringField("Title", validators=[DataRequired(), Length(max=150)])
    issuer = StringField("Issuer", validators=[DataRequired(), Length(max=100)])
    skills = StringField("Skills", validators=[Optional(), Length(max=200)])
    link = StringField(
        "Certificate Link", validators=[Optional(), URL(), Length(max=255)]
    )


class ResetPasswordForm(FlaskForm):
    new_password = PasswordField(
        "New Password",
        validators=[
            DataRequired(),
            Length(min=12, max=128, message="Use 12 to 128 characters."),
        ],
    )
    confirm_password = PasswordField(
        "Confirm Password",
        validators=[
            DataRequired(),
            EqualTo("new_password", message="Passwords must match."),
        ],
    )
    submit = SubmitField("Reset Password")
