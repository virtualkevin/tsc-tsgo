"""Read raw local captures or byte-equivalent committed gzip archives."""
from pathlib import Path
import gzip,hashlib

def read_capture(path):
 path=Path(path)
 if path.exists():return path.read_bytes()
 return gzip.decompress(Path(str(path)+'.gz').read_bytes())

def digest(data):return hashlib.sha256(data).hexdigest()
