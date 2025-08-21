from flask import Blueprint, render_template, flash, url_for, redirect, request
from flask_login import login_required
from Models.base_model import db
from Models.users import Users
from Models.transactions import Subscription, Payment
from Models.properties import Property, PropertyLocation, PropertyTypes
from .form import *

admin = Blueprint("admin", __name__, url_prefix="/admin")
