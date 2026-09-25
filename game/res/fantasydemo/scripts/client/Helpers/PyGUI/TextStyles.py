import BigWorld, GUI, Math, ResMgr
from bwdebug import ERROR_MSG



styles = {
	'Heading': ('Heading.font', (255,255,255,255)),
	'Label': ('Label.font', (255,255,255,255)),

	'ButtonNormal': ('Heading.font', (255,255,255,200)),
	'ButtonHover': ('Heading.font', (255,255,255,255)),
	'ButtonPressed': ('Heading.font', (255,255,255,255)),
	'ButtonActive': ('Heading.font', (0,0,0,255)),
	'ButtonDisabled': ('Heading.font', (128,128,128,255)),
	
	'MainMenuButtonNormal': ('default_medium.font', (255,255,255,255)),
	'MainMenuButtonHover': ('default_medium.font', (255,255,255,255)),
	'MainMenuButtonPressed': ('default_medium.font', (255,255,255,255)),
	'MainMenuButtonActive': ('default_medium.font', (255,255,255,255)),
	'MainMenuButtonDisabled': ('default_medium.font', (128,128,128,255)),
	
	'MainMenuBackButtonNormal': ('default_small.font', (255,255,255,255)),
	'MainMenuBackButtonHover': ('default_small.font', (255,255,255,255)),
	'MainMenuBackButtonPressed': ('default_small.font', (255,255,255,255)),
	'MainMenuBackButtonActive': ('default_small.font', (255,255,255,255)),
	'MainMenuBackButtonDisabled': ('default_small.font', (128,128,128,255)),
}

fontAliases = {}

def setStyle( component, styleName ):
	if styles.has_key( styleName ):
		style = styles[ styleName ]
		component.font = fontAliases.get( style[0], style[0] )
		component.colour = style[1]
	else:
		ERROR_MSG( "No style named '%s'." % (styleName,) )

