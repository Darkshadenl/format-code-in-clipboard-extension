from .crawl4ai_client import Crawl4AIClient


# Login function implementation
def login_to_website(url, email, password, session_id=None):
    print(f"Attempting to login to {url} with email: {email}")

    # Create client
    client = Crawl4AIClient(api_token="crawl4ai_api_token")

    js_code = [
        f"document.querySelector('input[type=\"email\"]').value = '{email}';",
        f"document.querySelector('input[type=\"password\"]').value = '{password}';",
        f"document.querySelector('button[type=\"submit\"]').click();",
    ]

    request_params = {
        "urls": url,
        "js_code": js_code,
        "crawler_params": {
            "session_id": session_id,
            "use_managed_browser": True,
            "user_data_dir": "./browser-data",
            "headless": False,
        },
        "js_code": js_code,
        "extra": {"bypass_cache": True},
    }

    # Perform the login
    login_result = client.crawl(urls=url, request=request_params)

    request_params_2 = {
        "urls": "https://hurenbij.vesteda.com/zoekopdracht/",
        "crawler_params": {
            "session_id": session_id,
            "use_managed_browser": True,
            "user_data_dir": "./browser-data",
            "headless": True,
        },
        "extra": {"bypass_cache": True},
    }
    zoekopdracht_result = client.crawl(
        urls="https://hurenbij.vesteda.com/zoekopdracht/", request=request_params_2
    )

    return login_result


# Example usage
if __name__ == "__main__":
    # Uncomment to test login
    login_result = login_to_website(
        url="https://hurenbij.vesteda.com/login",
        email="quinten_meijboom_96@outlook.com",
        password="ejv3kny*ahv8GAU9qkh",
        session_id="vesteda_session",
    )
    print(login_result)
