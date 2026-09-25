# Useful utility class when working with CLASS types.
# For example, if you have a CLASS type:
# 	<Type>		CLASS
#		<Properties>
#			<intMem> <Type> INT32 </Type> </intMem>
#			<stringMem> <Type> STRING </Type> </stringMem>
#			<arrayMem> <Type> ARRAY <of> UINT64 </of> </Type> </arrayMem>
#		</Properties>
#	</Type>
# You can initialise a property of this type by:
#	entity.classProp = ClassType( intMem = 1, stringMem = "Hi!", arrayMem = [] )
class ClassType:
	def __init__( self, **members ):
		self.__dict__.update( members )
