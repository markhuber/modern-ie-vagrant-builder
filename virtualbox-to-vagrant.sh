VERSION=20141027

function virtualbox_exist()
{
	local VM=$(vboxmanage list vms | grep -c "$VERSION-$1")
	if [ $VM -eq 0 ]
	then
		VBOXEXIST=0
	else
		VBOXEXIST=1
	fi

	return 0
}

function vagrant_file_exist()
{
	if [ -e "./box/$1_$VERSION.box" ]
	then
		VAGRANTFILEEXIST=1
	else
		VAGRANTFILEEXIST=0
	fi
	
	return 0	
}

function vagrant_exist()
{
	local VM=$(vagrant box list | grep -c "$1")
	if [ $VM -eq 0 ]
	then
		VAGRANTEXIST=0
	else
		VAGRANTEXIST=1
	fi
	
	return 0
}

function package()
{
	virtualbox_exist $1
	vagrant_file_exist $1
	vagrant_exist $1

	if [ $VBOXEXIST -eq 0 ]
	then
		echo "Virtualbox Image for $1 does not exist"
		return 1
	fi

	if [ $VAGRANTFILEEXIST -eq 0 ]
	then
		if [ $VAGRANTEXIST -eq 1 ]
		then
			vagrant box remove $1
			vagrant_exist $1
		fi
		vagrant package --base $VERSION-$1 --output ./box/$1_$VERSION.box --vagrantfile ./VagrantFile-Gui-WinRM
	fi

	if [ $VAGRANTEXIST -eq 0 ]
	then
		vagrant box add ./box/$1_$VERSION.box --name $1
	else
		echo "Vagrant box for $1 already imported."
	fi

	return 0
}

package IE6-WinXP
package IE8-WinXP
package IE7-Vista
package IE8-Win7 
package IE9-Win7 
package IE10-Win7
package IE10-Win8
package IE11-Win8.1
package IE11-Win7
package IE11-Win10
