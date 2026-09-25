import weakref

class WeakMethodBound:
    def __init__( self , f ):
        self.f = f.im_func
        self.c = weakref.ref( f.im_self )
    def __call__( self , *arg ):
        if self.c() == None:
            raise TypeError , 'Method called on dead object'
        apply( self.f , ( self.c() , ) + arg )

class WeakMethodFree:
    def __init__( self , f ):
        self.f = weakref.ref( f )
    def __call__( self , *arg ):
        if self.f() == None:
            raise TypeError , 'Function no longer exist'
        apply( self.f() , arg )

def WeakMethod( f ):
    ''' WeakMethod implementation taken from
        http://code.activestate.com/recipes/81253/ '''
    try:
        f.im_func
    except AttributeError:
        return WeakMethodFree( f )
    return WeakMethodBound( f )
