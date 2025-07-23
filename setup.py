from setuptools import setup, find_packages

setup(
    # The name of the package as it will appear on PyPI
    name="microweb",
    # Updated version to reflect new features (template engine with for loops, etc.)
    version="0.2.1",
    # Automatically find all packages and subpackages
    packages=find_packages(),
    # Include non-code files specified in MANIFEST.in or package_data
    include_package_data=True,
    # Specify additional files to include in the package
    package_data={
        'microweb': ['firmware/*', 'static/*']
    },
    # List of dependencies to install with the package
    install_requires=['pyserial', 'esptool', 'click', 'adafruit-ampy', 'mpremote'],
    # Define command-line scripts to be generated
    entry_points={
        'console_scripts': [
            'microweb=microweb.cli:cli'
        ]
    },
    # Author information
    author="Ishan Oshada",
    # Short description of the package, updated to highlight template engine
    description="A lightweight web server framework for MicroPython on ESP32, supporting dynamic routing, template rendering with for loops and conditionals, and static file serving.",
    # Long description from README file
    long_description=open("README.md", encoding="utf-8").read(),
    # Format of the long description
    long_description_content_type="text/markdown",
    # URL to the project homepage
    url="https://github.com/ishanoshada/microweb",
    # Classifiers to help users find the project by category
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Embedded Systems",
        "Topic :: Internet :: WWW/HTTP :: HTTP Servers",
        "Topic :: Software Development :: Libraries :: Application Frameworks",
    ],
    # Updated keywords to reflect new features
    keywords="micropython, esp32, web server, embedded, iot, http, microcontroller, python, template engine, for loops, conditionals, static files, json",
)