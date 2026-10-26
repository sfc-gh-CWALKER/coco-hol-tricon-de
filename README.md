# Tricon: Data Engineering with CoCo

A hands-on lab for turning team data engineering standards and recurring operations chores into reusable, reviewable Cortex Code (CoCo) automations.

- **Part 1** adapts Jeremiah Hansen's Snowflake guide, [Data Engineering with CoCo](https://www.snowflake.com/en/developers/guides/data-engineering-with-coco/) ([source](https://github.com/Snowflake-Labs/sfguide-data-engineering-with-coco)): `AGENTS.md`, a custom skill, and a plugin with a prod-safety hook and a dbt-review subagent, plus optional CI/CD.
- **Part 2** applies the same pattern to Tricon's automation list: dbt upkeep, classification sweeps, access reviews, KPI reports, anomaly explanation, warehouse right-sizing, and Adaptive Warehouses.

Every Part 2 automation **proposes**; a person **approves**.

## Repository layout

```
├── workshop_guide/        # Streamlit lab guide (deploy to Streamlit Community Cloud)
├── dbt/                   # Starter dbt project over SNOWFLAKE_SAMPLE_DATA.TPCH_SF1
│   ├── models/            # customers.sql, orders_summary.sql (with a planted convention violation), _sources.yml
│   ├── seeds/             # resident_contacts.csv - SYNTHETIC PII for the classification workflow
│   └── profiles.yml.example   # SSO (externalbrowser) profile, per-attendee schema
├── solutions/tricon-de-plugin/   # Reference skills, subagents, hook, and manifest
└── admin/                 # ADMIN_GUIDE.md + numbered setup, verify and teardown scripts
```

## For attendees

Open the lab guide app and follow **Getting Started**. In short: install CoCo Desktop, Git, and `dbt-core` + `dbt-snowflake`, clone this repo, open it in CoCo Desktop, configure `~/.dbt/profiles.yml`, and enter your initials in the app sidebar.

## For the admin

Follow [`admin/ADMIN_GUIDE.md`](admin/ADMIN_GUIDE.md) (one script: `tricon_de_lab_setup.sql`, then `05_verify.sql`; teardown `99_teardown.sql`). It creates:

| Object | Purpose |
|--------|---------|
| `TRICON_DE_ROLE` | Attendee role; can create schemas in `TRICON_DE` only |
| `TRICON_DE` database | Per-attendee `DBT_<INITIALS>` schemas |
| `TRICON_DE_WH` + resource monitor | Shared lab compute with a weekly credit cap |
| `TRICON_DE_REVIEWER` (optional) | Read-only `SNOWFLAKE` database roles for A3/A6. Sensitive; grant to admins only |
| `TRICON_DE_EMAIL_INT` (optional) | Email delivery for the KPI report |
| `TRICON_DE_ADAPTIVE_DEMO_WH` (optional) | Facilitator demo of the Adaptive Warehouse conversion |

### Differences from the original guide

- **Authentication:** dbt uses `authenticator: externalbrowser` (SSO). The guide's PAT + `MINS_TO_BYPASS_NETWORK_POLICY_REQUIREMENT` bypass is **not** used on the customer account. CI/CD needs a Tricon-approved service user and network policy.
- **Isolation:** each attendee builds into `TRICON_DE.DBT_<INITIALS>` rather than a shared `DEMO_DB.TPCH_TRANSFORMED`, and the setup avoids granting ownership of shared objects.
- **Safety rules** are added to `AGENTS.md`, and every automation writes to `proposals/` for approval.

## Run the guide locally

```bash
cd workshop_guide
pip install -r requirements.txt
streamlit run streamlit_app.py
```

All data is either TPC-H sample data or synthetic. No Tricon or resident data is included.
