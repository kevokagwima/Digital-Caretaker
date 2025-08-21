from flask import Blueprint, render_template, flash, url_for, redirect, request, make_response
from Dalali.routes import CachedResponse

main = Blueprint("main", __name__)

@main.route("/")
@main.route("/home")
def index():
  return CachedResponse(
    response = make_response(
      render_template("Main/index.html")
    ),
    timeout=600
  )

@main.route("/about")
def about():
  return CachedResponse(
    response = make_response(
      render_template("Main/about.html")
    ),
    timeout=600
  )

@main.route("/contact")
def contact():
  return CachedResponse(
    response = make_response(
      render_template("Main/contact.html")
    ),
    timeout=600
  )
