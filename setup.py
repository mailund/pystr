from setuptools import setup, find_packages

setup(
    name='pystr',
    version='0.0.1',
    url="http://github.com/mailund/pystr",
    author="Thomas Mailund",
    author_email="thomas@mailund.dk",
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'show-exact=pystr_scripts.exact:main',
            'show-lcp-sa=pystr_scripts.lcp:show_lcp_sa',
            'show-skew=pystr_scripts.skew:show_skew',
            'show-bwt-transition=pystr_scripts.bwt:show_bwt_transition',
            'show-bwt-search=pystr_scripts.bwt:show_bwt_search',
            'show-trie=pystr_scripts.trie:show_trie',
            'show-suffixtree=pystr_scripts.suffixtree:show_suffixtree',
        ],
    },
    install_requires=[],
)
