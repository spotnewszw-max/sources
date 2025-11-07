import httpx

async def fetch_url(url: str) -> dict:
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as e:
        return {"error": f"HTTP error occurred: {e.response.status_code}"}
    except Exception as e:
        return {"error": str(e)}

def fetch_url_sync(url: str) -> dict:
    try:
        response = httpx.get(url)
        response.raise_for_status()
        return response.json()
    except httpx.HTTPStatusError as e:
        return {"error": f"HTTP error occurred: {e.response.status_code}"}
    except Exception as e:
        return {"error": str(e)}