import struct
class NFTR:
    def __init__(self, data):
        self.d = bytearray(data)
        assert self.d[:4] == b'RTFN'
        hs = struct.unpack_from('<H', self.d, 0xC)[0]
        self.secs = []
        off = hs
        while off < len(self.d):
            mg = bytes(self.d[off:off+4]); sz = struct.unpack_from('<I', self.d, off+4)[0]
            self.secs.append((mg, off, sz)); off += sz
        self.finf = next(o for m,o,s in self.secs if m == b'FNIF')
        cglp_ptr, cwdh_ptr, cmap_ptr = struct.unpack_from('<III', self.d, self.finf + 0x10)
        self.cglp = cglp_ptr - 8; self.cwdh = cwdh_ptr - 8; self.cmap0 = cmap_ptr - 8
        c = self.cglp + 8
        self.tw, self.th, self.tsz = self.d[c], self.d[c+1], struct.unpack_from('<H', self.d, c+2)[0]
        self.bpp = self.d[c+6]
        self.gdata = c + 8
        self.nglyph = (struct.unpack_from('<I', self.d, self.cglp+4)[0] - 16) // self.tsz
        w = self.cwdh + 8
        self.w_first, self.w_last = struct.unpack_from('<HH', self.d, w)
        self.wdata = w + 8
    def glyph(self, i):
        o = self.gdata + i * self.tsz
        bits = int.from_bytes(self.d[o:o+self.tsz], 'big')
        tot = self.tsz * 8; px = []
        for y in range(self.th):
            row = []
            for x in range(self.tw):
                k = (y * self.tw + x) * self.bpp
                row.append((bits >> (tot - k - self.bpp)) & ((1 << self.bpp) - 1))
            px.append(row)
        return px
    def set_glyph(self, i, px):
        tot = self.tsz * 8; bits = 0
        for y in range(self.th):
            for x in range(self.tw):
                k = (y * self.tw + x) * self.bpp
                bits |= (px[y][x] & ((1 << self.bpp) - 1)) << (tot - k - self.bpp)
        o = self.gdata + i * self.tsz
        self.d[o:o+self.tsz] = bits.to_bytes(self.tsz, 'big')
    def width(self, i):
        o = self.wdata + (i - self.w_first) * 3
        return struct.unpack_from('<bBB', self.d, o)
    def set_width(self, i, t):
        struct.pack_into('<bBB', self.d, self.wdata + (i - self.w_first) * 3, *t)
    def cmaps(self):
        out = []; p = self.cmap0
        while True:
            lo, hi, method = struct.unpack_from('<HHH', self.d, p + 8)
            nxt = struct.unpack_from('<I', self.d, p + 16)[0]
            out.append((p, lo, hi, method, nxt)); 
            if nxt == 0: break
            p = nxt - 8
        return out
    def lookup(self, code):
        for p, lo, hi, m, nxt in self.cmaps():
            if m == 0 and lo <= code <= hi:
                return struct.unpack_from('<H', self.d, p + 20)[0] + (code - lo)
            if m == 1 and lo <= code <= hi:
                v = struct.unpack_from('<H', self.d, p + 20 + (code - lo) * 2)[0]
                if v != 0xFFFF: return v
            if m == 2:
                n = struct.unpack_from('<H', self.d, p + 20)[0]
                for j in range(n):
                    c, g = struct.unpack_from('<HH', self.d, p + 22 + j * 4)
                    if c == code: return g
        return None
    def set_map1(self, code, glyph):
        for p, lo, hi, m, nxt in self.cmaps():
            if m == 1 and lo <= code <= hi:
                struct.pack_into('<H', self.d, p + 20 + (code - lo) * 2, glyph); return p
        raise KeyError(hex(code))
