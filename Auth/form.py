from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, PasswordField
from wtforms.validators import Length, EqualTo, Email, DataRequired, ValidationError
from Models.models import Landlord, Tenant, Properties, Users

class LandlordRegistrationForm(FlaskForm):
  first_name = StringField(label="First Name", validators=[DataRequired(message="First Name field required")])
  last_name = StringField(label="Last Name", validators=[DataRequired(message="Last Name field required")])
  email_address = StringField(label="Email Address", validators=[Email(), DataRequired(message="Email Address field required")])
  phone_number = StringField(label="Phone number", validators=[Length(min=10, max=10, message="Invalid Phone Number"), DataRequired(message="Phone Number field required")])
  password = PasswordField(label="Password", validators=[Length(min=5,message="Password has to be between 5 and 25 characters long",), DataRequired(message="Password field required")])
  password1 = PasswordField(label="Confirm Password", validators=[EqualTo("password",message="Passwords do not match"), DataRequired(message="Confirm Password field required")])

  def validate_phone_number(self, phone_number_to_validate):
    phone_number = phone_number_to_validate.data
    if phone_number[0] != str(0):
      raise ValidationError("Invalid phone number. Phone number must begin with 0")
    elif phone_number[1] != str(7) and phone_number[1] != str(1):
      raise ValidationError("Invalid phone number. Phone number must begin with 0 followed by 7 or 1")
    elif Landlord.query.filter_by(phone=phone_number_to_validate.data).first():
      raise ValidationError("Phone Number already exists, Please try another one")

  def validate_email_address(self, email_to_validate):
    email = Landlord.query.filter_by(email=email_to_validate.data).first()
    if email:
      raise ValidationError("Email Address already exists, Please try another one")

class LandlordLoginForm(FlaskForm):
  landlord_id = IntegerField(label="Enter Landlord ID", validators=[DataRequired(message="Landlord ID field required")])
  password = PasswordField(label="Enter Password", validators=[DataRequired(message="Password field required")])

class TenantRegistrationForm(FlaskForm):
  first_name = StringField(label="First Name", validators=[DataRequired(message="First Name field required")])
  last_name = StringField(label="Last Name", validators=[DataRequired(message="Last Name field required")])
  email_address = StringField(label="Email Address", validators=[Email(), DataRequired(message="Email Address field required")])
  phone_number = StringField(label="Phone number", validators=[Length(min=10, max=10, message="Invalid Phone Number"), DataRequired(message="Phone Number field required")])
  landlord_id = IntegerField(label="Enter Landlord ID", validators=[DataRequired(message="Landlord ID field required")])
  property_id = IntegerField(label="Enter Property ID", validators=[DataRequired(message="Property ID field required")])
  password = PasswordField(label="Password", validators=[Length(min=5,message="Password has to be between 5 and 25 characters long"), DataRequired(message="Password field required")])
  password1 = PasswordField(label="Confirm Password",validators=[EqualTo("password",message="Passwords do not match"), DataRequired(message="Confirm Password field required")])

  def validate_phone_number(self, phone_number_to_validate):
    phone_number = phone_number_to_validate.data
    if phone_number[0] != str(0):
      raise ValidationError("Invalid phone number. Phone number must begin with 0")
    elif phone_number[1] != str(7) and phone_number[1] != str(1):
      raise ValidationError("Invalid phone number. Phone number must begin with 0 followed by 7 or 1")
    elif Landlord.query.filter_by(phone=phone_number_to_validate.data).first():
      raise ValidationError("Phone Number already exists, Please try another one")

  def validate_email_address(self, email_to_validate):
    email = Tenant.query.filter_by(email=email_to_validate.data).first()
    if email:
      raise ValidationError("Email Address already exists, Please try another one")

  def validate_landlord_id(self, landlord_id_to_validate):
    global landlord
    landlord = Landlord.query.filter_by(unique_id=landlord_id_to_validate.data).first()
    if not landlord:
      raise ValidationError("Invalid Landlord ID")

  def validate_property_id(self, property_id_to_validate):
    landlord_property = Properties.query.filter_by(property_id=property_id_to_validate.data).first()
    if landlord_property is None:
      raise ValidationError("Invalid Property ID")
    else:
      tenants = Tenant.query.filter_by(properties=landlord_property.id).count()
      if landlord_property.owner != landlord.id:
        raise ValidationError("Property does not belong to the specified landlord")
      elif landlord_property.rooms == tenants:
        raise ValidationError("Maximum occupancy of this property has been reached")
  
class TenantLoginForm(FlaskForm):
  tenant_id = IntegerField(label="Enter Tenant ID", validators=[DataRequired(message="Tenant ID field required")])
  password = PasswordField(label="Enter password", validators=[DataRequired(message="Password field required")])

class UserRegistrationForm(FlaskForm):
  first_name = StringField(label="First Name", validators=[DataRequired()])
  second_name = StringField(label="Second Name", validators=[DataRequired()])
  last_name = StringField(label="Last Name", validators=[DataRequired()])
  email_address = StringField(label="Email Address", validators=[Email(), DataRequired()])
  phone_number = StringField(label="Phone number",validators=[Length(min=10, max=10, message="Invalid Phone Number"), DataRequired()])
  password = PasswordField(label="Password", validators=[Length(min=5, message="Password must be more than 5 characters"), DataRequired()])
  password1 = PasswordField(label="Confirm Password", validators=[EqualTo("password", message="Passwords do not match"), DataRequired()])

  def validate_username(self, username_to_validate):
    username = Users.query.filter_by(username=username_to_validate.data).first()
    if username:
      raise ValidationError("Username already exists, Please try anotherone")
  
  def validate_phone_number(self, phone_number_to_validate):
    phone_number = phone_number_to_validate.data
    if phone_number[0] != str(0):
      raise ValidationError("Invalid phone number. Phone number must begin with 0")
    elif phone_number[1] != str(7) and phone_number[1] != str(1):
      raise ValidationError("Invalid phone number. Phone number must begin with 0 followed by 7 or 1")
    elif Users.query.filter_by(phone=phone_number_to_validate.data).first():
      raise ValidationError("Phone Number already exists, Please try another one")

  def validate_email_address(self, email_to_validate):
    email = Users.query.filter_by(email=email_to_validate.data).first()
    if email:
      raise ValidationError("Email Address already exists, Please try another one")

class UserLoginForm(FlaskForm):
  email_address = StringField(label="Email Address", validators=[DataRequired()])
  password = PasswordField(label="Password", validators=[DataRequired()])

class AdminLoginForm(FlaskForm):
  admin_id = IntegerField(label="Enter Admin ID", validators=[DataRequired()])
  password = PasswordField(label="Enter password", validators=[DataRequired()])
