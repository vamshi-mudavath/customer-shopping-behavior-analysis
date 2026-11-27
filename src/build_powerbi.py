"""Generate the Power BI project (powerbi/*.pbip) for the shopping-behaviour dashboard.

The report layout follows the dashboard in Amlan Mohanty's tutorial (MIT License), stored in
src/powerbi_template/. This script connects it to this repository's data model:
  * semantic model (model.bim) that imports data/processed/customer_shopping_clean.csv
  * DAX measures: Total Revenue, Number of Customers, Average Purchase Amount, Average Review Rating
  * report (report.json) with a Total Revenue KPI added to the card row

Open powerbi/Customer Shopping Behavior.pbip in Power BI Desktop.

    python src/build_powerbi.py ["C:\\path\\to\\repo\\data\\processed"]
"""
import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TEMPLATE = ROOT / "src" / "powerbi_template"
NAME = "Customer Shopping Behavior"
OUT = ROOT / "powerbi"
DATA_FOLDER = sys.argv[1] if len(sys.argv) > 1 else r"C:\Users\vamsh\Downloads\customer-shopping-behavior-analysis\data\processed"
T = "customer"  # table name, same as in the SQL step

# (column, data type, summarize by, M type)
COLUMNS = [
    ("customer_id", "int64", "none", "Int64.Type"),
    ("age", "int64", "none", "Int64.Type"),
    ("gender", "string", "none", "type text"),
    ("item_purchased", "string", "none", "type text"),
    ("category", "string", "none", "type text"),
    ("purchase_amount", "int64", "sum", "Int64.Type"),
    ("location", "string", "none", "type text"),
    ("size", "string", "none", "type text"),
    ("color", "string", "none", "type text"),
    ("season", "string", "none", "type text"),
    ("review_rating", "double", "none", "type number"),
    ("subscription_status", "string", "none", "type text"),
    ("shipping_type", "string", "none", "type text"),
    ("discount_applied", "string", "none", "type text"),
    ("previous_purchases", "int64", "none", "Int64.Type"),
    ("payment_method", "string", "none", "type text"),
    ("frequency_of_purchases", "string", "none", "type text"),
    ("age_group", "string", "none", "type text"),
    ("purchase_frequency_days", "int64", "none", "Int64.Type"),
    ("customer_segment", "string", "none", "type text"),
    ("age_group_order", "int64", "none", None),   # added in Power Query for sorting
    ("season_order", "int64", "none", None),
]
SORT_BY = {"age_group": "age_group_order", "season": "season_order"}

MEASURES = [
    ("Total Revenue", f"SUM({T}[purchase_amount])", "\\$#,0"),
    ("Number of Customers", f"DISTINCTCOUNT({T}[customer_id])", "#,0"),
    ("Average Purchase Amount", f"AVERAGE({T}[purchase_amount])", "\\$#,0.00"),
    ("Average Review Rating", f"AVERAGE({T}[review_rating])", "0.00"),
    ("Subscription Rate", f'DIVIDE(CALCULATE(COUNTROWS({T}), {T}[subscription_status] = "Yes"), COUNTROWS({T}))', "0.0%"),
    ("Discount Rate", f'DIVIDE(CALCULATE(COUNTROWS({T}), {T}[discount_applied] = "Yes"), COUNTROWS({T}))', "0.0%"),
]

M_TYPES = ", ".join(f'{{"{c}", {mt}}}' for c, _, _, mt in COLUMNS if mt)
M_QUERY = [
    "let",
    '    Source = Csv.Document(File.Contents(DataFolder & "\\customer_shopping_clean.csv"), [Delimiter = ",", Columns = 20, Encoding = 65001, QuoteStyle = QuoteStyle.Csv]),',
    "    Promoted = Table.PromoteHeaders(Source, [PromoteAllScalars = true]),",
    f'    Typed = Table.TransformColumnTypes(Promoted, {{{M_TYPES}}}, "en-US"),',
    '    AgeOrder = Table.AddColumn(Typed, "age_group_order", each List.PositionOf({"Young Adult", "Adult", "Middle-aged", "Senior"}, [age_group]) + 1, Int64.Type),',
    '    SeasonOrder = Table.AddColumn(AgeOrder, "season_order", each List.PositionOf({"Spring", "Summer", "Fall", "Winter"}, [season]) + 1, Int64.Type)',
    "in",
    "    SeasonOrder",
]


def model_bim():
    cols = []
    for name, dtype, summ, _ in COLUMNS:
        c = {"name": name, "dataType": dtype, "sourceColumn": name, "summarizeBy": summ}
        if name in SORT_BY:
            c["sortByColumn"] = SORT_BY[name]
        if name.endswith("_order"):
            c["isHidden"] = True
        cols.append(c)
    return {
        "compatibilityLevel": 1567,
        "model": {
            "culture": "en-US",
            "dataAccessOptions": {"legacyRedirects": True, "returnErrorValuesAsNull": True},
            "defaultPowerBIDataSourceVersion": "powerBI_V3",
            "sourceQueryCulture": "en-US",
            "tables": [{
                "name": T,
                "columns": cols,
                "partitions": [{"name": T, "mode": "import", "source": {"type": "m", "expression": M_QUERY}}],
                "measures": [{"name": n, "expression": e, "formatString": f} for n, e, f in MEASURES],
            }],
            "expressions": [{
                "name": "DataFolder",
                "kind": "m",
                "expression": [f'"{DATA_FOLDER}" meta [IsParameterQuery = true, Type = "Text", IsParameterQueryRequired = true]'],
                "annotations": [{"name": "PBI_ResultType", "value": "Text"}],
            }],
            "annotations": [
                {"name": "PBI_QueryOrder", "value": json.dumps(["DataFolder", T])},
                {"name": "__PBI_TimeIntelligenceEnabled", "value": "0"},
            ],
        },
    }


def report_json():
    layout = json.loads((TEMPLATE / "report_layout_template.json").read_text(encoding="utf-8"))
    # point every visual at this model's table
    text = json.dumps(layout).replace("public customer", T)
    # replace the pink theme colour (data colour 5, #E044A7) used by the header banner and the
    # donut's "No" slice with a lighter tint of the theme blue (data colour 1, #118DFF)
    text = text.replace('\\"ColorId\\":6,\\"Percent\\":0.2', '\\"ColorId\\":2,\\"Percent\\":0.3')
    layout = json.loads(text)
    for v in layout["sections"][0]["visualContainers"]:
        cfg = json.loads(v["config"])
        sv = cfg.get("singleVisual") or {}
        if sv.get("visualType") == "cardVisual":
            # add Total Revenue as the first KPI in the card row
            sel = {"Measure": {"Expression": {"SourceRef": {"Source": "p"}}, "Property": "Total Revenue"},
                   "Name": f"{T}.Total Revenue", "NativeReferenceName": "Total Revenue"}
            sv["prototypeQuery"]["Select"].insert(0, sel)
            sv["projections"]["Data"].insert(0, {"queryRef": f"{T}.Total Revenue"})
            v["config"] = json.dumps(cfg)
        if sv.get("visualType") == "advancedSlicerVisual" and \
                sv["projections"]["Values"][0]["queryRef"] == f"{T}.category":
            # four stacked button tiles are too short for the labels; use a list slicer instead
            sv["visualType"] = "listSlicer"
            sv.pop("objects", None)
            v["config"] = json.dumps(cfg)
    layout["sections"][0]["displayName"] = "Customer Behavior Dashboard"
    return layout


def write(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(obj if isinstance(obj, str) else json.dumps(obj, indent=2), encoding="utf-8")


def main():
    if OUT.exists():
        shutil.rmtree(OUT)
    sm, rp = OUT / f"{NAME}.SemanticModel", OUT / f"{NAME}.Report"
    write(OUT / f"{NAME}.pbip", {"version": "1.0", "artifacts": [{"report": {"path": f"{NAME}.Report"}}],
                                  "settings": {"enableAutoRecovery": True}})
    write(sm / "definition.pbism", {"version": "1.0", "settings": {}})
    write(sm / "model.bim", model_bim())
    write(rp / "definition.pbir", {"version": "1.0", "datasetReference": {
        "byPath": {"path": f"../{NAME}.SemanticModel"}, "byConnection": None}})
    write(rp / "report.json", report_json())
    theme = rp / "StaticResources" / "SharedResources" / "BaseThemes" / "CY24SU10.json"
    theme.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy(TEMPLATE / "CY24SU10.json", theme)
    write(OUT / ".gitignore", "**/.pbi/localSettings.json\n**/.pbi/cache.abf\n")
    print("Power BI project written to", OUT.relative_to(ROOT), "| data folder:", DATA_FOLDER)


if __name__ == "__main__":
    main()
