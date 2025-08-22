from celery import shared_task
from django.db.models import Q


@shared_task
def update_user_follower(instagram_id: str):
    from .models import User as InstagramUser

    user = InstagramUser.objects.get(instagram_id=instagram_id)
    user.update_user_follower()


@shared_task
def update_user_following(instagram_id: str):
    from .models import User as InstagramUser

    user = InstagramUser.objects.get(instagram_id=instagram_id)
    user.update_user_following()


@shared_task
def get_instagram_users_stories():
    from .models import User as InstagramUser

    instagram_user = InstagramUser.objects.filter(
        Q(allow_auto_update_stories=True) | Q(auto_update_stories_limit_count__gt=0)
    )

    for user in instagram_user:
        get_instagram_user_stories.delay(user.username)


@shared_task(soft_time_limit=600)
def get_instagram_user_stories(username: str):
    from .models import User as InstagramUser

    instagram_user = InstagramUser.objects.get(username=username)
    stories, saved_stories = instagram_user.update_user_stories()

    return f"{len(saved_stories)}/{len(stories)} stories updated"


@shared_task
def update_instagram_users_profile():
    from .models import User as InstagramUser

    instagram_user = InstagramUser.objects.all()

    for user in instagram_user:
        update_instagram_user_profile.delay(user.username)


@shared_task
def update_instagram_user_profile(uuid: str):
    from .models import User as InstagramUser

    instagram_user = InstagramUser.objects.get(uuid=uuid)
    instagram_user.update_information_from_api()


@shared_task
def update_instagram_auto_profiles():
    """Update profiles for users who have allowed automatic profile updates."""
    from .models import User as InstagramUser

    instagram_users = InstagramUser.objects.filter(
        Q(allow_auto_update_profile=True) | Q(auto_update_profile_limit_count__gt=0)
    )

    for user in instagram_users:
        update_instagram_user_profile.delay(user.uuid)


@shared_task
def user_following_update_profile_pictures(instagram_id: str) -> str:
    from .models import User as InstagramUser
    from .models import UserFollowing

    instagram_user = InstagramUser.objects.get(instagram_id=instagram_id)

    for user in UserFollowing.objects.filter(user=instagram_user):
        user_following_update_profile_picture.delay(user.id)

    return instagram_user.username


@shared_task
def user_following_update_profile_picture(id: str) -> str:
    from .models import UserFollowing

    user_following = UserFollowing.objects.get(id=id)
    user_following.save()

    return user_following.username


@shared_task
def user_follower_update_profile_pictures(instagram_id: str) -> str:
    from .models import User as InstagramUser
    from .models import UserFollower

    instagram_user = InstagramUser.objects.get(instagram_id=instagram_id)

    for user in UserFollower.objects.filter(user=instagram_user):
        user_follower_update_profile_picture.delay(user.id)

    return instagram_user.username


@shared_task
def user_follower_update_profile_picture(id: str) -> str:
    from .models import UserFollower

    user_follower = UserFollower.objects.get(id=id)
    user_follower.save()

    return user_follower.username
