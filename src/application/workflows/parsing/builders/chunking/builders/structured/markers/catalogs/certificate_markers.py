from src.application.workflows.parsing.builders.chunking.builders.structured.markers.models import (
    EvidenceMarker,
    MarkerStrength,
)


CERTIFICATE_DOCUMENT_MARKERS = (
    EvidenceMarker("certificate", MarkerStrength.MEDIUM),
    EvidenceMarker("certificate of conformity", MarkerStrength.STRONG),
    EvidenceMarker("inspection certificate", MarkerStrength.STRONG),
    EvidenceMarker("test certificate", MarkerStrength.STRONG),
    EvidenceMarker("type approval certificate", MarkerStrength.STRONG),
    EvidenceMarker("approval certificate", MarkerStrength.STRONG),
    EvidenceMarker("material certificate", MarkerStrength.STRONG),
    EvidenceMarker("calibration certificate", MarkerStrength.STRONG),
    EvidenceMarker("certificate number", MarkerStrength.MEDIUM),
)


CERTIFICATE_COVER_SHEET_MARKERS = (
    EvidenceMarker("cover sheet", MarkerStrength.STRONG),
    EvidenceMarker("certificate number", MarkerStrength.MEDIUM),
    EvidenceMarker("certificate no", MarkerStrength.MEDIUM),
    EvidenceMarker("certificate type", MarkerStrength.MEDIUM),
    EvidenceMarker("customer", MarkerStrength.WEAK),
    EvidenceMarker("project", MarkerStrength.WEAK),
    EvidenceMarker("model", MarkerStrength.WEAK),
    EvidenceMarker("series", MarkerStrength.WEAK),
    EvidenceMarker("revision", MarkerStrength.WEAK),
    EvidenceMarker("edition", MarkerStrength.WEAK),
    EvidenceMarker("order number", MarkerStrength.MEDIUM),
    EvidenceMarker("order no", MarkerStrength.MEDIUM),
    EvidenceMarker("issue date", MarkerStrength.MEDIUM),
    EvidenceMarker("date of issue", MarkerStrength.MEDIUM),
)


CERTIFICATE_GENERAL_INFORMATION_MARKERS = (
    EvidenceMarker("general information", MarkerStrength.MEDIUM),
    EvidenceMarker("certificate information", MarkerStrength.STRONG),
    EvidenceMarker("manufacturer", MarkerStrength.MEDIUM),
    EvidenceMarker("manufacturer name", MarkerStrength.MEDIUM),
    EvidenceMarker("certificate number", MarkerStrength.STRONG),
    EvidenceMarker("certificate no", MarkerStrength.STRONG),
    EvidenceMarker("purchase order", MarkerStrength.MEDIUM),
    EvidenceMarker("purchase order number", MarkerStrength.MEDIUM),
    EvidenceMarker("order number", MarkerStrength.MEDIUM),
    EvidenceMarker("customer work order", MarkerStrength.MEDIUM),
    EvidenceMarker("intended for", MarkerStrength.MEDIUM),
    EvidenceMarker("date of issue", MarkerStrength.MEDIUM),
    EvidenceMarker("issue date", MarkerStrength.MEDIUM),
    EvidenceMarker("valid from", MarkerStrength.MEDIUM),
    EvidenceMarker("valid until", MarkerStrength.MEDIUM),
    EvidenceMarker("expiry date", MarkerStrength.MEDIUM),
    EvidenceMarker("customer", MarkerStrength.WEAK),
)


CERTIFICATE_ATTACHMENT_INFORMATION_MARKERS = (
    EvidenceMarker("certificate attachment", MarkerStrength.STRONG),
    EvidenceMarker("attachment", MarkerStrength.MEDIUM),
    EvidenceMarker("annex", MarkerStrength.MEDIUM),
    EvidenceMarker("inspection scope", MarkerStrength.STRONG),
    EvidenceMarker("scope of inspection", MarkerStrength.STRONG),
    EvidenceMarker("areas inspected", MarkerStrength.STRONG),
    EvidenceMarker("areas/facilities inspected", MarkerStrength.STRONG),
    EvidenceMarker("facilities inspected", MarkerStrength.STRONG),
    EvidenceMarker("food", MarkerStrength.WEAK),
    EvidenceMarker("water", MarkerStrength.WEAK),
    EvidenceMarker("waste", MarkerStrength.WEAK),
    EvidenceMarker("swimming pools", MarkerStrength.MEDIUM),
    EvidenceMarker("medical facilities", MarkerStrength.MEDIUM),
)


CERTIFICATE_PARTICULARS_MARKERS = (
    EvidenceMarker("particulars", MarkerStrength.MEDIUM),
    EvidenceMarker("equipment particulars", MarkerStrength.STRONG),
    EvidenceMarker("product particulars", MarkerStrength.STRONG),
    EvidenceMarker("item particulars", MarkerStrength.STRONG),
    EvidenceMarker("quantity", MarkerStrength.WEAK),
    EvidenceMarker("nominal size", MarkerStrength.MEDIUM),
    EvidenceMarker("size", MarkerStrength.WEAK),
    EvidenceMarker("equipment type", MarkerStrength.MEDIUM),
    EvidenceMarker("product type", MarkerStrength.MEDIUM),
    EvidenceMarker("type", MarkerStrength.WEAK),
    EvidenceMarker("manufacturer designation", MarkerStrength.STRONG),
    EvidenceMarker("manufacturer", MarkerStrength.MEDIUM),
    EvidenceMarker("serial number", MarkerStrength.MEDIUM),
    EvidenceMarker("serial no", MarkerStrength.MEDIUM),
    EvidenceMarker("imo number", MarkerStrength.MEDIUM),
    EvidenceMarker("imo no", MarkerStrength.MEDIUM),
    EvidenceMarker("model number", MarkerStrength.MEDIUM),
    EvidenceMarker("model no", MarkerStrength.MEDIUM),
    EvidenceMarker("description", MarkerStrength.WEAK),
)


CERTIFICATE_COMPLIANCE_INFORMATION_MARKERS = (
    EvidenceMarker("certificate of conformity", MarkerStrength.STRONG),
    EvidenceMarker("declaration of conformity", MarkerStrength.STRONG),
    EvidenceMarker("statement of conformity", MarkerStrength.STRONG),
    EvidenceMarker("compliance statement", MarkerStrength.STRONG),
    EvidenceMarker("compliance", MarkerStrength.MEDIUM),
    EvidenceMarker("conformity", MarkerStrength.MEDIUM),
    EvidenceMarker("classification society", MarkerStrength.STRONG),
    EvidenceMarker("applicable standard", MarkerStrength.STRONG),
    EvidenceMarker("applicable standards", MarkerStrength.STRONG),
    EvidenceMarker("applicable directive", MarkerStrength.STRONG),
    EvidenceMarker("applicable regulation", MarkerStrength.STRONG),
    EvidenceMarker("complies with", MarkerStrength.STRONG),
    EvidenceMarker("in accordance with", MarkerStrength.MEDIUM),
    EvidenceMarker("directive", MarkerStrength.MEDIUM),
    EvidenceMarker("regulation", MarkerStrength.MEDIUM),
    EvidenceMarker("standard", MarkerStrength.WEAK),
    EvidenceMarker("approved", MarkerStrength.WEAK),
)


CERTIFICATE_APPROVAL_INFORMATION_MARKERS = (
    EvidenceMarker("type approval", MarkerStrength.STRONG),
    EvidenceMarker("type approval certificate", MarkerStrength.STRONG),
    EvidenceMarker("approval certificate", MarkerStrength.STRONG),
    EvidenceMarker("approval number", MarkerStrength.MEDIUM),
    EvidenceMarker("approval no", MarkerStrength.MEDIUM),
    EvidenceMarker("approval", MarkerStrength.MEDIUM),
    EvidenceMarker("certificate of conformity", MarkerStrength.STRONG),
    EvidenceMarker("conformity assessment", MarkerStrength.STRONG),
    EvidenceMarker("atex", MarkerStrength.STRONG),
    EvidenceMarker("iecex", MarkerStrength.STRONG),
    EvidenceMarker("atex certificate", MarkerStrength.STRONG),
    EvidenceMarker("iecex certificate", MarkerStrength.STRONG),
    EvidenceMarker("explosion protection", MarkerStrength.STRONG),
    EvidenceMarker("hazardous area", MarkerStrength.MEDIUM),
    EvidenceMarker("equipment protection level", MarkerStrength.STRONG),
    EvidenceMarker("epl", MarkerStrength.MEDIUM),
    EvidenceMarker("ex ia", MarkerStrength.STRONG),
    EvidenceMarker("ex ib", MarkerStrength.STRONG),
    EvidenceMarker("ex ic", MarkerStrength.STRONG),
    EvidenceMarker("ex d", MarkerStrength.STRONG),
    EvidenceMarker("ex e", MarkerStrength.STRONG),
    EvidenceMarker("ex n", MarkerStrength.STRONG),
    EvidenceMarker("certified", MarkerStrength.WEAK),
)


CERTIFICATE_TEST_DATA_MARKERS = (
    EvidenceMarker("test data", MarkerStrength.STRONG),
    EvidenceMarker("test results", MarkerStrength.STRONG),
    EvidenceMarker("inspection results", MarkerStrength.STRONG),
    EvidenceMarker("test pressure", MarkerStrength.STRONG),
    EvidenceMarker("hydrostatic test", MarkerStrength.STRONG),
    EvidenceMarker("hydrostatic test pressure", MarkerStrength.STRONG),
    EvidenceMarker("pressure test", MarkerStrength.STRONG),
    EvidenceMarker("design pressure", MarkerStrength.MEDIUM),
    EvidenceMarker("working pressure", MarkerStrength.MEDIUM),
    EvidenceMarker("maximum allowable working pressure", MarkerStrength.STRONG),
    EvidenceMarker("inspection result", MarkerStrength.STRONG),
    EvidenceMarker("acceptance criteria", MarkerStrength.STRONG),
    EvidenceMarker("acceptance result", MarkerStrength.STRONG),
    EvidenceMarker("nominal value", MarkerStrength.MEDIUM),
    EvidenceMarker("actual value", MarkerStrength.MEDIUM),
    EvidenceMarker("measured value", MarkerStrength.MEDIUM),
    EvidenceMarker("reference value", MarkerStrength.MEDIUM),
    EvidenceMarker("soll/nominal", MarkerStrength.MEDIUM),
    EvidenceMarker("ist/result", MarkerStrength.MEDIUM),
    EvidenceMarker("messdaten", MarkerStrength.STRONG),
    EvidenceMarker("pass", MarkerStrength.WEAK),
    EvidenceMarker("fail", MarkerStrength.WEAK),
    EvidenceMarker("results", MarkerStrength.WEAK),
)