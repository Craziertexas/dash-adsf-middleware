import os
from dotenv import load_dotenv
from flask import redirect, g, url_for, Response
from flask_saml2.utils import certificate_from_file, private_key_from_file
from flask_saml2.sp import ServiceProvider
from functools import wraps
from .exceptions import SettingEnvNotFound
from __main__ import server

class SPConfig():
    
    def __init__(self):
        load_dotenv()
        self.serverName = os.environ.get('SERVER_NAME', None)
        self.secret = os.environ.get('SECRET', None)
        self.private_key = os.environ.get('PRIVATE_KEY_PATH', None)
        self.certificateSP = os.environ.get('SP_CERTIFICATE_PATH', None)
        self.certificateIDP = os.environ.get('IDP_CERTIFICATE_PATH', None)
        self.entity_id = os.environ.get('ENTITY_ID', None)
        self.sso_url = os.environ.get('SSO_URL', None)
        self.slo_url = os.environ.get('SLO_URL', None)
        self.redirectLogIn = os.environ.get('REDIRECT_LOGIN', '/')
        self.redirectLogOut = os.environ.get('REDIRECT_LOGOUT', '/')
        
        if not(self.serverName and self.secret and self.private_key and self.certificateSP and self.certificateIDP and self.entity_id and self.sso_url and self.slo_url):
            raise SettingEnvNotFound

spConfig = SPConfig()
  
class ServiceProvider(ServiceProvider):
    
    def __init__(self) -> None:
        server.secret_key = spConfig.secret
        server.config['SERVER_NAME'] = spConfig.serverName

        server.config['SAML2_SP'] = {
            'certificate': certificate_from_file(spConfig.certificateSP),
            'private_key': private_key_from_file(spConfig.private_key),
        }

        server.config['SAML2_IDENTITY_PROVIDERS'] = [
        {
            'CLASS': 'flask_saml2.sp.idphandler.IdPHandler',
            'OPTIONS': {
                'display_name': 'SAML-TEST',
                'entity_id': spConfig.entity_id,
                'sso_url': spConfig.sso_url,
                'slo_url': spConfig.sso_url,
                'certificate': certificate_from_file(spConfig.certificateIDP),
            },
        },]
        self.get_login_return_url
        super().__init__()
    
    def get_logout_return_url(self):
         return url_for(spConfig.redirectLogOut, _external=True)
     
    def get_default_login_return_url(self):
         return url_for(spConfig.redirectLogIn, _external=True)

sp = ServiceProvider()
server.register_blueprint(sp.create_blueprint(), url_prefix='/saml/')

def saml_login(view_func):
    @wraps(view_func)
    def wrapped_view(**kwargs):
        if sp.is_user_logged_in():
            return view_func(**kwargs)
        return redirect(url_for('flask_saml2_sp.login', _external=True))
    return wrapped_view

def auth_required(view_func):
    @wraps(view_func)
    def wrapped_view(**kwargs):
        if sp.is_user_logged_in():
            return view_func(**kwargs)
        else:
            return Response("User Not authenticated!", status=401)
    return wrapped_view

@server.before_request
def before_request():
    if sp.is_user_logged_in():
        g.user = sp.get_auth_data_in_session()
    else:
        g.user = None