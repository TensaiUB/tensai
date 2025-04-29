import subprocess
import pkg_resources
import sys
import logging


logger = logging.getLogger(__name__)

def check_dependencies():
    print("Checking packages...")
    requirements_file = "requirements.txt"

    with open(requirements_file) as f:
        required = f.read().splitlines()

    installed_packages = {pkg.key: pkg.version for pkg in pkg_resources.working_set}

    missing_or_outdated = []
    for req in required:
        try:
            logger.info(f"Checking package: {req}")
            requirement = pkg_resources.Requirement.parse(req)
            installed_version = installed_packages.get(requirement.key)
            if installed_version is None or installed_version not in requirement:
                missing_or_outdated.append(req)
        except ValueError as e:
            logger.error(f"Error while installing package: {req}\nError: {e}")
            print(f"⚠️ Error while installing package: {req}")

    if missing_or_outdated:
        print(
            f"Installing missing packages: {', '.join(req for req in missing_or_outdated)}"
        )
        logger.info(
            f"Installing missing packages: {', '.join(req for req in missing_or_outdated)}"
        )
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", *missing_or_outdated]
        )


check_dependencies()
