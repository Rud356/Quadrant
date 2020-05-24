from app import loop
from models import UserModel
from config import tests_config

auth_credentials = {
    'login':tests_config['login'],
    'password':tests_config['password']
}
second_auth_credentials = {
    'login':tests_config['second_login'],
    'password':tests_config['second_password']
}

# Switch server to debug mode
async def setup_for_tests():
    await UserModel.registrate(
        "Tester1", **auth_credentials
    )
    await UserModel.registrate(
        "Tester2", **second_auth_credentials
    )

loop.run_until_complete(setup_for_tests())