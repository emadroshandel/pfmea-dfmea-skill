#!/usr/bin/env python3
"""
fmea_project.py — stateful FMEA project tracker

Companion to generate_fmea.py. Where generate_fmea.py is a one-shot "hand me
a complete chains.json, get a polished report" tool, this script lets you
build an FMEA incrementally across a conversation: create a project, add
failure chains one at a time as you discuss them, list/update them as the
analysis develops, pull a high-priority view, and — when it's ready — export
straight into the chains.json format generate_fmea.py consumes.

Risk is Action Priority (H/M/L) from S/O/D, per the rule table in
references/sod_scoring_tables.md — RPN is intentionally not supported, same
as generate_fmea.py.

Storage: one JSON file per project under ./fmea_projects/<safe_name>.json
(created relative to the current working directory).

Usage:
    python fmea_project.py --action create --project "Front Bumper PFMEA" \\
        --type PFMEA --item "Front Bumper Assembly" --customer "Acme Motors" \\
        --process-name "Injection Molding + Welding"

    python fmea_project.py --action add --project "Front Bumper PFMEA" \\
        --fe "Bumper cracks under low-speed impact" \\
        --fm "Insufficient wall thickness in the mounting boss" \\
        --fc "Injection pressure below the qualified process window" \\
        --s 6 --o 4 --d 5 --process-step "Injection Molding" --category-4m Machine \\
        --pc "Process parameter SOP with tolerance band" \\
        --dc "First-piece dimensional check each shift"

    python fmea_project.py --action list --project "Front Bumper PFMEA"
    python fmea_project.py --action update --project "Front Bumper PFMEA" --item-id 1 --o 2 --action-status Implemented
    python fmea_project.py --action high-priority --project "Front Bumper PFMEA"
    python fmea_project.py --action export --project "Front Bumper PFMEA" --format csv
    python fmea_project.py --action export --project "Front Bumper PFMEA" --format report-input --output-dir ./output

    # 'report-input' writes chains.json (+ prints the generate_fmea.py command
    # to run next) so the tracker feeds directly into the polished xlsx/docx
    # report generator instead of being a dead end.
"""

import argparse
import csv
import json
import os
import sys
from datetime import datetime, date
from pathlib import Path

DATA_DIR = Path("fmea_projects")


# ---------------------------------------------------------------------------
# Action Priority logic — duplicated from generate_fmea.py so this script
# runs standalone. Keep in sync with generate_fmea.py::compute_ap if you
# change the rule table in references/sod_scoring_tables.md.
# ---------------------------------------------------------------------------

def _ap_band(s, o, d):
    if s >= 9:
        if o == 1 and d == 1:
            return "M"
        return "H"
    if 6 <= s <= 8:
        if o >= 6:
            return "H"
        if o in (4, 5):
            return "H" if d >= 5 else "M"
        if o in (2, 3):
            return "M" if d >= 5 else "L"
        return "L"
    if 4 <= s <= 5:
        if o >= 6:
            return "H" if d >= 5 else "M"
        if 2 <= o <= 5:
            return "M" if d >= 5 else "L"
        return "L"
    if 2 <= s <= 3:
        if o >= 4 and d >= 5:
            return "M"
        return "L"
    return "L"


def compute_ap(s, o, d):
    for v, name in ((s, "S"), (o, "O"), (d, "D")):
        if not isinstance(v, int) or not (1 <= v <= 10):
            raise ValueError(f"{name} must be an integer 1-10, got {v!r}")
    ap = _ap_band(s, o, d)
    borderline = False
    for delta in (-1, 1):
        if 1 <= o + delta <= 10 and _ap_band(s, o + delta, d) != ap:
            borderline = True
        if 1 <= d + delta <= 10 and _ap_band(s, o, d + delta) != ap:
            borderline = True
    return ap, borderline


def flag_special_characteristic(s, ap):
    if s >= 9:
        return "CC"
    if s == 8 and ap in ("H", "M"):
        return "SC"
    return None


# ---------------------------------------------------------------------------
# Storage
# ---------------------------------------------------------------------------

def _safe_name(project_name):
    return "".join(c for c in project_name if c.isalnum() or c in "-_ ").strip().replace(" ", "_")


def _project_file(project_name):
    DATA_DIR.mkdir(exist_ok=True)
    return DATA_DIR / f"{_safe_name(project_name)}.json"


def load_project(project_name):
    f = _project_file(project_name)
    if not f.exists():
        return None
    with open(f, "r", encoding="utf-8") as fh:
        return json.load(fh)


def save_project(project):
    project["updated_at"] = datetime.now().isoformat()
    f = _project_file(project["meta"]["project_name"])
    with open(f, "w", encoding="utf-8") as fh:
        json.dump(project, fh, ensure_ascii=False, indent=2)
    return f


def recompute_summary(project):
    counts = {"H": 0, "M": 0, "L": 0}
    for item in project["items"]:
        counts[item["ap"]] += 1
    project["summary"] = {
        "total_items": len(project["items"]),
        "high": counts["H"],
        "medium": counts["M"],
        "low": counts["L"],
        "management_review_flagged": sum(
            1 for i in project["items"] if i["s"] >= 9 and i["ap"] in ("H", "M")
        ),
        "special_characteristics": sum(1 for i in project["items"] if i.get("special_char")),
    }


# ---------------------------------------------------------------------------
# Actions
# ---------------------------------------------------------------------------

def action_create(args):
    if load_project(args.project) is not None:
        return {"status": "exists", "message": f"Project '{args.project}' already exists"}

    project = {
        "meta": {
            "project_name": args.project,
            "fmea_type": args.fmea_type,
            "item_name": args.item or args.project,
            "customer": args.customer or "",
            "project_no": args.project_no or "",
            "team_members": args.team or "",
            "template": args.template or "generic-fmea",
            "system_level": args.system_level or "",
            "design_responsibility": args.design_responsibility or "",
            "process_name": args.process_name or "",
            "manufacturing_site": args.manufacturing_site or "",
            "structure_summary": args.structure_summary or "",
            "function_summary": args.function_summary or "",
        },
        "created_at": datetime.now().isoformat(),
        "items": [],
        "summary": {"total_items": 0, "high": 0, "medium": 0, "low": 0,
                     "management_review_flagged": 0, "special_characteristics": 0},
    }
    save_project(project)
    return {"status": "success", "message": f"Project '{args.project}' created", "meta": project["meta"]}


def action_add(args):
    project = load_project(args.project)
    if project is None:
        return {"status": "error", "message": f"Project '{args.project}' not found. Create it first."}

    for field, val in (("fe", args.fe), ("fm", args.fm), ("fc", args.fc),
                        ("s", args.s), ("o", args.o), ("d", args.d)):
        if val is None:
            return {"status": "error", "message": f"--{field.replace('_', '-')} is required for 'add'"}

    ap, borderline = compute_ap(args.s, args.o, args.d)
    item = {
        "id": (max((i["id"] for i in project["items"]), default=0) + 1),
        "process_step": args.process_step or "",
        "category_4m": args.category_4m or "",
        "fe": args.fe,
        "fm": args.fm,
        "fc": args.fc,
        "s": args.s,
        "o": args.o,
        "d": args.d,
        "ap": ap,
        "borderline": borderline,
        "special_char": flag_special_characteristic(args.s, ap),
        "pc": args.pc or "",
        "dc": args.dc or "",
        "action": args.action_text or "",
        "action_owner": args.action_owner or "",
        "action_due": args.action_due or "",
        "action_status": args.action_status or ("Suggested" if ap in ("H", "M") else ""),
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
    }
    project["items"].append(item)
    recompute_summary(project)
    save_project(project)

    msg = f"Chain #{item['id']} added: AP={ap}"
    if borderline:
        msg += " (borderline — recommend manual review)"
    if item["special_char"]:
        msg += f", flagged {item['special_char']}"
    if args.s >= 9 and ap in ("H", "M"):
        msg += " — S 9-10 with AP H/M: flag for management review"
    return {"status": "success", "message": msg, "item": item}


def action_list(args):
    project = load_project(args.project)
    if project is None:
        return {"status": "error", "message": f"Project '{args.project}' not found"}
    return {
        "status": "success",
        "project": args.project,
        "meta": project["meta"],
        "summary": project["summary"],
        "items": project["items"],
    }


def action_update(args):
    project = load_project(args.project)
    if project is None:
        return {"status": "error", "message": f"Project '{args.project}' not found"}

    item = next((i for i in project["items"] if i["id"] == args.item_id), None)
    if item is None:
        return {"status": "error", "message": f"Item #{args.item_id} not found in '{args.project}'"}

    changed_sod = False
    for field, val in (("s", args.s), ("o", args.o), ("d", args.d)):
        if val is not None:
            item[field] = val
            changed_sod = True

    if changed_sod:
        ap, borderline = compute_ap(item["s"], item["o"], item["d"])
        item["ap"] = ap
        item["borderline"] = borderline
        item["special_char"] = flag_special_characteristic(item["s"], ap)

    for field, val in (
        ("fe", args.fe), ("fm", args.fm), ("fc", args.fc), ("pc", args.pc), ("dc", args.dc),
        ("action", args.action_text), ("action_owner", args.action_owner),
        ("action_due", args.action_due), ("action_status", args.action_status),
        ("process_step", args.process_step), ("category_4m", args.category_4m),
    ):
        if val is not None:
            item[field] = val

    item["updated_at"] = datetime.now().isoformat()
    recompute_summary(project)
    save_project(project)
    return {"status": "success", "message": f"Item #{args.item_id} updated", "item": item}


def action_high_priority(args):
    project = load_project(args.project)
    if project is None:
        return {"status": "error", "message": f"Project '{args.project}' not found"}
    levels = {"H"} if args.high_only else {"H", "M"}
    items = [i for i in project["items"] if i["ap"] in levels]
    items.sort(key=lambda i: (i["ap"] != "H", -i["s"]))
    return {
        "status": "success",
        "project": args.project,
        "count": len(items),
        "items": items,
    }


def action_export(args):
    project = load_project(args.project)
    if project is None:
        return {"status": "error", "message": f"Project '{args.project}' not found"}

    out_dir = Path(args.output_dir or "fmea_projects")
    out_dir.mkdir(parents=True, exist_ok=True)
    safe = _safe_name(args.project)

    if args.format == "json":
        path = out_dir / f"{safe}_export.json"
        with open(path, "w", encoding="utf-8") as f:
            json.dump(project, f, ensure_ascii=False, indent=2)
        return {"status": "success", "file": str(path)}

    if args.format == "csv":
        path = out_dir / f"{safe}_export.csv"
        fieldnames = ["id", "process_step", "category_4m", "fe", "fm", "fc", "s", "o", "d",
                      "ap", "special_char", "pc", "dc", "action", "action_owner",
                      "action_due", "action_status"]
        with open(path, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
            writer.writeheader()
            for item in project["items"]:
                writer.writerow(item)
        return {"status": "success", "file": str(path)}

    if args.format == "report-input":
        # Bridges this tracker into generate_fmea.py's chains.json schema.
        chains_path = out_dir / f"{safe}_chains.json"
        chains = []
        for i in project["items"]:
            chains.append({
                "process_step": i["process_step"],
                "category_4m": i["category_4m"],
                "fe": i["fe"], "fm": i["fm"], "fc": i["fc"],
                "s": i["s"], "o": i["o"], "d": i["d"],
                "pc": i["pc"], "dc": i["dc"],
                "action": i["action"], "action_owner": i["action_owner"],
                "action_due": i["action_due"], "action_status": i["action_status"],
            })
        with open(chains_path, "w", encoding="utf-8") as f:
            json.dump(chains, f, ensure_ascii=False, indent=2)

        m = project["meta"]
        cmd = [
            "python generate_fmea.py",
            f'--type {m["fmea_type"]}',
            f'--item "{m["item_name"]}"',
            f'--customer "{m["customer"]}"',
            f'--template {m["template"]}',
            f'--chains {chains_path}',
            f'--output-dir {out_dir}',
        ]
        if m["fmea_type"] == "DFMEA":
            if m["system_level"]:
                cmd.append(f'--system-level "{m["system_level"]}"')
            if m["design_responsibility"]:
                cmd.append(f'--design-responsibility "{m["design_responsibility"]}"')
        else:
            if m["process_name"]:
                cmd.append(f'--process-name "{m["process_name"]}"')
            if m["manufacturing_site"]:
                cmd.append(f'--manufacturing-site "{m["manufacturing_site"]}"')
        if m["structure_summary"]:
            cmd.append(f'--structure-summary "{m["structure_summary"]}"')
        if m["function_summary"]:
            cmd.append(f'--function-summary "{m["function_summary"]}"')

        return {
            "status": "success",
            "file": str(chains_path),
            "next_step": " \\\n  ".join(cmd),
        }

    return {"status": "error", "message": f"Unsupported export format: {args.format}"}


def action_summary(args):
    project = load_project(args.project)
    if project is None:
        return {"status": "error", "message": f"Project '{args.project}' not found"}
    return {"status": "success", "project": args.project, "meta": project["meta"], "summary": project["summary"]}


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def parse_args(argv=None):
    p = argparse.ArgumentParser(description="Stateful DFMEA/PFMEA project tracker (companion to generate_fmea.py).")
    p.add_argument("--action", required=True,
                    choices=["create", "add", "list", "update", "high-priority", "export", "summary"])
    p.add_argument("--project", required=True, help="Project name (used as the storage key)")

    # create
    p.add_argument("--type", dest="fmea_type", choices=["DFMEA", "PFMEA"])
    p.add_argument("--item", help="Item/product/process name (defaults to --project)")
    p.add_argument("--customer", default=None)
    p.add_argument("--project-no", default=None)
    p.add_argument("--team", default=None)
    p.add_argument("--template", default=None)
    p.add_argument("--system-level", default=None)
    p.add_argument("--design-responsibility", default=None)
    p.add_argument("--process-name", default=None)
    p.add_argument("--manufacturing-site", default=None)
    p.add_argument("--structure-summary", default=None)
    p.add_argument("--function-summary", default=None)

    # add / update
    p.add_argument("--item-id", type=int, help="Required for 'update'")
    p.add_argument("--process-step", default=None)
    p.add_argument("--category-4m", dest="category_4m", default=None,
                    choices=[None, "Man", "Machine", "Material", "Method", "Environment", "Measurement"])
    p.add_argument("--fe", default=None, help="Failure Effect")
    p.add_argument("--fm", default=None, help="Failure Mode")
    p.add_argument("--fc", default=None, help="Failure Cause")
    p.add_argument("--s", type=int, choices=range(1, 11), default=None, metavar="[1-10]")
    p.add_argument("--o", type=int, choices=range(1, 11), default=None, metavar="[1-10]")
    p.add_argument("--d", type=int, choices=range(1, 11), default=None, metavar="[1-10]")
    p.add_argument("--pc", default=None, help="Prevention Control")
    p.add_argument("--dc", default=None, help="Detection Control")
    p.add_argument("--action-text", dest="action_text", default=None)
    p.add_argument("--action-owner", default=None)
    p.add_argument("--action-due", default=None)
    p.add_argument("--action-status", default=None,
                    choices=[None, "Suggested", "Decided", "Implemented", "Closed"])

    # high-priority
    p.add_argument("--high-only", action="store_true", help="Only AP=H (default includes H and M)")

    # export
    p.add_argument("--format", choices=["csv", "json", "report-input"], default="csv")
    p.add_argument("--output-dir", default=None)

    return p.parse_args(argv)


ACTIONS = {
    "create": action_create,
    "add": action_add,
    "list": action_list,
    "update": action_update,
    "high-priority": action_high_priority,
    "export": action_export,
    "summary": action_summary,
}


def main(argv=None):
    args = parse_args(argv)

    if args.action == "create" and not args.fmea_type:
        print(json.dumps({"status": "error", "message": "--type DFMEA|PFMEA is required for 'create'"},
                          ensure_ascii=False, indent=2))
        return 1
    if args.action == "update" and args.item_id is None:
        print(json.dumps({"status": "error", "message": "--item-id is required for 'update'"},
                          ensure_ascii=False, indent=2))
        return 1

    try:
        result = ACTIONS[args.action](args)
    except ValueError as e:
        result = {"status": "error", "message": str(e)}

    print(json.dumps(result, ensure_ascii=False, indent=2, default=str))
    return 0 if result.get("status") == "success" else 1


if __name__ == "__main__":
    sys.exit(main())
