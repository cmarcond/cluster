import os
import subprocess
import time
from functools import wraps

def time_function(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        print(f"Function '{func.__name__}' took {end_time - start_time:.2f} seconds.")
        return result
    return wrapper

@time_function
def wait_for_machines():
    for _ in range(10):  # Retry up to 10 times
        result = subprocess.run(["vagrant", "status", "--machine-readable"], capture_output=True, text=True)
        lines = result.stdout.splitlines()
        machines = list(set([
            line.split(",")[1] for line in lines
            if "state" in line and "running" in line and not line.split(",")[1].startswith("ui") and line.split(",")[1].strip()
        ]))
        if machines:
            return machines
        time.sleep(5)
    print("Error: Machines are not running after waiting.")
    return []

@time_function
def generate_inventory_file(machines):
    inventory_file = "inventory.ini"
    ansible_cfg_file = "ansible.cfg"

    # Generate inventory.ini
    with open(inventory_file, "w") as inventory:
        inventory.write("[machines]\n")
        for machine in set(machines):  # Ensure unique entries
            # Get the machine's IP address
            try:
                ip_result = subprocess.run(
                    [
                        "vagrant", "ssh", machine, "-c",
                        "ip addr show eth1 | grep 'inet ' | awk '{print $2}' | cut -d/ -f1"
                    ],
                    capture_output=True, text=True, timeout=15
                )
                ip_address = ip_result.stdout.strip()

                if not ip_address:
                    print(f"Warning: No IP address found for {machine}. Skipping.")
                    continue

                # Path to the private key
                private_key_path = f".vagrant/machines/{machine}/virtualbox/private_key"

                # Write machine entry
                inventory.write(f"{machine} ansible_host={ip_address} ansible_user=vagrant ansible_ssh_private_key_file={private_key_path}\n")

            except subprocess.TimeoutExpired:
                print(f"Error: Timeout while fetching IP for {machine}. Skipping.")
            except Exception as e:
                print(f"Error: Unable to fetch details for {machine}: {e}")

    print(f"Inventory file '{inventory_file}' generated.")

    # Generate ansible.cfg
    with open(ansible_cfg_file, "w") as ansible_cfg:
        ansible_cfg.write("[defaults]\n")
        ansible_cfg.write("inventory = inventory.ini\n")
        ansible_cfg.write("host_key_checking = False\n")
        ansible_cfg.write("\n[privilege_escalation]\n")
        ansible_cfg.write("become = True\n")
        ansible_cfg.write("become_method = sudo\n")

    print(f"Ansible configuration file '{ansible_cfg_file}' generated.")

@time_function
def generate_inventory():
    machines = wait_for_machines()
    if machines:
        generate_inventory_file(machines)

if __name__ == "__main__":
    generate_inventory()
