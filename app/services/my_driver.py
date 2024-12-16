from typing import TypedDict, Callable

class d(TypedDict):
    a:str
    b:str

type c = Callable[[**d], None]

def dd(**test:d):
    pass

import nodriver as uc
d = {'a':'a','b':'b'}


