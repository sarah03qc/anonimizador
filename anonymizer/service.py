from time import perf_counter
from collections import Counter
from . import workbook
from .column_analyzer import analyze_column
from .models import Analysis,Result,KINDS
from .presidio_engine import Detector
from .replacement import Replacer
from .review import validate_confirmation, validation_errors, ReviewError, TO_ENGINE, COMPLETE

class Service:
    def __init__(self,ner): self.ner=ner
    def analyze(self,data,filename,header_rows=None,progress=None):
        start=perf_counter(); wb=workbook.load(data,filename); headers=workbook.headers_for(wb,header_rows)
        detector=Detector(self.ner); columns=[]
        try:
            total=sum(ws.max_column for ws in wb)
            for ws in wb:
                h=headers[ws.title]
                for i in range(1,ws.max_column+1):
                    header=str(ws.cell(h,i).value or "")
                    vals=[ws.cell(r,i).value for r in range(h+1,ws.max_row+1) if ws.cell(r,i).data_type!="f"]
                    columns.append(analyze_column(detector,ws.title,i,header,vals))
                    if progress: progress(len(columns)/max(1,total))
            return Analysis(columns,perf_counter()-start,len(wb.worksheets),sum(max(0,ws.max_row-headers[ws.title]) for ws in wb),["Las fórmulas se conservan y Excel deberá recalcularlas. Encabezados y nombres de hojas requieren revisión."])
        finally:
            detector.clear(); wb.close()

    def anonymize_reviewed(self,data,filename,plan,progress=None):
        """UI entry point: a complete, explicit review bound to this workbook."""
        validate_confirmation(plan,data)
        wb=workbook.load(data,filename)
        try:
            supplied=dict(plan.header_rows)
            if len(supplied)!=len(plan.header_rows) or set(supplied)!=set(wb.sheetnames):
                raise ReviewError("Revise las filas de encabezados de todas las hojas.")
            headers=workbook.headers_for(wb,supplied)
            errors=validation_errors(plan.decisions,[(ws.title,i) for ws in wb for i in range(1,ws.max_column+1)])
            if errors:raise ReviewError(errors[0])
            if headers!=supplied:raise ReviewError("Las filas de encabezados cambiaron. Vuelva a confirmar.")
        finally:wb.close()
        # Release validation cells before the substitution engine opens its copy.
        del wb
        selections={r.key:TO_ENGINE[r.kind] for r in plan.decisions if r.selected}
        strategies={r.key:r.method for r in plan.decisions if r.selected}
        return self.anonymize(data,filename,selections,headers,progress,strategies)

    def anonymize(self,data,filename,selections,header_rows=None,progress=None,strategies=None):
        # Retained low-level API for existing integrations. The UI requires reviewed plans.
        start=perf_counter(); wb=workbook.load(data,filename); headers=workbook.headers_for(wb,header_rows)
        replacer=Replacer(); detector=Detector(self.ner); counts=Counter(); changed=0; sheets=set()
        try:
            for (sheet,col),kind in selections.items():
                if sheet not in wb.sheetnames or not isinstance(col,int) or not 1<=col<=wb[sheet].max_column or kind not in KINDS:
                    raise workbook.WorkbookError("La selección de columnas no es válida. Vuelva a analizar el archivo.")
                if kind in ("Institucional","No determinado"):
                    raise workbook.WorkbookError("Asigne un tipo de sustitución a todas las columnas seleccionadas.")
            # Register compatible known values so names remain consistent inside notes.
            for (sheet,col),kind in selections.items():
                if kind=="Persona":
                    for row in wb[sheet].iter_rows(min_row=headers[sheet]+1,min_col=col,max_col=col):
                        c=row[0]
                        if c.value is not None and c.data_type!="f": replacer.remember(c.value,kind)
            total=len(selections)
            for n,((sheet,col),kind) in enumerate(selections.items(),1):
                ws=wb[sheet]; cells=[row[0] for row in ws.iter_rows(min_row=headers[sheet]+1,min_col=col,max_col=col) if row[0].value is not None and row[0].data_type!="f" and not (isinstance(row[0].value,str) and not row[0].value.strip())]
                if kind=="Texto con PII" and (strategies or {}).get((sheet,col))==COMPLETE:
                    for c in cells:
                        if isinstance(c.value,str) and not c.value.strip():continue
                        c.value="[CONTENIDO ANONIMIZADO]"; changed+=1; counts["Texto libre — contenido completo"]+=1; sheets.add(sheet)
                elif kind=="Texto con PII":
                    # Bounded chunks avoid materializing inference for a whole workbook.
                    for offset in range(0,len(cells),64):
                        batch=cells[offset:offset+64]
                        spans=detector.batch([str(c.value) for c in batch])
                        for c,entities in zip(batch,spans):
                            value=replacer.text(str(c.value),entities)
                            if value!=c.value: c.value=value; changed+=1; counts[kind]+=1; sheets.add(sheet)
                        detector.clear()
                else:
                    for c in cells:
                        if isinstance(c.value,str) and not c.value.strip(): continue
                        c.value=replacer.value(c.value,kind); changed+=1; counts[kind]+=1; sheets.add(sheet)
                if progress: progress(n/max(1,total))
            return Result(workbook.export(wb),workbook.output_name(filename),perf_counter()-start,changed,len(selections),len(sheets),dict(counts))
        finally:
            replacer.clear(); detector.clear(); wb.close()
