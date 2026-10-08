"""Command-line adapter for deterministic Idea Refinery operations."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from collections.abc import Sequence

from .briefs import prepare_stage_brief
from .config import load_yaml, resolve_config
from .coverage import CoverageMatrix, derive_coverage_taxonomy
from .envelopes import validate_review_envelope
from .errors import RefineryError
from .evals.replay import replay_fixture
from .evals.scoring import score_bundle
from .evals.calibration import calibration_status
from .evals.promotion import promote_live_bundle
from .invalidation import calculate_invalidation
from .repair import validate_repair_packet
from .repair import RepairTransaction
from .readiness import assess_readiness
from .run_store import RunStore


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="idea-refinery")
    parser.add_argument("--run-dir")
    subparsers = parser.add_subparsers(dest="command", required=True)
    for name in (
        "resolve-config",
        "prepare-review",
        "validate-envelope",
        "build-coverage",
        "synthesize",
        "prepare-repair",
        "validate-repair",
        "promote-repair",
        "rollback-repair",
        "resume-plan",
        "validate-run",
        "readiness",
        "eval-replay",
        "eval-score",
        "calibrate",
        "promote-bundle",
    ):
        subparser = subparsers.add_parser(name)
        if name == "resolve-config":
            subparser.add_argument("--session-roster", type=Path, required=True)
            subparser.add_argument("--repo-config", type=Path)
            subparser.add_argument("--invocation-config", type=Path)
        elif name == "prepare-review":
            subparser.add_argument("--run-id", required=True)
            subparser.add_argument("--stage", default="review")
            subparser.add_argument("--role", required=True)
            subparser.add_argument("--objective", required=True)
            subparser.add_argument("--coverage", nargs="+", required=True)
            subparser.add_argument("--artifact-hash", action="append", default=[])
        elif name == "validate-envelope":
            subparser.add_argument("--envelope", type=Path, required=True)
            subparser.add_argument("--dispatch", type=Path, required=True)
            subparser.add_argument("--coverage", nargs="+", required=True)
            subparser.add_argument("--protected-hashes", type=Path, required=True)
        elif name == "build-coverage":
            subparser.add_argument("--requirements", type=Path, required=True)
        elif name in {"eval-replay", "eval-score", "readiness", "validate-run"}:
            subparser.add_argument("input", type=Path)
        elif name in {"synthesize", "prepare-repair", "validate-repair", "promote-repair", "rollback-repair", "resume-plan", "calibrate"}:
            subparser.add_argument("input", type=Path)
        elif name == "promote-bundle":
            subparser.add_argument("source", type=Path)
            subparser.add_argument("golden", type=Path)
            subparser.add_argument("--approved", action="store_true")
            subparser.add_argument("--approved-by")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        result = _dispatch(args)
    except RefineryError as error:
        print(json.dumps(error.as_dict(), sort_keys=True), flush=True)
        return 2
    if result is not None:
        print(json.dumps(result, sort_keys=True, default=str))
    return 0


def _read_json(path: Path) -> object:
    return json.loads(path.read_text(encoding="utf-8"))


def _dispatch(args: argparse.Namespace) -> object | None:
    if args.command == "resolve-config":
        roster = _read_json(args.session_roster)
        repository = load_yaml(args.repo_config) if args.repo_config else None
        invocation = load_yaml(args.invocation_config) if args.invocation_config else None
        return resolve_config(roster, repository=repository, invocation=invocation)
    if args.command == "prepare-review":
        hashes = dict(item.split("=", 1) for item in args.artifact_hash)
        return prepare_stage_brief(
            run_id=args.run_id, stage=args.stage, role=args.role, objective=args.objective,
            coverage_assignments=args.coverage, artifact_hashes=hashes,
        )
    if args.command == "validate-envelope":
        envelope = _read_json(args.envelope)
        dispatch = _read_json(args.dispatch)
        protected = _read_json(args.protected_hashes)
        validate_review_envelope(envelope, dispatch=dispatch, assigned_coverage=set(args.coverage), protected_hashes=protected)
        return {"valid": True, "envelope_id": envelope["envelope_id"]}
    if args.command == "build-coverage":
        requirements = _read_json(args.requirements)
        return {
            item.coverage_id: {
                **item.__dict__,
                "requirement_ids": list(item.requirement_ids),
            }
            for item in derive_coverage_taxonomy(requirements)
        }
    if args.command == "synthesize":
        source = _read_json(args.input)
        matrix = CoverageMatrix.from_items(derive_coverage_taxonomy(source.get("requirements", [])))
        for envelope in source.get("envelopes", []):
            matrix.aggregate(envelope["coverage_attestations"], envelope["role"])
        return matrix.as_dict()
    if args.command == "prepare-repair":
        packet = _read_json(args.input)
        packet["invalidated_artifacts"] = sorted(calculate_invalidation(packet["affected_artifacts"]))
        return packet
    if args.command == "validate-repair":
        return validate_repair_packet(_read_json(args.input))
    if args.command in {"promote-repair", "rollback-repair"}:
        specification = _read_json(args.input)
        transaction = RepairTransaction.resume(Path(specification["active_root"]), Path(specification["transaction_root"])) if args.command == "rollback-repair" else RepairTransaction.begin(Path(specification["active_root"]), Path(specification["transaction_root"]))
        result = transaction.rollback() if args.command == "rollback-repair" else transaction.promote(lambda _: specification.get("validation_errors", []))
        return {"status": result.status, "errors": list(result.errors)}
    if args.command == "resume-plan":
        store = RunStore.open(args.input)
        return {"run_id": store.manifest["run_id"], "stage_commits": store.manifest["stage_commits"], "active_stage": store.manifest["active_stage"]}
    if args.command == "calibrate":
        return calibration_status(_read_json(args.input))
    if args.command == "promote-bundle":
        return {"promoted": str(promote_live_bundle(args.source, args.golden, approved=args.approved, approved_by=args.approved_by))}
    if args.command == "eval-replay":
        return replay_fixture(args.input)
    if args.command == "eval-score":
        return score_bundle(_read_json(args.input))
    if args.command == "readiness":
        return assess_readiness(**_read_json(args.input))
    if args.command == "validate-run":
        store = RunStore.open(args.input)
        return {"valid": True, "run_id": store.manifest["run_id"], "status": store.manifest["status"]}
    return {"command": args.command, "status": "not-yet-wired-to-session-controller"}
