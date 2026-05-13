import httpx
from mcp.server.fastmcp import FastMCP

BASE_URL = "http://127.0.0.1:8000/api/smart-plugs"

mcp = FastMCP("SmartPlugs")


def _client() -> httpx.AsyncClient:
    return httpx.AsyncClient(timeout=10.0)


# ── GET all ───────────────────────────────────────────────────────────────────

@mcp.tool()
async def get_all_plugs() -> dict:
    """
    Return the information about smart plugs in the system.

    Output:
    - List of SmartPlug objects
    - Each includes: id, name, utility_type, status, real_time_consumption

    """
    async with _client() as client:
        response = await client.get(BASE_URL)
        response.raise_for_status()
        return {"plugs": response.json()}

# ── POST (create) ─────────────────────────────────────────────────────────────

@mcp.tool()
async def create_plug(
        id: str,
        name: str,
        utility_type: str,
        user_permission: bool = False,
        status: str = "off",
        real_time_consumption: float = 0.0
) -> dict:
    """
    CRITICAL: Requires user confirmation. This request requires a UserPermissionResponse explicit tag from the user in the user chat. Require
    the UserPermissionResponse tag before calling this tool

    Create a new smart plug.


    Args:
    - id (compute by slugify the name)
    - name
    - utility_type (ELECTRICITY | WATER | GAS)
    - status (default: off)
    - real_time_consumption (default: 0.0)
    - user_permission (Check for UserPermissionResponse tag from the user. Don't make up this data)

    Output:
    - Created SmartPlug

    Error:
    - 409 if already exists
    """
    if not user_permission:
        return {
            "response": ""
        }

    payload = {
        "id": id,
        "name": name,
        "utility_type": utility_type,
        "status": status.lower(),
        "real_time_consumption": real_time_consumption,
    }
    async with _client() as client:
        response = await client.post(BASE_URL, json=payload)
        if response.status_code == 409:
            return {"error": f"Plug '{id}' already exists"}
        response.raise_for_status()
        return response.json()


# ── PUT (update) ──────────────────────────────────────────────────────────────

@mcp.tool()
async def update_plug(
        plug_id: str,
        name: str | None = None,
        utility_type: str | None = None,
        status: str | None = None,
        real_time_consumption: float | None = None,
) -> dict:
    """
    Update a smart plug.

    Args:
    - plug_id
    - Optional fields: name, utility_type, status, real_time_consumption

    Output:
    - Updated SmartPlug

    Error:
    - 404 if not found
    """
    payload = {
        k: v for k, v in {
            "name": name,
            "utility_type": utility_type,
            "status": status,
            "real_time_consumption": real_time_consumption,
        }.items() if v is not None
    }
    async with _client() as client:
        response = await client.put(f"{BASE_URL}/{plug_id}", json=payload)
        if response.status_code == 404:
            return {"error": f"Plug '{plug_id}' not found"}
        response.raise_for_status()
        return response.json()


# ── PATCH (switch status) ─────────────────────────────────────────────────────

@mcp.tool()
async def switch_plug(plug_id: str) -> dict:
    """
    Toggle smart plug status (ON/OFF).

    Args:
    - plug_id

    Output:
    - { "message": str }

    Error:
    - 404 if not found
    """
    async with _client() as client:
        response = await client.patch(f"{BASE_URL}/{plug_id}")
        if response.status_code == 404:
            return {"error": f"Plug '{plug_id}' not found"}
        response.raise_for_status()
        return response.json()


# ── DELETE ────────────────────────────────────────────────────────────────────

@mcp.tool()
async def delete_plug(plug_id: str) -> dict:
    """
    Delete a smart plug.

    Args:
    - plug_id

    Output:
    - Empty response (204)

    Error:
    - 404 if not found
    """
    async with _client() as client:
        response = await client.delete(f"{BASE_URL}/{plug_id}")
        if response.status_code == 404:
            return {"error": f"Plug '{plug_id}' not found"}
        response.raise_for_status()
        return {"message": f"Plug '{plug_id}' deleted successfully"}


if __name__ == "__main__":
    mcp.run()