svn_stub.exe & p4_stub.exe are compiled using py2exe.
Even though we officialy support python 2.7.3, svn_stub.exe and p4_stub.exe must be compiled using 2.7.4.
This is due to either py2exe or pysvn (third party libs) having been built against 2.7.4.
If you try to compile svn_stub.exe or p4_stub.exe with 2.7.3 you will encounter an error "cannot import MAXREPEAT" when you try to run them.
This is due to an incompatibility between 2.7.4 and 2.7.3 where MAXREPEAT is not defined in versions prior to 2.7.4.