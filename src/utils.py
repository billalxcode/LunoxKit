from user_agent import generate_user_agent

def createHeaders(hostname: str = "", ua: bool =True):
    headers = {}
    headers["Host"] = hostname
    if ua:
        headers["User-Agent"] = generate_user_agent()
    
    return headers