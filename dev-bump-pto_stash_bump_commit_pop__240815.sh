git stash pyproject.toml jgtfxcon/__init__.py package.json && python bump_version.py  && git commit pyproject.toml jgtfxcon/__init__.py package.json -m "bump:dev-release-WITH-Other-CHG, we expect to get them back after the bump" &>/dev/null && git stash pop


