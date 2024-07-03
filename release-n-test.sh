#pip install -U jgtutils

. scripts/version-patcher.sh
cversion=$(cat pyproject.toml |tr '"' " " |awk '/version/ {print $3}')
git commit . -m "v$cversion" ;git tag "$cversion" && git push --tags ;git push &> /dev/null 

make dist && twine upload dist/* &&         echo "Bypassed install and prep testing :  " && \
	(echo "conda deactivate && pip install --user -U jgtfxcon";echo pip install --user jgtfxcon==$cversion) 
	#&& \
	#(conda deactivate && conda deactivate && conda deactivate && pip install --user -U jgtfxcon;pip install --user jgtfxcon==$cversion) &> /dev/null

#	&&    echo "        pip install -U jgtfxcon==$cversion"
#&& sleep 29 &&  . pypi-conda-gaia-env.sh $1
