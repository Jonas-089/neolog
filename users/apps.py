from django.apps import AppConfig


class UsersConfig(AppConfig):
    name = 'users'

    # for automatic profile creation after user registration
    def ready(self):
        import users.signals
