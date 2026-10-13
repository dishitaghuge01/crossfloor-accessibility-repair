class ValidationError(ValueError):
    """A deterministic, named failure of the instance or selection contract."""

    def __init__(self, code: str, detail: str):
        self.code = code
        super().__init__(f"{code}: {detail}")


def require(condition: bool, code: str, detail: str) -> None:
    if not condition:
        raise ValidationError(code, detail)
