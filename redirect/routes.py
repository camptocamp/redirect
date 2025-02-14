import pyramid.config


def includeme(config: pyramid.config.Configurator) -> None:
    """Pyramid includeme function."""
    config.add_static_view("static", "static", cache_max_age=3600)
