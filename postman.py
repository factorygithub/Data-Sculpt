import subprocess

def is_postman_installed():
    """Check if Postman is installed using PowerShell."""
    try:
        command = 'Get-AppxPackage -Name *Postman*'
        result = subprocess.run(["powershell", "-Command", command], capture_output=True, text=True)
        
        if "PackageFullName" in result.stdout:
            return True
        else:
            return False
    except Exception as e:
        print(f"Error checking Postman installation: {e}")
        return False

def uninstall_postman():
    """Uninstall Postman using PowerShell."""
    try:
        uninstall_command = 'Get-AppxPackage -Name *Postman* | Remove-AppxPackage'
        subprocess.run(["powershell", "-Command", uninstall_command], capture_output=True, text=True)
        print("Postman has been uninstalled successfully.")
    except Exception as e:
        print(f"Error uninstalling Postman: {e}")

# Main execution
if __name__ == "__main__":
    if is_postman_installed():
        print("Postman is installed. Uninstalling...")
        uninstall_postman()
    else:
        print("No")
