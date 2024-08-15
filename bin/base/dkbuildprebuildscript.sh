
BDIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
. $BDIR/_env.sh
rm -rf $BDIR/dist
if [ -d $BDIR/../../dist ];then
  cp -r $BDIR/../../dist $BDIR

else 
  #Assume we want to make dist
  (cd $BDIR/../../ && make dist) || exit 1
  cp -r $BDIR/../../dist $BDIR
fi
