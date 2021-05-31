from setuptools import setup

setup(
    name='pystr',
    version='0.0.1',
    url="http://github.com/mailund/pystr",
    author="Thomas Mailund",
    author_email="thomas@mailund.dk",
    packages=['pystr', 'pystr_vis'],
    entry_points={
        'console_scripts': [
            'show-exact=pystr_vis.exact:main',
            'show-trie=pystr_vis.trie:show_trie',
            'show-suffixtree=pystr_vis.suffixtree:show_suffixtree',
        ],
    },
    install_requires=[],
)
