from collections import OrderedDict

from app import app


class authorization_cache:
    salt_pwd = OrderedDict()
    login_salt = OrderedDict()

    CACHE_SIZE = app.config['LOGIN_CACHE_SIZE']

    @staticmethod
    def cache_passwords(f: callable):
        async def caching(password, salt):
            cached_key = (password, salt)
            if cached_key not in authorization_cache.salt_pwd:
                result = await f(password, salt)
                authorization_cache.salt_pwd[cached_key] = result

                if len(authorization_cache.salt_pwd) > authorization_cache.CACHE_SIZE:
                    keys = list(authorization_cache.salt_pwd)
                    authorization_cache.salt_pwd.pop(keys[0])

                return result

            else:
                return authorization_cache.salt_pwd[cached_key]

        caching.__name__ = f.__name__
        return caching

    @staticmethod
    def cache_login_salt(f: callable):
        async def caching_logins(login):
            if login not in authorization_cache.login_salt:
                result = await f(login)

                if result:
                    authorization_cache.login_salt[login] = result

                if len(authorization_cache.login_salt) > authorization_cache.CACHE_SIZE:
                    keys = list(authorization_cache.login_salt)
                    authorization_cache.login_salt.pop(keys[0])

                return result

            else:
                return authorization_cache.login_salt[login]

        caching_logins.__name__ = f.__name__
        return caching_logins
