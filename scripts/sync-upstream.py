"""Preview or merge the eight locked upstream skills into a clean checkout."""

import argparse
import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parents[1]
LOCK = "upstream-lock.json"
VALIDATOR = ROOT / "scripts/validate-skills.py"


def git(repo, *args, **options):
    return subprocess.run(
        ["git", "-c", "core.fsmonitor=false", "-C", str(repo), *args],
        stdout=subprocess.PIPE, check=True, timeout=120, **options,
    ).stdout


def oid(raw):
    value = raw.decode("ascii").strip()
    if not re.fullmatch(r"[0-9a-f]{40}", value):
        raise ValueError(f"Expected a full Git SHA, got {value!r}")
    return value


def require_clean(root):
    if git(root, "status", "--porcelain", "--untracked-files=all"):
        raise ValueError("Sync requires a clean checkout. Commit or set aside your changes first.")


def mapped_commit(repo, sha, lock):
    """Create a throwaway commit containing only the selected, mapped source files."""
    if git(repo, "cat-file", "-t", sha).strip() != b"commit":
        raise ValueError(f"{sha} is not a commit")
    index = repo / ".git" / "upstream-index"
    index.unlink(missing_ok=True)
    env = {**os.environ, "GIT_INDEX_FILE": str(index)}
    by_source = {entry["source"]: entry for entry in lock["skills"].values()}
    files = {source: [] for source in by_source}
    paths = {lock["license"], *by_source}
    records = git(repo, "ls-tree", "-rz", sha, "--", *sorted(paths)).split(b"\0")
    entries = []
    targets = set()
    license_blob = None
    for record in filter(None, records):
        meta, raw_path = record.split(b"\t", 1)
        mode, kind, blob = meta.decode("ascii").split()
        path = raw_path.decode("utf-8")
        if kind != "blob" or mode not in {"100644", "100755"}:
            raise ValueError(f"{sha}:{path}: only regular files are supported")
        if path == lock["license"]:
            target = "LICENSE"
            license_blob = blob
        else:
            source, resource = path.rsplit("/", 1)
            while source not in by_source and "/" in source:
                source, part = source.rsplit("/", 1)
                resource = f"{part}/{resource}"
            if source not in by_source:
                raise ValueError(f"Unexpected upstream path: {path}")
            parts = PurePosixPath(resource).parts
            if any(part.lower() in {".git", ".."} or re.search(r'[<>:"\\|?*\x00-\x1f]', part)
                   or part.endswith((".", " ")) for part in parts):
                raise ValueError(f"Non-portable upstream path: {path}")
            files[source].append(resource)
            target = f'{by_source[source]["target"]}/{resource}'
        if target.casefold() in targets:
            raise ValueError(f"Case-insensitive path collision: {target}")
        targets.add(target.casefold())
        entries.append(f"{mode} {blob}\t{target}\0".encode("utf-8"))

    if license_blob is None or any("SKILL.md" not in resources for resources in files.values()):
        raise ValueError(f"{sha}: a selected skill or its license moved or disappeared. Review the mapping.")
    git(repo, "update-index", "-z", "--index-info", input=b"".join(entries), env=env)
    tree = oid(git(repo, "write-tree", env=env))
    commit = oid(git(repo, "-c", "user.name=pstack sync", "-c", "user.email=sync@localhost",
                     "-c", "commit.gpgSign=false", "commit-tree", tree, "-m", f"Upstream {sha}"))
    return commit, license_blob, files


def show_diff(repo, title, base, target=None, paths=()):
    revisions = [base, target] if target else ["--cached", base]
    diff = git(repo, "diff", "--no-ext-diff", "--no-textconv", "--binary", "--no-color",
               *revisions, "--", *paths)
    print(f"\n{title}", flush=True)
    sys.stdout.buffer.write(diff if diff else b"(no changes)\n")
    sys.stdout.buffer.flush()
    return diff


def sync(args):
    subprocess.run([sys.executable, str(VALIDATOR)], check=True)
    lock = json.loads((ROOT / LOCK).read_text(encoding="utf-8"))
    previous = lock["commit"]
    target = args.to
    if target is None:
        rows = git(ROOT, "ls-remote", "--exit-code", lock["repository"], lock["ref"]).splitlines()
        if len(rows) != 1:
            raise ValueError("Upstream ref did not resolve to one commit")
        target = oid(rows[0].split(b"\t", 1)[0])
    print(f"Upstream: {previous} -> {target}", flush=True)
    if target == previous:
        print("Already at the requested commit.")
        return
    if args.check:
        print("A different upstream commit is available. Run with --dry-run to inspect it.")
        return

    require_clean(ROOT)
    head = oid(git(ROOT, "rev-parse", "HEAD"))
    with tempfile.TemporaryDirectory(prefix="pstack-sync-", dir=ROOT.parent) as scratch:
        repo = Path(scratch) / "candidate"
        git(ROOT, "clone", "--quiet", "--no-hardlinks", "--no-tags", ROOT.as_posix(), repo.as_posix())
        git(repo, "fetch", "--quiet", "--no-tags", "--depth=1", lock["repository"], previous, target)
        base, old_license, old_files = mapped_commit(repo, previous, lock)
        incoming, new_license, files = mapped_commit(repo, target, lock)
        if any(sorted(old_files[entry["source"]]) != entry["files"] for entry in lock["skills"].values()):
            raise ValueError("The locked file inventory differs from the pinned source. Review the lock.")
        show_diff(repo, "Upstream changes (mapped to local paths)", base, incoming)
        mapped_paths = ["LICENSE", *(entry["target"] for entry in lock["skills"].values())]
        show_diff(repo, "Local adaptations against the pinned source", base, head, mapped_paths)
        if old_license != new_license:
            raise ValueError("Upstream license changed. Review it before updating.")
        try:
            result = git(repo, "merge-tree", "--write-tree", "--merge-base", base, head, incoming)
        except subprocess.CalledProcessError as error:
            print(error.stdout.decode("utf-8", errors="replace"), file=sys.stderr)
            raise ValueError("Upstream merge failed. No update was applied. Review conflicts before retrying.") from error

        merged = oid(result.splitlines()[0])
        git(repo, "read-tree", "--reset", "-u", merged)
        lock["commit"] = target
        for entry in lock["skills"].values():
            entry["files"] = sorted(files[entry["source"]])
        (repo / LOCK).write_text(json.dumps(lock, indent=2) + "\n", encoding="utf-8", newline="\n")
        git(repo, "add", "--", LOCK)
        subprocess.run([sys.executable, str(VALIDATOR), "--root", str(repo)], check=True)
        diff = show_diff(repo, "Validated candidate update", head)
        if args.dry_run:
            return
        require_clean(ROOT)
        if oid(git(ROOT, "rev-parse", "HEAD")) != head:
            raise ValueError("HEAD moved during sync. Start again from the current checkout.")
        git(ROOT, "apply", "--index", "--check", input=diff)
        git(ROOT, "apply", "--index", input=diff)
        print("Validated update staged. Review git diff --cached before committing.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--check", action="store_true", help="Compare the pinned SHA with upstream HEAD")
    mode.add_argument("--dry-run", action="store_true", help="Merge and validate without updating the checkout")
    parser.add_argument("--to", type=lambda value: oid(value.encode("ascii")), metavar="SHA",
                        help="Select a full upstream commit SHA instead of HEAD")
    try:
        sync(parser.parse_args())
    except (OSError, ValueError, subprocess.CalledProcessError, subprocess.TimeoutExpired) as error:
        sys.exit(str(error))
