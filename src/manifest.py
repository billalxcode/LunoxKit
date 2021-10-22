import json
import os

def loadManifest():
    manifestPath = os.path.join(os.getcwd() + "/src/manifest.json")
    with open(manifestPath, "r") as f:
        content = f.read()
        return json.loads(content)
        