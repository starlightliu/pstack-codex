"""Check the pstack package and its upstream resource inventory."""

import argparse
import json
import re
import sys
from pathlib import Path, PurePosixPath
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
PLUGIN = Path("plugins/pstack-codex")
SKILLS = {
    "architect", "arena", "benchmark-checklist", "blast-radius", "correct", "create-verification-skill",
    "how", "interrogate", "maintain-verification-skill", "reflect", "sharpen", "show-me-your-work",
    "statechart", "teach", "technical-writing", "typescript-best-practices", "unslop", "why",
}
AUTOMATIC = {"blast-radius", "benchmark-checklist"}


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def frontmatter(path):
    text = path.read_text(encoding="utf-8")
    header = re.match(r"\A---\n(.*?)\n---\n", text, re.DOTALL)
    if not header:
        raise ValueError(f"{path}: missing YAML frontmatter")
    # The package uses two plain keys and a JSON-quoted YAML string.
    fields = {}
    for line in header[1].splitlines():
        key, separator, value = line.partition(": ")
        if not separator or key in fields or key not in {"name", "description"}:
            raise ValueError(f"{path}: unexpected frontmatter line {line!r}")
        fields[key] = json.loads(value) if key == "description" else value
    return fields


def check_links(root, path, expect):
    text = path.read_text(encoding="utf-8")
    expect(
        not re.search(r"\.cursor/(?:skills|rules|projects)/|agent-transcripts/|pstack-models\.mdc", text),
        f"{path.relative_to(root)}: stale Cursor path",
    )
    text = re.sub(r"```[^\n]*\n.*?\n```", "", text, flags=re.DOTALL)
    for destination in re.findall(r"\]\(([^\s)]+)\)", text):
        link = urlsplit(destination)
        if link.scheme or link.netloc:
            continue
        target = (path.parent / unquote(link.path)).resolve() if link.path else path
        label = f"{path.relative_to(root)}: {destination}"
        if not target.is_relative_to(root) or not target.exists():
            expect(False, f"{label}: broken local link")
        elif link.fragment and target.suffix == ".md":
            headers = re.findall(r"^#{1,6} (.+)$", target.read_text(encoding="utf-8"), re.MULTILINE)
            anchors = {re.sub(r"[^\w\s-]", "", h.lower()).replace(" ", "-") for h in headers}
            expect(unquote(link.fragment) in anchors, f"{label}: missing heading")


def validate(root, matt_skills):
    errors = []

    def expect(condition, message):
        if not condition:
            errors.append(message)

    lock = read_json(root / "upstream-lock.json")
    expect(lock["repository"] == "https://github.com/cursor/plugins.git", "Invalid upstream repository")
    expect(lock["ref"] == "HEAD", "Invalid upstream ref")
    expect(lock["license"] == "pstack/LICENSE", "Invalid upstream license path")
    expect(bool(re.fullmatch(r"[0-9a-f]{40}", lock["commit"])), "Invalid upstream SHA")
    expect(set(lock["skills"]) == SKILLS, "Unexpected upstream skill set")
    expect((root / "LICENSE").is_file(), "Missing upstream license")
    skills_dir = root / PLUGIN / "skills"
    expect({p.name for p in skills_dir.iterdir() if p.is_dir()} == SKILLS, "Unexpected plugin skill set")

    for name, entry in lock["skills"].items():
        expect(entry["source"] == f"pstack/skills/{name}", f"{name}: invalid source path")
        expect(entry["target"] == (PLUGIN / "skills" / name).as_posix(), f"{name}: invalid target path")
        skill_dir = skills_dir / name
        fields = frontmatter(skill_dir / "SKILL.md")
        expect(fields.get("name") == name, f"{name}: invalid or duplicate name")
        description = fields.get("description")
        expect(isinstance(description, str) and bool(description.strip()), f"{name}: missing description")
        resources = entry["files"]
        expect("SKILL.md" in resources and resources == sorted(set(resources)), f"{name}: invalid inventory")
        for resource in resources:
            path = PurePosixPath(resource)
            expect(
                not path.is_absolute() and ".." not in path.parts and "\\" not in resource
                and (skill_dir / path).is_file(),
                f"{name}: missing or invalid resource {resource}",
            )
        metadata = skill_dir / "agents/openai.yaml"
        expected = f'interface:\n  display_name: "PS · {name}"'
        if name not in AUTOMATIC:
            expected += "\n\npolicy:\n  allow_implicit_invocation: false"
        expect(
            metadata.is_file() and metadata.read_text(encoding="utf-8").strip() == expected,
            f"{name}: invalid display name or invocation policy",
        )
        for path in skill_dir.rglob("*.md"):
            check_links(root, path, expect)

    # Short names can overlap across plugins. Report where a qualified mention matters.
    if matt_skills:
        files = list(matt_skills.rglob("SKILL.md"))
        expect(bool(files), f"No Matt skills in {matt_skills}")
        matt_names = set()
        for path in files:
            header = path.read_text(encoding="utf-8").split("---", 2)[1]
            match = re.search(r"^name:\s*['\"]?([a-z0-9-]+)", header, re.MULTILINE)
            expect(bool(match), f"Missing Matt skill name in {path}")
            if match:
                matt_names.add(match[1])
        shared = SKILLS & matt_names
        if shared:
            print(f"Shared short names with Matt: {', '.join(sorted(shared))}. Use plugin-qualified names.")

    manifest = read_json(root / PLUGIN / ".codex-plugin/plugin.json")
    marketplace = read_json(root / ".agents/plugins/marketplace.json")
    expect(manifest["name"] == "pstack-codex", "Invalid plugin name")
    expect(bool(re.fullmatch(r"\d+\.\d+\.\d+", manifest["version"])), "Invalid plugin version")
    expect(manifest["skills"] == "./skills/" and bool(manifest["description"]), "Invalid manifest skills or description")
    expect(manifest["license"] == "MIT" and bool(manifest["interface"]["displayName"]), "Invalid plugin metadata")
    expect(marketplace["name"] == "starlightliu-pstack" and bool(marketplace["interface"]["displayName"]),
           "Invalid marketplace metadata")
    entries = marketplace["plugins"]
    expect(len(entries) == 1 and entries[0]["name"] == manifest["name"]
           and entries[0]["source"] == {"source": "local", "path": f"./{PLUGIN.as_posix()}"}
           and entries[0]["policy"] == {"installation": "AVAILABLE", "authentication": "ON_INSTALL"},
           "Invalid marketplace plugin entry")

    if errors:
        raise ValueError("\n".join(errors))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository to check")
    parser.add_argument("--matt-skills", type=Path, help="Matt plugin's skills directory to check for shared short names")
    args = parser.parse_args()
    try:
        validate(args.root.resolve(), args.matt_skills)
    except (OSError, ValueError, KeyError, IndexError, TypeError) as error:
        sys.exit(str(error))
    print(f"Validated {len(SKILLS)} skills, display names, resources, invocation policies, manifest, and marketplace.")
