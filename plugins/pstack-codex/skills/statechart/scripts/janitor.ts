import { once } from "node:events";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { killGroup } from "./run.ts";

const [workerPid, stage, stageParent, tmp] = process.argv.slice(2);
const pid = Number(workerPid);
if (!Number.isSafeInteger(pid) || pid < 1 || !stage || !stageParent || !tmp)
  throw new Error("Expected the statechart worker and its scratch directories");

function removeScratch(dir: string, parent: string, name: RegExp) {
  const stat = fs.lstatSync(dir, { throwIfNoEntry: false });
  if (!stat) return;
  const resolved = fs.realpathSync(dir);
  if (!stat.isDirectory() || path.dirname(resolved) !== fs.realpathSync(parent)
      || !name.test(path.basename(resolved)))
    throw new Error(`Unexpected statechart scratch directory: ${dir}`);
  fs.rmSync(resolved, { recursive: true, force: true, maxRetries: 5 });
}

process.stdin.resume();
await once(process.stdin, "end");
await killGroup(pid);
removeScratch(stage, stageParent, /^\..+\.statechart-[a-z0-9]{6}$/i);
removeScratch(tmp, os.tmpdir(), /^statechart-[a-z0-9]{6}$/i);
