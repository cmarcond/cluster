import os

def generate_inventory():
    output_file = "inventory.ini"

    try:
        ssh_pass = os.getenv("SSH_PASS")
        if not ssh_pass:
            print("Error: SSH_PASS environment variable is not set.")
            return

        # Prompt for the number of machines
        num_machines = int(input("How many physical machines would you like to add? "))

        machines = []
        for i in range(1, num_machines + 1):
            print(f"Enter details for machine {i}:")
            ip_address = input("  IP address: ").strip()
            machines.append((f"machine{i:02}", ip_address))

        with open(output_file, "w") as outfile:
            outfile.write("[machines]\n")
            for name, ip in machines:
                outfile.write(f"{name} ansible_host={ip} ansible_user=cesar\n")

        print(f"Inventory file has been generated and saved to {output_file}")

        print("\nTo use SSH_PASS from an environment variable, update your ansible.cfg:\n")
        print("[defaults]\n")
        print("vault_password_file = ~/.ansible_vault_password\n")
        print("\nThen use 'ansible-playbook' with the --ask-pass flag or configure SSH keys.")

    except ValueError:
        print("Error: Please enter a valid number of machines.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    generate_inventory()
