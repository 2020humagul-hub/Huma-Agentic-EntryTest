
import json
import urllib.request
import urllib.error
from datetime import datetime


def get_pypi_data(url):
    """Fetch JSON data from PyPI. Return None if the URL doesn't exist."""
    try:
        with urllib.request.urlopen(url, timeout=10) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as error:
        if error.code == 404:
            return None
        print(f"HTTP error: {error.code} for {url}")
        return None
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError):
        print(f"Could not retrieve data from: {url}")
        return None


def main():
    with open("requirements.txt", "r", encoding="utf-8") as file:
        lines = [
            line.strip()
            for line in file
            if line.strip() and not line.strip().startswith("#")
        ]

    dependencies_checked = len(lines)
    packages_not_found = 0
    versions_not_found = 0
    valid_releases = []

    for line in lines:
        if "==" not in line:
            print(f"Skipping unsupported requirement: {line}")
            continue

        name, version = line.split("==", 1)
        name = name.strip()
        version = version.strip()

        package_url = f"https://pypi.org/pypi/{name}/json"
        package_data = get_pypi_data(package_url)

        if package_data is None:
            packages_not_found += 1
            continue

        version_url = f"https://pypi.org/pypi/{name}/{version}/json"
        version_data = get_pypi_data(version_url)

        if version_data is None:
            versions_not_found += 1
            continue

        urls = version_data.get("urls", [])
        if not urls:
            continue

        upload_time = urls[0].get("upload_time")
        if not upload_time:
            continue

        try:
            year = datetime.fromisoformat(
                upload_time.replace("Z", "+00:00")
            ).year
        except ValueError:
            continue

        valid_releases.append((upload_time, name, version, year))

    print(f"Dependencies checked: {dependencies_checked}")
    print(f"Packages not on PyPI: {packages_not_found}")
    print(f"Versions not on PyPI: {versions_not_found}")

    if valid_releases:
        oldest = min(valid_releases, key=lambda release: release[0])
        print(
            f"Oldest pinned release: "
            f"{oldest[1]}=={oldest[2]} ({oldest[3]})"
        )
    else:
        print("Oldest pinned release: None")


if __name__ == "__main__":
    main()
