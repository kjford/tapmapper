import boto3
import os


def get_aws_parameter(param_name, region='us-west-2'):
    """
    This function reads a secure parameter from AWS' SSM service.
    The request must be passed a valid parameter name, as well as
    temporary credentials which can be used to access the parameter.
    The parameter's value is returned.
    """
    # Create the SSM Client
    ssm = boto3.client('ssm', region_name=region)

    # Get the requested parameter
    response = ssm.get_parameter(Name=param_name, WithDecryption=True)

    return response['Parameter']['Value']


ENV = os.environ.get('FLASK_ENV', 'production')
DATABASE_PORT = os.environ.get('DATABASE_PORT', 3306)
DATABASE_DB = os.environ.get('DATABASE_DB', 'tapmapper')

if ENV == 'production':
    region = os.environ.get('REGION', 'us-west-2')
    DEBUG = False
    DATABASE_HOST = os.environ.get('DATABASE_HOST', 'localhost')
    DATABASE_USER = os.environ.get('DATABASE_USER', 'webuser')
    DATABASE_PASSWORD = get_aws_parameter('DATABASE_PASSWORD', region)

elif ENV == 'development':
    DEBUG = True
    DATABASE_HOST = os.environ.get('DATABASE_HOST', 'db')
    DATABASE_USER = os.environ.get('DATABASE_USER', 'root')
    DATABASE_PASSWORD = os.environ.get('DATABASE_PASSWORD', 'demo')

else:
    raise ValueError("ENV must be production or development")
