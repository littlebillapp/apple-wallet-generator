from setuptools import setup

setup(
    name="apple-wallet-generator",
    version="1.0.3",
    description="A tool to generate Apple Wallet passes",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Geoffrey Sautreau",
    author_email="geoffrey@littlebill.io",
    url="https://github.com/littlebillapp/apple-wallet-generator",
    packages=["apple_wallet_generator"],
    install_requires=[
        "cffi==1.14.4",
        "pycparser==2.20",
        "six==1.15.0",
        "cryptography>=3.3.1",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
