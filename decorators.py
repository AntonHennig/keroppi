# decorators.py
def delete_command_message(delay=None):
    """Decorator to set the deletion delay for the command message."""

    def decorator(func):
        setattr(func, "_delete_command_delay", delay)
        return func

    return decorator


def delete_bot_response(delay=None):
    """Decorator to set the deletion delay for the bot's response message."""

    def decorator(func):
        setattr(func, "_delete_response_delay", delay)
        return func

    return decorator
