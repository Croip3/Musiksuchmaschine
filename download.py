import requests
import re
from pathlib import Path
url = 'http://sing-kikk.de/download/Kling-Gloeckchen-XML.xml'
r = requests.get(url, allow_redirects=True)
file_name = Path(url).name
file_ext = Path(url).suffix
open(file_name, 'wb').write(r.content)

