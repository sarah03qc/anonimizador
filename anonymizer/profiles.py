"""Static, exact-header defaults. Profiles never confirm human review."""
from dataclasses import dataclass,replace
from pathlib import Path
import yaml
from .header_analyzer import normalize
from .review import REVIEW_TYPES,METHODS,PENDING,PRESERVE,default_method,ReviewError

@dataclass(frozen=True)
class Profile:
    name:str
    description:str
    required_headers:tuple
    rules:tuple

def load_profile(path):
    try:
        source=Path(path)
        if source.stat().st_size>100000:raise ValueError()
        data=yaml.safe_load(source.read_text(encoding="utf-8"))
        if not isinstance(data,dict) or not isinstance(data.get("name"),str) or not isinstance(data.get("rules"),list):raise ValueError()
        rules=[];seen=set()
        for rule in data["rules"]:
            header=rule["header"];action=rule["action"];kind=rule.get("type","Conservar");method=rule.get("method",default_method(kind));sheet=rule.get("sheet","*")
            if not isinstance(header,str) or not isinstance(sheet,str) or action not in ("anonymize","preserve") or kind not in REVIEW_TYPES or method not in METHODS:raise ValueError()
            key=sheet,normalize(header)
            if key in seen:raise ValueError()
            seen.add(key);rules.append((sheet,normalize(header),action,kind,method))
        required=data.get("required_headers",[])
        if not isinstance(required,list) or not all(isinstance(h,str) for h in required):raise ValueError()
        return Profile(data["name"],str(data.get("description","")),tuple(normalize(h) for h in required),tuple(rules))
    except Exception:
        raise ReviewError("No fue posible cargar el perfil. Revise su estructura y sus tipos o métodos.") from None

def suggest_profiles(columns,profiles):
    headers={normalize(c.header) for c in columns}
    return [p for p in profiles if p.required_headers and set(p.required_headers)<=headers]

def apply_profile(rows,profile):
    result=[]
    for row in rows:
        matches=[r for r in profile.rules if r[0] in ("*",row.sheet) and r[1]==normalize(row.header)]
        if not matches:result.append(row);continue
        # Sheet-specific exact rule has precedence over a wildcard.
        rule=next((r for r in matches if r[0]==row.sheet),matches[0])
        _,_,action,kind,method=rule;selected=action=="anonymize"
        result.append(replace(row,selected=selected,kind=kind,method=method if selected else PRESERVE,resolution=PENDING if row.automatic_state=="Revisar" else "Anonimizar" if selected else PRESERVE,source="Perfil: "+profile.name))
    return result
