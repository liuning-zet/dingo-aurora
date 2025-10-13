openstack flavor create 2c4g100G --ram 4196 --disk 100 --vcpus 2 --public
openstack flavor set 2c4g100G --property hw:cpu_sockets=1 --property hw:cpu_cores=2 --property hw:numa_nodes=1 --property dingo_command_cluster=true
# ...existing code...

# 4c4g50g: 4 vCPUs, 4GB RAM, 50GB disk
openstack flavor create 4c4g50g --ram 4096 --disk 50 --vcpus 4 --public
openstack flavor set 4c4g50g --property hw:cpu_sockets=1 --property hw:cpu_cores=4 --property hw:numa_nodes=1 --property dingo_command_cluster=true

# 4c8g50g: 4 vCPUs, 8GB RAM, 50GB disk
openstack flavor create 4c8g50g --ram 8192 --disk 50 --vcpus 4 --public
openstack flavor set 4c8g50g --property hw:cpu_sockets=1 --property hw:cpu_cores=4 --property hw:numa_nodes=1 --property dingo_command_cluster=true


# 8c8g100g: 8 vCPUs, 8GB RAM, 100GB disk
openstack flavor create 8c8g100g --ram 8192 --disk 100 --vcpus 8 --public
openstack flavor set 8c8g100g --property hw:cpu_sockets=1 --property hw:cpu_cores=8 --property hw:numa_nodes=1 --property dingo_command_cluster=true


# 8c16g100g: 8 vCPUs, 16GB RAM, 100GB disk
openstack flavor create 8c16g100g --ram 16384 --disk 100 --vcpus 8 --public
openstack flavor set 8c16g100g --property hw:cpu_sockets=1 --property hw:cpu_cores=8 --property hw:numa_nodes=1 --property dingo_command_cluster=true


# 16c16g100g: 16 vCPUs, 16GB RAM, 100GB disk
openstack flavor create 16c16g100g --ram 16384 --disk 100 --vcpus 16 --public
openstack flavor set 16c16g100g --property hw:cpu_sockets=1 --property hw:cpu_cores=16 --property hw:numa_nodes=1 --property dingo_command_cluster=true


# 16c32g100g: 16 vCPUs, 32GB RAM, 100GB disk
openstack flavor create 16c32g100g --ram 32768 --disk 100 --vcpus 16 --public
openstack flavor set 16c32g100g --property hw:cpu_sockets=1 --property hw:cpu_cores=16 --property hw:numa_nodes=1 --property dingo_command_cluster=true


# 32c64g100g: 32 vCPUs, 64GB RAM, 100GB disk
openstack flavor create 32c64g100g --ram 65536 --disk 100 --vcpus 32 --public
openstack flavor set 32c64g100g --property hw:cpu_sockets=1 --property hw:cpu_cores=32 --property hw:numa_nodes=1 --property dingo_command_cluster=true
