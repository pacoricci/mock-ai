from mcp.server.fastmcp import FastMCP, Context
import anyio

mcp_steteful = FastMCP("mcp")


@mcp_steteful.tool()
async def start_notification_stream(
    interval: int, count: int, caller: str, ctx: Context
) -> str:
    """Sends a stream of notifications with configurable count and interval"""

    for i in range(count):
        notification_msg = f"[{i + 1}/{count}] Event from '{caller}'"
        ctx.info(notification_msg)

        if i < count - 1:
            anyio.sleep(interval)
    return f"Sent {count} notifications with {interval}s interval for caller: {caller}"
