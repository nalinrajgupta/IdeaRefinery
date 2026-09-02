"""Feature-local, versioned and stage-committed run persistence."""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4

from .errors import StateError
from .io import atomic_write_json, content_hash, ensure_within, read_json


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


class RunStore:
    def __init__(self, path: Path):
        self.path = path.resolve()
        self.manifest_path = self.path / "manifest.json"
        self.events_path = self.path / "events.jsonl"

    @classmethod
    def create(cls, feature_dir: Path, run_id: str, feature_id: str, resolved_config_hash: str) -> "RunStore":
        root = feature_dir.resolve() / "runs"
        root.mkdir(parents=True, exist_ok=True)
        path = ensure_within(root, root / run_id)
        path.mkdir()
        store = cls(path)
        now = utc_now()
        manifest = {
            "schema_version": "1.0",
            "run_id": run_id,
            "feature_id": feature_id,
            "status": "created",
            "created_at": now,
            "updated_at": now,
            "resolved_config_hash": resolved_config_hash,
            "active_stage": "created",
            "artifact_hashes": {},
            "schema_hashes": {},
            "stage_commits": [],
            "worker_attempts": {},
            "repair_counts": {},
        }
        atomic_write_json(store.manifest_path, manifest)
        store.events_path.touch()
        return store

    @classmethod
    def open(cls, path: Path) -> "RunStore":
        store = cls(path)
        if not store.manifest_path.is_file():
            raise StateError("manifest-missing", f"no run manifest at {path}")
        return store

    @property
    def manifest(self) -> dict[str, Any]:
        return read_json(self.manifest_path)

    def update_manifest(self, **changes: Any) -> dict[str, Any]:
        manifest = self.manifest
        manifest.update(changes)
        manifest["updated_at"] = utc_now()
        atomic_write_json(self.manifest_path, manifest)
        return manifest

    def append_event(
        self,
        event_type: str,
        stage: str,
        actor: str,
        *,
        input_refs: list[str] | None = None,
        output_refs: list[str] | None = None,
        data: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        sequence = sum(1 for line in self.events_path.read_text(encoding="utf-8").splitlines() if line) + 1
        event = {
            "schema_version": "1.0",
            "event_id": f"EVT-{uuid4().hex}",
            "sequence": sequence,
            "run_id": self.manifest["run_id"],
            "occurred_at": utc_now(),
            "event_type": event_type,
            "stage": stage,
            "actor": actor,
            "input_refs": input_refs or [],
            "output_refs": output_refs or [],
            "data": data or {},
        }
        with self.events_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(event, sort_keys=True, separators=(",", ":")) + "\n")
            handle.flush()
            os.fsync(handle.fileno())
        return event

    def put_object(self, category: str, value: Any) -> tuple[Path, str]:
        digest = content_hash(value)
        directory = ensure_within(self.path, self.path / "objects" / category)
        path = ensure_within(directory, directory / f"{digest}.json")
        if not path.exists():
            atomic_write_json(path, value)
        return path, digest

    def commit_stage(
        self,
        stage: str,
        *,
        input_hashes: dict[str, str],
        output_hashes: dict[str, str],
        schema_hashes: dict[str, str],
        protected_hashes: dict[str, str],
    ) -> dict[str, Any]:
        combined_inputs = {
            **{f"input:{key}": value for key, value in input_hashes.items()},
            **{f"schema:{key}": value for key, value in schema_hashes.items()},
            **{f"protected:{key}": value for key, value in protected_hashes.items()},
        }
        marker_body = {
            "stage": stage,
            "input_hashes": combined_inputs,
            "output_hashes": output_hashes,
        }
        marker_hash = content_hash(marker_body)
        marker_relative = Path("commits") / f"{stage}-{marker_hash[:16]}.json"
        marker_path = ensure_within(self.path, self.path / marker_relative)
        atomic_write_json(marker_path, marker_body)
        commit = {
            **marker_body,
            "marker_path": marker_relative.as_posix(),
            "marker_hash": marker_hash,
            "committed_at": utc_now(),
            "reusable": True,
        }
        manifest = self.manifest
        manifest["stage_commits"] = [item for item in manifest["stage_commits"] if item["stage"] != stage]
        manifest["stage_commits"].append(commit)
        manifest["artifact_hashes"].update(output_hashes)
        manifest["schema_hashes"].update(schema_hashes)
        manifest["active_stage"] = stage
        manifest["updated_at"] = utc_now()
        atomic_write_json(self.manifest_path, manifest)
        self.append_event(
            "stage-committed",
            stage,
            "controller",
            input_refs=sorted(combined_inputs.values()),
            output_refs=sorted(output_hashes.values()),
            data={"marker": marker_relative.as_posix(), "marker_hash": marker_hash},
        )
        return commit

    def resume_eligibility(
        self,
        stage: str,
        *,
        input_hashes: dict[str, str],
        schema_hashes: dict[str, str],
        protected_hashes: dict[str, str],
    ) -> tuple[bool, list[str]]:
        commit = next((item for item in self.manifest["stage_commits"] if item["stage"] == stage), None)
        if not commit or not commit.get("reusable"):
            return False, ["stage-not-committed"]
        marker_path = ensure_within(self.path, self.path / commit["marker_path"])
        if not marker_path.is_file() or content_hash(read_json(marker_path)) != commit["marker_hash"]:
            return False, ["commit-marker-mismatch"]
        actual = commit["input_hashes"]
        reasons: list[str] = []
        if {key.removeprefix("input:"): value for key, value in actual.items() if key.startswith("input:")} != input_hashes:
            reasons.append("input-hash-mismatch")
        if {key.removeprefix("schema:"): value for key, value in actual.items() if key.startswith("schema:")} != schema_hashes:
            reasons.append("schema-hash-mismatch")
        if {key.removeprefix("protected:"): value for key, value in actual.items() if key.startswith("protected:")} != protected_hashes:
            reasons.append("protected-artifact-drift")
        return not reasons, reasons
