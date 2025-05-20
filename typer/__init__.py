from __future__ import annotations

import inspect
from pathlib import Path
from typing import Any, Callable, Optional, Union, get_args, get_origin, Annotated
import types

import click
from click.testing import CliRunner


__all__ = ["Typer", "Option", "CliRunner"]


def Option(*_args: Any, **_kwargs: Any) -> None:
    """Placeholder for typer.Option."""
    return None


class Typer(click.Group):
    """Very small subset of Typer built on Click."""

    def __init__(self, name: str | None = None, **_kwargs: Any) -> None:
        super().__init__(name=name)

    def command(self, *d_args: Any, **d_kwargs: Any) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
        def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
            params = []
            sig = inspect.signature(func)
            for name, param in sig.parameters.items():
                if param.kind is not inspect.Parameter.KEYWORD_ONLY:
                    continue
                annotation = param.annotation
                origin = get_origin(annotation)
                if origin is Annotated:
                    annotation = get_args(annotation)[0]
                    origin = get_origin(annotation)
                if origin in {Union, types.UnionType} and type(None) in get_args(annotation):
                    annotation = next(a for a in get_args(annotation) if a is not type(None))
                if annotation is bool:
                    param_type = click.BOOL
                elif annotation is int:
                    param_type = click.INT
                elif annotation is Path:
                    param_type = click.Path(path_type=Path)
                else:
                    param_type = click.STRING
                option = click.Option(
                    [f"--{name.replace('_', '-')}"], default=param.default, type=param_type
                )
                params.append(option)
            cmd = click.Command(func.__name__, params=params, callback=func)
            self.add_command(cmd)
            return func

        return decorator

