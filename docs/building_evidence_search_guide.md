# What building evidence to look for

We need one documented building case, not a large machine-learning dataset. Start with one building with two or more floors. A school, college, library, office or hospital can work. Three floors would help test additional cross-floor choices but is not a prerequisite.

| Evidence | Preferred format | Acceptable starting point |
| --- | --- | --- |
| Building geometry: rooms, floors, doors, stairs and lifts, with dimensions | IFC .ifc model plus source documentation | Dimensioned/scaled PDF floor plans for each relevant floor; DWG/DXF drawings are also worth sending for an extraction audit |
| Existing accessibility and barriers | PDF accessibility/access audit, dated and naming the building | An official survey/report with dimensions, observations and photos tied to locations on the plans |
| Proposed improvements and usable locations | PDF retrofit proposal or marked-up plans reviewed by an architect/facilities/accessibility professional | A report identifying specific changes and their locations; feasibility/permission gaps stay explicit |
| Intervention costs | Dated itemized estimate, bill of quantities or tender schedule in PDF/XLSX/CSV | Documented relative costs approved for the case; otherwise our prices remain abstract experimental assumptions |
| Provenance and reuse | Original download page, report author/date and license/permission information | Send the source URL with whatever documents you find; public availability alone does not establish redistribution rights |

IFC is a building-information model format. You do not need to learn it or convert files. JSON is our internal experiment format; I handle the conversion. If only an RVT model exists, a provider-exported IFC is preferable to requiring you to buy software. A PDF audit alone is useful as a lead even when plans still need to be found.

## Search terms to copy

```text
"access audit report" "floor plan" filetype:pdf
site:gov.in "access audit" "lift" filetype:pdf
site:ac.in "access audit" "building" filetype:pdf
"accessibility retrofit" "existing floor plans" filetype:pdf
"barrier removal plan" "floor plans" filetype:pdf
"building accessibility" "IFC" dataset
```

You can substitute your college, city or a named public building. Look on government, university, facilities-management and project-owner pages. Official audit/retrofit documentation for the SAME building as the plans is especially useful. Generic accessibility guidelines, attractive 3D renders, room photographs alone and unrelated geometry models do not supply case-specific intervention evidence.

A concrete example of the kind of document to look for is the [National Archives of India Annexe access-audit PDF](https://www.mohua.gov.in/upload/uploadfiles/files/National_Archives_Annexe.pdf). Its indexed excerpt discusses a ramp drawing and specific observations; it is a lead, not a selected/validated dataset. Full download access, complete floor coverage and reuse rights have not yet been audited. The [CHARUSAT PDPIAS access-audit link](https://www.charusat.ac.in/documents/pdfs/data/7/7-1-7/Access_Audit_PDPIAS.pdf) is another lead; its content and geometry coverage are not yet verified. Do not assume either is sufficient.

## What to send me

Send a few original URLs or the files you find. You do not need to assemble a perfect package, buy a dataset, contact anyone or enter data by hand. I will check whether the plans and audit refer to the same building, whether dimensions and floors are usable, what the evidence actually verifies, and what permissions/licensing are available.

For actual-building repair validation, each asserted permission, feasible intervention and price needs supporting evidence or qualified confirmation. An audit can document an existing barrier without proving that a proposed new lift is structurally feasible. If some evidence is missing, we can use the documented portions and label the rest as assumptions; that does not magically become a fully validated repair.

Our present licensed Clinic/Molio geometry remains useful for building-derived controlled experiments. Another geometry-only IFC adds breadth, but does not close the missing intervention-evidence gate. The literature assessment can proceed independently of any dataset you find.
