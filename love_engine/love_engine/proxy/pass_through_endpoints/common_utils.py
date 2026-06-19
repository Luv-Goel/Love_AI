from fastapi import Request


def get_love_engine_virtual_key(request: Request) -> str:
    """
    Extract and format API key from request headers.
    Prioritizes x-love_engine-api-key over Authorization header.


    Vertex JS SDK uses `Authorization` header, we use `x-love_engine-api-key` to pass love_engine virtual key

    """
    love_engine_api_key = request.headers.get("x-love_engine-api-key")
    if love_engine_api_key:
        return f"Bearer {love_engine_api_key}"
    return request.headers.get("Authorization", "")
