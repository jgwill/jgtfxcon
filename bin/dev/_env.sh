ctlid=2408011203
dockertag=jgwill/jgt:fxcon-dev
dockertag1=jgwill/jgt:fxcon #so we can use the cli wrapper dkfxcli

containername=fxdev
dkhostname=$containername

# PORT
#dkport=4000:4000

xmount=$HOME/.jgt/config.json:/home/user/.jgt/config.json
xmount2=$HOME/.jgt/settings.json:/home/user/.jgt/settings.json
#xmount2=/var:/a/var


dkcommand=bash #command to execute (default is the one in the dockerfile)
# dkextra=" -e user_id=$user_id \
#   -e password=$password \
#   -e url=$url "


#dkextra=" -v \$dworoot/x:/x -p 2288:2288 "

#dkmounthome=true


##########################
############# RUN MODE
#dkrunmode="bg" #default fg
#dkrestart="--restart" #default
#dkrestarttype="unless-stopped" #default


#########################################
################## VOLUMES
#dkvolume="myvolname220413:/app" #create or use existing one
#dkvolume="$containername:/app" #create with containername name



#dkecho=true #just echo the docker run


# Use TZ
#DK_TZ=1



#####################################
#Build related
#
##chg back to that user
#dkchguser=vscode

######################## HOOKS BASH
### IF THEY EXIST, THEY are Executed, you can change their names

dkbuildprebuildscript=dkbuildprebuildscript.sh
dkbuildbuildsuccessscript=dkbuildbuildsuccessscript.sh
dkbuildfailedscript=dkbuildfailedscript.sh
dkbuildpostbuildscript=dkbuildpostbuildscript.sh

###########################################
# Unset deprecated
unset DOCKER_BUILDKIT

