
import json
import pandas as pd
from pathlib import Path

def generate_schemas(excel_path: str, output_dir: str = "./data"):
    xls = pd.ExcelFile(excel_path)
    df = pd.read_excel(xls, sheet_name="RESUMO", header=None)

    # Campos de entrada (linhas 5–14, colunas A e B)
    entradas = {}
    for i in range(5, 15):
        label = str(df.iloc[i, 0]).strip() if pd.notna(df.iloc[i, 0]) else None
        valor = df.iloc[i, 1]
        if not label or label.lower().startswith("nan"):
            continue
        field_name = label.split("(")[0].split("...")[0].strip().lower().replace(" ", "_").replace("/", "_")
        tipo = "number" if isinstance(valor, (int, float)) else "string"
        if "data" in field_name or "ação" in field_name or "até" in field_name:
            tipo = "string"
        entradas[field_name] = {"type": tipo}

    schema_input = {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "title": "CalculateInput",
        "type": "object",
        "properties": entradas,
        "required": list(entradas.keys())
    }

    # Blocos de saída (linhas 21–104)
    blocos = []
    for n in range(21, 105):
        titulo = df.iloc[n, 0]
        if pd.isna(titulo):
            continue
        if "Descrição" in str(titulo) or "TOTAL" in str(titulo).upper():
            blocos.append(str(titulo))

    schema_output = {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "title": "CalculateResult",
        "type": "object",
        "properties": {
            "id": {"type": "string"},
            "created_at": {"type": "string", "format": "date-time"},
            "results": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "titulo": {"type": "string"},
                        "header": {"type": "array", "items": {"type": "string"}},
                        "rows": {
                            "type": "array",
                            "items": {"type": "array", "items": {"type": ["string", "number", "null"]}}
                        },
                        "total": {"type": "array", "items": {"type": ["string", "number", "null"]}}
                    },
                    "required": ["titulo", "header", "rows"]
                }
            }
        },
        "required": ["id", "results"]
    }

    Path(output_dir).mkdir(parents=True, exist_ok=True)
    with open(Path(output_dir) / "schema_input.json", "w", encoding="utf-8") as f:
        json.dump(schema_input, f, indent=2, ensure_ascii=False)
    with open(Path(output_dir) / "schema_output.json", "w", encoding="utf-8") as f:
        json.dump(schema_output, f, indent=2, ensure_ascii=False)

    print("✅ Schemas gerados com sucesso em", output_dir)

if __name__ == "__main__":
    generate_schemas("./data/planilhamae.xlsx")
