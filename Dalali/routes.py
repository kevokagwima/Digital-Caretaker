from flask import Blueprint, render_template, flash, url_for, redirect, request, session, make_response
from flask_login import login_required, current_user
from Models.base_model import db, get_local_time
from Models.properties import Property, PropertyTypes, PropertyLocation
from .aws_credentials import awsCredentials
from botocore.exceptions import NoCredentialsError, PartialCredentialsError, ClientError
from datetime import date
from flask_caching import Cache, CachedResponse
from slugify import slugify
import boto3

dalali = Blueprint("dalali", __name__)
s3 = boto3.resource(
  "s3",
  aws_access_key_id = awsCredentials.aws_access_key,
  aws_secret_access_key = awsCredentials.aws_secret_key
)
bucket_name = awsCredentials.bucket_name
region = awsCredentials.region
cache = Cache()