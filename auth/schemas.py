from marshmallow import Schema, fields, validates_schema, ValidationError

from home.models import Users

class SignupSchema(Schema):
  
  email = fields.Email(required=True)
  password = fields.String(required=True)
  full_name = fields.String(required=True)

  @validates_schema
  def validate_name(self, data, **kwargs):
    errors = {}
    if data["full_name"] == "":
      errors["full_name"] = ["Full Name is empty"]
    if errors:
      raise ValidationError(errors)

  @validates_schema
  def validate_email(self, data, **kwargs):
    errors = {}
    result = Users.objects.filter(email=data["email"]).exists()
    if result:
      errors["email"] = ["email already exist"]
    if errors:
      raise ValidationError(errors)

class SigninSchema(Schema):
  
  email = fields.Email(required=True)
  password = fields.String(required=True)

  @validates_schema
  def validate_email(self, data, **kwargs):
    errors = {}
    result = Users.objects.filter(email=data["email"]).exists()
    if not result:
      errors["email"] = ["email don't exist"]
    if errors:
      raise ValidationError(errors)

class InitializeResetPasswordSchema(Schema):
  email = fields.Email(required=True)

  @validates_schema
  def validate_email(self, data, **kwargs):
    errors = {}
    result = Users.objects.filter(email=data["email"]).exists()
    if not result:
      errors["email"] = ["email don't exist"]
    if errors:
      raise ValidationError(errors)

class ResetPasswordSchema(Schema):
  password = fields.String(required=True)