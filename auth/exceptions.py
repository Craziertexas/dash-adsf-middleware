class SettingEnvNotFound(Exception):
    
    def __init__(self, *args: object):
        ErrorMessage = 'Enviroment variables not found please check SERVER_NAME, SECRET, PRIVATE_KEY_PATH, SP_CERTIFICATE, IDP_CERTIFICATE, ENTITY_ID, SSO_URL, SLO_URL'
        super().__init__(ErrorMessage,*args)
