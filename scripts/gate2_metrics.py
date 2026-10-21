"""One-to-one span evaluation. QA only, no production user data."""
ALIASES={
 "PERSON":"PERSON","FIRSTNAME":"PERSON","LASTNAME":"PERSON","MIDDLENAME":"PERSON","GIVENNAME":"PERSON","SURNAME":"PERSON","PREFIX":"PERSON","TITLE":"PERSON",
 "EMAIL":"EMAIL","EMAIL_ADDRESS":"EMAIL",
 "PHONE":"PHONE","PHONE_NUMBER":"PHONE","TEL":"PHONE","TELEPHONENUM":"PHONE",
 "ID":"ID","CR_NATIONAL_ID":"ID","CR_DIMEX":"ID","SSN":"ID","IDCARD":"ID","IDCARDNUM":"ID","SOCIALNUM":"ID","SOCIALNUMBER":"ID","DRIVERLICENSE":"ID","DRIVERLICENSENUM":"ID","PASSPORT":"ID","TAXNUM":"ID","IMEI":"ID","VIN":"ID","VRM":"ID","MASKEDNUMBER":"ID",
 "DATE":"DATE","DATEOFBIRTH":"DATE","DATE_OF_BIRTH":"DATE","BOD":"DATE",
 "LOCATION":"LOCATION","STREET":"LOCATION","STREET_ADDRESS":"LOCATION","CITY":"LOCATION","STATE":"LOCATION","COUNTY":"LOCATION","COUNTRY":"LOCATION","ZIPCODE":"LOCATION","POSTCODE":"LOCATION","SECONDARYADDRESS":"LOCATION","SECADDRESS":"LOCATION","BUILDING":"LOCATION","BUILDINGNUM":"LOCATION","BUILDINGNUMBER":"LOCATION","GPSCOORDINATES":"LOCATION","GEOCOORD":"LOCATION",
 "USERNAME":"USERNAME","ACCOUNTNAME":"USERNAME",
 "PASSWORD":"CREDENTIAL","PASS":"CREDENTIAL","PIN":"CREDENTIAL","CREDENTIAL":"CREDENTIAL",
 "BANKACCOUNT":"FINANCIAL","ACCOUNTNUM":"FINANCIAL","IBAN":"FINANCIAL","CREDITCARD":"FINANCIAL","CREDITCARDNUMBER":"FINANCIAL","CREDIT_CARD":"FINANCIAL","CREDITCARDISSUER":"FINANCIAL","CARDISSUER":"FINANCIAL","CVV":"FINANCIAL","BIC":"FINANCIAL","BITCOINADDRESS":"FINANCIAL","ETHEREUMADDRESS":"FINANCIAL","LITECOINADDRESS":"FINANCIAL","FINANCIAL":"FINANCIAL",
 "IP":"IP","IPADDRESS":"IP","IP_ADDRESS":"IP","MACADDRESS":"IP",
 "URL":"CREDENTIAL","USERAGENT":"CREDENTIAL",
}
CONTEXT_ONLY={"AGE","AMOUNT","CURRENCY","CURRENCYCODE","CURRENCYNAME","CURRENCYSYMBOL","EYECOLOR","GENDER","HEIGHT","JOBDEPARTMENT","JOBTITLE","OCCUPATION","ORDINALDIRECTION","ORGANIZATION","SEX","TIME"}

def base(label):return label[2:] if label.startswith(("B-","I-")) else label
def canonical(label):return ALIASES.get(base(label),base(label))

def normalize_predictions(text,predictions,threshold=0.0):
    result=[]
    for p in predictions:
        raw=base(p.get("entity_group",p.get("entity",p.get("label","O"))))
        if raw=="O" or raw in CONTEXT_ONLY or p["score"]<threshold:continue
        if raw not in ALIASES:raise ValueError("Unmapped QA label: "+raw)
        result.append({"start":int(p["start"]),"end":int(p["end"]),"type":ALIASES[raw],"score":float(p["score"]),"label":raw})
    result.sort(key=lambda p:(p["start"],p["end"]))
    merged=[]
    for p in result:
        if merged and p["type"]==merged[-1]["type"]=="PERSON" and p["start"]>=merged[-1]["end"] and not text[merged[-1]["end"]:p["start"]].strip():
            merged[-1]={**merged[-1],"end":p["end"],"score":min(merged[-1]["score"],p["score"])}
        else:merged.append(p.copy())
    return merged

def expected(case):
    if isinstance(case["entities"],list) and case["entities"] and isinstance(case["entities"][0],list):
        return [{"start":a,"end":b,"type":canonical(t)} for a,b,t in case["entities"]]
    return [{**p,"type":canonical(p["type"])} for p in case["entities"]]

def metric(tp,fp,fn):
    p=tp/(tp+fp) if tp+fp else 0.;r=tp/(tp+fn) if tp+fn else 0.
    return {"tp":tp,"fp":fp,"fn":fn,"precision":p,"recall":r,"f1":2*p*r/(p+r) if p+r else 0.}

def match_counts(gold,pred,mode="strict",aware=True):
    graph=[]
    for p in pred:
        edges=[]
        for i,g in enumerate(gold):
            if aware and p["type"]!=g["type"]:continue
            overlap=max(0,min(p["end"],g["end"])-max(p["start"],g["start"]))
            union=max(p["end"],g["end"])-min(p["start"],g["start"])
            iou=overlap/union if union else 0
            eligible=(p["start"]==g["start"] and p["end"]==g["end"]) if mode=="strict" else iou>=.5 if mode=="iou50" else overlap>0
            if eligible:edges.append((iou,i))
        graph.append([i for _,i in sorted(edges,reverse=True)])
    assigned={}
    def augment(j,seen):
        for i in graph[j]:
            if i in seen:continue
            seen.add(i)
            if i not in assigned or augment(assigned[i],seen):assigned[i]=j;return True
        return False
    tp=sum(augment(j,set()) for j in range(len(pred)))
    return tp,len(pred)-tp,len(gold)-tp

def evaluate(cases,predictions):
    result={}
    for mode in ("strict","iou50","overlap"):
        for aware in (True,False):
            sums=[0,0,0]
            for c,p in zip(cases,predictions):
                counts=match_counts(expected(c),p,mode,aware)
                sums=[a+b for a,b in zip(sums,counts)]
            result[mode+("_type_aware" if aware else "_type_agnostic")]=metric(*sums)
    per={}
    for typ in sorted({g["type"] for c in cases for g in expected(c)}|{p["type"] for group in predictions for p in group}):
        sums=[0,0,0]
        for c,p in zip(cases,predictions):
            counts=match_counts([g for g in expected(c) if g["type"]==typ],[g for g in p if g["type"]==typ])
            sums=[a+b for a,b in zip(sums,counts)]
        per[typ]=metric(*sums)
    result["per_entity_strict"]=per
    return result
