import BigWorld
import GUI
import Math

GREETER_MODEL_NAME = "characters/barbarian.model"

class Greeter( BigWorld.Entity ):

    def prerequisites( self ):
        # Make sure our model is loaded asynchronously before putting us 
        # into the world.
        return [ GREETER_MODEL_NAME ]

    def onEnterWorld( self, prereqs ):
        # The entity has entered this client's AoI and has been added to
        # the set of entities that this client knows about. Note that this
        # method is not called until all prerequisite resources have been 
        # loaded.

        # Model has been loaded and is in the engine resource cache. Construct
        # the model and assign it as the primary entity model.
        self.model = BigWorld.Model( GREETER_MODEL_NAME )

        # Setup an appropriate filter. Since this entity is never going to move
        # we can use the simple "dumb" filter (performs no interpolation).
        self.filter = BigWorld.DumbFilter()

        # Initialise some members.
        self._messageAttachment = None
        self._messageTimerHandle = None

    def onLeaveWorld( self ):
        # The entity has left this client's AoI and has been removed from
        # the set of entities that this client knows about.

        # Clean up our resources.
        self._clearMessage()
        self.model = None
        self.filter = None

    def use( self ):
        # Implement a generic "use" function so that when the player "uses"
        # this entity, it will toggle the activation state on the server.
        self.cell.toggleActive()

    def greet( self, targetID, msg ):
        # The server part of the entity has instructed us to "greet" the target
        # entity ID. 

        # Get the target entity. This client should know about the targe entity
        # since it's all happening in the same vicinity. In the few cases that 
        # we don't know about the entity (e.g. race condition between issuing 
        # command and the target leaving the AoI, or the Greeter and the target
        # entity are sitting right near the edge of the AoI) we can simply just
        # ignore the greet command.
        try:
            targetEntity = BigWorld.entities[targetID]
        except KeyError:
            return

        # Play the Wave action on our model (the Wave action is setup in 
        # Model Editor). Note how we can call the action as if it were
        # a standard Python method call. To stop the code from breaking
        # because the artist forgot to add an action, we can catch the
        # exception and print an error.
        try:
            self.model.Wave()
        except AttributeError:
            print "WARNING: Greeter model missing Wave action (%s)" % self.model.sources

        # Display the greet message above our head.
        addressee = targetEntity.name        
        if targetID == BigWorld.player().id:
            addressee += "! Yes you"

        self._displayMessage( "Hey %s! '%s'!" % (addressee, msg) )

    def set_activated( self, oldValue ):
        # This method is automatically called by the engine when the activated
        # property is changed by the server. This set_ prefix naming scheme will
        # work with any client exposed property.
        if self.activated:
            self._displayMessage( "Alright! I'm now ready to GREET." )
        else:
            self._displayMessage( "Shutting up now." )

    def _displayMessage( self, msg ):
        # Helper method to temporarily display a text message floating above
        # our head. This is achieved by creating a GUI text component, and
        # then using a GUI.Attachment to display the GUI element within the
        # 3D world.

        # First make sure any previous message is cleared.
        self._clearMessage()

        # Create our text component. Since we want to diplsay it in the world
        # we shall explicitly set our width and height in world units.
        text = GUI.Text( msg )
        text.explicitSize = True
        text.size = ( 0, 0.5 )             # Specifying 0 for x to auto-calculate aspect ratio.
        text.colour = (255, 0, 0, 255)     # Change the colour.
        text.filterType = "LINEAR"         # Don't use point filtering.
        text.verticalAnchor = "BOTTOM"     # Position relative to the bottom of the text.

        # The origin of our model is at our feet. To place the text above
        # our head, move it up on the Y by our model's height.
        text.position = (0, self.model.height + 0.1, 0)

        # Setup our GUI->World attachment. Tell it that we want the GUI 
        # component to always face the camera.
        atch = GUI.Attachment()
        atch.component = text
        atch.faceCamera = True

        # Attach to our model's root node. Another way of doing this might
        # be to create a specialised hard point within the model itself.
        # This would make the message position artist definable.
        self.model.root.attach( atch )

        # Save a reference to the attachment so we can clean it up later.
        self._messageAttachment = atch

        # Setup the timer.
        self._setMessageHideTimer()

    def _clearMessage( self ):
        # Helper method to remove any message currently above our head.    

        # Make sure any timer is cancelled.
        self._cancelMessageTimer()

        # Detach from our model and forget about it.
        if self._messageAttachment is not None:
            self.model.root.detach( self._messageAttachment )
            self._messageAttachment = None

    def _setMessageHideTimer( self, timeout=5.0 ):
        # Helper method to setup a timer to hide the message above our head 
        # after a given amount of time. If a timer already exists then we 
        # cancel it before resetting.
        self._cancelMessageTimer()

        self._messageTimerHandle = \
            BigWorld.callback( timeout, self._handleMessageHideTimer )

    def _cancelMessageTimer( self ):
        # Helper method to cancel any current timer callback.
        if self._messageTimerHandle is not None:
            BigWorld.cancelCallback( self._messageTimerHandle )
            self._messageTimerHandle = None

    def _handleMessageHideTimer( self ):
        # This will get called by the engine when the hide timer has
        # expired. Reset the timer handle and clear any message.
        self._messageTimerHandle = None
        self._clearMessage()

# Greeter.py
