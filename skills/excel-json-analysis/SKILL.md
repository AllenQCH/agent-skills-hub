---
name: excel-json-analysis
description: Use when a spreadsheet or CSV needs structured field extraction, deduplication, or deterministic SQL generation for review, especially when the user wants to pull fields out, flatten rows, generate insert SQL, or produce pre-insert verification queries from exports with JSON columns or material master data.
---

# Excel JSON Analysis

## Overview

Extract structured data from spreadsheets or CSV files, then generate a deterministic review artifact such as a clean workbook, `INSERT` SQL, or pre-insert query SQL. Prefer repeatable scripts or simple parsing flows over ad-hoc manual editing.

## Workflow

1. Confirm the real workbook path and whether the current session can read it.
2. If the source is under `~/Downloads` and direct reads fail with `Operation not permitted`, look for or create a readable copy in the current workspace before parsing.
3. Inspect the headers first. Do not assume the JSON column name, business field name, or SQL mapping from user wording.
4. Sample a few non-empty rows and confirm whether this is a JSON-in-cell extraction case or a flat table-to-SQL case.
5. If the task is JSON extraction, run the bundled script to extract the fields and write a new workbook.
6. If the task is table-to-SQL, map the source columns to the target SQL fields explicitly, filter out blank rows, and generate both:
   - the target `INSERT` SQL
   - the pre-insert verification SQL used to confirm the target rows do not already exist
7. Verify row count, key-field mapping, dedup result, and a small sample of the generated output before claiming completion.

## Quick Start

Use the bundled script:

```bash
python3 /Users/heytea/Documents/myHeytea/code/agent-skills-hub/skills/excel-json-analysis/scripts/extract_json_fields_from_excel.py \
  --input /abs/path/source.xlsx \
  --json-column snapshot_json \
  --records-path blueInvoiceOrder.orderLines \
  --fields goodsCode goodsName \
  --dedupe-fields goodsCode goodsName
```

Default output path is:

```text
<source_stem>_extracted.xlsx
```

## Parameters

- `--input`: Source `.xlsx` file.
- `--sheet`: Sheet name. Omit to use the first sheet.
- `--json-column`: Header name containing JSON text.
- `--records-path`: Dot path to a list of records inside the JSON. Example: `blueInvoiceOrder.orderLines`.
- `--fields`: Output fields to extract from each record.
- `--dedupe-fields`: Fields used as the dedupe key. Omit to use all extracted fields.
- `--output`: Optional output workbook path.

## Flat Table To SQL

Use this branch when the sheet or CSV already contains direct business columns such as material code, material name, tax rate, category code, or other master-data fields.

Required steps:

1. Confirm the exact source columns used for each SQL field.
2. Ignore fully blank rows and obvious note rows.
3. Normalize values before SQL generation, for example converting `13%` to `0.13`.
4. Escape single quotes in string values.
5. When generating `INSERT` SQL for new rows, also generate a verification SQL file in the same turn.

Default verification SQL should include:

- pre-insert count check for the candidate keys
- pre-insert detail query for the candidate keys
- post-insert count check
- post-insert detail query

Default candidate key:

- Prefer the business key the user is using to insert, for example `goods_code`
- If uniqueness may depend on multiple columns, state that assumption and offer a stricter query variant

## Decision Rules

- If the JSON value is an object but `records-path` is empty, treat the object itself as one record.
- If the JSON value contains a list at `records-path`, emit one row per item.
- If a row has invalid JSON, count it and report it; do not silently claim success.
- If the requested path is missing in all rows, stop and report that the assumed JSON path is wrong.
- If `Downloads` permission blocks direct reads, explain that the restriction is macOS TCC for the current terminal process, then continue by using a readable copy instead of stopping at the error.
- If the file is CSV or a flat spreadsheet rather than JSON-in-cell data, do not force the JSON script path; switch to direct header mapping.
- If generating `INSERT` SQL for new master data, produce verification SQL in the same turn unless the user explicitly says not to.
- If there are many blank rows, filter them out before counting valid records.
- If the source lacks an explicit “新增” marker, state the assumption used to decide which rows are candidates for insertion.

## Verification

Always verify:

- source sheet name or file type
- actual source headers used
- output file path
- extracted or generated row count
- deduplicated row count when dedupe applies
- invalid JSON count when JSON parsing applies
- generated SQL sample when SQL output applies
- verification query sample when insert SQL output applies

## Common Mistakes

| Mistake | Fix |
|---|---|
| Assuming the column is `shot_json` because the user said so | Read headers first and use the real column name |
| Parsing the whole JSON object when the fields live in a nested list | Sample a row and identify the exact `records-path` |
| Declaring “没权限” and stopping | Try a readable workspace copy and continue |
| Exporting rows without dedupe verification | Re-read the output workbook and check duplicate count |
| Treating a flat CSV like a JSON extraction task | Switch to direct table mapping and confirm SQL field mapping |
| Generating only `INSERT` SQL for new rows | Also generate pre-insert and post-insert verification SQL |
| Counting blank rows as valid materials | Filter blank rows before row-count or SQL generation |

## Script

Primary script:

```text
scripts/extract_json_fields_from_excel.py
```
