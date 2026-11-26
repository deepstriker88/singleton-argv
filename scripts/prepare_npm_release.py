#!/usr/bin/env python3
"""Build a reviewed source commit, verify its npm payload, and smoke the install.
No publishing or npm authentication.
"""
import argparse, hashlib, json, os, re, shutil, subprocess, tarfile, tempfile
from pathlib import Path, PurePosixPath
ROOT=Path(__file__).resolve().parents[1]
NAMES={'singleton-argv','layer-contrast-check','entry-filename-preflight','minor-unit-label','json-field-lens'}
MAX=262144
NPM=([shutil.which("node"),os.environ["EZ_NPM_CLI"]] if os.environ.get("EZ_NPM_CLI") else [shutil.which("npm")])
def run(cmd,cwd=ROOT,stdin=None,exit=0):
 r=subprocess.run(cmd,cwd=cwd,input=stdin,text=True,capture_output=True,timeout=90)
 if r.returncode!=exit:raise RuntimeError("command failed: "+str(cmd[0])+" "+str(r.returncode)+" "+r.stderr[-300:])
 return r.stdout.strip()
def npm(*a,cwd=ROOT):return run(NPM+list(a),cwd)
def sha(b):return hashlib.sha256(b).hexdigest()
def main():
 p=argparse.ArgumentParser()
 p.add_argument("--expected-sha",required=True)
 p.add_argument("--version",required=True)
 p.add_argument("--output",required=True,type=Path)
 a=p.parse_args()
 if not re.fullmatch(r"[0-9a-f]{40}",a.expected_sha) or not re.fullmatch(r"[0-9]+\.[0-9]+\.[0-9]+",a.version):p.error("invalid release identity")
 if run(["git","rev-parse","HEAD"])!=a.expected_sha or run(["git","status","--porcelain"]):p.error("reviewed clean revision required")
 meta=json.loads((ROOT/"package.json").read_text());name=meta["name"]
 if name not in NAMES or meta["version"]!=a.version or meta.get("private") or meta.get("license")!="MIT":p.error("package identity mismatch")
 if meta.get("repository",{}).get("url")!="git+https://github.com/deepstriker88/"+name+".git":p.error("repository mismatch")
 if any(meta.get(k) for k in ("dependencies","devDependencies","optionalDependencies","peerDependencies","bundledDependencies","bundleDependencies")):p.error("dependency-free release required")
 if meta.get("scripts")!={"test":meta.get("scripts",{}).get("test")} or not re.fullmatch(r"node --test(?: tests/[a-z-]+\.test\.js)?",meta["scripts"]["test"]):p.error("unexpected npm scripts")
 if not (ROOT/"LICENSE").is_file():p.error("missing license")
 test=npm("test","--ignore-scripts")
 out=a.output.resolve()
 if ROOT==out or ROOT in out.parents:p.error("output must be outside source repository")
 out.mkdir(mode=0o700)
 packed=json.loads(npm("pack","--offline","--ignore-scripts","--json","--pack-destination",str(out)))
 if isinstance(packed,list) and len(packed)==1:pack=packed[0]
 elif isinstance(packed,dict) and set(packed)=={name}:pack=packed[name]
 else:raise ValueError("unexpected npm pack result schema")
 archive=out/pack["filename"]
 if pack["name"]!=name or pack["version"]!=a.version or archive.name!=name+"-"+a.version+".tgz" or archive.stat().st_size>MAX:p.error("pack mismatch")
 seen=set()
 with tarfile.open(archive,"r:gz") as t:
  total=0
  for m in t:
   path=PurePosixPath(m.name)
   if not m.isfile() or path.is_absolute() or ".." in path.parts or len(path.parts)<2 or path.parts[0]!="package" or m.size>MAX:raise ValueError("unsafe archive member")
   rel=PurePosixPath(*path.parts[1:]).as_posix()
   if rel in seen or (rel not in {"README.md","LICENSE","SECURITY.md","CHANGELOG.md","package.json"} and path.parts[1] not in {"src","bin"}):raise ValueError("unexpected package member")
   data=t.extractfile(m).read();total+=len(data)
   if total>2*1024*1024:raise ValueError("unpacked limit")
   if rel=="package.json":
    if json.loads(data)!=meta:raise ValueError("metadata drift")
   elif data!=(ROOT/rel).read_bytes():raise ValueError("file content drift")
   seen.add(rel)
 if not {"package.json","README.md","LICENSE"}<=seen:raise ValueError("incomplete archive")
 fixtures=ROOT/".github"/"release-fixtures"
 with tempfile.TemporaryDirectory(prefix="npm-release-smoke-") as tmp:
  t=Path(tmp)
  npm("install","--offline","--ignore-scripts","--no-audit","--no-fund",str(archive),cwd=t)
  for f in fixtures.iterdir():
   if f.is_file():shutil.copyfile(f,t/f.name)
  actual=""
  if name in {"singleton-argv","json-field-lens"}:actual=run(["node","example.mjs"],t)
  elif name=="minor-unit-label":actual=run(["node","example.cjs"],t)
  else:
   pkg=t/"node_modules"/name
   cli=pkg/meta["bin"][name]
   cmd=["node",str(cli)]+(["--portable"] if name=="entry-filename-preflight" else [])
   actual=run(cmd,t,(t/"example.json").read_text(),1 if name=="entry-filename-preflight" else 0)
  expected=(t/"example-result.txt").read_text().strip()
  try:ok=json.loads(actual)==json.loads(expected)
  except ValueError:ok=actual==expected
  if not ok:raise ValueError("installed smoke mismatch")
 report={"source_sha":a.expected_sha,"package":name,"package_version":a.version,"archive":archive.name,"sha256":sha(archive.read_bytes()),"members":sorted(seen),"core_tests":"passed","installed_cli_smoke":"passed","published":False}
 (out/"release-receipt.json").write_text(json.dumps(report,indent=2)+"\n")
 print(name,"PASS",report["sha256"],flush=True)
if __name__=="__main__":main()
