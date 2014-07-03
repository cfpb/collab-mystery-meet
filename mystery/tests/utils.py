from django.contrib.auth import get_user_model
from django.test.client import RequestFactory
from core.models import Person
import random
import string

def random_user():
    user = get_user_model().objects.create_user(
            ''.join(random.choice(string.lowercase) for _ in range(12)))
    person = Person.objects.create(user=user)
    return user


def mock_req(path='/', user = None):
    """
    Mock request -- with user!
    """
    if not user:
        user = random_user()
    req = RequestFactory().get(path)
    req.user = user
    return req

