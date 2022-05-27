var lzr = {};
lzr.engine = {};
lzr.engine.geom = {};
lzr.utils = {}

lzr.utils.intFromBytes = function(a, c, b) {
    for (var f = 0; c < b; ++c) {
        f += a[c]
        c < b - 1 && (f <<= 8)
    }
    return f;
};

lzr.engine.geom.Point = function(a, c) {
    this.x = a || 0;
    this.y = c || 0
};

lzr.engine.geom.Point.toPoint = function(a) {
    if (a) {
        if (a instanceof lzr.engine.geom.Point) return a;
        if ("number" === typeof a.x) return new lzr.engine.geom.Point(a.x, a.y);
        if ("string" === typeof a.x) {
            var c = parseFloat(a.x);
            a = parseFloat(a.y);
            if (!isNaN(c) && !isNaN(a)) return new lzr.engine.geom.Point(c,
                a)
        }
    }
    return null
};

function decodeArrayBuffer(a) {
    var keyStr = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/=";
    var c = new ArrayBuffer(a.length / 4 * 3);
    return this.decode(a, c)
}

function decode(a, c) {
    var keyStr= "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/=";

    var b = keyStr.indexOf(a.charAt(a.length -
            1)),
        f = keyStr.indexOf(a.charAt(a.length - 2)),
        d = a.length / 4 * 3;
    64 === b && d--;
    64 === f && d--;
    for (var e, k, h, l, m = 0, b = c ? new Uint8Array(c) : new Uint8Array(d), g = 0; g < d; g += 3) {
        e = keyStr.indexOf(a.charAt(m++))
        k = keyStr.indexOf(a.charAt(m++))
        f = keyStr.indexOf(a.charAt(m++))
        l = keyStr.indexOf(a.charAt(m++))
        e = e << 2 | k >> 4
        k = (k & 15) << 4 | f >> 2
        h = (f & 3) << 6 | l
        b[g] = e
        64 !== f && (b[g + 1] = k)
        64 !== l && (b[g + 2] = h)
    }
    return b
}

export function decodeBorder(a){
    var b = [];
    if ("string" === typeof a) {
        a = decode(a);
        for (var d = 0, c = a.length; d < c; d += 4) {
            var f = lzr.utils.intFromBytes(a, d, d + 2),
                g = lzr.utils.intFromBytes(a, d + 2, d + 4);
            b.push(new lzr.engine.geom.Point(f, g))
        }
    } else b = a.map(lzr.engine.geom.Point.toPoint);return b
}