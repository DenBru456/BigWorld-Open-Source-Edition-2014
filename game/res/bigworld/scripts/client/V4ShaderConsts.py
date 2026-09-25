#Vector4Shader helper script
#
#Note - if script_math's Vector4Shader is updated, this must be kept in line.
import Math

#These opcodes take 1 parameter
_mov = 0		#move parm1 to output
_rcp = 1		#put the reciprocal of parm1 in output
_bias = 2		#bias parm1 by -0.5 and place in output
_comp = 3		#output = 1.0 - parm1

#These opcodes take 2 paramters
_mul = 4		#out = parm1 * parm2
_div = 5		#out = parm1 / parm2
_add = 6		#out = parm1 + parm2
_sub = 7		#out = parm1 - parm2
_dot = 8		#out = parm1 dot( parm2 )
_min = 9		#out = min( parm1, parm2 )
_max = 10		#out = max( parm1, parm2 )
_sge = 11		#out = ( parm1 >= parm2 )
_slt = 12		#out = ( parm1 < parm2 )


#These are 16 of the temporary registers
_r0 = Math.getRegister(0)
_r1 = Math.getRegister(1)
_r2 = Math.getRegister(2)
_r3 = Math.getRegister(3)
_r4 = Math.getRegister(4)
_r5 = Math.getRegister(5)
_r6 = Math.getRegister(6)
_r7 = Math.getRegister(7)
_r8 = Math.getRegister(8)
_r9 = Math.getRegister(9)
_r10 = Math.getRegister(10)
_r11 = Math.getRegister(11)
_r12 = Math.getRegister(12)
_r13 = Math.getRegister(13)
_r14 = Math.getRegister(14)
_r15 = Math.getRegister(15)