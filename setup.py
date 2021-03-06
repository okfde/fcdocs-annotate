from setuptools import find_packages, setup

setup(
    name="fcdocs_annotate",
    version="0.0.1",
    author="Magdalena Noffke",
    author_email="magdalena.noffke@okfn.de",
    license="MIT",
    url="https://github.com/okfde/fcdocs-annotate",
    install_requires=["django-filingcabinet"],
    packages=find_packages(),
    include_package_data=True,
)
