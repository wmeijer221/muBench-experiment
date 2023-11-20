from subprocess import Popen
from time import sleep

def safe_apply_k8s_yaml_file(file_path: str, sleep_between_reapply: int = 30):
    """Applies a yaml field using kubectl"""
    # Deletes old deployment
    args = ["kubectl", "delete", "-f", file_path]
    proc = Popen(args)
    statuscode = proc.wait()
    if statuscode != 0:
        print(f'Could not delete "{file_path}".')
    print(f'Sleeping {sleep_between_reapply} seconds before reapplying "{file_path}".')
    sleep(sleep_between_reapply)
    # Applies the new one.
    args = ["kubectl", "create", "-f", file_path]
    proc = Popen(args)
    statuscode = proc.wait()
    if statuscode != 0:
        raise ValueError(f'Could not apply "{file_path}".')
