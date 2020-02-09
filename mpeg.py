from struct import *

class Header:
    size=0
    type=""
    subtype=""

    def __init__(self, size, t, subt):
        self.size=size
        self.type=t
        self.subtype=subt

def GetHeaderSize(f):
    chunk = f.read(4)
    if len(chunk)!=4: return False
    size=unpack(">i",chunk)[0]
    return size-4

def GetHeader(f):
    size=GetHeaderSize(f)
    if not size: return False
    
    print("Header file size: {}".format(size))

    header=f.read(size)
    if len(header)!=size: return False

    print("="*16)
    type=header[:4].decode()
    print("File type: {}".format(type))
    subtype=header[4:8].decode()
    print("File subtype: {}".format(subtype))
    print("="*16)

    return Header(size, type, subtype)

class Atom:
    size=0
    type=""
    raw=b""

    def __init__(self, size, type, raw):
        self.size=size
        self.type=type
        self.raw=raw

def GetNextAtomStream(f):
    # Getting next atom size
    sizeb=f.read(4)
    if len(sizeb)!=4: return False
    size=unpack(">i",sizeb)[0] - 4 # removing the size of the 32 bit 'atom size' number
    
    # now getting next atom

    atom=f.read(size)
    if len(atom)>size: return False

    type=atom[:4].decode()

    return Atom(size, type, atom[4:])

def GetAtomsFromContent(content):
    atoms=[]
    s=0
    
    while s<len(content):
        # Getting next atom size
        sizeb=content[s:s+4]
        if len(sizeb)!=4:
            return False
        sizebdec=unpack(">i",sizeb)[0] # removing the size of the 32 bit 'atom size' number
        size=sizebdec-4

        # now getting next atom
        atom=content[s+4:s+size]
        if len(atom)>size:
            return False
        type=atom[:4].decode()
        #print(type, len(atom), size)
        atoms.append(Atom(size, type, atom[4:]))
        s+=sizebdec
    return atoms

class TrunAtom:
    flags=0
    sample_count=0
    data_offset=0
    entries=[]

def TrunAtom_Parse(atom):
    trun=TrunAtom()
    trun.entries=[]
    s=0

    trun.flags=unpack(">i",atom.raw[s:s+4])[0]
    s+=4
    trun.sample_count=unpack(">i",atom.raw[s:s+4])[0]
    s+=4
    trun.data_offset=unpack(">i",atom.raw[s:s+4])[0]
    s+=4

    while s<len(atom.raw):
        trun.entries.append(unpack(">i",atom.raw[s:s+4])[0])
        s+=4
    return trun


class MdatAtom_Frame:
    size=0
    raw=b''
    def __init__(self, size, raw):
        self.size=size
        self.raw=raw

class MdatAtom:
    frames=[]

def MdatAtom_Parse(mdat, trun):
    mdat_ret=MdatAtom()
    mdat_ret.frames=[]

    print(len(trun.entries))
    
    last=0
    for e in trun.entries:
        #print(last,last+e)
        mdat_ret.frames.append(
            MdatAtom_Frame(e, mdat.raw[last:last+e])
        )
        last=last+e
    return mdat_ret
