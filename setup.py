from setuptools import setup

version = __import__("apple-wallet-generator").__version__

setup(
    name="apple-wallet-generator",
    version=version,
    author="Geoffrey Sautreau",
    author_email="geoffrey@littlebill.io",
    packages=["apple-wallet-generator"],
    url="https://github.com/littlebillapp/apple-wallet-generator",
    license=open("LICENSE.txt").read(),
    description="Apple Wallet file generator",
    long_description=open("README.md").read(),
    install_requires=[
        "cryptography>=3.3.1",
    ],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Other Environment",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3 :: Only",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
)
