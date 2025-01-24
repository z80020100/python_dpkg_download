#!/usr/bin/env python3

import requests
import gzip
from io import BytesIO


def download_deb_from_repo(repo_url, package_name, arch="amd64", dist="stable", component="main"):
    print(f"Try to download package {package_name} from {repo_url}")
    print(f"Architecture: {arch}")
    print(f"Distribution: {dist}")
    print(f"Component: {component}")

    packages_gz_url = f"{
        repo_url}/dists/{dist}/{component}/binary-{arch}/Packages.gz"

    try:
        response = requests.get(packages_gz_url)
        response.raise_for_status()

        with gzip.GzipFile(fileobj=BytesIO(response.content)) as f:
            packages_content = f.read().decode('utf-8')

        packages = []
        current_pkg = {}
        current_key = None

        for line in packages_content.splitlines():
            stripped_line = line.strip()
            if not stripped_line:
                if current_pkg:
                    packages.append(current_pkg)
                    current_pkg = {}
                    current_key = None
                continue

            if line.startswith(' '):
                if current_key and current_key in current_pkg:
                    current_pkg[current_key] += '\n' + line.strip()
                continue

            if ': ' not in line:
                continue  # Ignore invalid lines

            key, value = line.split(': ', 1)
            current_key = key
            current_pkg[key] = value

        if current_pkg:
            packages.append(current_pkg)

        matched_pkgs = [pkg for pkg in packages if pkg.get(
            "Package") == package_name]
        if not matched_pkgs:
            print(f"Error: cannot find package {package_name}")
            return

        latest_pkg = sorted(
            matched_pkgs, key=lambda x: x["Version"], reverse=True)[0]
        print(f"The latest version is {latest_pkg['Version']}")

        filename = latest_pkg["Filename"]
        deb_url = f"{repo_url}/{filename}"
        print(f"Download {deb_url}")

        deb_response = requests.get(deb_url)
        deb_response.raise_for_status()
        output_file = f"{package_name}.deb"
        with open(output_file, "wb") as f:
            f.write(deb_response.content)
        print(f"Saved to {output_file}")

    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")


def main():
    REPO_URL = "https://deb.debian.org/debian/"
    PACKAGE_NAME = "htop"
    download_deb_from_repo(REPO_URL, PACKAGE_NAME)


if __name__ == "__main__":
    main()
