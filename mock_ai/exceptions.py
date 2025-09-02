from fastapi import HTTPException


class ModelNotFound(HTTPException):
    def __init__(self, model_name: str):
        super().__init__(
            status_code=404, detail=f"Model `{model_name}` not found"
        )


class ModelTypeError(HTTPException):
    def __init__(self, model_name: str, expected_type: str):
        super().__init__(
            status_code=422,
            detail=f"Model `{model_name}` is not a {expected_type} model",
        )


class FileNotFound(HTTPException):
    def __init__(self):
        super().__init__(status_code=404, detail="File not found")
