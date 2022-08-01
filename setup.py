from setuptools import setup

setup(
    name="mkdocs-term-validator",
    version='0.0.1',
    description="",
    long_description="",
    py_modules=['mkdocs_term_validator'],
    entry_points={
        "mkdocs.plugins": ["term-validator = mkdocs_term_validator:TermValidatorPlugin"]
    },
)
