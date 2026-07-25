from setuptools import find_packages, setup

package_name = "ab_harness"

setup(
    name=package_name,
    version="0.1.0",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    data_files=[
        ("share/ament_index/resource_index/packages", ["resource/" + package_name]),
        ("share/" + package_name, ["package.xml"]),
    ],
    python_requires=">=3.10",
    install_requires=["setuptools"],
    zip_safe=True,
    maintainer="juanbeck",
    maintainer_email="juanbeck@icloud.com",
    description="Pure-Python AB-grounded agent harness contracts and gates",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    license="BSD-3-Clause",
    extras_require={"test": ["pytest>=8"]},
)
