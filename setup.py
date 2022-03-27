#
import setuptools

with open("README.md", encoding="utf-8") as readme_file:
    readme = readme_file.read()

setuptools.setup(
    name='chrome_manager',
    python_requires=">=3.6",
    long_description=readme,
    long_description_content_type="text/markdown",
    # packages=setuptools.find_packages(exclude=['tests']),
    include_package_data=True,
    version='0.0.33',
    description=(
        'Library to auto install chrome for Selenium usage.'),
    author='Luiz Antonio Lazoti',
    author_email='luizlazoti@hotmail.com',
    url='https://github.com/luizoti/chrome_manager.git',
    keywords=['testing', 'selenium', 'driver', 'test automation'],
    install_requires=[
        'requests',
        'webdriver-manager',
    ],
)
