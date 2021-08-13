from pathlib import Path
Path.ls = lambda x: list(x.iterdir())
import os

PATH_ABIS = Path("abis")
PATH_KEY = Path(".key/aragon-analytics-f4f193b8ab5f.json")

COLS_TO_DROP_EVENTS = [
"inputs",
"payable",
"stateMutability",
"type",
"anonymous",
"constant",
"outputs",
]


os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = PATH_KEY.as_posix()
