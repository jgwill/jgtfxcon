




oldjgtfx2consoleversion=$(cat pyproject.toml|grep "jgtfx2console"|tr '>' ' '|tr "'" " "|tr "=" " "|tr "," " "|awk '{print $2}')
. .env 
(conda activate $WS_CONDA_ENV_NAME&>/dev/null;pip install -U jgtfx2console|tr '(' ' '|tr ')' ' '|grep "jgtfx2console in"|awk '/jgtfx2console/{print $7}')
newjgtfx2consoleversion=$(conda activate $WS_CONDA_ENV_NAME&>/dev/null;pip install -U jgtfx2console|tr '(' ' '|tr ')' ' '|grep "jgtfx2console in"|awk '/jgtfx2console/{print $7}')

# We want to replace jgtfx2console>=0.4.70 with jgtfx2console>=0.4.71
## run if they are different
if [ "$oldjgtfx2consoleversion" == "$newjgtfx2consoleversion" ]; then
    echo "No need to update jgtfx2console version in $WS_CONDA_ENV_NAME package/env"
else

	sed -i "s/jgtfx2console>=$oldjgtfx2consoleversion/jgtfx2console>=$newjgtfx2consoleversion/g" pyproject.toml
	git add pyproject.toml &>/dev/null
	git commit -m "auto bump:jgtfx2console  $oldjgtfx2consoleversion to $newjgtfx2consoleversion"&>/dev/null
fi


#(conda activate baseprod && pip install --user -U jgtfx2console) &>/dev/null &

