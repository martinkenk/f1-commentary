"""Check an editorial patch against the compiled safe-output file/size policies."""
import argparse
import json
import os
from pathlib import Path
import re
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parent
LOCK = ROOT / ".github/workflows/critical-race-coverage.lock.yml"


def policies(path=LOCK):
    for line in path.read_text().splitlines():
        if line.strip().startswith("GH_AW_SAFE_OUTPUTS_CONFIG:"):
            config = json.loads(json.loads(line.split(": ", 1)[1]))
            return {name: config[name] for name in (
                "create_pull_request", "push_to_pull_request_branch")}
    raise ValueError("Compiled safe-output configuration not found; recompile the workflow")


def matches(path, pattern):
    # gh-aw's matcher treats **/ as requiring a slash, not zero directories.
    expression = re.escape(pattern).replace(r"\*\*", ".*").replace(r"\*", "[^/]*")
    return re.fullmatch(expression, path) is not None


def validate(paths, size, config):
    errors = []
    for name, policy in config.items():
        rejected = [path for path in paths if not any(
            matches(path, pattern) for pattern in policy["allowed_files"])]
        if rejected:
            errors.append(f"{name}: outside allowed-files: {', '.join(rejected)}")
        if size > policy["max_patch_size"] * 1024:
            errors.append(f"{name}: patch is {size} bytes; limit is "
                          f'{policy["max_patch_size"] * 1024}')
        if len(paths) > policy.get("max_patch_files", 100):
            errors.append(f"{name}: too many changed files ({len(paths)})")
    return errors


def snapshot(base, root=ROOT):
    def git(*args, env=None):
        return subprocess.check_output(["git", *args], cwd=root, env=env)

    # A temporary index includes new files without changing the editor's staged work.
    with tempfile.TemporaryDirectory(prefix="coverage-preflight-") as temporary:
        env = dict(os.environ, GIT_INDEX_FILE=str(Path(temporary) / "index"))
        git("read-tree", "HEAD", env=env)
        git("add", "-A", "--", ".", env=env)
        names = git("diff", "--cached", "--no-renames", "--name-only", "-z", base, "--", env=env)
        patch = git("diff", "--cached", "--no-renames", "--binary", base, "--", env=env)
    return [name.decode() for name in names.split(b"\0") if name], len(patch)


def committed_patch(base, root=ROOT):
    def git(*args):
        return subprocess.check_output(["git", *args], cwd=root)

    if git("status", "--porcelain", "--untracked-files=all").strip():
        raise ValueError("Commit intended changes before final preflight; working tree is not clean")
    base_sha = git("rev-parse", "--verify", f"{base}^{{commit}}").decode().strip()
    commits = f"{base_sha}..HEAD"
    patch = git("format-patch", commits, "--stdout")
    if patch:
        first, rest = patch.split(b"\n", 1)
        patch = first + f"\nX-GH-AW-Base-Commit: {base_sha}\n".encode() + rest
    # Include both rename paths and files changed then reverted in separate commits.
    names = git("log", "--format=", "--no-renames", "--name-only", "-z", commits, "--")
    paths = sorted({name.decode().strip("\n") for name in names.split(b"\0")
                    if name.strip(b"\n")})
    return paths, len(patch)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base", required=True, help="origin/main or origin/<existing-PR-head>")
    parser.add_argument("--committed", action="store_true",
                        help="final check: require clean tree and measure the actual format-patch")
    args = parser.parse_args()
    try:
        paths, size = (committed_patch if args.committed else snapshot)(args.base)
    except ValueError as error:
        print(f"ERROR: {error}")
        return 1
    errors = validate(paths, size, policies())
    for error in errors:
        print(f"ERROR: {error}")
    if errors:
        return 1
    print(f"Editorial patch preflight passed: {len(paths)} files, {size} bytes. "
          "Safe outputs still enforce protected-file and repository policy.")
    if not args.committed:
        print("Preliminary net diff only. Commit changes and rerun with --committed before submission.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
