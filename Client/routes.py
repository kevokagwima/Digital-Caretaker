from flask import Blueprint, render_template, flash, url_for, redirect, request
from flask_login import login_required, current_user
from Models.base_model import db

client = Blueprint("client", __name__)
