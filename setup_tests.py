from app import loop, client
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

async def drop_db():
    await client.drop_database("debug_chat")
