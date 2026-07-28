from django.http import HttpResponse

from .utils import DiscordAPI


def index(request):
    return HttpResponse("Hello, world. You're at the discord index.")


def refresh_url_health_check(request):
    refreshed_url = DiscordAPI.refresh_url(
        "https://cdn.discordapp.com/attachments/858938620425404426/1248453128991412224/animemoeus-waifu.jpg"
    )

    if refreshed_url:
        return HttpResponse(status=200)

    return HttpResponse(status=404)
