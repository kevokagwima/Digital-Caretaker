from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import Length, EqualTo, Email, DataRequired, ValidationError
from models import Members, Tenant, Landlord

class user_registration(FlaskForm):
  first_name = StringField(label="First Name", validators=[DataRequired()])
  second_name = StringField(label="Second Name", validators=[DataRequired()])
  last_name = StringField(label="Last Name", validators=[DataRequired()])
  email_address = StringField(label="Email Address", validators=[Email(), DataRequired()])
  phone_number = StringField(label="Phone number",validators=[Length(min=10, max=10, message="Invalid Phone Number"),DataRequired()])
  username = StringField(label="Username", validators=[Length(min=5, max=25,message="Username must be more than 5 characters"), DataRequired()])
  password = PasswordField(label="Password", validators=[Length(min=5, message="Password must be more than 5 characters"), DataRequired()])
  password1 = PasswordField(label="Confirm Password", validators=[EqualTo("password", message="Passwords do not match"), DataRequired()])

  def validate_username(self, username_to_validate):
    username = (Members.query.filter_by(username=username_to_validate.data).first() or Tenant.query.filter_by(username=username_to_validate.data).first() or Landlord.query.filter_by(username=username_to_validate.data).first())
    if username:
      raise ValidationError("Username already exists, Please try anotherone")

  def validate_phone_number(self, phone_number_to_validate):
    phone_number = Members.query.filter_by(phone=phone_number_to_validate.data).first()
    if phone_number:
      raise ValidationError("Phone Number already exists, Please try another one")
  
  def validate_phone_number(self, phone_number_to_validate):
    phone_number = phone_number_to_validate.data
    if phone_number[0] != str(0):
      raise ValidationError("Invalid phone number. Phone number must begin with 0")
    elif phone_number[1] != str(7) and phone_number[1] != str(1):
      raise ValidationError("Invalid phone number. Phone number must begin with 0 followed by 7 or 1")

  def validate_email_address(self, email_to_validate):
    email = Members.query.filter_by(email=email_to_validate.data).first()
    if email:
      raise ValidationError("Email Address already exists, Please try another one")

class login(FlaskForm):
  username = StringField(label="Username", validators=[DataRequired()])
  password = PasswordField(label="Password", validators=[DataRequired()])
