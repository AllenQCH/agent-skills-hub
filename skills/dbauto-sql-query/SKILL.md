---
name: dbauto-sql-query
description: Use when Codex needs to query HeyTea domestic production or test databases through the dbauto SQL query page at https://dbauto.heyteago.com/sqlquery/ and opencli Browser Bridge.
---

# DBAuto SQL Query

Use this skill for domestic production and test dbauto online SQL queries through `opencli` Browser Bridge. Both environments are selected from the same domestic dbauto page. This is for the web SQL query page, not the local dbauto export tool.

Use `opencli-browser-reuse` for page opening so dbauto exploration stays on the stable `dbauto-query` session.

## Safety

- Treat dbauto as production unless the user explicitly selects the domestic test instance.
- Keep the environment, instance, and database explicit in every result summary.
- Default to read-only SQL only: `SELECT`, `SHOW`, `DESC`, `DESCRIBE`, `EXPLAIN`, or `WITH`.
- Do not print cookies, CSRF values, session IDs, tokens, or browser profile data.
- For any `UPDATE`, `INSERT`, `DELETE`, `DDL`, or other write SQL, generate the SQL for the user to submit as a dbauto work order; do not execute it.
- For data queries, use narrow predicates and explicit `LIMIT`.

## Domestic Instances

When the user asks to query domestic production dbauto without specifying an instance, assume the target is one of these three MySQL instances. Ask only if the database or exact instance is ambiguous.

| Environment | Alias | Instance | Engine |
|---|---|---|---|
| `cn-prod` | `hsp-ids` | `供应链中台prod-hsp-ids--生产MySQL灾备` | MySQL |
| `cn-prod` | `hsp-pof` | `供应链中台prod-hsp-pof--生产MySQL灾备` | MySQL |
| `cn-prod` | `hsp-pof-scm` | `供应链中台prod-hsp-pof-scm--生产MySQL灾备` | MySQL |
| `cn-test` | `cn-test` / `cn-test-mysql57` | `国内--测试环境--MySQL5.7` | MySQL |
| `cn-test` | `cn-test-mysql80` | `国内--测试环境--MySQL8.0` | MySQL |

The short `cn-test` alias intentionally points to MySQL 5.7, matching the default domestic test instance. Use `cn-test-mysql80` only when MySQL 8.0 is explicitly required.

Known database for invoice work:

```text
hsp-ids / center_hsp_invoice
```

## Workflow

1. Confirm `opencli` Browser Bridge is connected:
   ```bash
   opencli doctor -v
   ```
2. Open or reuse the domestic dbauto page:
   ```bash
   bash /Users/heytea/Documents/myHeytea/code/agent-skills-hub/skills/opencli-browser-reuse/scripts/opencli_reuse.sh --session dbauto-query open https://dbauto.heyteago.com/sqlquery/
   ```
3. If the page is not logged in, use the opencli-backed SSO path:
   ```bash
   python3 /Users/heytea/Documents/myHeytea/code/agent-skills-hub/skills/sso-login/scripts/sso_opencli.py --platform cn
   ```
4. For read-only SQL, prefer the bundled script:
   ```bash
   /Users/heytea/Documents/myHeytea/code/agent-skills-hub/skills/dbauto-sql-query/scripts/dbauto_sql_query.py --instance hsp-ids --db center_hsp_invoice --sql "SHOW CREATE TABLE hsp_goods_rate"
   ```
5. To list relevant HSP/POF instances from the page:
   ```bash
   /Users/heytea/Documents/myHeytea/code/agent-skills-hub/skills/dbauto-sql-query/scripts/dbauto_sql_query.py --list-common-instances
   ```
6. To list domestic test MySQL instances from the page:
   ```bash
   /Users/heytea/Documents/myHeytea/code/agent-skills-hub/skills/dbauto-sql-query/scripts/dbauto_sql_query.py --list-cn-test-instances
   ```
7. To list databases for a selected instance:
   ```bash
   /Users/heytea/Documents/myHeytea/code/agent-skills-hub/skills/dbauto-sql-query/scripts/dbauto_sql_query.py --instance hsp-ids --list-dbs
   /Users/heytea/Documents/myHeytea/code/agent-skills-hub/skills/dbauto-sql-query/scripts/dbauto_sql_query.py --instance cn-test --list-dbs
   ```
8. To list tables after the user chooses a database:
   ```bash
   /Users/heytea/Documents/myHeytea/code/agent-skills-hub/skills/dbauto-sql-query/scripts/dbauto_sql_query.py --instance hsp-ids --db center_hsp_invoice --list-tables
   /Users/heytea/Documents/myHeytea/code/agent-skills-hub/skills/dbauto-sql-query/scripts/dbauto_sql_query.py --instance cn-test --db test_hsp_1_center_hsp_invoice --list-tables
   ```

Default interaction order:

```text
choose cn-prod or cn-test
-> choose one of hsp-ids / hsp-pof / hsp-pof-scm / cn-test aliases
-> list databases
-> user chooses database
-> list tables or run read-only SQL
```

## Script

Primary script:

```text
scripts/dbauto_sql_query.py
```

The script executes JavaScript in the logged-in dbauto page and calls the page's own `/instance/instance_resource/` or `/query/` endpoint. It refuses non-read-only SQL.
