from setuptools import setup, find_packages

setup(
    name='budget_app',
    version='0.1.0',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'flask',
        'flask-sqlalchemy',
        'flask-login',
        'werkzeug',
        'google-generativeai'
    ],
    entry_points={
        'console_scripts': [
            'budget-app = budget_app.run:main'
        ]
    }
)