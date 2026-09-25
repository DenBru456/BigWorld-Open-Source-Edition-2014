import wx
import string
import os

import util

class Field( object ):
	def __init__( self, label, text ):
		self.label = label
		self.text = text

class OptionalField( Field ):
	def __init__( self, label, text, checkbox ):
		Field.__init__( self, label, text )
		self.checkbox = checkbox

class GetMultipleTextDialog( wx.Dialog ):
	"""Query a user for multiple text values, some of which may be optional."""

	PAD = 10

	def __init__( self, parent, title, fields ):
		wx.Dialog.__init__( self, parent, -1, "Enter Parameters" )

		self.fields = []

		# The top level sizer
		topSizer = wx.BoxSizer( wx.VERTICAL )
		topSizer.Add( wx.StaticText( self, -1, title ),
					  1, wx.ALL | wx.ALIGN_CENTRE, self.PAD )

		# Add in a row for each option
		for f in fields:

			label = f[ "label" ]
			optional = f.has_key( "opt" ) and f[ "opt" ] == "True"

			if f.has_key( "default" ):
				default = f[ "default" ]
			else:
				default = None
			if f.has_key( "tooltip" ):
				tooltip = f[ "tooltip" ]
			else:
				tooltip = None

			if optional:
				topSizer.Add(
					self.addOptionalField( label, default, tooltip, f ),
					0, wx.ALL|wx.EXPAND, self.PAD )
			else:
				topSizer.Add(
					self.addMandatoryField( label, default, tooltip, f ),
					0, wx.ALL|wx.EXPAND, self.PAD )

		# Section for OK/Cancel buttons at the bottom
		okButton = wx.Button( self, wx.ID_OK, "OK" ); okButton.SetDefault()
		cancelButton = wx.Button( self, wx.ID_CANCEL, "Cancel" )
		buttonSizer = wx.BoxSizer( wx.HORIZONTAL )
		buttonSizer.Add( okButton, 0, wx.ALL, self.PAD )
		buttonSizer.Add( cancelButton, 0, wx.ALL, self.PAD )
		topSizer.Add( buttonSizer, 0, wx.ALL | wx.ALIGN_CENTRE, self.PAD )

		self.SetAutoLayout( True )
		self.SetSizer( topSizer )
		topSizer.Fit( self )

		# If the user clicks OK, set up results
		if self.ShowModal() == wx.ID_OK:
			self.results = []
			for field in self.fields:
				if isinstance( field, OptionalField ):
					if field.checkbox.IsChecked():
						self.results.append( field.text )
					else:
						self.results.append( None )
				else:
					self.results.append( field.text )
		else:
			self.results = None

	def getSimpleResults( self ):
		if not self.results:
			return None
		else:
			return [ t.GetValue() for t in self.results ]

	def addMandatoryField( self, label, default, tooltip, field ):

		# The label
		st = wx.StaticText( self, wx.ID_ANY, label )
		if tooltip: st.SetToolTip( wx.ToolTip( tooltip ) )

		# The text entry control
		text = wx.TextCtrl( self, wx.ID_ANY )
		self.fields.append( Field( label, text ) )
		if default: text.SetValue( default )

		# Add bogus field hash in there for optional extras
		text.userFields = field

		rowSizer = wx.BoxSizer( wx.HORIZONTAL )
		rowSizer.Add( st, 1, wx.LEFT | wx.RIGHT | wx.ALIGN_CENTRE, self.PAD )
		rowSizer.Add( text, 1, wx.LEFT | wx.RIGHT | wx.ALIGN_CENTRE, self.PAD )
		return rowSizer

	def addOptionalField( self, label, default, tooltip, field ):

		# Checkbox to enable passing this option
		chkID = wx.NewId()
		chk = wx.CheckBox( self, chkID, label )

		# Text area where the user can input the option's value
		text = wx.TextCtrl( self, wx.ID_ANY )
		text.Enable( False )
		if default: text.SetValue( default )

		# Add bogus field hash in there for optional extras
		text.userFields = field

		# Tooltip to describe the option more fully.  I create two separate
		# tooltips because you get segfaults if you create a single one and bind
		# it to both controls for some bizarre reason ...
		if tooltip:
			chk.SetToolTip( wx.ToolTip( tooltip ) )
			text.SetToolTip( wx.ToolTip( tooltip ) )

		# When the checkbox is toggled, this enables setting the option
		def onCheck( evt ):
			if chk.IsChecked():
				text.Enable( True )
			else:
				text.Enable( False )

		wx.EVT_CHECKBOX( self, chkID, onCheck )
		self.fields.append( OptionalField( label, text, chk ) )

		rowSizer = wx.BoxSizer( wx.HORIZONTAL )
		rowSizer.Add( chk, 1, wx.LEFT | wx.RIGHT | wx.ALIGN_CENTRE, self.PAD )
		rowSizer.Add( text, 1, wx.LEFT | wx.RIGHT | wx.ALIGN_CENTRE, self.PAD )
		return rowSizer

class StartupDialog( GetMultipleTextDialog ):
	"""Reads cmdline args from a user and then starts a process."""

	def __init__( self, parent, dir, command, fields ):

		GetMultipleTextDialog.__init__(
			self, parent, "Starting %s" % command, fields )

		# Bail if the user hit cancel
		if not self.results:
			self.executed = False
			return

		# Glob together the cmdline args
		self.executed = True
		args = []
		for t in filter( lambda x: x, self.results):
			args.append( t.userFields[ "switch" ] )
			args.append( t.GetValue() )

		# Glob the cwd and requested dir onto the command
		command = util.getProgDir() + "/" + dir + "/" + command

		# Actually execute the command
		print "Executing %s %s" % (command, string.join( args, ' ' ))
		self.pid = os.spawnv( os.P_NOWAIT, command, [command] + args )
