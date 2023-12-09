
. scripts/version-patcher.sh
cversion=$(cat pyproject.toml |tr '"' " " |awk '/version/ {print $3}')
git commit . -m "v$cversion" && git tag "$cversion" && git push --tags && git push 

make dist && twine upload dist/*  &&         echo "Bypassed install and prep testing :  " \
	&&    echo "        pip install -U jgtfxcon==$cversion"
#&& sleep 29 &&  . pypi-conda-gaia-env.sh $1
