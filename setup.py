from setuptools import setup, find_packages

setup(
    # The name of your package as it will appear on PyPI
    name="microweb",
    # The current version of your package
    version="0.1.1",
    # Automatically find all packages and subpackages
    packages=find_packages(),
    # Include non-code files specified in MANIFEST.in or package_data
    include_package_data=True,
    # Specify additional files to include in the package
    package_data={
        'microweb': ['firmware/*', 'static/*']
    },
    # List of dependencies to install with your package
    install_requires=['pyserial', 'esptool', 'click'],
    # Define command-line scripts to be generated
    entry_points={
        'console_scripts': [
            'microweb=microweb.cli:cli'
        ]
    },
    # Author information
    author="Your Name",
    # Short description of your package
    description="A web server framework for MicroPython . Easily build and deploy web applications using MicroPython.",
    # Long description, usually from your README file
    long_description=open("README.md").read(),
    # Format of the long description
    long_description_content_type="text/markdown",
    # URL to the project homepage
    url="https://github.com/ishanoshada/microweb",
    # Classifiers help users find your project by category
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Embedded Systems",
        "Topic :: Internet :: WWW/HTTP :: HTTP Servers",
    ],
    # Keywords for your project
    keywords="micropython, esp32, web server, embedded, iot, http, microcontroller, python",
)
