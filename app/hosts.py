from django_hosts import host, patterns

host_patterns = patterns(
    "",
    host("", "app.urls", name="www"),
    host("discord-storage", "discord_storage.urls", name="discord-storage"),
)
