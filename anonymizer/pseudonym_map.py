import re
import unicodedata

def canonical(value,kind):
    s=" ".join(unicodedata.normalize("NFKC",str(value)).casefold().split())
    if kind=="Teléfono":
        s=re.sub(r"\D","",s)
        if len(s)==11 and s.startswith("506"): s=s[3:]
    return s

class PseudonymMap:
    def __init__(self): self.values={}; self.used={}
    def get(self,value,kind,generate):
        key=(kind,canonical(value,kind))
        if key not in self.values:
            replacement=generate()
            for _ in range(25):
                if canonical(replacement,kind)!=key[1] and (kind=="Fecha personal" or (kind,str(replacement)) not in self.used): break
                replacement=generate()
            else: replacement=f"{replacement} [PRUEBA-{len(self.values)+1}]"
            self.values[key]=replacement; self.used[kind,str(replacement)]=True
        return self.values[key]
    def clear(self): self.values.clear(); self.used.clear()
