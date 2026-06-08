def extract_url_features(url):
    return [
        len(url),                 # url_length
        1 if "https" in url else 0,  # has_https
        url.count(".")           # num_dots
    ]
def extract_upi_features(amount, location_change, device_change):
    return [
        float(amount),
        int(location_change),
        int(device_change)
    ]

def extract_sms_features(message):
    return [
        len(message),
        1 if "free" in message.lower() else 0,
        1 if "win" in message.lower() else 0
    ]

def extract_call_features(duration, unknown_number, international):
    return [
        int(duration),
        int(unknown_number),
        int(international)
    ]