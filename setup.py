import setuptools

setuptools.setup(
    name="myapp",
    version="0.0.1",
    author="ofelya",
    author_email="ofelyaaaliyeva@gmail.com",
    python_requires=">=3.6",
    packages=setuptools.find_packages(),
    install_requires=[
        "spotipy~=2.23.0",
        "streamlit~=1.35.0",
        "faicons",
        "shiny",
        "seaborn",
        "pandas~=2.0.3",
        "plotly~=5.9.0",
        "scikit-learn~=1.3.0",
    ],
)
