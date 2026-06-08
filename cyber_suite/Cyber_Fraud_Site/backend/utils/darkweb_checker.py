def check_email_leak(email):
    if "test" in email:
        return "Email Found in Dark Web Leak"
    return "No Leak Found"