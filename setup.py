import distribute_setup
distribute_setup.use_setuptools()

from setuptools import setup
from colorbuilder import __version__

setup(
	name = "colorbuilder",
	version = __version__,
	author = "Mark Riedesel",
	author_email = "mark@klowner.com",
	license = "GPL",
	keywords = "css template color",
	url = "https://github.com/Klowner/colorbuilder",
	packages = ['colorbuilder'],
	include_package_data = True,
	exclude_package_data = { 'examples':["*"] },
	entry_points = {
		'console_scripts': [
			'colorbuilder = colorbuilder:main',
		],
		'setuptools.installation': [
			'eggsecutable = colorbuilder:main',
		]
	},
	zip_safe = True,

)
