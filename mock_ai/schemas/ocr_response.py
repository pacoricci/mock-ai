from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field, model_validator

# --- Leaf types --------------------------------------------------------------


class Dimensions(BaseModel):
    """Physical/rendering dimensions of a page/image."""

    model_config = ConfigDict(frozen=True, extra="ignore")

    dpi: int = 0
    height: int = 0
    width: int = 0


class ImageRegion(BaseModel):
    """
    An embedded image on a page, optionally with a base64 payload.
    Coordinates are given in page-pixel space.
    """

    model_config = ConfigDict(frozen=True, extra="ignore")

    id: str
    top_left_x: int = 0
    top_left_y: int = 0
    bottom_right_x: int = 0
    bottom_right_y: int = 0
    image_base64: str | None = None


# --- Aggregates --------------------------------------------------------------


class Page(BaseModel):
    """A single page of the document."""

    model_config = ConfigDict(frozen=True, extra="ignore")

    index: int = 0
    markdown: str = ""
    dimensions: Dimensions = Field(default_factory=Dimensions)
    images: list[ImageRegion] = Field(default_factory=list)

    @model_validator(mode="before")
    @classmethod
    def _filter_images_without_id(cls, data: Any) -> Any:
        """
        Tolerate dicts that might be empty or missing an id, as in the original dataclass logic.
        Unknown keys are ignored due to `extra="ignore"`.
        """
        if isinstance(data, dict):
            imgs = data.get("images")
            if isinstance(imgs, list):
                data["images"] = [
                    img
                    for img in imgs
                    if isinstance(img, dict) and img.get("id") is not None
                ]
        return data


class Document(BaseModel):
    """Root container holding all pages."""

    model_config = ConfigDict(frozen=True, extra="ignore")

    pages: list[Page] = Field(default_factory=list)

    # -------- Convenience constructors --------

    @staticmethod
    def from_dict(data: dict[str, Any]) -> Document:
        """
        Build a Document from a dict shaped like the provided JSON.
        Unknown keys are ignored; missing optional fields default sensibly.
        """
        return Document.model_validate(data)

    def to_dict(self) -> dict[str, Any]:
        """Serialize back to a plain-JSON-able dict (omit None fields)."""
        return self.model_dump(exclude_none=True)
