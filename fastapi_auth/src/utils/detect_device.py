def detect_device_type(user_agent: str) -> str:
    user_agent = user_agent.lower()
    device_types = {"mobile": ["mobile", "android", "iphone"], "smart": ["smart", "tv", "watch"]}
    for (
        device_type,
        keywords,
    ) in device_types.items():
        if any(key in user_agent for key in keywords):
            return device_type
    return "web"
