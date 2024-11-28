from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SelectField, TextAreaField
from wtforms.validators import Length, DataRequired

class ComplaintForm(FlaskForm):
  tenant_id = IntegerField(label="Enter Tenant ID", validators=[DataRequired(message="Tenant ID field required")])
  title = StringField(label="Enter a title", validators=[Length(min=5, max=100), DataRequired(message="Title field required")])
  category = SelectField(label="Choose a category",choices=["Electricity", "Water", "Repairs", "Other"], validators=[DataRequired(message="Category field required")])
  body = TextAreaField(label="Type your complaint", validators=[DataRequired(message="Body field required")])
