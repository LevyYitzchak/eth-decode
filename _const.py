from pathlib import Path
Path.ls = lambda x: list(x.iterdir())
import os

PATH_ABIS = Path("abis")
PATH_KEY = Path(".key/aragon-analytics-f4f193b8ab5f.json")
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = PATH_KEY.as_posix()

COLS_TO_DROP_EVENTS = [
"inputs",
"payable",
"stateMutability",
"type",
"anonymous",
"constant",
"outputs",
]


ADDRESS_COURT = "0xab647b8fd9e370448d4eeb96582fe839f3d0bb24"
FUNC_SIGN_GUARDIANS_ACTIVATED = "0x3bb1ff40e32fd6b2e3b81f6a7441852a5c72ec25d116b141b1a1a2e8f0404095"