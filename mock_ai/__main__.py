from pathlib import Path
from typing import Annotated, Any

import typer
import uvicorn
from rich.console import Console

from mock_ai.settings import uvicorn_settings

app = typer.Typer(
    no_args_is_help=True,
    rich_markup_mode="rich",
)


err_console = Console(stderr=True)
console = Console()


def main() -> None:
    app()


def _run(
    *,
    command: str,
) -> None:
    server_type = "development" if command == "dev" else "production"

    console.print(f"Starting {server_type} server 🚀")

    run_ssl = (
        uvicorn_settings.ssl_certfile is not None
        and uvicorn_settings.ssl_keyfile is not None
    )

    # Print documentation
    protocol = "https" if run_ssl else "http"
    url = f"{protocol}://{uvicorn_settings.host}:{uvicorn_settings.port}"
    url_docs = f"{url}/docs"

    console.print("")
    console.print(f"Server started at [link={url}]{url}[/]")
    console.print(f"Documentation at [link={url_docs}]{url_docs}[/]")

    if command == "dev":
        console.print("")
        console.print(
            "Running in development mode, for production use: "
            "[bold]mock-ai run[/]",
        )

    console.print("")
    console.print("Logs:")

    # Launch the server
    uvicorn.run(
        app="mock_ai.app:app",
        host=uvicorn_settings.host,
        port=uvicorn_settings.port,
        reload=uvicorn_settings.reload,
        workers=uvicorn_settings.workers,
        root_path=uvicorn_settings.root_path,
        proxy_headers=uvicorn_settings.proxy_headers,
        timeout_keep_alive=uvicorn_settings.timeout_keep_alive,
        ssl_certfile=uvicorn_settings.ssl_certfile,
        ssl_keyfile=uvicorn_settings.ssl_keyfile,
        ssl_keyfile_password=uvicorn_settings.ssl_keyfile_password,
    )


@app.command()
def dev(
    *,
    # uvicorn options
    host: Annotated[
        str,
        typer.Option(
            help=(
                "The host to serve on. For local development in localhost "
                "use [blue]127.0.0.1[/blue]. To enable public access, "
                "e.g. in a container, use all the IP addresses "
                "available with [blue]0.0.0.0[/blue]."
            )
        ),
    ] = "127.0.0.1",
    port: Annotated[
        int,
        typer.Option(help="The port to serve on."),
    ] = uvicorn_settings.port,
    reload: Annotated[
        bool,
        typer.Option(
            help=(
                "Enable auto-reload of the server when (code) files change. "
                "This is [bold]resource intensive[/bold], "
                "use it only during development."
            )
        ),
    ] = True,
    root_path: Annotated[
        str,
        typer.Option(
            help=(
                "The root path is used to tell your app that it is being served "
                "to the outside world with some [bold]path prefix[/bold] "
                "set up in some termination proxy or similar."
            )
        ),
    ] = uvicorn_settings.root_path,
    proxy_headers: Annotated[
        bool,
        typer.Option(
            help=(
                "Enable/Disable X-Forwarded-Proto, X-Forwarded-For, "
                "X-Forwarded-Port to populate remote address info."
            )
        ),
    ] = uvicorn_settings.proxy_headers,
    timeout_keep_alive: Annotated[
        int, typer.Option(help="Timeout for the server response.")
    ] = uvicorn_settings.timeout_keep_alive,
    ssl_certfile: Annotated[
        Path | None, typer.Option(help="SSL certificate file")
    ] = uvicorn_settings.ssl_certfile,
    ssl_keyfile: Annotated[
        Path | None, typer.Option(help="SSL key file")
    ] = uvicorn_settings.ssl_keyfile,
    ssl_keyfile_password: Annotated[
        str | None, typer.Option(help="SSL keyfile password")
    ] = uvicorn_settings.ssl_keyfile_password,
) -> Any:
    uvicorn_settings.host = host
    uvicorn_settings.port = port
    uvicorn_settings.reload = reload
    uvicorn_settings.root_path = root_path
    uvicorn_settings.proxy_headers = proxy_headers
    uvicorn_settings.timeout_keep_alive = timeout_keep_alive
    uvicorn_settings.ssl_certfile = ssl_certfile
    uvicorn_settings.ssl_keyfile = ssl_keyfile
    uvicorn_settings.ssl_keyfile_password = ssl_keyfile_password

    _run(command="dev")


@app.command()
def run(
    *,
    host: Annotated[
        str,
        typer.Option(
            help=(
                "The host to serve on. For local development in localhost "
                "use [blue]127.0.0.1[/blue]. To enable public access, "
                "e.g. in a container, use all the IP addresses "
                "available with [blue]0.0.0.0[/blue]."
            )
        ),
    ] = uvicorn_settings.host,
    port: Annotated[
        int,
        typer.Option(help="The port to serve on."),
    ] = uvicorn_settings.port,
    reload: Annotated[
        bool,
        typer.Option(
            help=(
                "Enable auto-reload of the server when (code) files change. "
                "This is [bold]resource intensive[/bold], "
                "use it only during development."
            )
        ),
    ] = uvicorn_settings.reload,
    workers: Annotated[
        int | None,
        typer.Option(
            help=(
                "Use multiple worker processes. "
                "Mutually exclusive with the --reload flag."
            )
        ),
    ] = uvicorn_settings.workers,
    root_path: Annotated[
        str,
        typer.Option(
            help=(
                "The root path is used to tell your app that it is being served "
                "to the outside world with some [bold]path prefix[/bold] "
                "set up in some termination proxy or similar."
            )
        ),
    ] = uvicorn_settings.root_path,
    proxy_headers: Annotated[
        bool,
        typer.Option(
            help=(
                "Enable/Disable X-Forwarded-Proto, X-Forwarded-For, "
                "X-Forwarded-Port to populate remote address info."
            )
        ),
    ] = uvicorn_settings.proxy_headers,
    timeout_keep_alive: Annotated[
        int, typer.Option(help="Timeout for the server response.")
    ] = uvicorn_settings.timeout_keep_alive,
    ssl_certfile: Annotated[
        Path | None, typer.Option(help="SSL certificate file")
    ] = uvicorn_settings.ssl_certfile,
    ssl_keyfile: Annotated[
        Path | None, typer.Option(help="SSL key file")
    ] = uvicorn_settings.ssl_keyfile,
    ssl_keyfile_password: Annotated[
        str | None, typer.Option(help="SSL keyfile password")
    ] = uvicorn_settings.ssl_keyfile_password,
) -> Any:
    uvicorn_settings.host = host
    uvicorn_settings.port = port
    uvicorn_settings.reload = reload
    uvicorn_settings.workers = workers
    uvicorn_settings.root_path = root_path
    uvicorn_settings.proxy_headers = proxy_headers
    uvicorn_settings.timeout_keep_alive = timeout_keep_alive
    uvicorn_settings.ssl_certfile = ssl_certfile
    uvicorn_settings.ssl_keyfile = ssl_keyfile
    uvicorn_settings.ssl_keyfile_password = ssl_keyfile_password

    _run(
        command="run",
    )


if __name__ == "__main__":
    main()
