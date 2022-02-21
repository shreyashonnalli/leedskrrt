import os

# CSRF prevention is enabled here
WTF_CSRF_ENABLED = True

# Secret key allows the creation of cryptographically secure tokens, adds some security to the web application
SECRET_KEY = 'a-239c0da225cc50a321cf06c7ea87aae2806ea6'

basedir = os.path.abspath(os.path.dirname(__file__))
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db')
# Keep track modifications to False, unless required
SQLALCHEMY_TRACK_MODIFICATIONS = True
