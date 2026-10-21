import pytest
from anonymizer.cr_recognizers import recognizers

@pytest.mark.parametrize("entity,text",[("PHONE_NUMBER","8888-1234"),("PHONE_NUMBER","+506 8888 1234"),("PHONE_NUMBER","88881234"),("CR_NATIONAL_ID","Cédula 1-0999-0888"),("CR_NATIONAL_ID","identificación 109990888"),("CR_DIMEX","DIMEX 123456789012")])
def test_T11_T12_T13(entity,text):
    assert any(r.analyze(text,[entity]) for r in recognizers() if entity in r.supported_entities)

@pytest.mark.parametrize("text",["1100102","101","1","2026","125000","7","123456789","Código establecimiento: 123456789"])
def test_identifiers_need_context(text):
    for r in recognizers():
        assert not r.analyze(text,["CR_NATIONAL_ID","CR_DIMEX"])

def test_contextual_person_preserves_narrative():
    text="La madre María Rodríguez llamó al 8888-1234."
    r=next(r for r in recognizers() if r.supported_entities==["PERSON"])
    spans=r.analyze(text,["PERSON"])
    assert [text[s.start:s.end] for s in spans]==["María Rodríguez"]
