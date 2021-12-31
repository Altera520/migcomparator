from setuptools import setup
setup(
    name='mypackage',
    version='0.0.1',
    packages=['mypackage'],
    install_requires=[
        'requests',                                     # 최신버전 설치
        'pandas >= 3.0',                                # 버전 특정
        "pywin32 >= 1.0;platform_system=='Windows'",    # 플랫폼 구분
        'importlib; python_version >= "3.5"',
    ],
)