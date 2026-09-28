"""EarnAgent verifier: fail closed unless a work product is narrowly scoped and auditable."""
import os

FORBIDDEN_SUFFIXES={".exe",".dll",".so",".bin",".key",".pem",".p12"}
MAX_FILES=5
MAX_BYTES=200_000

def verify(product):
    files=product.get("files",[])
    checks={
      "has_files": bool(files),
      "minimal_file_count": len(files)<=MAX_FILES,
      "size_limit": sum(int(f.get("bytes",0)) for f in files)<=MAX_BYTES,
      "no_binaries": all(not any(str(f.get("path","")).lower().endswith(s) for s in FORBIDDEN_SUFFIXES) for f in files),
      "no_secret_paths": all(not any(x in str(f.get("path","")).lower() for x in (".env","secret","credential","private_key")) for f in files),
      "acceptance_criteria_checked": bool(product.get("acceptance_criteria_checked")),
      "tests_passed": product.get("tests_passed") is True,
    }
    return {"verified":all(checks.values()),"checks":checks}

if __name__=="__main__":
    print(verify({"files":[],"acceptance_criteria_checked":False,"tests_passed":False}))
