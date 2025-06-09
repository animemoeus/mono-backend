import factory
from django.utils import timezone

from instagram.models import User as InstagramUser


class InstagramUserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = InstagramUser

    uuid = factory.Faker("uuid4")
    instagram_id = factory.LazyFunction(lambda: str(factory.Faker._get_faker().random.randint(1000000000, 9999999999)))
    username = factory.LazyFunction(
        lambda: factory.Faker._get_faker()
        .lexify("??" + factory.Faker._get_faker().random.choice(["._", ".", "_"]) + "????")
        .lower()
    )
    full_name = factory.Faker("name")
    profile_picture_url = factory.Faker("image_url")
    biography = factory.Faker("text", max_nb_chars=200)
    is_private = factory.Faker("boolean")
    is_verified = factory.Faker("boolean")
    media_count = factory.Faker("random_int", min=0, max=1000)
    follower_count = factory.Faker("random_int", min=0, max=10000)
    following_count = factory.Faker("random_int", min=0, max=1000)
    allow_auto_update_stories = factory.Faker("boolean")
    allow_auto_update_profile = factory.Faker("boolean")
    created_at = factory.LazyFunction(timezone.now)
    updated_at = factory.LazyFunction(timezone.now)
    updated_at_from_api = factory.LazyFunction(timezone.now)
