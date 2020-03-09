from itsdangerous import URLSafeTimedSerializer

from newspipe.bootstrap import application


def generate_confirmation_token(nickname):
    serializer = URLSafeTimedSerializer(application.config["SECRET_KEY"])
    return serializer.dumps(nickname, salt=application.config["SECURITY_PASSWORD_SALT"])


def confirm_token(token):
    serializer = URLSafeTimedSerializer(application.config["SECRET_KEY"])
    try:
        nickname = serializer.loads(
            token,
            salt=application.config["SECURITY_PASSWORD_SALT"],
            max_age=application.config['TOKEN_VALIDITY_PERIOD'],
        )
    except:
        return False
    return nickname
