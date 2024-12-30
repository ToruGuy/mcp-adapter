from setuptools import setup, find_packages

setup(
    name="mcp-adapter",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "google-generativeai>=0.3.0",
        "openai>=1.0.0",
        "python-dotenv>=1.0.0",
        "mcp>=0.1.0"
    ]
)
