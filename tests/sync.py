"""Exercise the sync workflow with a local mirror of the pinned upstream files."""

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LOCK = "upstream-lock.json"


def git(repo, *args):
    return subprocess.check_output(["git", "-c", "core.fsmonitor=false", "-C", str(repo), *args]).decode().strip()


def commit(repo, message):
    git(repo, "add", ".")
    git(repo, "-c", "user.name=Fixture", "-c", "user.email=fixture@example.test",
        "-c", "commit.gpgsign=false", "commit", "-qm", message)
    return git(repo, "rev-parse", "HEAD")


def test_sync(source):
    lock = json.loads((ROOT / LOCK).read_text(encoding="utf-8"))
    if git(source, "rev-parse", "HEAD") != lock["commit"]:
        raise ValueError("Check out the locked commit in the upstream source repository first.")
    with tempfile.TemporaryDirectory(prefix="pstack-test-", dir=ROOT.parent) as scratch:
        scratch = Path(scratch)
        upstream = scratch / "upstream"
        upstream.mkdir()
        git(upstream, "init", "-q", "-b", "main")
        for path in [lock["license"], *(s["source"] for s in lock["skills"].values())]:
            target = upstream / path
            target.parent.mkdir(parents=True, exist_ok=True)
            if (source / path).is_dir():
                shutil.copytree(source / path, target)
            else:
                shutil.copy2(source / path, target)
        git(upstream, "add", ".")
        git(upstream, "update-index", "--chmod=+x", "pstack/skills/show-me-your-work/scripts/log.sh")
        pinned = commit(upstream, "Mirror selected upstream files")

        skill = lock["skills"]["benchmark-checklist"]
        entry = upstream / skill["source"] / "SKILL.md"
        text = entry.read_text(encoding="utf-8")
        entry.write_text(text.replace("5. **Does it reproduce?**", "An upstream addition.\n\n5. **Does it reproduce?**"),
                         encoding="utf-8", newline="\n")
        extra = entry.with_name("extra.md")
        extra.write_text("# New upstream resource\n", encoding="utf-8", newline="\n")
        clean = commit(upstream, "Extend the benchmark checklist")
        extra.write_text("[Missing](missing.md)\n", encoding="utf-8", newline="\n")
        invalid = commit(upstream, "Add a broken link")
        text = entry.read_text(encoding="utf-8")
        upstream_description = next(line for line in text.splitlines() if line.startswith("description: "))
        entry.write_text(text.replace(upstream_description, 'description: "Conflicting upstream description."', 1),
                         encoding="utf-8", newline="\n")
        conflict = commit(upstream, "Change the description adapted by Codex")

        local = scratch / "local"
        git(ROOT, "clone", "-q", "--no-hardlinks", ROOT.as_posix(), local.as_posix())
        lock["commit"] = pinned
        (local / LOCK).write_text(json.dumps(lock, indent=2) + "\n", encoding="utf-8", newline="\n")
        commit(local, "Point the test checkout at the mirror")
        env = {
            **os.environ,
            "GIT_CONFIG_COUNT": "1",
            "GIT_CONFIG_KEY_0": f"url.{upstream.as_uri()}.insteadOf",
            "GIT_CONFIG_VALUE_0": lock["repository"],
        }

        def sync(*args):
            result = subprocess.run([sys.executable, str(local / "scripts/sync-upstream.py"), *args],
                                    env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            return result.returncode, result.stdout.decode("utf-8", errors="replace")

        lock_path = local / LOCK
        initial = lock_path.read_bytes()
        status, output = sync("--check")
        assert status == 0 and conflict in output, output[-2000:]
        for sha, expected in [(invalid, "broken local link"), (conflict, "CONFLICT")]:
            status, output = sync("--to", sha)
            assert status != 0 and expected in output, output[-2000:]
            assert not git(local, "status", "--porcelain") and lock_path.read_bytes() == initial
        status, output = sync("--dry-run", "--to", clean)
        assert status == 0 and "Validated candidate update" in output, output[-2000:]
        assert not git(local, "status", "--porcelain") and lock_path.read_bytes() == initial
        status, output = sync("--to", clean)
        assert status == 0, output[-2000:]
        merged = local / skill["target"] / "SKILL.md"
        text = merged.read_text(encoding="utf-8")
        original = (ROOT / skill["target"] / "SKILL.md").read_text(encoding="utf-8")
        local_description = next(line for line in original.splitlines() if line.startswith("description: "))
        assert "name: benchmark-checklist" in text and "An upstream addition." in text
        assert local_description in text.splitlines()
        assert merged.with_name("extra.md").is_file()
        assert json.loads(lock_path.read_text(encoding="utf-8"))["commit"] == clean
        assert not git(local, "diff", "--name-only")
        assert git(local, "diff", "--cached", "--name-only")
    print("Sync passed: check, dry run, merged resources, retained adaptations, and no writes on conflict or invalid links.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("upstream_checkout", type=Path)
    args = parser.parse_args()
    test_sync(args.upstream_checkout.resolve())
