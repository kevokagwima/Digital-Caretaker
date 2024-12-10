from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, TextAreaField
from wtforms.validators import Length, DataRequired

class ComplaintForm(FlaskForm):
  title = StringField(label="Enter a title", validators=[Length(min=5, max=100), DataRequired(message="Title field required")])
  category = SelectField(label="Choose a category",choices=["Electricity", "Water", "Repairs", "Other"], validators=[DataRequired(message="Category field required")])
  message = TextAreaField(label="Type your complaint", validators=[DataRequired(message="Body field required")])
