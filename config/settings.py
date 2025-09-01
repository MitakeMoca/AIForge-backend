TORTOISE_ORM = {
    "connections": {
        "default": {
            "engine": "tortoise.backends.mysql",
            "credentials": {
                "host": "host",
                "port": "24660",
                "user": "root",
                "password": "password",
                "database": "aiforge",
                "charset": "utf8mb4",
                "autocommit": True,
            }
        },
    },
    "apps": {
        "models": {
            "models": [
                "models.dataset", "models.hypara", "models.model",
                "models.project", "models.tag", "models.user", "aerich.models"
            ],
            "default_connection": "default",
        },
    },
    "use_tz": False,
}
