#!/usr/bin/env python3
"""Conservative exact-index checks, not a complete secret detector."""
import re,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
BLOCKED={'.env','.venv','private','.private','.runs','logs','__pycache__'}
PATTERNS=[r'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----',r'gh[pousr]_[A-Za-z0-9]{30,}',r'github_pat_[A-Za-z0-9_]{30,}',r'sk-[A-Za-z0-9_-]{24,}',r'AKIA[A-Z0-9]{16}',r'(?i)"(?:api_key|password|token)"\s*:\s*"[A-Za-z0-9_+/=-]{24,}"']
def main():
 files=subprocess.check_output(['git','ls-files','-z'],cwd=ROOT).decode().strip('\0').split('\0');issues=[]
 for name in files:
  if not name:continue
  path=Path(name)
  if set(path.parts)&BLOCKED:issues.append((name,'forbidden-path'))
  if path.suffix in {'.sqlite','.db','.pem','.key','.npy','.zip'}:issues.append((name,'forbidden-extension'))
  raw=subprocess.check_output(['git','show',':'+name],cwd=ROOT)
  if len(raw)>1024*1024:issues.append((name,'unexpected-large-file'))
  try:text=raw.decode('utf-8')
  except UnicodeDecodeError:issues.append((name,'unexpected-binary'));continue
  for pattern in PATTERNS:
   if re.search(pattern,text):issues.append((name,'possible-secret'))
 for name,reason in issues:print(reason,name)
 print('Public tree audit:',len(files),'tracked files,',len(issues),'findings')
 return 1 if issues or not any(files) else 0
if __name__=='__main__':raise SystemExit(main())
