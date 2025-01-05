from setuptools import setup, find_packages

setup(
    name="mcp-adapter",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "google-generativeai",
        "python-dotenv",
        "mcp"
    ]
)
