#pip install -U jgtutils
git commit pyproject.toml jgtfxcon/__init__.py package.json -m bump &>/dev/null
. /opt/binscripts/load.sh && _bump_jgtutils
. scripts/version-patcher.sh && \
cversion=$(cat pyproject.toml |tr '"' " " |awk '/version/ {print $3}') && \
(git commit . -m "v$cversion" ;git tag "$cversion" && git push --tags ;git push &> /dev/null) && \
make dist && twine upload dist/* &&         echo "Bypassed install and prep testing :  " && \
	(echo "conda deactivate && pip install --user -U jgtfxcon";echo pip install --user jgtfxcon==$cversion) && \
(echo "Building Docker image in +/- 30s...";sleep 33 ;. dkbuild.sh)

#(cd bin/base && dkbuild && dkpush) && echo "Docker image built and pushed to Docker Hub"



