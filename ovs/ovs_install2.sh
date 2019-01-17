cd ovs

./boot.sh
./configure -with-linux=/lib/modules/$(uname -r)/build --enable-Werror
make
make install
config_file="/etc/depmod.d/openvswitch.conf"
for module in datapath/linux/*.ko; do
    modname="\$(basename \${module})"
    echo "override \${modname%.ko} * extra" >> "\$config_file"
    echo "override \${modname%.ko} * weak-updates" >> "\$config_file"
done

depmod -a
/sbin/modprobe openvswitch

export PATH=$PATH:/usr/local/share/openvswitch/scripts
ovs-ctl start
