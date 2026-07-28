from django_hosts import host, patterns

host_patterns = patterns(
    "",
    host("www", "config.urls", name="www"),
    host("discord-storage", "discord_storage.urls", name="discord_storage"),
)
