from pydantic import BaseModel, ConfigDict


class StrictBaseModel(BaseModel, validate_assignment=True):
    """
    A simple subclass of ``BaseModel`` to reduce the repetition of common settings.
    This class sets both ``validate_assignment`` and ``strict`` within its ``model_config`` to ``True``,
    disabling type coercion and revalidating fields when their values are changed.
    """
    model_config = ConfigDict(strict=True)
