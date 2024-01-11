from typing import Literal

from pydantic import RootModel


class Ok(RootModel):
    root: Literal["ok"] = "ok"
