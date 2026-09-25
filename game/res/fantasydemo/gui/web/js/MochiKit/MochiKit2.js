/***

MochiKit.MochiKit 1.5

See <http://mochikit.com/> for documentation, downloads, license, etc.

(c) 2005 Bob Ippolito.  All rights Reserved.

***/

if (typeof(MochiKit) == 'undefined') {
    MochiKit = {};
}

if (typeof(MochiKit.MochiKit) == 'undefined') {
    /** @id MochiKit.MochiKit */
    MochiKit.MochiKit = {};
}

MochiKit.MochiKit.NAME = "MochiKit.MochiKit";
MochiKit.MochiKit.VERSION = "1.5";
MochiKit.MochiKit.__repr__ = function () {
    return "[" + this.NAME + " " + this.VERSION + "]";
};

/** @id MochiKit.MochiKit.toString */
MochiKit.MochiKit.toString = function () {
    return this.__repr__();
};

/***

MochiKit.Base 1.5

See <http://mochikit.com/> for documentation, downloads, license, etc.

(c) 2005 Bob Ippolito.  All rights Reserved.

***/

if (typeof(MochiKit) == 'undefined') {
    MochiKit = {};
}
if (typeof(MochiKit.__export__) == "undefined") {
    MochiKit.__export__ = true;
}
if (typeof(MochiKit.Base) == 'undefined') {
    MochiKit.Base = {};
}

/**
 * Registers a new MochiKit module. This function will insert a new
 * property into the "MochiKit" object, making sure that all
 * dependency modules have already been inserted. It will also make
 * sure that the appropriate properties and default module functions
 * are defined.
 *
 * @param {String} name the module name, e.g. "Base"
 * @param {String} version the module version, e.g. "1.5"
 * @param {Array} deps the array of module dependencies (as strings)
 */
MochiKit.Base._module = function (name, version, deps) {
    if (!(name in MochiKit)) {
        MochiKit[name] = {};
    }
    var module = MochiKit[name];
    module.NAME = "MochiKit." + name;
    module.VERSION = version;
    module.__repr__ = function () {
        return "[" + this.NAME + " " + this.VERSION + "]";
    };
    module.toString = function () {
        return this.__repr__();
    };
    for (var i = 0; i < deps.length; i++) {
        if (!(deps[i] in MochiKit)) {
            throw 'MochiKit.' + name + ' depends on MochiKit.' + deps[i] + '!';
        }
    }
}

MochiKit.Base._module("Base", "1.5", []);

/** @id MochiKit.Base.update */
MochiKit.Base.update = function (self, obj/*, ... */) {
    if (self === null || self === undefined) {
        self = {};
    }
    for (var i = 1; i < arguments.length; i++) {
        var o = arguments[i];
        if (typeof(o) != 'undefined' && o !== null) {
            for (var k in o) {
                self[k] = o[k];
            }
        }
    }
    return self;
};

MochiKit.Base.update(MochiKit.Base, {
    /** @id MochiKit.Base.camelize */
    camelize: function (selector) {
        /* from dojo.style.toCamelCase */
        var arr = selector.split('-');
        var cc = arr[0];
        for (var i = 1; i < arr.length; i++) {
            cc += arr[i].charAt(0).toUpperCase() + arr[i].substring(1);
        }
        return cc;
    },

    /** @id MochiKit.Base.counter */
    counter: function (n/* = 1 */) {
        if (arguments.length === 0) {
            n = 1;
        }
        return function () {
            return n++;
        };
    },

    /** @id MochiKit.Base.clone */
    clone: function (obj) {
        var me = arguments.callee;
        if (arguments.length == 1) {
            me.prototype = obj;
            return new me();
        }
    },
    
    _flattenArray: function (res, lst) {
        for (var i = 0; i < lst.length; i++) {
            var o = lst[i];
            if (o instanceof Array) {
                arguments.callee(res, o);
            } else {
                res.push(o);
            }
        }
        return res;
    },

    /** @id MochiKit.Base.flattenArray */
    flattenArray: function (lst) {
        return MochiKit.Base._flattenArray([], lst);
    },

    /** @id MochiKit.Base.flattenArguments */
    flattenArguments: function (lst/* ...*/) {
        var res = [];
        var m = MochiKit.Base;
        var args = m.extend(null, arguments);
        while (args.length) {
            var o = args.shift();
            if (o && typeof(o) == "object" && typeof(o.length) == "number") {
                for (var i = o.length - 1; i >= 0; i--) {
                    args.unshift(o[i]);
                }
            } else {
                res.push(o);
            }
        }
        return res;
    },

    /** @id MochiKit.Base.extend */
    extend: function (self, obj, /* optional */skip) {
        // Extend an array with an array-like object starting
        // from the skip index
        if (!skip) {
            skip = 0;
        }
        if (obj) {
            // allow iterable fall-through, but skip the full isArrayLike
            // check for speed, this is called often.
            var l = obj.length;
            if (typeof(l) != 'number' /* !isArrayLike(obj) */) {
                if (typeof(MochiKit.Iter) != "undefined") {
                    obj = MochiKit.Iter.list(obj);
                    l = obj.length;
                } else {
                    throw new TypeError("Argument not an array-like and MochiKit.Iter not present");
                }
            }
            if (!self) {
                self = [];
            }
            for (var i = skip; i < l; i++) {
                self.push(obj[i]);
            }
        }
        // This mutates, but it's convenient to return because
        // it's often used like a constructor when turning some
        // ghetto array-like to a real array
        return self;
    },


    /** @id MochiKit.Base.updatetree */
    updatetree: function (self, obj/*, ...*/) {
        if (self === null || self === undefined) {
            self = {};
        }
        for (var i = 1; i < arguments.length; i++) {
            var o = arguments[i];
            if (typeof(o) != 'undefined' && o !== null) {
                for (var k in o) {
                    var v = o[k];
                    if (typeof(self[k]) == 'object' && typeof(v) == 'object') {
                        arguments.callee(self[k], v);
                    } else {
                        self[k] = v;
                    }
                }
            }
        }
        return self;
    },

    /** @id MochiKit.Base.setdefault */
    setdefault: function (self, obj/*, ...*/) {
        if (self === null || self === undefined) {
            self = {};
        }
        for (var i = 1; i < arguments.length; i++) {
            var o = arguments[i];
            for (var k in o) {
                if (!(k in self)) {
                    self[k] = o[k];
                }
            }
        }
        return self;
    },

    /** @id MochiKit.Base.keys */
    keys: function (obj) {
        var rval = [];
        for (var prop in obj) {
            rval.push(prop);
        }
        return rval;
    },

    /** @id MochiKit.Base.values */
    values: function (obj) {
        var rval = [];
        for (var prop in obj) {
            rval.push(obj[prop]);
        }
        return rval;
    },

     /** @id MochiKit.Base.items */
    items: function (obj) {
        var rval = [];
        var e;
        for (var prop in obj) {
            var v;
            try {
                v = obj[prop];
            } catch (e) {
                continue;
            }
            rval.push([prop, v]);
        }
        return rval;
    },


    _newNamedError: function (module, name, func) {
        func.prototype = new MochiKit.Base.NamedError(module.NAME + "." + name);
        module[name] = func;
    },


    /** @id MochiKit.Base.operator */
    operator: {
        // unary logic operators
        /** @id MochiKit.Base.truth */
        truth: function (a) { return !!a; },
        /** @id MochiKit.Base.lognot */
        lognot: function (a) { return !a; },
        /** @id MochiKit.Base.identity */
        identity: function (a) { return a; },

        // bitwise unary operators
        /** @id MochiKit.Base.not */
        not: function (a) { return ~a; },
        /** @id MochiKit.Base.neg */
        neg: function (a) { return -a; },

        // binary operators
        /** @id MochiKit.Base.add */
        add: function (a, b) { return a + b; },
        /** @id MochiKit.Base.sub */
        sub: function (a, b) { return a - b; },
        /** @id MochiKit.Base.div */
        div: function (a, b) { return a / b; },
        /** @id MochiKit.Base.mod */
        mod: function (a, b) { return a % b; },
        /** @id MochiKit.Base.mul */
        mul: function (a, b) { return a * b; },

        // bitwise binary operators
        /** @id MochiKit.Base.and */
        and: function (a, b) { return a & b; },
        /** @id MochiKit.Base.or */
        or: function (a, b) { return a | b; },
        /** @id MochiKit.Base.xor */
        xor: function (a, b) { return a ^ b; },
        /** @id MochiKit.Base.lshift */
        lshift: function (a, b) { return a << b; },
        /** @id MochiKit.Base.rshift */
        rshift: function (a, b) { return a >> b; },
        /** @id MochiKit.Base.zrshift */
        zrshift: function (a, b) { return a >>> b; },

        // near-worthless built-in comparators
        /** @id MochiKit.Base.eq */
        eq: function (a, b) { return a == b; },
        /** @id MochiKit.Base.ne */
        ne: function (a, b) { return a != b; },
        /** @id MochiKit.Base.gt */
        gt: function (a, b) { return a > b; },
        /** @id MochiKit.Base.ge */
        ge: function (a, b) { return a >= b; },
        /** @id MochiKit.Base.lt */
        lt: function (a, b) { return a < b; },
        /** @id MochiKit.Base.le */
        le: function (a, b) { return a <= b; },

        // strict built-in comparators
        seq: function (a, b) { return a === b; },
        sne: function (a, b) { return a !== b; },

        // compare comparators
        /** @id MochiKit.Base.ceq */
        ceq: function (a, b) { return MochiKit.Base.compare(a, b) === 0; },
        /** @id MochiKit.Base.cne */
        cne: function (a, b) { return MochiKit.Base.compare(a, b) !== 0; },
        /** @id MochiKit.Base.cgt */
        cgt: function (a, b) { return MochiKit.Base.compare(a, b) == 1; },
        /** @id MochiKit.Base.cge */
        cge: function (a, b) { return MochiKit.Base.compare(a, b) != -1; },
        /** @id MochiKit.Base.clt */
        clt: function (a, b) { return MochiKit.Base.compare(a, b) == -1; },
        /** @id MochiKit.Base.cle */
        cle: function (a, b) { return MochiKit.Base.compare(a, b) != 1; },

        // binary logical operators
        /** @id MochiKit.Base.logand */
        logand: function (a, b) { return a && b; },
        /** @id MochiKit.Base.logor */
        logor: function (a, b) { return a || b; },
        /** @id MochiKit.Base.contains */
        contains: function (a, b) { return b in a; }
    },

    /** @id MochiKit.Base.forwardCall */
    forwardCall: function (func) {
        return function () {
            return this[func].apply(this, arguments);
        };
    },

    /** @id MochiKit.Base.itemgetter */
    itemgetter: function (func) {
        return function (arg) {
            return arg[func];
        };
    },

    /** @id MochiKit.Base.bool */
    bool: function (value) {
        if (typeof(value) === "boolean" || value instanceof Boolean) {
            return value.valueOf();
        } else if (typeof(value) === "string" || value instanceof String) {
            return value.length > 0 && value != "false" && value != "null" &&
                   value != "undefined" && value != "0";
        } else if (typeof(value) === "number" || value instanceof Number) {
            return !isNaN(value) && value != 0;
        } else if (value != null && typeof(value.length) === "number") {
            return value.length !== 0
        } else {
            return value != null;
        }
    },

    /** @id MochiKit.Base.typeMatcher */
    typeMatcher: function (/* typ */) {
        var types = {};
        for (var i = 0; i < arguments.length; i++) {
            var typ = arguments[i];
            types[typ] = typ;
        }
        return function () {
            for (var i = 0; i < arguments.length; i++) {
                if (!(typeof(arguments[i]) in types)) {
                    return false;
                }
            }
            return true;
        };
    },

    /** @id MochiKit.Base.isNull */
    isNull: function (/* ... */) {
        for (var i = 0; i < arguments.length; i++) {
            if (arguments[i] !== null) {
                return false;
            }
        }
        return true;
    },

    /** @id MochiKit.Base.isUndefinedOrNull */
    isUndefinedOrNull: function (/* ... */) {
        for (var i = 0; i < arguments.length; i++) {
            var o = arguments[i];
            if (!(typeof(o) == 'undefined' || o === null)) {
                return false;
            }
        }
        return true;
    },

    /** @id MochiKit.Base.isEmpty */
    isEmpty: function (obj) {
        return !MochiKit.Base.isNotEmpty.apply(this, arguments);
    },

    /** @id MochiKit.Base.isNotEmpty */
    isNotEmpty: function (obj) {
        for (var i = 0; i < arguments.length; i++) {
            var o = arguments[i];
            if (!(o && o.length)) {
                return false;
            }
        }
        return true;
    },

    /** @id MochiKit.Base.isArrayLike */
    isArrayLike: function () {
        for (var i = 0; i < arguments.length; i++) {
            var o = arguments[i];
            var typ = typeof(o);
            if (
                (typ != 'object' && !(typ == 'function' && typeof(o.item) == 'function')) ||
                o === null ||
                typeof(o.length) != 'number' ||
                o.nodeType === 3 ||
                o.nodeType === 4
            ) {
                return false;
            }
        }
        return true;
    },

    /** @id MochiKit.Base.isDateLike */
    isDateLike: function () {
        for (var i = 0; i < arguments.length; i++) {
            var o = arguments[i];
            if (typeof(o) != "object" || o === null
                    || typeof(o.getTime) != 'function') {
                return false;
            }
        }
        return true;
    },


    /** @id MochiKit.Base.xmap */
    xmap: function (fn/*, obj... */) {
        if (fn === null) {
            return MochiKit.Base.extend(null, arguments, 1);
        }
        var rval = [];
        for (var i = 1; i < arguments.length; i++) {
            rval.push(fn(arguments[i]));
        }
        return rval;
    },

    /** @id MochiKit.Base.map */
    map: function (fn, lst/*, lst... */) {
        var m = MochiKit.Base;
        var itr = MochiKit.Iter;
        var isArrayLike = m.isArrayLike;
        if (arguments.length <= 2) {
            // allow an iterable to be passed
            if (!isArrayLike(lst)) {
                if (itr) {
                    // fast path for map(null, iterable)
                    lst = itr.list(lst);
                    if (fn === null) {
                        return lst;
                    }
                } else {
                    throw new TypeError("Argument not an array-like and MochiKit.Iter not present");
                }
            }
            // fast path for map(null, lst)
            if (fn === null) {
                return m.extend(null, lst);
            }
            // disabled fast path for map(fn, lst)
            /*
            if (false && typeof(Array.prototype.map) == 'function') {
                // Mozilla fast-path
                return Array.prototype.map.call(lst, fn);
            }
            */
            var rval = [];
            for (var i = 0; i < lst.length; i++) {
                rval.push(fn(lst[i]));
            }
            return rval;
        } else {
            // default for map(null, ...) is zip(...)
            if (fn === null) {
                fn = Array;
            }
            var length = null;
            for (var i = 1; i < arguments.length; i++) {
                // allow iterables to be passed
                if (!isArrayLike(arguments[i])) {
                    if (itr) {
                        return itr.list(itr.imap.apply(null, arguments));
                    } else {
                        throw new TypeError("Argument not an array-like and MochiKit.Iter not present");
                    }
                }
                // find the minimum length
                var l = arguments[i].length;
                if (length === null || length > l) {
                    length = l;
                }
            }
            rval = [];
            for (var i = 0; i < length; i++) {
                var args = [];
                for (var j = 1; j < arguments.length; j++) {
                    args.push(arguments[j][i]);
                }
                rval.push(fn.apply(this, args));
            }
            return rval;
        }
    },

    /** @id MochiKit.Base.xfilter */
    xfilter: function (fn/*, obj... */) {
        var rval = [];
        if (fn === null) {
            fn = MochiKit.Base.operator.truth;
        }
        for (var i = 1; i < arguments.length; i++) {
            var o = arguments[i];
            if (fn(o)) {
                rval.push(o);
            }
        }
        return rval;
    },

    /** @id MochiKit.Base.filter */
    filter: function (fn, lst, self) {
        var rval = [];
        // allow an iterable to be passed
        var m = MochiKit.Base;
        if (!m.isArrayLike(lst)) {
            if (MochiKit.Iter) {
                lst = MochiKit.Iter.list(lst);
            } else {
                throw new TypeError("Argument not an array-like and MochiKit.Iter not present");
            }
        }
        if (fn === null) {
            fn = m.operator.truth;
        }
        if (typeof(Array.prototype.filter) == 'function') {
            // Mozilla fast-path
            return Array.prototype.filter.call(lst, fn, self);
        } else if (typeof(self) == 'undefined' || self === null) {
            for (var i = 0; i < lst.length; i++) {
                var o = lst[i];
                if (fn(o)) {
                    rval.push(o);
                }
            }
        } else {
            for (var i = 0; i < lst.length; i++) {
                o = lst[i];
                if (fn.call(self, o)) {
                    rval.push(o);
                }
            }
        }
        return rval;
    },


    _wrapDumbFunction: function (func) {
        return function () {
            // fast path!
            switch (arguments.length) {
                case 0: return func();
                case 1: return func(arguments[0]);
                case 2: return func(arguments[0], arguments[1]);
                case 3: return func(arguments[0], arguments[1], arguments[2]);
            }
            var args = [];
            for (var i = 0; i < arguments.length; i++) {
                args.push("arguments[" + i + "]");
            }
            return eval("(func(" + args.join(",") + "))");
        };
    },

    /** @id MochiKit.Base.methodcaller */
    methodcaller: function (func/*, args... */) {
        var args = MochiKit.Base.extend(null, arguments, 1);
        if (typeof(func) == "function") {
            return function (obj) {
                return func.apply(obj, args);
            };
        } else {
            return function (obj) {
                return obj[func].apply(obj, args);
            };
        }
    },

    /** @id MochiKit.Base.method */
    method: function (self, func) {
        var m = MochiKit.Base;
        return m.bind.apply(this, m.extend([func, self], arguments, 2));
    },

    /** @id MochiKit.Base.compose */
    compose: function (f1, f2/*, f3, ... fN */) {
        var fnlist = [];
        var m = MochiKit.Base;
        if (arguments.length === 0) {
            throw new TypeError("compose() requires at least one argument");
        }
        for (var i = 0; i < arguments.length; i++) {
            var fn = arguments[i];
            if (typeof(fn) != "function") {
                throw new TypeError(m.repr(fn) + " is not a function");
            }
            fnlist.push(fn);
        }
        return function () {
            var args = arguments;
            for (var i = fnlist.length - 1; i >= 0; i--) {
                args = [fnlist[i].apply(this, args)];
            }
            return args[0];
        };
    },

    /** @id MochiKit.Base.bind */
    bind: function (func, self/* args... */) {
        if (typeof(func) == "string") {
            func = self[func];
        }
        var im_func = func.im_func;
        var im_preargs = func.im_preargs;
        var im_self = func.im_self;
        var m = MochiKit.Base;
        if (typeof(func) == "function" && typeof(func.apply) == "undefined") {
            // this is for cases where JavaScript sucks ass and gives you a
            // really dumb built-in function like alert() that doesn't have
            // an apply
            func = m._wrapDumbFunction(func);
        }
        if (typeof(im_func) != 'function') {
            im_func = func;
        }
        if (typeof(self) != 'undefined') {
            im_self = self;
        }
        if (typeof(im_preargs) == 'undefined') {
            im_preargs = [];
        } else  {
            im_preargs = im_preargs.slice();
        }
        m.extend(im_preargs, arguments, 2);
        var newfunc = function () {
            var args = arguments;
            var me = arguments.callee;
            if (me.im_preargs.length > 0) {
                args = m.concat(me.im_preargs, args);
            }
            var self = me.im_self;
            if (!self) {
                self = this;
            }
            return me.im_func.apply(self, args);
        };
        newfunc.im_self = im_self;
        newfunc.im_func = im_func;
        newfunc.im_preargs = im_preargs;
        return newfunc;
    },

    /** @id MochiKit.Base.bindLate */
    bindLate: function (func, self/* args... */) {
        var m = MochiKit.Base;
        var args = arguments;
        if (typeof(func) === "string") {
            args = m.extend([m.forwardCall(func)], arguments, 1);
            return m.bind.apply(this, args);
        }
        return m.bind.apply(this, args);
    },

    /** @id MochiKit.Base.bindMethods */
    bindMethods: function (self) {
        var bind = MochiKit.Base.bind;
        for (var k in self) {
            var func = self[k];
            if (typeof(func) == 'function') {
                self[k] = bind(func, self);
            }
        }
    },

    /** @id MochiKit.Base.registerComparator */
    registerComparator: function (name, check, comparator, /* optional */ override) {
        MochiKit.Base.comparatorRegistry.register(name, check, comparator, override);
    },

    _primitives: {'boolean': true, 'string': true, 'number': true},

    /** @id MochiKit.Base.compare */
    compare: function (a, b) {
        if (a == b) {
            return 0;
        }
        var aIsNull = (typeof(a) == 'undefined' || a === null);
        var bIsNull = (typeof(b) == 'undefined' || b === null);
        if (aIsNull && bIsNull) {
            return 0;
        } else if (aIsNull) {
            return -1;
        } else if (bIsNull) {
            return 1;
        }
        var m = MochiKit.Base;
        // bool, number, string have meaningful comparisons
        var prim = m._primitives;
        if (!(typeof(a) in prim && typeof(b) in prim)) {
            try {
                return m.comparatorRegistry.match(a, b);
            } catch (e) {
                if (e != m.NotFound) {
                    throw e;
                }
            }
        }
        if (a < b) {
            return -1;
        } else if (a > b) {
            return 1;
        }
        // These types can't be compared
        var repr = m.repr;
        throw new TypeError(repr(a) + " and " + repr(b) + " can not be compared");
    },

    /** @id MochiKit.Base.compareDateLike */
    compareDateLike: function (a, b) {
        return MochiKit.Base.compare(a.getTime(), b.getTime());
    },

    /** @id MochiKit.Base.compareArrayLike */
    compareArrayLike: function (a, b) {
        var compare = MochiKit.Base.compare;
        var count = a.length;
        var rval = 0;
        if (count > b.length) {
            rval = 1;
            count = b.length;
        } else if (count < b.length) {
            rval = -1;
        }
        for (var i = 0; i < count; i++) {
            var cmp = compare(a[i], b[i]);
            if (cmp) {
                return cmp;
            }
        }
        return rval;
    },

    /** @id MochiKit.Base.registerRepr */
    registerRepr: function (name, check, wrap, /* optional */override) {
        MochiKit.Base.reprRegistry.register(name, check, wrap, override);
    },

    /** @id MochiKit.Base.repr */
    repr: function (o) {
        if (typeof(o) == "undefined") {
            return "undefined";
        } else if (o === null) {
            return "null";
        }
        try {
            if (typeof(o.__repr__) == 'function') {
                return o.__repr__();
            } else if (typeof(o.repr) == 'function' && o.repr != arguments.callee) {
                return o.repr();
            }
            return MochiKit.Base.reprRegistry.match(o);
        } catch (e) {
            if (typeof(o.NAME) == 'string' && (
                    o.toString == Function.prototype.toString ||
                    o.toString == Object.prototype.toString
                )) {
                return o.NAME;
            }
        }
        try {
            var ostring = (o + "");
        } catch (e) {
            return "[" + typeof(o) + "]";
        }
        if (typeof(o) == "function") {
            ostring = ostring.replace(/^\s+/, "").replace(/\s+/g, " ");
            ostring = ostring.replace(/,(\S)/, ", $1");
            var idx = ostring.indexOf("{");
            if (idx != -1) {
                ostring = ostring.substr(0, idx) + "{...}";
            }
        }
        return ostring;
    },

    /** @id MochiKit.Base.reprArrayLike */
    reprArrayLike: function (o) {
        var m = MochiKit.Base;
        return "[" + m.map(m.repr, o).join(", ") + "]";
    },

    /** @id MochiKit.Base.reprString */
    reprString: function (o) {
        return ('"' + o.replace(/(["\\])/g, '\\$1') + '"'
            ).replace(/[\f]/g, "\\f"
            ).replace(/[\b]/g, "\\b"
            ).replace(/[\n]/g, "\\n"
            ).replace(/[\t]/g, "\\t"
            ).replace(/[\v]/g, "\\v"
            ).replace(/[\r]/g, "\\r");
    },

    /** @id MochiKit.Base.reprNumber */
    reprNumber: function (o) {
        return o + "";
    },

    /** @id MochiKit.Base.registerJSON */
    registerJSON: function (name, check, wrap, /* optional */override) {
        MochiKit.Base.jsonRegistry.register(name, check, wrap, override);
    },


    /** @id MochiKit.Base.evalJSON */
    evalJSON: function () {
        return eval("(" + MochiKit.Base._filterJSON(arguments[0]) + ")");
    },

    _filterJSON: function (s) {
        var m = s.match(/^\s*\/\*(.*)\*\/\s*$/);
        if (m) {
            return m[1];
        }
        return s;
    },

    /** @id MochiKit.Base.serializeJSON */
    serializeJSON: function (o) {
        var objtype = typeof(o);
        if (objtype == "number" || objtype == "boolean") {
            return o + "";
        } else if (o === null) {
            return "null";
        } else if (objtype == "string") {
            var res = "";
            for (var i = 0; i < o.length; i++) {
                var c = o.charAt(i);
                if (c == '\"') {
                    res += '\\"';
                } else if (c == '\\') {
                    res += '\\\\';
                } else if (c == '\b') {
                    res += '\\b';
                } else if (c == '\f') {
                    res += '\\f';
                } else if (c == '\n') {
                    res += '\\n';
                } else if (c == '\r') {
                    res += '\\r';
                } else if (c == '\t') {
                    res += '\\t';
                } else if (o.charCodeAt(i) <= 0x1F) {
                    var hex = o.charCodeAt(i).toString(16);
                    if (hex.length < 2) {
                        hex = '0' + hex;
                    }
                    res += '\\u00' + hex.toUpperCase();
                } else {
                    res += c;
                }
            }
            return '"' + res + '"';
        }
        // recurse
        var me = arguments.callee;
        // short-circuit for objects that support "json" serialization
        // if they return "self" then just pass-through...
        var newObj;
        if (typeof(o.__json__) == "function") {
            newObj = o.__json__();
            if (o !== newObj) {
                return me(newObj);
            }
        }
        if (typeof(o.json) == "function") {
            newObj = o.json();
            if (o !== newObj) {
                return me(newObj);
            }
        }
        // array
        if (objtype != "function" && typeof(o.length) == "number") {
            var res = [];
            for (var i = 0; i < o.length; i++) {
                var val = me(o[i]);
                if (typeof(val) != "string") {
                    // skip non-serializable values
                    continue;
                }
                res.push(val);
            }
            return "[" + res.join(", ") + "]";
        }
        // look in the registry
        var m = MochiKit.Base;
        try {
            newObj = m.jsonRegistry.match(o);
            if (o !== newObj) {
                return me(newObj);
            }
        } catch (e) {
            if (e != m.NotFound) {
                // something really bad happened
                throw e;
            }
        }
        // undefined is outside of the spec
        if (objtype == "undefined") {
            throw new TypeError("undefined can not be serialized as JSON");
        }
        // it's a function with no adapter, bad
        if (objtype == "function") {
            return null;
        }
        // generic object code path
        res = [];
        for (var k in o) {
            var useKey;
            if (typeof(k) == "number") {
                useKey = '"' + k + '"';
            } else if (typeof(k) == "string") {
                useKey = me(k);
            } else {
                // skip non-string or number keys
                continue;
            }
            val = me(o[k]);
            if (typeof(val) != "string") {
                // skip non-serializable values
                continue;
            }
            res.push(useKey + ":" + val);
        }
        return "{" + res.join(", ") + "}";
    },


    /** @id MochiKit.Base.objEqual */
    objEqual: function (a, b) {
        return (MochiKit.Base.compare(a, b) === 0);
    },

    /** @id MochiKit.Base.arrayEqual */
    arrayEqual: function (self, arr) {
        if (self.length != arr.length) {
            return false;
        }
        return (MochiKit.Base.compare(self, arr) === 0);
    },

    /** @id MochiKit.Base.concat */
    concat: function (/* lst... */) {
        var rval = [];
        var extend = MochiKit.Base.extend;
        for (var i = 0; i < arguments.length; i++) {
            extend(rval, arguments[i]);
        }
        return rval;
    },

    /** @id MochiKit.Base.keyComparator */
    keyComparator: function (key/* ... */) {
        // fast-path for single key comparisons
        var m = MochiKit.Base;
        var compare = m.compare;
        if (arguments.length == 1) {
            return function (a, b) {
                return compare(a[key], b[key]);
            };
        }
        var compareKeys = m.extend(null, arguments);
        return function (a, b) {
            var rval = 0;
            // keep comparing until something is inequal or we run out of
            // keys to compare
            for (var i = 0; (rval === 0) && (i < compareKeys.length); i++) {
                var key = compareKeys[i];
                rval = compare(a[key], b[key]);
            }
            return rval;
        };
    },

    /** @id MochiKit.Base.reverseKeyComparator */
    reverseKeyComparator: function (key) {
        var comparator = MochiKit.Base.keyComparator.apply(this, arguments);
        return function (a, b) {
            return comparator(b, a);
        };
    },

    /** @id MochiKit.Base.partial */
    partial: function (func) {
        var m = MochiKit.Base;
        return m.bind.apply(this, m.extend([func, undefined], arguments, 1));
    },

    /** @id MochiKit.Base.listMinMax */
    listMinMax: function (which, lst) {
        if (lst.length === 0) {
            return null;
        }
        var cur = lst[0];
        var compare = MochiKit.Base.compare;
        for (var i = 1; i < lst.length; i++) {
            var o = lst[i];
            if (compare(o, cur) == which) {
                cur = o;
            }
        }
        return cur;
    },

    /** @id MochiKit.Base.objMax */
    objMax: function (/* obj... */) {
        return MochiKit.Base.listMinMax(1, arguments);
    },

    /** @id MochiKit.Base.objMin */
    objMin: function (/* obj... */) {
        return MochiKit.Base.listMinMax(-1, arguments);
    },

    /** @id MochiKit.Base.findIdentical */
    findIdentical: function (lst, value, start/* = 0 */, /* optional */end) {
        if (typeof(end) == "undefined" || end === null) {
            end = lst.length;
        }
        if (typeof(start) == "undefined" || start === null) {
            start = 0;
        }
        for (var i = start; i < end; i++) {
            if (lst[i] === value) {
                return i;
            }
        }
        return -1;
    },

    /** @id MochiKit.Base.mean */
    mean: function(/* lst... */) {
        /* http://www.nist.gov/dads/HTML/mean.html */
        var sum = 0;

        var m = MochiKit.Base;
        var args = m.extend(null, arguments);
        var count = args.length;

        while (args.length) {
            var o = args.shift();
            if (o && typeof(o) == "object" && typeof(o.length) == "number") {
                count += o.length - 1;
                for (var i = o.length - 1; i >= 0; i--) {
                    sum += o[i];
                }
            } else {
                sum += o;
            }
        }

        if (count <= 0) {
            throw new TypeError('mean() requires at least one argument');
        }

        return sum/count;
    },

    /** @id MochiKit.Base.median */
    median: function(/* lst... */) {
        /* http://www.nist.gov/dads/HTML/median.html */
        var data = MochiKit.Base.flattenArguments(arguments);
        if (data.length === 0) {
            throw new TypeError('median() requires at least one argument');
        }
        data.sort(compare);
        if (data.length % 2 == 0) {
            var upper = data.length / 2;
            return (data[upper] + data[upper - 1]) / 2;
        } else {
            return data[(data.length - 1) / 2];
        }
    },

    /** @id MochiKit.Base.findValue */
    findValue: function (lst, value, start/* = 0 */, /* optional */end) {
        if (typeof(end) == "undefined" || end === null) {
            end = lst.length;
        }
        if (typeof(start) == "undefined" || start === null) {
            start = 0;
        }
        var cmp = MochiKit.Base.compare;
        for (var i = start; i < end; i++) {
            if (cmp(lst[i], value) === 0) {
                return i;
            }
        }
        return -1;
    },

    /** @id MochiKit.Base.nodeWalk */
    nodeWalk: function (node, visitor) {
        var nodes = [node];
        var extend = MochiKit.Base.extend;
        while (nodes.length) {
            var res = visitor(nodes.shift());
            if (res) {
                extend(nodes, res);
            }
        }
    },


    /** @id MochiKit.Base.nameFunctions */
    nameFunctions: function (namespace) {
        var base = namespace.NAME;
        if (typeof(base) == 'undefined') {
            base = '';
        } else {
            base = base + '.';
        }
        for (var name in namespace) {
            var o = namespace[name];
            if (typeof(o) == 'function' && typeof(o.NAME) == 'undefined') {
                try {
                    o.NAME = base + name;
                } catch (e) {
                    // pass
                }
            }
        }
    },


    /** @id MochiKit.Base.queryString */
    queryString: function (names, values) {
        // check to see if names is a string or a DOM element, and if
        // MochiKit.DOM is available.  If so, drop it like it's a form
        // Ugliest conditional in MochiKit?  Probably!
        if (typeof(MochiKit.DOM) != "undefined" && arguments.length == 1
            && (typeof(names) == "string" || (
                typeof(names.nodeType) != "undefined" && names.nodeType > 0
            ))
        ) {
            var kv = MochiKit.DOM.formContents(names);
            names = kv[0];
            values = kv[1];
        } else if (arguments.length == 1) {
            // Allow the return value of formContents to be passed directly
            if (typeof(names.length) == "number" && names.length == 2) {
                return arguments.callee(names[0], names[1]);
            }
            var o = names;
            names = [];
            values = [];
            for (var k in o) {
                var v = o[k];
                if (typeof(v) == "function") {
                    continue;
                } else if (MochiKit.Base.isArrayLike(v)){
                    for (var i = 0; i < v.length; i++) {
                        names.push(k);
                        values.push(v[i]);
                    }
                } else {
                    names.push(k);
                    values.push(v);
                }
            }
        }
        var rval = [];
        var len = Math.min(names.length, values.length);
        var urlEncode = MochiKit.Base.urlEncode;
        for (var i = 0; i < len; i++) {
            v = values[i];
            if (typeof(v) != 'undefined' && v !== null) {
                rval.push(urlEncode(names[i]) + "=" + urlEncode(v));
            }
        }
        return rval.join("&");
    },


    /** @id MochiKit.Base.parseQueryString */
    parseQueryString: function (encodedString, useArrays) {
        // strip a leading '?' from the encoded string
        var qstr = (encodedString.charAt(0) == "?")
            ? encodedString.substring(1)
            : encodedString;
        var pairs = qstr.replace(/\+/g, "%20").split(/\&amp\;|\&\#38\;|\&#x26;|\&/);
        var o = {};
        var decode;
        if (typeof(decodeURIComponent) != "undefined") {
            decode = decodeURIComponent;
        } else {
            decode = unescape;
        }
        if (useArrays) {
            for (var i = 0; i < pairs.length; i++) {
                var pair = pairs[i].split("=");
                var name = decode(pair.shift());
                if (!name) {
                    continue;
                }
                var arr = o[name];
                if (!(arr instanceof Array)) {
                    arr = [];
                    o[name] = arr;
                }
                arr.push(decode(pair.join("=")));
            }
        } else {
            for (var i = 0; i < pairs.length; i++) {
                pair = pairs[i].split("=");
                var name = pair.shift();
                if (!name) {
                    continue;
                }
                o[decode(name)] = decode(pair.join("="));
            }
        }
        return o;
    }
});

/** @id MochiKit.Base.AdapterRegistry */
MochiKit.Base.AdapterRegistry = function () {
    this.pairs = [];
};

MochiKit.Base.AdapterRegistry.prototype = {
    /** @id MochiKit.Base.AdapterRegistry.prototype.register */
    register: function (name, check, wrap, /* optional */ override) {
        if (override) {
            this.pairs.unshift([name, check, wrap]);
        } else {
            this.pairs.push([name, check, wrap]);
        }
    },

    /** @id MochiKit.Base.AdapterRegistry.prototype.match */
    match: function (/* ... */) {
        for (var i = 0; i < this.pairs.length; i++) {
            var pair = this.pairs[i];
            if (pair[1].apply(this, arguments)) {
                return pair[2].apply(this, arguments);
            }
        }
        throw MochiKit.Base.NotFound;
    },

    /** @id MochiKit.Base.AdapterRegistry.prototype.unregister */
    unregister: function (name) {
        for (var i = 0; i < this.pairs.length; i++) {
            var pair = this.pairs[i];
            if (pair[0] == name) {
                this.pairs.splice(i, 1);
                return true;
            }
        }
        return false;
    }
};

MochiKit.Base._exportSymbols = function (globals, module) {
    if (MochiKit.__export__ === false || module.__export__ === false) {
        return;
    }
    for (var k in module) {
        var v = module[k];
        if (v != null) {
            var okName = (k[0] !== "_" && k !== "toString");
            if (v.__export__ === true || (v.__export__ !== false && okName)) {
                globals[k] = module[k];
            }
        }
    }
};

/**
 * Creates a deprecated function alias in the specified module. The
 * deprecated function will forward all calls and arguments to a
 * target function, while also logging a debug message on the first
 * call (if MochiKit.Logging is loaded). The destination function may
 * be located in another module, which must be loaded, or an
 * exception will be thrown.
 *
 * @param {Object/String} module the source module or module name
 *            (e.g. 'DOM' or 'MochiKit.DOM')
 * @param {String} name the deprecated function name (e.g. 'getStyle')
 * @param {String} target the fully qualified name of the target
 *            function (e.g. 'MochiKit.Style.getStyle')
 * @param {String} version the first version when the source function
 *            was deprecated (e.g. '1.4')
 * @param {Boolean} [exportable] the exportable function flag,
 *            defaults to false
 */
MochiKit.Base._deprecated = function (module, name, target, version, exportable) {
    if (typeof(module) === 'string') {
        if (module.indexOf('MochiKit.') === 0) {
            module = module.substring(9);
        }
        module = MochiKit[module];
    }
    var targetModule = target.split('.')[1];
    var targetName = target.split('.')[2];
    var func = function () {
        var self = arguments.callee;
        var msg = module.NAME + '.' + name + ' is deprecated since version ' +
                  version + '. Use ' + target + ' instead.';
        if (self.logged !== true) {
            self.logged = true;
            if (MochiKit.Logging) {
                MochiKit.Logging.logDebug(msg);
            } else if (console && console.log) {
                console.log(msg);
            }
        }
        if (!MochiKit[targetModule]) {
            throw new Error(msg);
        }
        return MochiKit[targetModule][targetName].apply(this, arguments);
    };
    func.__export__ = (exportable === true);
    module[name] = func;
}

MochiKit.Base.__new__ = function () {
    var m = this;

    /** @id MochiKit.Base.noop */
    m.noop = m.operator.identity;

    // Backwards compat
    m._deprecated(m, 'forward', 'MochiKit.Base.forwardCall', '1.3');
    m._deprecated(m, 'find', 'MochiKit.Base.findValue', '1.3');

    if (typeof(encodeURIComponent) != "undefined") {
        /** @id MochiKit.Base.urlEncode */
        m.urlEncode = function (unencoded) {
            return encodeURIComponent(unencoded).replace(/\'/g, '%27');
        };
    } else {
        m.urlEncode = function (unencoded) {
            return escape(unencoded
                ).replace(/\+/g, '%2B'
                ).replace(/\"/g,'%22'
                ).rval.replace(/\'/g, '%27');
        };
    }

    /** @id MochiKit.Base.NamedError */
    m.NamedError = function (name) {
        this.message = name;
        this.name = name;
    };
    m.NamedError.prototype = new Error();
    m.update(m.NamedError.prototype, {
        repr: function () {
            if (this.message && this.message != this.name) {
                return this.name + "(" + m.repr(this.message) + ")";
            } else {
                return this.name + "()";
            }
        },
        toString: m.forwardCall("repr")
    });

    /** @id MochiKit.Base.NotFound */
    m.NotFound = new m.NamedError("MochiKit.Base.NotFound");


    /** @id MochiKit.Base.listMax */
    m.listMax = m.partial(m.listMinMax, 1);
    /** @id MochiKit.Base.listMin */
    m.listMin = m.partial(m.listMinMax, -1);

    /** @id MochiKit.Base.isCallable */
    m.isCallable = m.typeMatcher('function');
    /** @id MochiKit.Base.isUndefined */
    m.isUndefined = m.typeMatcher('undefined');

    /** @id MochiKit.Base.merge */
    m.merge = m.partial(m.update, null);
    /** @id MochiKit.Base.zip */
    m.zip = m.partial(m.map, null);

    /** @id MochiKit.Base.average */
    m.average = m.mean;

    /** @id MochiKit.Base.comparatorRegistry */
    m.comparatorRegistry = new m.AdapterRegistry();
    m.registerComparator("dateLike", m.isDateLike, m.compareDateLike);
    m.registerComparator("arrayLike", m.isArrayLike, m.compareArrayLike);

    /** @id MochiKit.Base.reprRegistry */
    m.reprRegistry = new m.AdapterRegistry();
    m.registerRepr("arrayLike", m.isArrayLike, m.reprArrayLike);
    m.registerRepr("string", m.typeMatcher("string"), m.reprString);
    m.registerRepr("numbers", m.typeMatcher("number", "boolean"), m.reprNumber);

    /** @id MochiKit.Base.jsonRegistry */
    m.jsonRegistry = new m.AdapterRegistry();

    m.nameFunctions(this);

};

MochiKit.Base.__new__();

//
// XXX: Internet Explorer blows
//
if (MochiKit.__export__) {
    compare = MochiKit.Base.compare;
    compose = MochiKit.Base.compose;
    serializeJSON = MochiKit.Base.serializeJSON;
    mean = MochiKit.Base.mean;
    median = MochiKit.Base.median;
}

MochiKit.Base._exportSymbols(this, MochiKit.Base);
/***

MochiKit.Iter 1.5

See <http://mochikit.com/> for documentation, downloads, license, etc.

(c) 2005 Bob Ippolito.  All rights Reserved.

***/

MochiKit.Base._module('Iter', '1.5', ['Base']);

MochiKit.Base.update(MochiKit.Iter, {
    /** @id MochiKit.Iter.registerIteratorFactory */
    registerIteratorFactory: function (name, check, iterfactory, /* optional */ override) {
        MochiKit.Iter.iteratorRegistry.register(name, check, iterfactory, override);
    },

    /** @id MochiKit.Iter.isIterable */
    isIterable: function(o) {
        return o != null &&
               (typeof(o.next) == "function" || typeof(o.iter) == "function");
    },

    /** @id MochiKit.Iter.iter */
    iter: function (iterable, /* optional */ sentinel) {
        var self = MochiKit.Iter;
        if (arguments.length == 2) {
            return self.takewhile(
                function (a) { return a != sentinel; },
                iterable
            );
        }
        if (typeof(iterable.next) == 'function') {
            return iterable;
        } else if (typeof(iterable.iter) == 'function') {
            return iterable.iter();
        /*
        }  else if (typeof(iterable.__iterator__) == 'function') {
            //
            // XXX: We can't support JavaScript 1.7 __iterator__ directly
            //      because of Object.prototype.__iterator__
            //
            return iterable.__iterator__();
        */
        }

        try {
            return self.iteratorRegistry.match(iterable);
        } catch (e) {
            var m = MochiKit.Base;
            if (e == m.NotFound) {
                e = new TypeError(typeof(iterable) + ": " + m.repr(iterable) + " is not iterable");
            }
            throw e;
        }
    },

    /** @id MochiKit.Iter.count */
    count: function (n) {
        if (!n) {
            n = 0;
        }
        var m = MochiKit.Base;
        return {
            repr: function () { return "count(" + n + ")"; },
            toString: m.forwardCall("repr"),
            next: m.counter(n)
        };
    },

    /** @id MochiKit.Iter.cycle */
    cycle: function (p) {
        var self = MochiKit.Iter;
        var m = MochiKit.Base;
        var lst = [];
        var iterator = self.iter(p);
        return {
            repr: function () { return "cycle(...)"; },
            toString: m.forwardCall("repr"),
            next: function () {
                try {
                    var rval = iterator.next();
                    lst.push(rval);
                    return rval;
                } catch (e) {
                    if (e != self.StopIteration) {
                        throw e;
                    }
                    if (lst.length === 0) {
                        this.next = function () {
                            throw self.StopIteration;
                        };
                    } else {
                        var i = -1;
                        this.next = function () {
                            i = (i + 1) % lst.length;
                            return lst[i];
                        };
                    }
                    return this.next();
                }
            }
        };
    },

    /** @id MochiKit.Iter.repeat */
    repeat: function (elem, /* optional */n) {
        var m = MochiKit.Base;
        if (typeof(n) == 'undefined') {
            return {
                repr: function () {
                    return "repeat(" + m.repr(elem) + ")";
                },
                toString: m.forwardCall("repr"),
                next: function () {
                    return elem;
                }
            };
        }
        return {
            repr: function () {
                return "repeat(" + m.repr(elem) + ", " + n + ")";
            },
            toString: m.forwardCall("repr"),
            next: function () {
                if (n <= 0) {
                    throw MochiKit.Iter.StopIteration;
                }
                n -= 1;
                return elem;
            }
        };
    },

    /** @id MochiKit.Iter.next */
    next: function (iterator) {
        return iterator.next();
    },

    /** @id MochiKit.Iter.izip */
    izip: function (p, q/*, ...*/) {
        var m = MochiKit.Base;
        var self = MochiKit.Iter;
        var next = self.next;
        var iterables = m.map(self.iter, arguments);
        return {
            repr: function () { return "izip(...)"; },
            toString: m.forwardCall("repr"),
            next: function () { return m.map(next, iterables); }
        };
    },

    /** @id MochiKit.Iter.ifilter */
    ifilter: function (pred, seq) {
        var m = MochiKit.Base;
        seq = MochiKit.Iter.iter(seq);
        if (pred === null) {
            pred = m.operator.truth;
        }
        return {
            repr: function () { return "ifilter(...)"; },
            toString: m.forwardCall("repr"),
            next: function () {
                while (true) {
                    var rval = seq.next();
                    if (pred(rval)) {
                        return rval;
                    }
                }
                // mozilla warnings aren't too bright
                return undefined;
            }
        };
    },

    /** @id MochiKit.Iter.ifilterfalse */
    ifilterfalse: function (pred, seq) {
        var m = MochiKit.Base;
        seq = MochiKit.Iter.iter(seq);
        if (pred === null) {
            pred = m.operator.truth;
        }
        return {
            repr: function () { return "ifilterfalse(...)"; },
            toString: m.forwardCall("repr"),
            next: function () {
                while (true) {
                    var rval = seq.next();
                    if (!pred(rval)) {
                        return rval;
                    }
                }
                // mozilla warnings aren't too bright
                return undefined;
            }
        };
    },

    /** @id MochiKit.Iter.islice */
    islice: function (seq/*, [start,] stop[, step] */) {
        var self = MochiKit.Iter;
        var m = MochiKit.Base;
        seq = self.iter(seq);
        var start = 0;
        var stop = 0;
        var step = 1;
        var i = -1;
        if (arguments.length == 2) {
            stop = arguments[1];
        } else if (arguments.length == 3) {
            start = arguments[1];
            stop = arguments[2];
        } else {
            start = arguments[1];
            stop = arguments[2];
            step = arguments[3];
        }
        return {
            repr: function () {
                return "islice(" + ["...", start, stop, step].join(", ") + ")";
            },
            toString: m.forwardCall("repr"),
            next: function () {
                var rval;
                while (i < start) {
                    rval = seq.next();
                    i++;
                }
                if (start >= stop) {
                    throw self.StopIteration;
                }
                start += step;
                return rval;
            }
        };
    },

    /** @id MochiKit.Iter.imap */
    imap: function (fun, p, q/*, ...*/) {
        var m = MochiKit.Base;
        var self = MochiKit.Iter;
        var iterables = m.map(self.iter, m.extend(null, arguments, 1));
        var map = m.map;
        var next = self.next;
        return {
            repr: function () { return "imap(...)"; },
            toString: m.forwardCall("repr"),
            next: function () {
                return fun.apply(this, map(next, iterables));
            }
        };
    },

    /** @id MochiKit.Iter.applymap */
    applymap: function (fun, seq, self) {
        seq = MochiKit.Iter.iter(seq);
        var m = MochiKit.Base;
        return {
            repr: function () { return "applymap(...)"; },
            toString: m.forwardCall("repr"),
            next: function () {
                return fun.apply(self, seq.next());
            }
        };
    },

    /** @id MochiKit.Iter.chain */
    chain: function (p, q/*, ...*/) {
        // dumb fast path
        var self = MochiKit.Iter;
        var m = MochiKit.Base;
        if (arguments.length == 1) {
            return self.iter(arguments[0]);
        }
        var argiter = m.map(self.iter, arguments);
        return {
            repr: function () { return "chain(...)"; },
            toString: m.forwardCall("repr"),
            next: function () {
                while (argiter.length > 1) {
                    try {
                        var result = argiter[0].next();
                        return result;
                    } catch (e) {
                        if (e != self.StopIteration) {
                            throw e;
                        }
                        argiter.shift();
                        var result = argiter[0].next();
                        return result;
                    }
                }
                if (argiter.length == 1) {
                    // optimize last element
                    var arg = argiter.shift();
                    this.next = m.bind("next", arg);
                    return this.next();
                }
                throw self.StopIteration;
            }
        };
    },

    /** @id MochiKit.Iter.takewhile */
    takewhile: function (pred, seq) {
        var self = MochiKit.Iter;
        seq = self.iter(seq);
        return {
            repr: function () { return "takewhile(...)"; },
            toString: MochiKit.Base.forwardCall("repr"),
            next: function () {
                var rval = seq.next();
                if (!pred(rval)) {
                    this.next = function () {
                        throw self.StopIteration;
                    };
                    this.next();
                }
                return rval;
            }
        };
    },

    /** @id MochiKit.Iter.dropwhile */
    dropwhile: function (pred, seq) {
        seq = MochiKit.Iter.iter(seq);
        var m = MochiKit.Base;
        var bind = m.bind;
        return {
            "repr": function () { return "dropwhile(...)"; },
            "toString": m.forwardCall("repr"),
            "next": function () {
                while (true) {
                    var rval = seq.next();
                    if (!pred(rval)) {
                        break;
                    }
                }
                this.next = bind("next", seq);
                return rval;
            }
        };
    },

    _tee: function (ident, sync, iterable) {
        sync.pos[ident] = -1;
        var m = MochiKit.Base;
        var listMin = m.listMin;
        return {
            repr: function () { return "tee(" + ident + ", ...)"; },
            toString: m.forwardCall("repr"),
            next: function () {
                var rval;
                var i = sync.pos[ident];

                if (i == sync.max) {
                    rval = iterable.next();
                    sync.deque.push(rval);
                    sync.max += 1;
                    sync.pos[ident] += 1;
                } else {
                    rval = sync.deque[i - sync.min];
                    sync.pos[ident] += 1;
                    if (i == sync.min && listMin(sync.pos) != sync.min) {
                        sync.min += 1;
                        sync.deque.shift();
                    }
                }
                return rval;
            }
        };
    },

    /** @id MochiKit.Iter.tee */
    tee: function (iterable, n/* = 2 */) {
        var rval = [];
        var sync = {
            "pos": [],
            "deque": [],
            "max": -1,
            "min": -1
        };
        if (arguments.length == 1 || typeof(n) == "undefined" || n === null) {
            n = 2;
        }
        var self = MochiKit.Iter;
        iterable = self.iter(iterable);
        var _tee = self._tee;
        for (var i = 0; i < n; i++) {
            rval.push(_tee(i, sync, iterable));
        }
        return rval;
    },

    /** @id MochiKit.Iter.list */
    list: function (iterable) {
        // Fast-path for Array and Array-like
        var rval;
        if (iterable instanceof Array) {
            return iterable.slice();
        } 
        // this is necessary to avoid a Safari crash
        if (typeof(iterable) == "function" &&
                !(iterable instanceof Function) &&
                typeof(iterable.length) == 'number') {
            rval = [];
            for (var i = 0; i < iterable.length; i++) {
                rval.push(iterable[i]);
            }
            return rval;
        }

        var self = MochiKit.Iter;
        iterable = self.iter(iterable);
        var rval = [];
        var a_val;
        try {
            while (true) {
                a_val = iterable.next();
                rval.push(a_val);
            }
        } catch (e) {
            if (e != self.StopIteration) {
                throw e;
            }
            return rval;
        }
        // mozilla warnings aren't too bright
        return undefined;
    },


    /** @id MochiKit.Iter.reduce */
    reduce: function (fn, iterable, /* optional */initial) {
        var i = 0;
        var x = initial;
        var self = MochiKit.Iter;
        iterable = self.iter(iterable);
        if (arguments.length < 3) {
            try {
                x = iterable.next();
            } catch (e) {
                if (e == self.StopIteration) {
                    e = new TypeError("reduce() of empty sequence with no initial value");
                }
                throw e;
            }
            i++;
        }
        try {
            while (true) {
                x = fn(x, iterable.next());
            }
        } catch (e) {
            if (e != self.StopIteration) {
                throw e;
            }
        }
        return x;
    },

    /** @id MochiKit.Iter.range */
    range: function (/* [start,] stop[, step] */) {
        var start = 0;
        var stop = 0;
        var step = 1;
        if (arguments.length == 1) {
            stop = arguments[0];
        } else if (arguments.length == 2) {
            start = arguments[0];
            stop = arguments[1];
        } else if (arguments.length == 3) {
            start = arguments[0];
            stop = arguments[1];
            step = arguments[2];
        } else {
            throw new TypeError("range() takes 1, 2, or 3 arguments!");
        }
        if (step === 0) {
            throw new TypeError("range() step must not be 0");
        }
        return {
            next: function () {
                if ((step > 0 && start >= stop) || (step < 0 && start <= stop)) {
                    throw MochiKit.Iter.StopIteration;
                }
                var rval = start;
                start += step;
                return rval;
            },
            repr: function () {
                return "range(" + [start, stop, step].join(", ") + ")";
            },
            toString: MochiKit.Base.forwardCall("repr")
        };
    },

    /** @id MochiKit.Iter.sum */
    sum: function (iterable, start/* = 0 */) {
        if (typeof(start) == "undefined" || start === null) {
            start = 0;
        }
        var x = start;
        var self = MochiKit.Iter;
        iterable = self.iter(iterable);
        try {
            while (true) {
                x += iterable.next();
            }
        } catch (e) {
            if (e != self.StopIteration) {
                throw e;
            }
        }
        return x;
    },

    /** @id MochiKit.Iter.exhaust */
    exhaust: function (iterable) {
        var self = MochiKit.Iter;
        iterable = self.iter(iterable);
        try {
            while (true) {
                iterable.next();
            }
        } catch (e) {
            if (e != self.StopIteration) {
                throw e;
            }
        }
    },

    /** @id MochiKit.Iter.forEach */
    forEach: function (iterable, func, /* optional */obj) {
        var m = MochiKit.Base;
        var self = MochiKit.Iter;
        if (arguments.length > 2) {
            func = m.bind(func, obj);
        }
        // fast path for array
        if (m.isArrayLike(iterable) && !self.isIterable(iterable)) {
            try {
                for (var i = 0; i < iterable.length; i++) {
                    func(iterable[i]);
                }
            } catch (e) {
                if (e != self.StopIteration) {
                    throw e;
                }
            }
        } else {
            self.exhaust(self.imap(func, iterable));
        }
    },

    /** @id MochiKit.Iter.every */
    every: function (iterable, func) {
        var self = MochiKit.Iter;
        try {
            self.ifilterfalse(func, iterable).next();
            return false;
        } catch (e) {
            if (e != self.StopIteration) {
                throw e;
            }
            return true;
        }
    },

    /** @id MochiKit.Iter.sorted */
    sorted: function (iterable, /* optional */cmp) {
        var rval = MochiKit.Iter.list(iterable);
        if (arguments.length == 1) {
            cmp = MochiKit.Base.compare;
        }
        rval.sort(cmp);
        return rval;
    },

    /** @id MochiKit.Iter.reversed */
    reversed: function (iterable) {
        var rval = MochiKit.Iter.list(iterable);
        rval.reverse();
        return rval;
    },

    /** @id MochiKit.Iter.some */
    some: function (iterable, func) {
        var self = MochiKit.Iter;
        try {
            self.ifilter(func, iterable).next();
            return true;
        } catch (e) {
            if (e != self.StopIteration) {
                throw e;
            }
            return false;
        }
    },

    /** @id MochiKit.Iter.iextend */
    iextend: function (lst, iterable) {
        var m = MochiKit.Base;
        var self = MochiKit.Iter;
        if (m.isArrayLike(iterable) && !self.isIterable(iterable)) {
            // fast-path for array-like
            for (var i = 0; i < iterable.length; i++) {
                lst.push(iterable[i]);
            }
        } else {
            iterable = self.iter(iterable);
            try {
                while (true) {
                    lst.push(iterable.next());
                }
            } catch (e) {
                if (e != self.StopIteration) {
                    throw e;
                }
            }
        }
        return lst;
    },

    /** @id MochiKit.Iter.groupby */
    groupby: function(iterable, /* optional */ keyfunc) {
        var m = MochiKit.Base;
        var self = MochiKit.Iter;
        if (arguments.length < 2) {
            keyfunc = m.operator.identity;
        }
        iterable = self.iter(iterable);

        // shared
        var pk = undefined;
        var k = undefined;
        var v;

        function fetch() {
            v = iterable.next();
            k = keyfunc(v);
        };

        function eat() {
            var ret = v;
            v = undefined;
            return ret;
        };

        var first = true;
        var compare = m.compare;
        return {
            repr: function () { return "groupby(...)"; },
            next: function() {
                // iterator-next

                // iterate until meet next group
                while (compare(k, pk) === 0) {
                    fetch();
                    if (first) {
                        first = false;
                        break;
                    }
                }
                pk = k;
                return [k, {
                    next: function() {
                        // subiterator-next
                        if (v == undefined) { // Is there something to eat?
                            fetch();
                        }
                        if (compare(k, pk) !== 0) {
                            throw self.StopIteration;
                        }
                        return eat();
                    }
                }];
            }
        };
    },

    /** @id MochiKit.Iter.groupby_as_array */
    groupby_as_array: function (iterable, /* optional */ keyfunc) {
        var m = MochiKit.Base;
        var self = MochiKit.Iter;
        if (arguments.length < 2) {
            keyfunc = m.operator.identity;
        }

        iterable = self.iter(iterable);
        var result = [];
        var first = true;
        var prev_key;
        var compare = m.compare;
        while (true) {
            try {
                var value = iterable.next();
                var key = keyfunc(value);
            } catch (e) {
                if (e == self.StopIteration) {
                    break;
                }
                throw e;
            }
            if (first || compare(key, prev_key) !== 0) {
                var values = [];
                result.push([key, values]);
            }
            values.push(value);
            first = false;
            prev_key = key;
        }
        return result;
    },

    /** @id MochiKit.Iter.arrayLikeIter */
    arrayLikeIter: function (iterable) {
        var i = 0;
        return {
            repr: function () { return "arrayLikeIter(...)"; },
            toString: MochiKit.Base.forwardCall("repr"),
            next: function () {
                if (i >= iterable.length) {
                    throw MochiKit.Iter.StopIteration;
                }
                return iterable[i++];
            }
        };
    },

    /** @id MochiKit.Iter.hasIterateNext */
    hasIterateNext: function (iterable) {
        return (iterable && typeof(iterable.iterateNext) == "function");
    },

    /** @id MochiKit.Iter.iterateNextIter */
    iterateNextIter: function (iterable) {
        return {
            repr: function () { return "iterateNextIter(...)"; },
            toString: MochiKit.Base.forwardCall("repr"),
            next: function () {
                var rval = iterable.iterateNext();
                if (rval === null || rval === undefined) {
                    throw MochiKit.Iter.StopIteration;
                }
                return rval;
            }
        };
    }
});


MochiKit.Iter.__new__ = function () {
    var m = MochiKit.Base;
    // Re-use StopIteration if exists (e.g. SpiderMonkey)
    if (typeof(StopIteration) != "undefined") {
        this.StopIteration = StopIteration;
    } else {
        /** @id MochiKit.Iter.StopIteration */
        this.StopIteration = new m.NamedError("StopIteration");
    }
    this.iteratorRegistry = new m.AdapterRegistry();
    // Register the iterator factory for arrays
    this.registerIteratorFactory(
        "arrayLike",
        m.isArrayLike,
        this.arrayLikeIter
    );

    this.registerIteratorFactory(
        "iterateNext",
        this.hasIterateNext,
        this.iterateNextIter
    );

    m.nameFunctions(this);

};

MochiKit.Iter.__new__();

//
// XXX: Internet Explorer blows
//
if (MochiKit.__export__) {
    reduce = MochiKit.Iter.reduce;
}

MochiKit.Base._exportSymbols(this, MochiKit.Iter);
/***

MochiKit.Logging 1.5

See <http://mochikit.com/> for documentation, downloads, license, etc.

(c) 2005 Bob Ippolito.  All rights Reserved.

***/

MochiKit.Base._module('Logging', '1.5', ['Base']);

    /** @id MochiKit.Logging.LogMessage */
MochiKit.Logging.LogMessage = function (num, level, info) {
    this.num = num;
    this.level = level;
    this.info = info;
    this.timestamp = new Date();
};

MochiKit.Logging.LogMessage.prototype = {
     /** @id MochiKit.Logging.LogMessage.prototype.repr */
    repr: function () {
        var m = MochiKit.Base;
        return 'LogMessage(' +
            m.map(
                m.repr,
                [this.num, this.level, this.info]
            ).join(', ') + ')';
    },
    /** @id MochiKit.Logging.LogMessage.prototype.toString */
    toString: MochiKit.Base.forwardCall("repr")
};

MochiKit.Base.update(MochiKit.Logging, {
    /** @id MochiKit.Logging.logLevelAtLeast */
    logLevelAtLeast: function (minLevel) {
        var self = MochiKit.Logging;
        if (typeof(minLevel) == 'string') {
            minLevel = self.LogLevel[minLevel];
        }
        return function (msg) {
            var msgLevel = msg.level;
            if (typeof(msgLevel) == 'string') {
                msgLevel = self.LogLevel[msgLevel];
            }
            return msgLevel >= minLevel;
        };
    },

    /** @id MochiKit.Logging.isLogMessage */
    isLogMessage: function (/* ... */) {
        var LogMessage = MochiKit.Logging.LogMessage;
        for (var i = 0; i < arguments.length; i++) {
            if (!(arguments[i] instanceof LogMessage)) {
                return false;
            }
        }
        return true;
    },

    /** @id MochiKit.Logging.compareLogMessage */
    compareLogMessage: function (a, b) {
        return MochiKit.Base.compare([a.level, a.info], [b.level, b.info]);
    },

    /** @id MochiKit.Logging.alertListener */
    alertListener: function (msg) {
        alert(
            "num: " + msg.num +
            "\nlevel: " +  msg.level +
            "\ninfo: " + msg.info.join(" ")
        );
    }

});

/** @id MochiKit.Logging.Logger */
MochiKit.Logging.Logger = function (/* optional */maxSize) {
    this.counter = 0;
    if (typeof(maxSize) == 'undefined' || maxSize === null) {
        maxSize = -1;
    }
    this.maxSize = maxSize;
    this._messages = [];
    this.listeners = {};
    this.useNativeConsole = false;
};

MochiKit.Logging.Logger.prototype = {
    /** @id MochiKit.Logging.Logger.prototype.clear */
    clear: function () {
        this._messages.splice(0, this._messages.length);
    },

    /** @id MochiKit.Logging.Logger.prototype.logToConsole */
    logToConsole: function (msg) {
        if (typeof(window) != "undefined" && window.console
                && window.console.log) {
            // Safari and FireBug 0.4
            // Percent replacement is a workaround for cute Safari crashing bug
            window.console.log(msg.replace(/%/g, '\uFF05'));
        } else if (typeof(opera) != "undefined" && opera.postError) {
            // Opera
            opera.postError(msg);
        } else if (typeof(Debug) != "undefined" && Debug.writeln) {
            // IE Web Development Helper (?)
            // http://www.nikhilk.net/Entry.aspx?id=93
            Debug.writeln(msg);
        } else if (typeof(debug) != "undefined" && debug.trace) {
            // Atlas framework (?)
            // http://www.nikhilk.net/Entry.aspx?id=93
            debug.trace(msg);
        }
    },

    /** @id MochiKit.Logging.Logger.prototype.dispatchListeners */
    dispatchListeners: function (msg) {
        for (var k in this.listeners) {
            var pair = this.listeners[k];
            if (pair.ident != k || (pair[0] && !pair[0](msg))) {
                continue;
            }
            pair[1](msg);
        }
    },

    /** @id MochiKit.Logging.Logger.prototype.addListener */
    addListener: function (ident, filter, listener) {
        if (typeof(filter) == 'string') {
            filter = MochiKit.Logging.logLevelAtLeast(filter);
        }
        var entry = [filter, listener];
        entry.ident = ident;
        this.listeners[ident] = entry;
    },

    /** @id MochiKit.Logging.Logger.prototype.removeListener */
    removeListener: function (ident) {
        delete this.listeners[ident];
    },

    /** @id MochiKit.Logging.Logger.prototype.baseLog */
    baseLog: function (level, message/*, ...*/) {
        if (typeof(level) == "number") {
            if (level >= MochiKit.Logging.LogLevel.FATAL) {
                level = 'FATAL';
            } else if (level >= MochiKit.Logging.LogLevel.ERROR) {
                level = 'ERROR';
            } else if (level >= MochiKit.Logging.LogLevel.WARNING) {
                level = 'WARNING';
            } else if (level >= MochiKit.Logging.LogLevel.INFO) {
                level = 'INFO';
            } else {
                level = 'DEBUG';
            }
        }
        var msg = new MochiKit.Logging.LogMessage(
            this.counter,
            level,
            MochiKit.Base.extend(null, arguments, 1)
        );
        this._messages.push(msg);
        this.dispatchListeners(msg);
        if (this.useNativeConsole) {
            this.logToConsole(msg.level + ": " + msg.info.join(" "));
        }
        this.counter += 1;
        while (this.maxSize >= 0 && this._messages.length > this.maxSize) {
            this._messages.shift();
        }
    },

    /** @id MochiKit.Logging.Logger.prototype.getMessages */
    getMessages: function (howMany) {
        var firstMsg = 0;
        if (!(typeof(howMany) == 'undefined' || howMany === null)) {
            firstMsg = Math.max(0, this._messages.length - howMany);
        }
        return this._messages.slice(firstMsg);
    },

    /** @id MochiKit.Logging.Logger.prototype.getMessageText */
    getMessageText: function (howMany) {
        if (typeof(howMany) == 'undefined' || howMany === null) {
            howMany = 30;
        }
        var messages = this.getMessages(howMany);
        if (messages.length) {
            var lst = map(function (m) {
                return '\n  [' + m.num + '] ' + m.level + ': ' + m.info.join(' ');
            }, messages);
            lst.unshift('LAST ' + messages.length + ' MESSAGES:');
            return lst.join('');
        }
        return '';
    },

    /** @id MochiKit.Logging.Logger.prototype.debuggingBookmarklet */
    debuggingBookmarklet: function (inline) {
        if (typeof(MochiKit.LoggingPane) == "undefined") {
            alert(this.getMessageText());
        } else {
            MochiKit.LoggingPane.createLoggingPane(inline || false);
        }
    }
};

MochiKit.Logging.__new__ = function () {
    this.LogLevel = {
        ERROR: 40,
        FATAL: 50,
        WARNING: 30,
        INFO: 20,
        DEBUG: 10
    };

    var m = MochiKit.Base;
    m.registerComparator("LogMessage",
        this.isLogMessage,
        this.compareLogMessage
    );

    var partial = m.partial;

    var Logger = this.Logger;
    var baseLog = Logger.prototype.baseLog;
    m.update(this.Logger.prototype, {
        debug: partial(baseLog, 'DEBUG'),
        log: partial(baseLog, 'INFO'),
        error: partial(baseLog, 'ERROR'),
        fatal: partial(baseLog, 'FATAL'),
        warning: partial(baseLog, 'WARNING')
    });

    // indirectly find logger so it can be replaced
    var self = this;
    var connectLog = function (name) {
        return function () {
            self.logger[name].apply(self.logger, arguments);
        };
    };

    /** @id MochiKit.Logging.log */
    this.log = connectLog('log');
    /** @id MochiKit.Logging.logError */
    this.logError = connectLog('error');
    /** @id MochiKit.Logging.logDebug */
    this.logDebug = connectLog('debug');
    /** @id MochiKit.Logging.logFatal */
    this.logFatal = connectLog('fatal');
    /** @id MochiKit.Logging.logWarning */
    this.logWarning = connectLog('warning');
    this.logger = new Logger();
    this.logger.useNativeConsole = true;

    m.nameFunctions(this);
};

MochiKit.Logging.__new__();

MochiKit.Base._exportSymbols(this, MochiKit.Logging);
/***

MochiKit.DateTime 1.5

See <http://mochikit.com/> for documentation, downloads, license, etc.

(c) 2005 Bob Ippolito.  All rights Reserved.

***/

MochiKit.Base._module('DateTime', '1.5', ['Base']);

/** @id MochiKit.DateTime.isoDate */
MochiKit.DateTime.isoDate = function (str) {
    str = str + "";
    if (typeof(str) != "string" || str.length === 0) {
        return null;
    }
    var iso = str.split('-');
    if (iso.length === 0) {
        return null;
    }
	var date = new Date(iso[0], iso[1] - 1, iso[2]);
	date.setFullYear(iso[0]);
	date.setMonth(iso[1] - 1);
	date.setDate(iso[2]);
    return date;
};

MochiKit.DateTime._isoRegexp = /(\d{4,})(?:-(\d{1,2})(?:-(\d{1,2})(?:[T ](\d{1,2}):(\d{1,2})(?::(\d{1,2})(?:\.(\d+))?)?(?:(Z)|([+-])(\d{1,2})(?::(\d{1,2}))?)?)?)?)?/;

/** @id MochiKit.DateTime.isoTimestamp */
MochiKit.DateTime.isoTimestamp = function (str) {
    str = str + "";
    if (typeof(str) != "string" || str.length === 0) {
        return null;
    }
    var res = str.match(MochiKit.DateTime._isoRegexp);
    if (typeof(res) == "undefined" || res === null) {
        return null;
    }
    var year, month, day, hour, min, sec, msec;
    year = parseInt(res[1], 10);
    if (typeof(res[2]) == "undefined" || res[2] === '') {
        return new Date(year);
    }
    month = parseInt(res[2], 10) - 1;
    day = parseInt(res[3], 10);
    if (typeof(res[4]) == "undefined" || res[4] === '') {
        return new Date(year, month, day);
    }
    hour = parseInt(res[4], 10);
    min = parseInt(res[5], 10);
    sec = (typeof(res[6]) != "undefined" && res[6] !== '') ? parseInt(res[6], 10) : 0;
    if (typeof(res[7]) != "undefined" && res[7] !== '') {
        msec = Math.round(1000.0 * parseFloat("0." + res[7]));
    } else {
        msec = 0;
    }
    if ((typeof(res[8]) == "undefined" || res[8] === '') && (typeof(res[9]) == "undefined" || res[9] === '')) {
        return new Date(year, month, day, hour, min, sec, msec);
    }
    var ofs;
    if (typeof(res[9]) != "undefined" && res[9] !== '') {
        ofs = parseInt(res[10], 10) * 3600000;
        if (typeof(res[11]) != "undefined" && res[11] !== '') {
            ofs += parseInt(res[11], 10) * 60000;
        }
        if (res[9] == "-") {
            ofs = -ofs;
        }
    } else {
        ofs = 0;
    }
    return new Date(Date.UTC(year, month, day, hour, min, sec, msec) - ofs);
};

/** @id MochiKit.DateTime.toISOTime */
MochiKit.DateTime.toISOTime = function (date, realISO/* = false */) {
    if (typeof(date) == "undefined" || date === null) {
        return null;
    }
    var hh = date.getHours();
    var mm = date.getMinutes();
    var ss = date.getSeconds();
    var lst = [
        ((realISO && (hh < 10)) ? "0" + hh : hh),
        ((mm < 10) ? "0" + mm : mm),
        ((ss < 10) ? "0" + ss : ss)
    ];
    return lst.join(":");
};

/** @id MochiKit.DateTime.toISOTimeStamp */
MochiKit.DateTime.toISOTimestamp = function (date, realISO/* = false*/) {
    if (typeof(date) == "undefined" || date === null) {
        return null;
    }
    var sep = realISO ? "T" : " ";
    var foot = realISO ? "Z" : "";
    if (realISO) {
        date = new Date(date.getTime() + (date.getTimezoneOffset() * 60000));
    }
    return MochiKit.DateTime.toISODate(date) + sep + MochiKit.DateTime.toISOTime(date, realISO) + foot;
};

/** @id MochiKit.DateTime.toISODate */
MochiKit.DateTime.toISODate = function (date) {
    if (typeof(date) == "undefined" || date === null) {
        return null;
    }
    var _padTwo = MochiKit.DateTime._padTwo;
	var _padFour = MochiKit.DateTime._padFour;
    return [
        _padFour(date.getFullYear()),
        _padTwo(date.getMonth() + 1),
        _padTwo(date.getDate())
    ].join("-");
};

/** @id MochiKit.DateTime.americanDate */
MochiKit.DateTime.americanDate = function (d) {
    d = d + "";
    if (typeof(d) != "string" || d.length === 0) {
        return null;
    }
    var a = d.split('/');
    return new Date(a[2], a[0] - 1, a[1]);
};

MochiKit.DateTime._padTwo = function (n) {
    return (n > 9) ? n : "0" + n;
};

MochiKit.DateTime._padFour = function(n) {
	switch(n.toString().length) {
		case 1: return "000" + n; break;
		case 2: return "00" + n; break;
		case 3: return "0" + n; break;
		case 4:
		default:
			return n;
	}
};

/** @id MochiKit.DateTime.toPaddedAmericanDate */
MochiKit.DateTime.toPaddedAmericanDate = function (d) {
    if (typeof(d) == "undefined" || d === null) {
        return null;
    }
    var _padTwo = MochiKit.DateTime._padTwo;
    return [
        _padTwo(d.getMonth() + 1),
        _padTwo(d.getDate()),
        d.getFullYear()
    ].join('/');
};

/** @id MochiKit.DateTime.toAmericanDate */
MochiKit.DateTime.toAmericanDate = function (d) {
    if (typeof(d) == "undefined" || d === null) {
        return null;
    }
    return [d.getMonth() + 1, d.getDate(), d.getFullYear()].join('/');
};

MochiKit.DateTime.__new__ = function () {
    MochiKit.Base.nameFunctions(this);
};

MochiKit.DateTime.__new__();

MochiKit.Base._exportSymbols(this, MochiKit.DateTime);
/***

MochiKit.Format 1.5

See <http://mochikit.com/> for documentation, downloads, license, etc.

(c) 2005 Bob Ippolito.  All rights Reserved.

***/

MochiKit.Base._module('Format', '1.5', ['Base']);

MochiKit.Format._numberFormatter = function (placeholder, header, footer, locale, isPercent, precision, leadingZeros, separatorAt, trailingZeros) {
    return function (num) {
        num = parseFloat(num);
        if (typeof(num) == "undefined" || num === null || isNaN(num)) {
            return placeholder;
        }
        var curheader = header;
        var curfooter = footer;
        if (num < 0) {
            num = -num;
        } else {
            curheader = curheader.replace(/-/, "");
        }
        var me = arguments.callee;
        var fmt = MochiKit.Format.formatLocale(locale);
        if (isPercent) {
            num = num * 100.0;
            curfooter = fmt.percent + curfooter;
        }
        num = MochiKit.Format.roundToFixed(num, precision);
        var parts = num.split(/\./);
        var whole = parts[0];
        var frac = (parts.length == 1) ? "" : parts[1];
        var res = "";
        while (whole.length < leadingZeros) {
            whole = "0" + whole;
        }
        if (separatorAt) {
            while (whole.length > separatorAt) {
                var i = whole.length - separatorAt;
                //res = res + fmt.separator + whole.substring(i, whole.length);
                res = fmt.separator + whole.substring(i, whole.length) + res;
                whole = whole.substring(0, i);
            }
        }
        res = whole + res;
        if (precision > 0) {
            while (frac.length < trailingZeros) {
                frac = frac + "0";
            }
            res = res + fmt.decimal + frac;
        }
        return curheader + res + curfooter;
    };
};

/** @id MochiKit.Format.numberFormatter */
MochiKit.Format.numberFormatter = function (pattern, placeholder/* = "" */, locale/* = "default" */) {
    // http://java.sun.com/docs/books/tutorial/i18n/format/numberpattern.html
    // | 0 | leading or trailing zeros
    // | # | just the number
    // | , | separator
    // | . | decimal separator
    // | % | Multiply by 100 and format as percent
    if (typeof(placeholder) == "undefined") {
        placeholder = "";
    }
    var match = pattern.match(/((?:[0#]+,)?[0#]+)(?:\.([0#]+))?(%)?/);
    if (!match) {
        throw TypeError("Invalid pattern");
    }
    var header = pattern.substr(0, match.index);
    var footer = pattern.substr(match.index + match[0].length);
    if (header.search(/-/) == -1) {
        header = header + "-";
    }
    var whole = match[1];
    var frac = (typeof(match[2]) == "string" && match[2] != "") ? match[2] : "";
    var isPercent = (typeof(match[3]) == "string" && match[3] != "");
    var tmp = whole.split(/,/);
    var separatorAt;
    if (typeof(locale) == "undefined") {
        locale = "default";
    }
    if (tmp.length == 1) {
        separatorAt = null;
    } else {
        separatorAt = tmp[1].length;
    }
    var leadingZeros = whole.length - whole.replace(/0/g, "").length;
    var trailingZeros = frac.length - frac.replace(/0/g, "").length;
    var precision = frac.length;
    var rval = MochiKit.Format._numberFormatter(
        placeholder, header, footer, locale, isPercent, precision,
        leadingZeros, separatorAt, trailingZeros
    );
    var m = MochiKit.Base;
    if (m) {
        var fn = arguments.callee;
        var args = m.concat(arguments);
        rval.repr = function () {
            return [
                self.NAME,
                "(",
                map(m.repr, args).join(", "),
                ")"
            ].join("");
        };
    }
    return rval;
};

/** @id MochiKit.Format.formatLocale */
MochiKit.Format.formatLocale = function (locale) {
    if (typeof(locale) == "undefined" || locale === null) {
        locale = "default";
    }
    if (typeof(locale) == "string") {
        var rval = MochiKit.Format.LOCALE[locale];
        if (typeof(rval) == "string") {
            rval = arguments.callee(rval);
            MochiKit.Format.LOCALE[locale] = rval;
        }
        return rval;
    } else {
        return locale;
    }
};

/** @id MochiKit.Format.twoDigitAverage */
MochiKit.Format.twoDigitAverage = function (numerator, denominator) {
    if (denominator) {
        var res = numerator / denominator;
        if (!isNaN(res)) {
            return MochiKit.Format.twoDigitFloat(res);
        }
    }
    return "0";
};

/** @id MochiKit.Format.twoDigitFloat */
MochiKit.Format.twoDigitFloat = function (aNumber) {
    var res = roundToFixed(aNumber, 2);
    if (res.indexOf(".00") > 0) {
        return res.substring(0, res.length - 3);
    } else if (res.charAt(res.length - 1) == "0") {
        return res.substring(0, res.length - 1);
    } else {
        return res;
    }
};

/** @id MochiKit.Format.lstrip */
MochiKit.Format.lstrip = function (str, /* optional */chars) {
    str = str + "";
    if (typeof(str) != "string") {
        return null;
    }
    if (!chars) {
        return str.replace(/^\s+/, "");
    } else {
        return str.replace(new RegExp("^[" + chars + "]+"), "");
    }
};

/** @id MochiKit.Format.rstrip */
MochiKit.Format.rstrip = function (str, /* optional */chars) {
    str = str + "";
    if (typeof(str) != "string") {
        return null;
    }
    if (!chars) {
        return str.replace(/\s+$/, "");
    } else {
        return str.replace(new RegExp("[" + chars + "]+$"), "");
    }
};

/** @id MochiKit.Format.strip */
MochiKit.Format.strip = function (str, /* optional */chars) {
    var self = MochiKit.Format;
    return self.rstrip(self.lstrip(str, chars), chars);
};

/** @id MochiKit.Format.truncToFixed */
MochiKit.Format.truncToFixed = function (aNumber, precision) {
    var fixed = MochiKit.Format._numberToFixed(aNumber, precision);
    var fracPos = fixed.indexOf(".");
    if (fracPos > 0 && fracPos + precision + 1 < fixed.length) {
        fixed = fixed.substring(0, fracPos + precision + 1);
        fixed = MochiKit.Format._shiftNumber(fixed, 0);
    }
    return fixed;
}

/** @id MochiKit.Format.roundToFixed */
MochiKit.Format.roundToFixed = function (aNumber, precision) {
    var fixed = MochiKit.Format._numberToFixed(aNumber, precision);
    var fracPos = fixed.indexOf(".");
    if (fracPos > 0 && fracPos + precision + 1 < fixed.length) {
        var str = MochiKit.Format._shiftNumber(fixed, precision);
        str = MochiKit.Format._numberToFixed(Math.round(parseFloat(str)), 0);
        fixed = MochiKit.Format._shiftNumber(str, -precision);
    }
    return fixed;
}

/**
 * Converts a number to a fixed format string. This function handles
 * conversion of exponents by shifting the decimal point to the left
 * or the right. It also guarantees a specified minimum number of
 * fractional digits (but no maximum).
 *
 * @param {Number} aNumber the number to convert
 * @param {Number} precision the minimum number of decimal digits
 *
 * @return {String} the fixed format number string
 */
MochiKit.Format._numberToFixed = function (aNumber, precision) {
    var str = aNumber.toString();
    var parts = str.split(/[eE]/);
    var exp = (parts.length === 1) ? 0 : parseInt(parts[1]) || 0;
    var fixed = MochiKit.Format._shiftNumber(parts[0], exp);
    parts = fixed.split(/\./);
    var whole = parts[0];
    var frac = (parts.length === 1) ? "" : parts[1];
    while (frac.length < precision) {
        frac += "0";
    }
    if (frac.length > 0) {
        return whole + "." + frac;
    } else {
        return whole;
    }
}

/**
 * Shifts the decimal dot location in a fixed format number string.
 * This function handles negative values and will add and remove
 * leading and trailing zeros as needed.
 *
 * @param {String} num the fixed format number string
 * @param {Number} exp the base-10 exponent to apply
 *
 * @return {String} the new fixed format number string
 */
MochiKit.Format._shiftNumber = function (num, exp) {
    var pos = num.indexOf(".");
    if (pos < 0) {
        pos = num.length;
    } else {
        num = num.substring(0, pos) + num.substring(pos + 1);
    }
    pos += exp;
    while (pos <= 0 || (pos <= 1 && num.charAt(0) === "-")) {
        if (num.charAt(0) === "-") {
            num = "-0" + num.substring(1);
        } else {
            num = "0" + num;
        }
        pos++;
    }
    while (pos > num.length) {
        num += "0";
    }
    if (pos < num.length) {
        num = num.substring(0, pos) + "." + num.substring(pos);
    }
    while (/^0[^.]/.test(num)) {
        num = num.substring(1);
    }
    while (/^-0[^.]/.test(num)) {
        num = "-" + num.substring(2);
    }
    return num;
}

/** @id MochiKit.Format.percentFormat */
MochiKit.Format.percentFormat = function (aNumber) {
    return MochiKit.Format.twoDigitFloat(100 * aNumber) + '%';
};

MochiKit.Format.LOCALE = {
    en_US: {separator: ",", decimal: ".", percent: "%"},
    de_DE: {separator: ".", decimal: ",", percent: "%"},
    pt_BR: {separator: ".", decimal: ",", percent: "%"},
    fr_FR: {separator: " ", decimal: ",", percent: "%"},
    "default": "en_US",
    __export__: false
};

MochiKit.Format.__new__ = function () {
    MochiKit.Base.nameFunctions(this);
    var base = this.NAME + ".";
    var k, v, o;
    for (k in this.LOCALE) {
        o = this.LOCALE[k];
        if (typeof(o) == "object") {
            o.repr = function () { return this.NAME; };
            o.NAME = base + "LOCALE." + k;
        }
    }
};

MochiKit.Format.__new__();

MochiKit.Base._exportSymbols(this, MochiKit.Format);
/***

MochiKit.Text 1.5

See <http://mochikit.com/> for documentation, downloads, license, etc.

(c) 2008 Per Cederberg.  All rights Reserved.

***/

MochiKit.Base._module('Text', '1.5', ['Base', 'Format']);

/**
 * Checks if a text string starts with the specified substring. If
 * either of the two strings is null, false will be returned.
 *
 * @param {String} substr the substring to search for
 * @param {String} str the string to search in
 *
 * @return {Boolean} true if the string starts with the substring, or
 *         false otherwise
 */
MochiKit.Text.startsWith = function (substr, str) {
    return str != null && substr != null && str.indexOf(substr) == 0;
}

/**
 * Checks if a text string ends with the specified substring. If
 * either of the two strings is null, false will be returned.
 *
 * @param {String} substr the substring to search for
 * @param {String} str the string to search in
 *
 * @return {Boolean} true if the string ends with the substring, or
 *         false otherwise
 */
MochiKit.Text.endsWith = function (substr, str) {
    return str != null && substr != null &&
           str.lastIndexOf(substr) == Math.max(str.length - substr.length, 0);
}

/**
 * Checks if a text string contains the specified substring. If
 * either of the two strings is null, false will be returned.
 *
 * @param {String} substr the substring to search for
 * @param {String} str the string to search in
 *
 * @return {Boolean} true if the string contains the substring, or
 *         false otherwise
 */
MochiKit.Text.contains = function (substr, str) {
    return str != null && substr != null && str.indexOf(substr) >= 0;
}

/**
 * Adds a character to the left-hand side of a string until it
 * reaches the specified minimum length.
 *
 * @param {String} str the string to process
 * @param {Number} minLength the requested minimum length
 * @param {String} fillChar the padding character to add, defaults
 *            to a space
 *
 * @return {String} the padded string
 */
MochiKit.Text.padLeft = function (str, minLength, fillChar) {
    str = str || "";
    fillChar = fillChar || " ";
    while (str.length < minLength) {
        str = fillChar + str;
    }
    return str;
}

/**
 * Adds a character to the right-hand side of a string until it
 * reaches the specified minimum length.
 *
 * @param {String} str the string to process
 * @param {Number} minLength the requested minimum length
 * @param {String} fillChar the padding character to add, defaults
 *            to a space
 *
 * @return {String} the padded string
 */
MochiKit.Text.padRight = function (str, minLength, fillChar) {
    str = str || "";
    fillChar = fillChar || " ";
    while (str.length < minLength) {
        str += fillChar;
    }
    return str;
}

/**
 * Returns a truncated copy of a string. If the string is shorter
 * than the specified maximum length, the object will be returned
 * unmodified. If an optional tail string is specified, additional
 * elements will be removed in order to accomodate the tail (that
 * will be appended). This function also works on arrays.
 *
 * @param {String} str the string to truncate
 * @param {Number} maxLength the maximum length
 * @param {String} [tail] the tail to append on truncation
 *
 * @return {String} the truncated string
 */
MochiKit.Text.truncate = function (str, maxLength, tail) {
    if (str == null || str.length <= maxLength || maxLength < 0) {
        return str;
    } else if (tail != null) {
        str = str.slice(0, Math.max(0, maxLength - tail.length));
        if (typeof(str) == "string") {
            return str + tail;
        } else {
            return MochiKit.Base.extend(str, tail);
        }
    } else {
        return str.slice(0, maxLength);
    }
}

/**
 * Splits a text string using separator as the split point
 * If max is given, at most max splits are done, giving at most
 * max + 1 elements in the returned list.
 *
 * @param {String} str the string to split
 * @param {String} [separator] the separator character to use,
 *            defaults to newline
 * @param {Int} [max] the maximum number of parts to return
 * @return {Array} an array of parts of the string
 */
MochiKit.Text.split = function (str, separator, max) {
    if (str == null || str.length == 0) {
        return str;
    }
    separator = separator || '\n'
    var bits = str.split(separator);
    if ((typeof(max) == "undefined") || max >= bits.length-1){
	return bits;
    }
    bits.splice(max, bits.length, bits.slice(max, bits.length).join(separator))
    return bits;
}

/**
 * Splits a text string using separator as the split point
 * If max is given, at most max splits are done,
 * using splits from the right
 *
 * @param {String} str the string to split
 * @param {String} [separator] the separator character to use,
 *            defaults to newline
 * @param {Int} [max] the maximum number of parts to return
 * @return {Array} an array of parts of the string
 */
MochiKit.Text.rsplit = function (str, separator, max) {
    if (str == null || str.length == 0) {
        return str;
    }
    separator = separator || '\n'
    var bits = str.split(separator);
    if ((typeof(max) == "undefined") || max >= bits.length-1){
	return bits;
    }
    bits.splice(0, bits.length-max, bits.slice(0, bits.length-max).join(separator))
    return bits;
}

/**
 * Splits a text string, applies a function and joins the results
 * back together again. This is a convenience function for calling
 * split(), map() and join() separately. It can be used to easily
 * trim each line in a text string (using the strip function), or to
 * translate a text word-by-word.
 *
 * @param {Function} func the function to apply
 * @param {String} str the string to split
 * @param {String} [separator] the separator character to use,
 *            defaults to newline
 *
 * @return {String} a string with the joined up results
 */
MochiKit.Text.splitJoin = function (func, str, separator) {
    if (str == null || str.length == 0) {
        return str;
    }
    separator = separator || '\n'
    return MochiKit.Base.map(func, str.split(separator)).join(separator);
}

/**
 * Creates a formatter function for the specified formatter pattern
 * and locale. The returned function takes as many arguments as the
 * formatter pattern requires. See separate documentation for
 * information about the formatter pattern syntax.
 *
 * @param {String} pattern the formatter pattern string
 * @param {Object} [locale] the locale to use, defaults to
 *            LOCALE.en_US
 *
 * @return {Function} the formatter function created
 *
 * @throws FormatPatternError if the format pattern was invalid
 */
MochiKit.Text.formatter = function (pattern, locale) {
    if (typeof(locale) == "undefined") {
        locale = MochiKit.Format.formatLocale();
    } else if (typeof(locale) == "string") {
        locale = MochiKit.Format.formatLocale(locale);
    }
    var parts = MochiKit.Text._parsePattern(pattern);
    return function() {
        var values = MochiKit.Base.extend([], arguments);
        var res = [];
        for (var i = 0; i < parts.length; i++) {
            if (typeof(parts[i]) == "string") {
                res.push(parts[i]);
            } else {
                res.push(MochiKit.Text.formatValue(parts[i], values, locale));
            }
        }
        return res.join("");
    }
}

/**
 * Formats the specified arguments according to a formatter pattern.
 * See separate documentation for information about the formatter
 * pattern syntax.
 *
 * @param {String} pattern the formatter pattern string
 * @param {Object} [...] the optional values to format
 *
 * @return {String} the formatted output string
 *
 * @throws FormatPatternError if the format pattern was invalid
 */
MochiKit.Text.format = function (pattern/*, ...*/) {
    var func = MochiKit.Text.formatter(pattern);
    return func.apply(this, MochiKit.Base.extend([], arguments, 1));
}

/**
 * Format a value with the specified format specifier.
 *
 * @param {String/Object} spec the format specifier string or parsed
 *            format specifier object
 * @param {Object} value the value to format
 * @param {Object} [locale] the locale to use, defaults to
 *            LOCALE.en_US
 *
 * @return {String} the formatted output string
 */
MochiKit.Text.formatValue = function (spec, value, locale) {
    var self = MochiKit.Text;
    if (typeof(spec) === "string") {
        spec = self._parseFormatFlags(spec, 0, spec.length - 1);
    }
    for (var i = 0; spec.path != null && i < spec.path.length; i++) {
        if (value != null) {
            value = value[spec.path[i]];
        }
    }
    if (typeof(locale) == "undefined") {
        locale = MochiKit.Format.formatLocale();
    } else if (typeof(locale) == "string") {
        locale = MochiKit.Format.formatLocale(locale);
    }
    var str = "";
    if (spec.numeric) {
        if (typeof(value) != "number" || isNaN(value)) {
            str = "";
        } else if (value === Number.POSITIVE_INFINITY) {
            str = "\u221e";
        } else if (value === Number.NEGATIVE_INFINITY) {
            str = "-\u221e";
        } else {
            var sign = (spec.sign === "-") ? "" : spec.sign;
            sign = (value < 0) ? "-" : sign;
            value = Math.abs(value);
            if (spec.format === "%") {
                str = self._truncToPercent(value, spec.precision);
            } else if (spec.format === "d") {
                str = MochiKit.Format.roundToFixed(value, 0);
            } else if (spec.radix != 10) {
                str = Math.floor(value).toString(spec.radix);
                if (spec.format === "x") {
                    str = str.toLowerCase();
                } else if (spec.format === "X") {
                    str = str.toUpperCase();
                }
            } else if (spec.precision >= 0) {
                str = MochiKit.Format.roundToFixed(value, spec.precision);
            } else {
                str = value.toString();
            }
            if (spec.padding === "0" && spec.format === "%") {
                str = self.padLeft(str, spec.width - sign.length - 1, "0");
            } else if (spec.padding == "0") {
                str = self.padLeft(str, spec.width - sign.length, "0");
            }
            str = self._localizeNumber(str, locale, spec.grouping);
            str = sign + str;
        }
        if (str !== "" && spec.format === "%") {
            str = str + locale.percent;
        }
    } else {
        if (spec.format == "r") {
            str = MochiKit.Base.repr(value);
        } else {
            str = (value == null) ? "null" : value.toString();
        }
        str = self.truncate(str, spec.precision);
    }
    if (spec.align == "<") {
        str = self.padRight(str, spec.width);
    } else {
        str = self.padLeft(str, spec.width);
    }
    return str;
}

/**
 * Adjust an already formatted numeric string for locale-specific
 * grouping and decimal separators. The grouping is optional and
 * will attempt to keep the number string length intact by removing
 * padded zeros (if possible).
 *
 * @param {String} num the formatted number string
 * @param {Object} locale the formatting locale to use
 * @param {Boolean} grouping the grouping flag
 *
 * @return {String} the localized number string
 */
MochiKit.Text._localizeNumber = function (num, locale, grouping) {
    var parts = num.split(/\./);
    var whole = parts[0];
    var frac = (parts.length == 1) ? "" : parts[1];
    var res = (frac.length > 0) ? locale.decimal : "";
    while (grouping && frac.length > 3) {
        res = res + frac.substring(0, 3) + locale.separator;
        frac = frac.substring(3);
        if (whole.charAt(0) == "0") {
            whole = whole.substring(1);
        }
    }
    if (frac.length > 0) {
        res += frac;
    }
    while (grouping && whole.length > 3) {
        var pos = whole.length - 3;
        res = locale.separator + whole.substring(pos) + res;
        whole = whole.substring((whole.charAt(0) == "0") ? 1 : 0, pos);
    }
    return whole + res;
}

/**
 * Parses a format pattern and returns an array of constant strings
 * and format info objects.
 *
 * @param {String} pattern the format pattern to analyze
 *
 * @return {Array} an array of strings and format info objects
 *
 * @throws FormatPatternError if the format pattern was invalid
 */
MochiKit.Text._parsePattern = function (pattern) {
    var self = MochiKit.Text;
    var parts = [];
    var start = 0;
    var pos = 0;
    for (pos = 0; pos < pattern.length; pos++) {
        if (pattern.charAt(pos) == "{") {
            if (pos + 1 >= pattern.length) {
                var msg = "unescaped { char, should be escaped as {{";
                throw new self.FormatPatternError(pattern, pos, msg);
            } else if (pattern.charAt(pos + 1) == "{") {
                parts.push(pattern.substring(start, pos + 1));
                start = pos + 2;
                pos++;
            } else {
                if (start < pos) {
                    parts.push(pattern.substring(start, pos));
                }
                start = pattern.indexOf("}", pos) + 1;
                if (start <= 0) {
                    var msg = "unmatched { char, not followed by a } char";
                    throw new self.FormatPatternError(pattern, pos, msg);
                }
                parts.push(self._parseFormat(pattern, pos + 1, start - 1));
                pos = start - 1;
            }
        } else if (pattern.charAt(pos) == "}") {
            if (pos + 1 >= pattern.length || pattern.charAt(pos + 1) != "}") {
                var msg = "unescaped } char, should be escaped as }}";
                throw new self.FormatPatternError(pattern, pos, msg);
            }
            parts.push(pattern.substring(start, pos + 1));
            start = pos + 2;
            pos++;
        }
    }
    if (start < pos) {
        parts.push(pattern.substring(start, pos));
    }
    return parts;
}

/**
 * Parses a format instruction and returns a format info object.
 *
 * @param {String} pattern the format pattern string
 * @param {Number} startPos the first index of the format instruction
 * @param {Number} endPos the last index of the format instruction
 *
 * @return {Object} the format info object
 *
 * @throws FormatPatternError if the format pattern was invalid
 */
MochiKit.Text._parseFormat = function (pattern, startPos, endPos) {
    var self = MochiKit.Text;
    var text = pattern.substring(startPos, endPos);
    var info;
    var pos = text.indexOf(":");
    if (pos == 0) {
        info = self._parseFormatFlags(pattern, startPos + 1, endPos);
        info.path = [0];
    } else if (pos > 0) {
        info = self._parseFormatFlags(pattern, startPos + pos + 1, endPos);
        info.path = text.substring(0, pos).split(".");
    } else {
        info = self._parseFormatFlags(pattern, endPos, endPos);
        info.path = text.split(".");
    }
    var DIGITS = /^\d+$/;
    for (var i = 0; i < info.path.length; i++) {
        var e = info.path[i];
        if (typeof(e) == "string") {
            // TODO: replace with MochiKit.Format.strip?
            e = e.replace(/^\s+/, "").replace(/\s+$/, "");
            if (e == "" && info.path.length == 1) {
                e = 0;
            } else if (e == "") {
                var msg = "format value path contains blanks";
                throw new self.FormatPatternError(pattern, startPos, msg);
            } else if (DIGITS.test(e)) {
                e = parseInt(e);
            }
        }
        info.path[i] = e;
    }
    if (info.path.length < 0 || typeof(info.path[0]) != "number") {
        info.path.unshift(0);
    }
    return info;
}

/**
 * Parses a string with format flags and returns a format info object.
 *
 * @param {String} pattern the format pattern string
 * @param {Number} startPos the first index of the format instruction
 * @param {Number} endPos the last index of the format instruction
 *
 * @return {Object} the format info object
 *
 * @throws FormatPatternError if the format pattern was invalid
 */
MochiKit.Text._parseFormatFlags = function (pattern, startPos, endPos) {
    var self = MochiKit.Text;
    var info = { numeric: false, format: "s", width: 0, precision: -1,
                 align: ">", sign: "-", padding: " ", grouping: false };
    // TODO: replace with MochiKit.Format.rstrip?
    var flags = pattern.substring(startPos, endPos).replace(/\s+$/, "");
    while (flags.length > 0) {
        switch (flags.charAt(0)) {
        case ">":
        case "<":
            info.align = flags.charAt(0);
            flags = flags.substring(1);
            break;
        case "+":
        case "-":
        case " ":
            info.sign = flags.charAt(0);
            flags = flags.substring(1);
            break;
        case ",":
            info.grouping = true;
            flags = flags.substring(1);
            break;
        case ".":
            var chars = /^\d*/.exec(flags.substring(1))[0];
            info.precision = parseInt(chars);
            flags = flags.substring(1 + chars.length);
            break;
        case "0":
            info.padding = flags.charAt(0);
            flags = flags.substring(1);
            break;
        case "1":
        case "2":
        case "3":
        case "4":
        case "5":
        case "6":
        case "7":
        case "8":
        case "9":
            var chars = /^\d*/.exec(flags)[0];
            info.width = parseInt(chars);
            flags = flags.substring(chars.length);
            break;
        case "s":
        case "r":
            info.format = flags.charAt(0);
            flags = flags.substring(1);
            break;
        case "b":
        case "d":
        case "o":
        case "x":
        case "X":
        case "f":
        case "%":
            info.numeric = true;
            info.format = flags.charAt(0);
            info.radix = 10;
            if (info.format === "b") {
                info.radix = 2;
            } else if (info.format === "o") {
                info.radix = 8;
            } else if (info.format === "x" || info.format === "X") {
                info.radix = 16;
            }
            flags = flags.substring(1);
            break;
        default:
            var msg = "unsupported format flag: " + flags.charAt(0);
            throw new self.FormatPatternError(pattern, startPos, msg);
        }
    }
    return info;
}

/**
 * Formats a value as a percentage. This method avoids multiplication
 * by 100 since it leads to weird numeric rounding errors. Instead it
 * just move the decimal separator in the text string. It is ugly,
 * but works...
 *
 * @param {Number} value the value to format
 * @param {Number} precision the number of precision digits
 */
MochiKit.Text._truncToPercent = function (value, precision) {
    // TODO: This can be simplified by using the same helper function
    //       as roundToFixed now does.
    var str;
    if (precision >= 0) {
        str = MochiKit.Format.roundToFixed(value, precision + 2);
    } else {
        str = (value == null) ? "0" : value.toString();
    }
    var fracPos = str.indexOf(".");
    if (fracPos < 0) {
        str = str + "00";
    } else if (fracPos + 3 >= str.length) {
        var fraction = str.substring(fracPos + 1);
        while (fraction.length < 2) {
            fraction = fraction + "0";
        }
        str = str.substring(0, fracPos) + fraction;
    } else {
        var fraction = str.substring(fracPos + 1);
        str = str.substring(0, fracPos) + fraction.substring(0, 2) +
              "." + fraction.substring(2);
    }
    while (str.length > 1 && str.charAt(0) == "0" && str.charAt(1) != ".") {
        str = str.substring(1);
    }
    return str;
}

/**
 * Creates a new format pattern error.
 *
 * @param {String} pattern the format pattern string
 * @param {Number} pos the position of the error
 * @param {String} message the error message text
 *
 * @return {Error} the format pattern error
 *
 * @class The format pattern error class. This error is thrown when
 *     a syntax error is encountered inside a format string.
 * @property {String} pattern The format pattern string.
 * @property {Number} pos The position of the error.
 * @property {String} message The error message text.
 * @extends MochiKit.Base.NamedError
 */
MochiKit.Text.FormatPatternError = function (pattern, pos, message) {
    this.pattern = pattern;
    this.pos = pos;
    this.message = message;
}
MochiKit.Text.FormatPatternError.prototype =
    new MochiKit.Base.NamedError("MochiKit.Text.FormatPatternError");


//
//XXX: Internet Explorer exception handling blows
//
if (MochiKit.__export__) {
    formatter = MochiKit.Text.formatter;
    format = MochiKit.Text.format;
    formatValue = MochiKit.Text.formatValue;
}


MochiKit.Base.nameFunctions(MochiKit.Text);
MochiKit.Base._exportSymbols(this, MochiKit.Text);
/***

MochiKit.Async 1.5

See <http://mochikit.com/> for documentation, downloads, license, etc.

(c) 2005 Bob Ippolito.  All rights Reserved.

***/

MochiKit.Base._module('Async', '1.5', ['Base']);

/** @id MochiKit.Async.Deferred */
MochiKit.Async.Deferred = function (/* optional */ canceller) {
    this.chain = [];
    this.id = this._nextId();
    this.fired = -1;
    this.paused = 0;
    this.results = [null, null];
    this.canceller = canceller;
    this.silentlyCancelled = false;
    this.chained = false;
};

MochiKit.Async.Deferred.prototype = {
    /** @id MochiKit.Async.Deferred.prototype.repr */
    repr: function () {
        var state;
        if (this.fired == -1) {
            state = 'unfired';
        } else if (this.fired === 0) {
            state = 'success';
        } else {
            state = 'error';
        }
        return 'Deferred(' + this.id + ', ' + state + ')';
    },

    toString: MochiKit.Base.forwardCall("repr"),

    _nextId: MochiKit.Base.counter(),

    /** @id MochiKit.Async.Deferred.prototype.cancel */
    cancel: function () {
        var self = MochiKit.Async;
        if (this.fired == -1) {
            if (this.canceller) {
                this.canceller(this);
            } else {
                this.silentlyCancelled = true;
            }
            if (this.fired == -1) {
                this.errback(new self.CancelledError(this));
            }
        } else if ((this.fired === 0) && (this.results[0] instanceof self.Deferred)) {
            this.results[0].cancel();
        }
    },

    _resback: function (res) {
        /***

        The primitive that means either callback or errback

        ***/
        this.fired = ((res instanceof Error) ? 1 : 0);
        this.results[this.fired] = res;
        this._fire();
    },

    _check: function () {
        if (this.fired != -1) {
            if (!this.silentlyCancelled) {
                throw new MochiKit.Async.AlreadyCalledError(this);
            }
            this.silentlyCancelled = false;
            return;
        }
    },

    /** @id MochiKit.Async.Deferred.prototype.callback */
    callback: function (res) {
        this._check();
        if (res instanceof MochiKit.Async.Deferred) {
            throw new Error("Deferred instances can only be chained if they are the result of a callback");
        }
        this._resback(res);
    },

    /** @id MochiKit.Async.Deferred.prototype.errback */
    errback: function (res) {
        this._check();
        var self = MochiKit.Async;
        if (res instanceof self.Deferred) {
            throw new Error("Deferred instances can only be chained if they are the result of a callback");
        }
        if (!(res instanceof Error)) {
            res = new self.GenericError(res);
        }
        this._resback(res);
    },

    /** @id MochiKit.Async.Deferred.prototype.addBoth */
    addBoth: function (fn) {
        if (arguments.length > 1) {
            fn = MochiKit.Base.partial.apply(null, arguments);
        }
        return this.addCallbacks(fn, fn);
    },

    /** @id MochiKit.Async.Deferred.prototype.addCallback */
    addCallback: function (fn) {
        if (arguments.length > 1) {
            fn = MochiKit.Base.partial.apply(null, arguments);
        }
        return this.addCallbacks(fn, null);
    },

    /** @id MochiKit.Async.Deferred.prototype.addErrback */
    addErrback: function (fn) {
        if (arguments.length > 1) {
            fn = MochiKit.Base.partial.apply(null, arguments);
        }
        return this.addCallbacks(null, fn);
    },

    /** @id MochiKit.Async.Deferred.prototype.addCallbacks */
    addCallbacks: function (cb, eb) {
        if (this.chained) {
            throw new Error("Chained Deferreds can not be re-used");
        }
        this.chain.push([cb, eb]);
        if (this.fired >= 0) {
            this._fire();
        }
        return this;
    },

    _fire: function () {
        /***

        Used internally to exhaust the callback sequence when a result
        is available.

        ***/
        var chain = this.chain;
        var fired = this.fired;
        var res = this.results[fired];
        var self = this;
        var cb = null;
        while (chain.length > 0 && this.paused === 0) {
            // Array
            var pair = chain.shift();
            var f = pair[fired];
            if (f === null) {
                continue;
            }
            try {
                res = f(res);
                fired = ((res instanceof Error) ? 1 : 0);
                if (res instanceof MochiKit.Async.Deferred) {
                    cb = function (res) {
                        self._resback(res);
                        self.paused--;
                        if ((self.paused === 0) && (self.fired >= 0)) {
                            self._fire();
                        }
                    };
                    this.paused++;
                }
            } catch (err) {
                fired = 1;
                if (!(err instanceof Error)) {
                    err = new MochiKit.Async.GenericError(err);
                }
                res = err;
            }
        }
        this.fired = fired;
        this.results[fired] = res;
        if (cb && this.paused) {
            // this is for "tail recursion" in case the dependent deferred
            // is already fired
            res.addBoth(cb);
            res.chained = true;
        }
    }
};

MochiKit.Base.update(MochiKit.Async, {
    /** @id MochiKit.Async.evalJSONRequest */
    evalJSONRequest: function (req) {
        return MochiKit.Base.evalJSON(req.responseText);
    },

    /** @id MochiKit.Async.succeed */
    succeed: function (/* optional */result) {
        var d = new MochiKit.Async.Deferred();
        d.callback.apply(d, arguments);
        return d;
    },

    /** @id MochiKit.Async.fail */
    fail: function (/* optional */result) {
        var d = new MochiKit.Async.Deferred();
        d.errback.apply(d, arguments);
        return d;
    },

    /** @id MochiKit.Async.getXMLHttpRequest */
    getXMLHttpRequest: function () {
        var self = arguments.callee;
        if (!self.XMLHttpRequest) {
            var tryThese = [
                function () { return new XMLHttpRequest(); },
                function () { return new ActiveXObject('Msxml2.XMLHTTP'); },
                function () { return new ActiveXObject('Microsoft.XMLHTTP'); },
                function () { return new ActiveXObject('Msxml2.XMLHTTP.4.0'); },
                function () {
                    throw new MochiKit.Async.BrowserComplianceError("Browser does not support XMLHttpRequest");
                }
            ];
            for (var i = 0; i < tryThese.length; i++) {
                var func = tryThese[i];
                try {
                    self.XMLHttpRequest = func;
                    return func();
                } catch (e) {
                    // pass
                }
            }
        }
        return self.XMLHttpRequest();
    },

    _xhr_onreadystatechange: function (d) {
        // MochiKit.Logging.logDebug('this.readyState', this.readyState);
        var m = MochiKit.Base;
        if (this.readyState == 4) {
            // IE SUCKS
            try {
                this.onreadystatechange = null;
            } catch (e) {
                try {
                    this.onreadystatechange = m.noop;
                } catch (e) {
                }
            }
            var status = null;
            try {
                status = this.status;
                if (!status && m.isNotEmpty(this.responseText)) {
                    // 0 or undefined seems to mean cached or local
                    status = 304;
                }
            } catch (e) {
                // pass
                // MochiKit.Logging.logDebug('error getting status?', repr(items(e)));
            }
            // 200 is OK, 201 is CREATED, 204 is NO CONTENT
            // 304 is NOT MODIFIED, 1223 is apparently a bug in IE
            if (status == 200 || status == 201 || status == 204 ||
                    status == 304 || status == 1223) {
                d.callback(this);
            } else {
                var err = new MochiKit.Async.XMLHttpRequestError(this, "Request failed");
                if (err.number) {
                    // XXX: This seems to happen on page change
                    d.errback(err);
                } else {
                    // XXX: this seems to happen when the server is unreachable
                    d.errback(err);
                }
            }
        }
    },

    _xhr_canceller: function (req) {
        // IE SUCKS
        try {
            req.onreadystatechange = null;
        } catch (e) {
            try {
                req.onreadystatechange = MochiKit.Base.noop;
            } catch (e) {
            }
        }
        req.abort();
    },


    /** @id MochiKit.Async.sendXMLHttpRequest */
    sendXMLHttpRequest: function (req, /* optional */ sendContent) {
        if (typeof(sendContent) == "undefined" || sendContent === null) {
            sendContent = "";
        }

        var m = MochiKit.Base;
        var self = MochiKit.Async;
        var d = new self.Deferred(m.partial(self._xhr_canceller, req));

        try {
            req.onreadystatechange = m.bind(self._xhr_onreadystatechange,
                req, d);
            req.send(sendContent);
        } catch (e) {
            try {
                req.onreadystatechange = null;
            } catch (ignore) {
                // pass
            }
            d.errback(e);
        }

        return d;

    },

    /** @id MochiKit.Async.doXHR */
    doXHR: function (url, opts) {
        /*
            Work around a Firefox bug by dealing with XHR during
            the next event loop iteration. Maybe it's this one:
            https://bugzilla.mozilla.org/show_bug.cgi?id=249843
        */
        var self = MochiKit.Async;
        return self.callLater(0, self._doXHR, url, opts);
    },

    _doXHR: function (url, opts) {
        var m = MochiKit.Base;
        opts = m.update({
            method: 'GET',
            sendContent: ''
            /*
            queryString: undefined,
            username: undefined,
            password: undefined,
            headers: undefined,
            mimeType: undefined
            */
        }, opts);
        var self = MochiKit.Async;
        var req = self.getXMLHttpRequest();
        if (opts.queryString) {
            var qs = m.queryString(opts.queryString);
            if (qs) {
                url += "?" + qs;
            }
        }
        // Safari will send undefined:undefined, so we have to check.
        // We can't use apply, since the function is native.
        if ('username' in opts) {
            req.open(opts.method, url, true, opts.username, opts.password);
        } else {
            req.open(opts.method, url, true);
        }
        if (req.overrideMimeType && opts.mimeType) {
            req.overrideMimeType(opts.mimeType);
        }
        req.setRequestHeader("X-Requested-With", "XMLHttpRequest");
        if (opts.headers) {
            var headers = opts.headers;
            if (!m.isArrayLike(headers)) {
                headers = m.items(headers);
            }
            for (var i = 0; i < headers.length; i++) {
                var header = headers[i];
                var name = header[0];
                var value = header[1];
                req.setRequestHeader(name, value);
            }
        }
        return self.sendXMLHttpRequest(req, opts.sendContent);
    },

    _buildURL: function (url/*, ...*/) {
        if (arguments.length > 1) {
            var m = MochiKit.Base;
            var qs = m.queryString.apply(null, m.extend(null, arguments, 1));
            if (qs) {
                return url + "?" + qs;
            }
        }
        return url;
    },

    /** @id MochiKit.Async.doSimpleXMLHttpRequest */
    doSimpleXMLHttpRequest: function (url/*, ...*/) {
        var self = MochiKit.Async;
        url = self._buildURL.apply(self, arguments);
        return self.doXHR(url);
    },

    /** @id MochiKit.Async.loadJSONDoc */
    loadJSONDoc: function (url/*, ...*/) {
        var self = MochiKit.Async;
        url = self._buildURL.apply(self, arguments);
        var d = self.doXHR(url, {
            'mimeType': 'text/plain',
            'headers': [['Accept', 'application/json']]
        });
        d = d.addCallback(self.evalJSONRequest);
        return d;
    },

    /** @id MochiKit.Async.wait */
    wait: function (seconds, /* optional */value) {
        var d = new MochiKit.Async.Deferred();
        var m = MochiKit.Base;
        if (typeof(value) != 'undefined') {
            d.addCallback(function () { return value; });
        }
        var timeout = setTimeout(
            m.bind("callback", d),
            Math.floor(seconds * 1000));
        d.canceller = function () {
            try {
                clearTimeout(timeout);
            } catch (e) {
                // pass
            }
        };
        return d;
    },

    /** @id MochiKit.Async.callLater */
    callLater: function (seconds, func) {
        var m = MochiKit.Base;
        var pfunc = m.partial.apply(m, m.extend(null, arguments, 1));
        return MochiKit.Async.wait(seconds).addCallback(
            function (res) { return pfunc(); }
        );
    }
});


/** @id MochiKit.Async.DeferredLock */
MochiKit.Async.DeferredLock = function () {
    this.waiting = [];
    this.locked = false;
    this.id = this._nextId();
};

MochiKit.Async.DeferredLock.prototype = {
    __class__: MochiKit.Async.DeferredLock,
    /** @id MochiKit.Async.DeferredLock.prototype.acquire */
    acquire: function () {
        var d = new MochiKit.Async.Deferred();
        if (this.locked) {
            this.waiting.push(d);
        } else {
            this.locked = true;
            d.callback(this);
        }
        return d;
    },
    /** @id MochiKit.Async.DeferredLock.prototype.release */
    release: function () {
        if (!this.locked) {
            throw TypeError("Tried to release an unlocked DeferredLock");
        }
        this.locked = false;
        if (this.waiting.length > 0) {
            this.locked = true;
            this.waiting.shift().callback(this);
        }
    },
    _nextId: MochiKit.Base.counter(),
    repr: function () {
        var state;
        if (this.locked) {
            state = 'locked, ' + this.waiting.length + ' waiting';
        } else {
            state = 'unlocked';
        }
        return 'DeferredLock(' + this.id + ', ' + state + ')';
    },
    toString: MochiKit.Base.forwardCall("repr")

};

/** @id MochiKit.Async.DeferredList */
MochiKit.Async.DeferredList = function (list, /* optional */fireOnOneCallback, fireOnOneErrback, consumeErrors, canceller) {

    // call parent constructor
    MochiKit.Async.Deferred.apply(this, [canceller]);

    this.list = list;
    var resultList = [];
    this.resultList = resultList;

    this.finishedCount = 0;
    this.fireOnOneCallback = fireOnOneCallback;
    this.fireOnOneErrback = fireOnOneErrback;
    this.consumeErrors = consumeErrors;

    var cb = MochiKit.Base.bind(this._cbDeferred, this);
    for (var i = 0; i < list.length; i++) {
        var d = list[i];
        resultList.push(undefined);
        d.addCallback(cb, i, true);
        d.addErrback(cb, i, false);
    }

    if (list.length === 0 && !fireOnOneCallback) {
        this.callback(this.resultList);
    }

};

MochiKit.Async.DeferredList.prototype = new MochiKit.Async.Deferred();

MochiKit.Async.DeferredList.prototype._cbDeferred = function (index, succeeded, result) {
    this.resultList[index] = [succeeded, result];
    this.finishedCount += 1;
    if (this.fired == -1) {
        if (succeeded && this.fireOnOneCallback) {
            this.callback([index, result]);
        } else if (!succeeded && this.fireOnOneErrback) {
            this.errback(result);
        } else if (this.finishedCount == this.list.length) {
            this.callback(this.resultList);
        }
    }
    if (!succeeded && this.consumeErrors) {
        result = null;
    }
    return result;
};

/** @id MochiKit.Async.gatherResults */
MochiKit.Async.gatherResults = function (deferredList) {
    var d = new MochiKit.Async.DeferredList(deferredList, false, true, false);
    d.addCallback(function (results) {
        var ret = [];
        for (var i = 0; i < results.length; i++) {
            ret.push(results[i][1]);
        }
        return ret;
    });
    return d;
};

/** @id MochiKit.Async.maybeDeferred */
MochiKit.Async.maybeDeferred = function (func) {
    var self = MochiKit.Async;
    var result;
    try {
        var r = func.apply(null, MochiKit.Base.extend([], arguments, 1));
        if (r instanceof self.Deferred) {
            result = r;
        } else if (r instanceof Error) {
            result = self.fail(r);
        } else {
            result = self.succeed(r);
        }
    } catch (e) {
        result = self.fail(e);
    }
    return result;
};


MochiKit.Async.__new__ = function () {
    var m = MochiKit.Base;
    var ne = m.partial(m._newNamedError, this);

    ne("AlreadyCalledError",
        /** @id MochiKit.Async.AlreadyCalledError */
        function (deferred) {
            /***

            Raised by the Deferred if callback or errback happens
            after it was already fired.

            ***/
            this.deferred = deferred;
        }
    );

    ne("CancelledError",
        /** @id MochiKit.Async.CancelledError */
        function (deferred) {
            /***

            Raised by the Deferred cancellation mechanism.

            ***/
            this.deferred = deferred;
        }
    );

    ne("BrowserComplianceError",
        /** @id MochiKit.Async.BrowserComplianceError */
        function (msg) {
            /***

            Raised when the JavaScript runtime is not capable of performing
            the given function.  Technically, this should really never be
            raised because a non-conforming JavaScript runtime probably
            isn't going to support exceptions in the first place.

            ***/
            this.message = msg;
        }
    );

    ne("GenericError",
        /** @id MochiKit.Async.GenericError */
        function (msg) {
            this.message = msg;
        }
    );

    ne("XMLHttpRequestError",
        /** @id MochiKit.Async.XMLHttpRequestError */
        function (req, msg) {
            /***

            Raised when an XMLHttpRequest does not complete for any reason.

            ***/
            this.req = req;
            this.message = msg;
            try {
                // Strange but true that this can raise in some cases.
                this.number = req.status;
            } catch (e) {
                // pass
            }
        }
    );

    m.nameFunctions(this);
};

MochiKit.Async.__new__();

MochiKit.Base._exportSymbols(this, MochiKit.Async);
/***

MochiKit.DOM 1.5

See <http://mochikit.com/> for documentation, downloads, license, etc.

(c) 2005 Bob Ippolito.  All rights Reserved.

***/

MochiKit.Base._module('DOM', '1.5', ['Base']);

MochiKit.Base.update(MochiKit.DOM, {

    /** @id MochiKit.DOM.currentWindow */
    currentWindow: function () {
        return MochiKit.DOM._window;
    },

    /** @id MochiKit.DOM.currentDocument */
    currentDocument: function () {
        return MochiKit.DOM._document;
    },

    /** @id MochiKit.DOM.withWindow */
    withWindow: function (win, func) {
        var self = MochiKit.DOM;
        var oldDoc = self._document;
        var oldWin = self._window;
        var rval;
        try {
            self._window = win;
            self._document = win.document;
            rval = func();
        } catch (e) {
            self._window = oldWin;
            self._document = oldDoc;
            throw e;
        }
        self._window = oldWin;
        self._document = oldDoc;
        return rval;
    },

    /** @id MochiKit.DOM.formContents  */
    formContents: function (elem/* = document.body */) {
        var names = [];
        var values = [];
        var m = MochiKit.Base;
        var self = MochiKit.DOM;
        if (typeof(elem) == "undefined" || elem === null) {
            elem = self._document.body;
        } else {
            elem = self.getElement(elem);
        }
        m.nodeWalk(elem, function (elem) {
            var name = elem.name;
            if (m.isNotEmpty(name)) {
                var tagName = elem.tagName.toUpperCase();
                if (tagName === "INPUT"
                    && (elem.type == "radio" || elem.type == "checkbox")
                    && !elem.checked
                ) {
                    return null;
                }
                if (tagName === "SELECT") {
                    if (elem.type == "select-one") {
                        if (elem.selectedIndex >= 0) {
                            var opt = elem.options[elem.selectedIndex];
                            var v = opt.value;
                            if (!v) {
                                var h = opt.outerHTML;
                                // internet explorer sure does suck.
                                if (h && !h.match(/^[^>]+\svalue\s*=/i)) {
                                    v = opt.text;
                                }
                            }
                            names.push(name);
                            values.push(v);
                            return null;
                        }
                        // no form elements?
                        names.push(name);
                        values.push("");
                        return null;
                    } else {
                        var opts = elem.options;
                        if (!opts.length) {
                            names.push(name);
                            values.push("");
                            return null;
                        }
                        for (var i = 0; i < opts.length; i++) {
                            var opt = opts[i];
                            if (!opt.selected) {
                                continue;
                            }
                            var v = opt.value;
                            if (!v) {
                                var h = opt.outerHTML;
                                // internet explorer sure does suck.
                                if (h && !h.match(/^[^>]+\svalue\s*=/i)) {
                                    v = opt.text;
                                }
                            }
                            names.push(name);
                            values.push(v);
                        }
                        return null;
                    }
                }
                if (tagName === "FORM" || tagName === "P" || tagName === "SPAN"
                    || tagName === "DIV"
                ) {
                    return elem.childNodes;
                }
                names.push(name);
                values.push(elem.value || '');
                return null;
            }
            return elem.childNodes;
        });
        return [names, values];
    },

    /** @id MochiKit.DOM.withDocument */
    withDocument: function (doc, func) {
        var self = MochiKit.DOM;
        var oldDoc = self._document;
        var rval;
        try {
            self._document = doc;
            rval = func();
        } catch (e) {
            self._document = oldDoc;
            throw e;
        }
        self._document = oldDoc;
        return rval;
    },

    /** @id MochiKit.DOM.registerDOMConverter */
    registerDOMConverter: function (name, check, wrap, /* optional */override) {
        MochiKit.DOM.domConverters.register(name, check, wrap, override);
    },

    /** @id MochiKit.DOM.coerceToDOM */
    coerceToDOM: function (node, ctx) {
        var m = MochiKit.Base;
        var im = MochiKit.Iter;
        var self = MochiKit.DOM;
        if (im) {
            var iter = im.iter;
            var repeat = im.repeat;
        }
        var map = m.map;
        var domConverters = self.domConverters;
        var coerceToDOM = arguments.callee;
        var NotFound = m.NotFound;
        while (true) {
            if (typeof(node) == 'undefined' || node === null) {
                return null;
            }
            // this is a safari childNodes object, avoiding crashes w/ attr
            // lookup
            if (typeof(node) == "function" &&
                    typeof(node.length) == "number" &&
                    !(node instanceof Function)) {
                node = im ? im.list(node) : m.extend(null, node);
            }
            if (typeof(node.nodeType) != 'undefined' && node.nodeType > 0) {
                return node;
            }
            if (typeof(node) == 'number' || typeof(node) == 'boolean') {
                node = node.toString();
                // FALL THROUGH
            }
            if (typeof(node) == 'string') {
                return self._document.createTextNode(node);
            }
            if (typeof(node.__dom__) == 'function') {
                node = node.__dom__(ctx);
                continue;
            }
            if (typeof(node.dom) == 'function') {
                node = node.dom(ctx);
                continue;
            }
            if (typeof(node) == 'function') {
                node = node.apply(ctx, [ctx]);
                continue;
            }

            if (im) {
                // iterable
                var iterNodes = null;
                try {
                    iterNodes = iter(node);
                } catch (e) {
                    // pass
                }
                if (iterNodes) {
                    return map(coerceToDOM, iterNodes, repeat(ctx));
                }
            } else if (m.isArrayLike(node)) {
                var func = function (n) { return coerceToDOM(n, ctx); };
                return map(func, node);
            }

            // adapter
            try {
                node = domConverters.match(node, ctx);
                continue;
            } catch (e) {
                if (e != NotFound) {
                    throw e;
                }
            }

            // fallback
            return self._document.createTextNode(node.toString());
        }
        // mozilla warnings aren't too bright
        return undefined;
    },

    /** @id MochiKit.DOM.isChildNode */
    isChildNode: function (node, maybeparent) {
        var self = MochiKit.DOM;
        if (typeof(node) == "string") {
            node = self.getElement(node);
        }
        if (typeof(maybeparent) == "string") {
            maybeparent = self.getElement(maybeparent);
        }
        if (typeof(node) == 'undefined' || node === null) {
            return false;
        }
        while (node != null && node !== self._document) {
            if (node === maybeparent) {
                return true;
            }
            node = node.parentNode;
        }
        return false;
    },

    /** @id MochiKit.DOM.setNodeAttribute */
    setNodeAttribute: function (node, attr, value) {
        var o = {};
        o[attr] = value;
        try {
            return MochiKit.DOM.updateNodeAttributes(node, o);
        } catch (e) {
            // pass
        }
        return null;
    },

    /** @id MochiKit.DOM.getNodeAttribute */
    getNodeAttribute: function (node, attr) {
        var self = MochiKit.DOM;
        var rename = self.attributeArray.renames[attr];
        var ignoreValue = self.attributeArray.ignoreAttr[attr];
        node = self.getElement(node);
        try {
            if (rename) {
                return node[rename];
            }
            var value = node.getAttribute(attr);
            if (value != ignoreValue) {
                return value;
            }
        } catch (e) {
            // pass
        }
        return null;
    },

    /** @id MochiKit.DOM.removeNodeAttribute */
    removeNodeAttribute: function (node, attr) {
        var self = MochiKit.DOM;
        var rename = self.attributeArray.renames[attr];
        node = self.getElement(node);
        try {
            if (rename) {
                return node[rename];
            }
            return node.removeAttribute(attr);
        } catch (e) {
            // pass
        }
        return null;
    },

    /** @id MochiKit.DOM.updateNodeAttributes */
    updateNodeAttributes: function (node, attrs) {
        var elem = node;
        var self = MochiKit.DOM;
        if (typeof(node) == 'string') {
            elem = self.getElement(node);
        }
        if (attrs) {
            var updatetree = MochiKit.Base.updatetree;
            if (self.attributeArray.compliant) {
                // not IE, good.
                for (var k in attrs) {
                    var v = attrs[k];
                    if (typeof(v) == 'object' && typeof(elem[k]) == 'object') {
                        if (k == "style" && MochiKit.Style) {
                            MochiKit.Style.setStyle(elem, v);
                        } else {
                            updatetree(elem[k], v);
                        }
                    } else if (k.substring(0, 2) == "on") {
                        if (typeof(v) == "string") {
                            v = new Function(v);
                        }
                        elem[k] = v;
                    } else {
                        elem.setAttribute(k, v);
                    }
                    if (typeof(elem[k]) == "string" && elem[k] != v) {
                        // Also set property for weird attributes (see #302)
                        elem[k] = v;
                    }
                }
            } else {
                // IE is insane in the membrane
                var renames = self.attributeArray.renames;
                for (var k in attrs) {
                    v = attrs[k];
                    var renamed = renames[k];
                    if (k == "style" && typeof(v) == "string") {
                        elem.style.cssText = v;
                    } else if (typeof(renamed) == "string") {
                        elem[renamed] = v;
                    } else if (typeof(elem[k]) == 'object'
                            && typeof(v) == 'object') {
                        if (k == "style" && MochiKit.Style) {
                            MochiKit.Style.setStyle(elem, v);
                        } else {
                            updatetree(elem[k], v);
                        }
                    } else if (k.substring(0, 2) == "on") {
                        if (typeof(v) == "string") {
                            v = new Function(v);
                        }
                        elem[k] = v;
                    } else {
                        elem.setAttribute(k, v);
                    }
                    if (typeof(elem[k]) == "string" && elem[k] != v) {
                        // Also set property for weird attributes (see #302)
                        elem[k] = v;
                    }
                }
            }
        }
        return elem;
    },

    /** @id MochiKit.DOM.appendChildNodes */
    appendChildNodes: function (node/*, nodes...*/) {
        var elem = node;
        var self = MochiKit.DOM;
        if (typeof(node) == 'string') {
            elem = self.getElement(node);
        }
        var nodeStack = [
            self.coerceToDOM(
                MochiKit.Base.extend(null, arguments, 1),
                elem
            )
        ];
        var concat = MochiKit.Base.concat;
        while (nodeStack.length) {
            var n = nodeStack.shift();
            if (typeof(n) == 'undefined' || n === null) {
                // pass
            } else if (typeof(n.nodeType) == 'number') {
                elem.appendChild(n);
            } else {
                nodeStack = concat(n, nodeStack);
            }
        }
        return elem;
    },


    /** @id MochiKit.DOM.insertSiblingNodesBefore */
    insertSiblingNodesBefore: function (node/*, nodes...*/) {
        var elem = node;
        var self = MochiKit.DOM;
        if (typeof(node) == 'string') {
            elem = self.getElement(node);
        }
        var nodeStack = [
            self.coerceToDOM(
                MochiKit.Base.extend(null, arguments, 1),
                elem
            )
        ];
        var parentnode = elem.parentNode;
        var concat = MochiKit.Base.concat;
        while (nodeStack.length) {
            var n = nodeStack.shift();
            if (typeof(n) == 'undefined' || n === null) {
                // pass
            } else if (typeof(n.nodeType) == 'number') {
                parentnode.insertBefore(n, elem);
            } else {
                nodeStack = concat(n, nodeStack);
            }
        }
        return parentnode;
    },

    /** @id MochiKit.DOM.insertSiblingNodesAfter */
    insertSiblingNodesAfter: function (node/*, nodes...*/) {
        var elem = node;
        var self = MochiKit.DOM;

        if (typeof(node) == 'string') {
            elem = self.getElement(node);
        }
        var nodeStack = [
            self.coerceToDOM(
                MochiKit.Base.extend(null, arguments, 1),
                elem
            )
        ];

        if (elem.nextSibling) {
            return self.insertSiblingNodesBefore(elem.nextSibling, nodeStack);
        }
        else {
            return self.appendChildNodes(elem.parentNode, nodeStack);
        }
    },

    /** @id MochiKit.DOM.replaceChildNodes */
    replaceChildNodes: function (node/*, nodes...*/) {
        var elem = node;
        var self = MochiKit.DOM;
        if (typeof(node) == 'string') {
            elem = self.getElement(node);
            arguments[0] = elem;
        }
        var child;
        while ((child = elem.firstChild)) {
            elem.removeChild(child);
        }
        if (arguments.length < 2) {
            return elem;
        } else {
            return self.appendChildNodes.apply(this, arguments);
        }
    },

    /** @id MochiKit.DOM.createDOM */
    createDOM: function (name, attrs/*, nodes... */) {
        var elem;
        var self = MochiKit.DOM;
        var m = MochiKit.Base;
        if (typeof(attrs) == "string" || typeof(attrs) == "number") {
            var args = m.extend([name, null], arguments, 1);
            return arguments.callee.apply(this, args);
        }
        if (typeof(name) == 'string') {
            // Internet Explorer is dumb
            var xhtml = self._xhtml;
            if (attrs && !self.attributeArray.compliant) {
                // http://msdn.microsoft.com/workshop/author/dhtml/reference/properties/name_2.asp
                var contents = "";
                if ('name' in attrs) {
                    contents += ' name="' + self.escapeHTML(attrs.name) + '"';
                }
                if (name == 'input' && 'type' in attrs) {
                    contents += ' type="' + self.escapeHTML(attrs.type) + '"';
                }
                if (contents) {
                    name = "<" + name + contents + ">";
                    xhtml = false;
                }
            }
            var d = self._document;
            if (xhtml && d === document) {
                elem = d.createElementNS("http://www.w3.org/1999/xhtml", name);
            } else {
                elem = d.createElement(name);
            }
        } else {
            elem = name;
        }
        if (attrs) {
            self.updateNodeAttributes(elem, attrs);
        }
        if (arguments.length <= 2) {
            return elem;
        } else {
            var args = m.extend([elem], arguments, 2);
            return self.appendChildNodes.apply(this, args);
        }
    },

    /** @id MochiKit.DOM.createDOMFunc */
    createDOMFunc: function (/* tag, attrs, *nodes */) {
        var m = MochiKit.Base;
        return m.partial.apply(
            this,
            m.extend([MochiKit.DOM.createDOM], arguments)
        );
    },

    /** @id MochiKit.DOM.removeElement */
    removeElement: function (elem) {
        var self = MochiKit.DOM;
        if (typeof(elem) == "string") {
            elem = self.getElement(elem);
        }
        var e = self.coerceToDOM(elem);
        e.parentNode.removeChild(e);
        return e;
    },

    /** @id MochiKit.DOM.swapDOM */
    swapDOM: function (dest, src) {
        var self = MochiKit.DOM;
        dest = self.getElement(dest);
        var parent = dest.parentNode;
        if (src) {
            if (typeof(src) == "string") {
                src = self.getElement(src);
            }
            src = self.coerceToDOM(src, parent);
            parent.replaceChild(src, dest);
        } else {
            parent.removeChild(dest);
        }
        return src;
    },

    /** @id MochiKit.DOM.getElement */
    getElement: function (id) {
        var self = MochiKit.DOM;
        if (arguments.length == 1) {
            return ((typeof(id) == "string") ?
                self._document.getElementById(id) : id);
        } else {
            return MochiKit.Base.map(self.getElement, arguments);
        }
    },

    /** @id MochiKit.DOM.getElementsByTagAndClassName */
    getElementsByTagAndClassName: function (tagName, className,
            /* optional */parent) {
        var self = MochiKit.DOM;
        if (typeof(tagName) == 'undefined' || tagName === null) {
            tagName = '*';
        }
        if (typeof(parent) == 'undefined' || parent === null) {
            parent = self._document;
        }
        parent = self.getElement(parent);
        if (parent == null) {
            return [];
        }
        var children = (parent.getElementsByTagName(tagName)
            || self._document.all);
        if (typeof(className) == 'undefined' || className === null) {
            return MochiKit.Base.extend(null, children);
        }

        var elements = [];
        for (var i = 0; i < children.length; i++) {
            var child = children[i];
            var cls = child.className;
            if (typeof(cls) != "string") {
                cls = child.getAttribute("class");
            }
            if (typeof(cls) == "string") {
                var classNames = cls.split(' ');
                for (var j = 0; j < classNames.length; j++) {
                    if (classNames[j] == className) {
                        elements.push(child);
                        break;
                    }
                }
            }
        }

        return elements;
    },

    _newCallStack: function (path, once) {
        var rval = function () {
            var callStack = arguments.callee.callStack;
            for (var i = 0; i < callStack.length; i++) {
                if (callStack[i].apply(this, arguments) === false) {
                    break;
                }
            }
            if (once) {
                try {
                    this[path] = null;
                } catch (e) {
                    // pass
                }
            }
        };
        rval.callStack = [];
        return rval;
    },

    /** @id MochiKit.DOM.addToCallStack */
    addToCallStack: function (target, path, func, once) {
        var self = MochiKit.DOM;
        var existing = target[path];
        var regfunc = existing;
        if (!(typeof(existing) == 'function'
                && typeof(existing.callStack) == "object"
                && existing.callStack !== null)) {
            regfunc = self._newCallStack(path, once);
            if (typeof(existing) == 'function') {
                regfunc.callStack.push(existing);
            }
            target[path] = regfunc;
        }
        regfunc.callStack.push(func);
    },

    /** @id MochiKit.DOM.addLoadEvent */
    addLoadEvent: function (func) {
        var self = MochiKit.DOM;
        self.addToCallStack(self._window, "onload", func, true);

    },

    /** @id MochiKit.DOM.focusOnLoad */
    focusOnLoad: function (element) {
        var self = MochiKit.DOM;
        self.addLoadEvent(function () {
            element = self.getElement(element);
            if (element) {
                element.focus();
            }
        });
    },

    /** @id MochiKit.DOM.setElementClass */
    setElementClass: function (element, className) {
        var self = MochiKit.DOM;
        var obj = self.getElement(element);
        if (self.attributeArray.compliant) {
            obj.setAttribute("class", className);
        } else {
            obj.setAttribute("className", className);
        }
    },

    /** @id MochiKit.DOM.toggleElementClass */
    toggleElementClass: function (className/*, element... */) {
        var self = MochiKit.DOM;
        for (var i = 1; i < arguments.length; i++) {
            var obj = self.getElement(arguments[i]);
            if (!self.addElementClass(obj, className)) {
                self.removeElementClass(obj, className);
            }
        }
    },

    /** @id MochiKit.DOM.addElementClass */
    addElementClass: function (element, className) {
        var self = MochiKit.DOM;
        var obj = self.getElement(element);
        var cls = obj.className;
        if (typeof(cls) != "string") {
            cls = obj.getAttribute("class");
        }
        // trivial case, no className yet
        if (typeof(cls) != "string" || cls.length === 0) {
            self.setElementClass(obj, className);
            return true;
        }
        // the other trivial case, already set as the only class
        if (cls == className) {
            return false;
        }
        var classes = cls.split(" ");
        for (var i = 0; i < classes.length; i++) {
            // already present
            if (classes[i] == className) {
                return false;
            }
        }
        // append class
        self.setElementClass(obj, cls + " " + className);
        return true;
    },

    /** @id MochiKit.DOM.removeElementClass */
    removeElementClass: function (element, className) {
        var self = MochiKit.DOM;
        var obj = self.getElement(element);
        var cls = obj.className;
        if (typeof(cls) != "string") {
            cls = obj.getAttribute("class");
        }
        // trivial case, no className yet
        if (typeof(cls) != "string" || cls.length === 0) {
            return false;
        }
        // other trivial case, set only to className
        if (cls == className) {
            self.setElementClass(obj, "");
            return true;
        }
        var classes = cls.split(" ");
        for (var i = 0; i < classes.length; i++) {
            // already present
            if (classes[i] == className) {
                // only check sane case where the class is used once
                classes.splice(i, 1);
                self.setElementClass(obj, classes.join(" "));
                return true;
            }
        }
        // not found
        return false;
    },

    /** @id MochiKit.DOM.swapElementClass */
    swapElementClass: function (element, fromClass, toClass) {
        var obj = MochiKit.DOM.getElement(element);
        var res = MochiKit.DOM.removeElementClass(obj, fromClass);
        if (res) {
            MochiKit.DOM.addElementClass(obj, toClass);
        }
        return res;
    },

    /** @id MochiKit.DOM.hasElementClass */
    hasElementClass: function (element, className/*...*/) {
        var obj = MochiKit.DOM.getElement(element);
        if (obj == null) {
            return false;
        }
        var cls = obj.className;
        if (typeof(cls) != "string" && typeof(obj.getAttribute) == "function") {
            cls = obj.getAttribute("class");
        }
        if (typeof(cls) != "string") {
            return false;
        }
        var classes = cls.split(" ");
        for (var i = 1; i < arguments.length; i++) {
            var good = false;
            for (var j = 0; j < classes.length; j++) {
                if (classes[j] == arguments[i]) {
                    good = true;
                    break;
                }
            }
            if (!good) {
                return false;
            }
        }
        return true;
    },

    /** @id MochiKit.DOM.escapeHTML */
    escapeHTML: function (s) {
        return s.replace(/&/g, "&amp;"
            ).replace(/"/g, "&quot;"
            ).replace(/</g, "&lt;"
            ).replace(/>/g, "&gt;");
    },

    /** @id MochiKit.DOM.toHTML */
    toHTML: function (dom) {
        return MochiKit.DOM.emitHTML(dom).join("");
    },

    /** @id MochiKit.DOM.emitHTML */
    emitHTML: function (dom, /* optional */lst) {
        if (typeof(lst) == 'undefined' || lst === null) {
            lst = [];
        }
        // queue is the call stack, we're doing this non-recursively
        var queue = [dom];
        var self = MochiKit.DOM;
        var escapeHTML = self.escapeHTML;
        var attributeArray = self.attributeArray;
        while (queue.length) {
            dom = queue.pop();
            if (typeof(dom) == 'string') {
                lst.push(dom);
            } else if (dom.nodeType == 1) {
                // we're not using higher order stuff here
                // because safari has heisenbugs.. argh.
                //
                // I think it might have something to do with
                // garbage collection and function calls.
                lst.push('<' + dom.tagName.toLowerCase());
                var attributes = [];
                var domAttr = attributeArray(dom);
                for (var i = 0; i < domAttr.length; i++) {
                    var a = domAttr[i];
                    attributes.push([
                        " ",
                        a.name,
                        '="',
                        escapeHTML(a.value),
                        '"'
                    ]);
                }
                attributes.sort();
                for (i = 0; i < attributes.length; i++) {
                    var attrs = attributes[i];
                    for (var j = 0; j < attrs.length; j++) {
                        lst.push(attrs[j]);
                    }
                }
                if (dom.hasChildNodes()) {
                    lst.push(">");
                    // queue is the FILO call stack, so we put the close tag
                    // on first
                    queue.push("</" + dom.tagName.toLowerCase() + ">");
                    var cnodes = dom.childNodes;
                    for (i = cnodes.length - 1; i >= 0; i--) {
                        queue.push(cnodes[i]);
                    }
                } else {
                    lst.push('/>');
                }
            } else if (dom.nodeType == 3) {
                lst.push(escapeHTML(dom.nodeValue));
            }
        }
        return lst;
    },

    /** @id MochiKit.DOM.scrapeText */
    scrapeText: function (node, /* optional */asArray) {
        var rval = [];
        (function (node) {
            var cn = node.childNodes;
            if (cn) {
                for (var i = 0; i < cn.length; i++) {
                    arguments.callee.call(this, cn[i]);
                }
            }
            var nodeValue = node.nodeValue;
            if (typeof(nodeValue) == 'string') {
                rval.push(nodeValue);
            }
        })(MochiKit.DOM.getElement(node));
        if (asArray) {
            return rval;
        } else {
            return rval.join("");
        }
    },

    /** @id MochiKit.DOM.removeEmptyTextNodes */
    removeEmptyTextNodes: function (element) {
        element = MochiKit.DOM.getElement(element);
        for (var i = 0; i < element.childNodes.length; i++) {
            var node = element.childNodes[i];
            if (node.nodeType == 3 && !/\S/.test(node.nodeValue)) {
                node.parentNode.removeChild(node);
            }
        }
    },

    /** @id MochiKit.DOM.getFirstElementByTagAndClassName */
    getFirstElementByTagAndClassName: function (tagName, className,
            /* optional */parent) {
        var self = MochiKit.DOM;
        if (typeof(tagName) == 'undefined' || tagName === null) {
            tagName = '*';
        }
        if (typeof(parent) == 'undefined' || parent === null) {
            parent = self._document;
        }
        parent = self.getElement(parent);
        if (parent == null) {
            return null;
        }
        var children = (parent.getElementsByTagName(tagName)
            || self._document.all);
        if (children.length <= 0) {
            return null;
        } else if (typeof(className) == 'undefined' || className === null) {
            return children[0];
        }

        for (var i = 0; i < children.length; i++) {
            var child = children[i];
            var cls = child.className;
            if (typeof(cls) != "string") {
                cls = child.getAttribute("class");
            }
            if (typeof(cls) == "string") {
                var classNames = cls.split(' ');
                for (var j = 0; j < classNames.length; j++) {
                    if (classNames[j] == className) {
                        return child;
                    }
                }
            }
        }
        return null;
    },

    /** @id MochiKit.DOM.getFirstParentByTagAndClassName */
    getFirstParentByTagAndClassName: function (elem, tagName, className) {
        var self = MochiKit.DOM;
        elem = self.getElement(elem);
        if (typeof(tagName) == 'undefined' || tagName === null) {
            tagName = '*';
        } else {
            tagName = tagName.toUpperCase();
        }
        if (typeof(className) == 'undefined' || className === null) {
            className = null;
        }
        if (elem) {
            elem = elem.parentNode;
        }
        while (elem && elem.tagName) {
            var curTagName = elem.tagName.toUpperCase();
            if ((tagName === '*' || tagName == curTagName) &&
                (className === null || self.hasElementClass(elem, className))) {
                return elem;
            }
            elem = elem.parentNode;
        }
        return null;
    },

    __new__: function (win) {

        var m = MochiKit.Base;
        if (typeof(document) != "undefined") {
            this._document = document;
            var kXULNSURI = "http://www.mozilla.org/keymaster/gatekeeper/there.is.only.xul";
            this._xhtml = (document.documentElement &&
                document.createElementNS &&
                document.documentElement.namespaceURI === kXULNSURI);
        } else if (MochiKit.MockDOM) {
            this._document = MochiKit.MockDOM.document;
        }
        this._window = win;

        this.domConverters = new m.AdapterRegistry();

        var __tmpElement = this._document.createElement("span");
        var attributeArray;
        if (__tmpElement && __tmpElement.attributes &&
                __tmpElement.attributes.length > 0) {
            // for braindead browsers (IE) that insert extra junk
            var filter = m.filter;
            attributeArray = function (node) {
                /***

                    Return an array of attributes for a given node,
                    filtering out attributes that don't belong for
                    that are inserted by "Certain Browsers".

                ***/
                return filter(attributeArray.ignoreAttrFilter, node.attributes);
            };
            attributeArray.ignoreAttr = {};
            var attrs = __tmpElement.attributes;
            var ignoreAttr = attributeArray.ignoreAttr;
            for (var i = 0; i < attrs.length; i++) {
                var a = attrs[i];
                ignoreAttr[a.name] = a.value;
            }
            attributeArray.ignoreAttrFilter = function (a) {
                return (attributeArray.ignoreAttr[a.name] != a.value);
            };
            attributeArray.compliant = false;
            attributeArray.renames = {
                "class": "className",
                "checked": "defaultChecked",
                "usemap": "useMap",
                "for": "htmlFor",
                "readonly": "readOnly",
                "colspan": "colSpan",
                "bgcolor": "bgColor",
                "cellspacing": "cellSpacing",
                "cellpadding": "cellPadding"
            };
        } else {
            attributeArray = function (node) {
                return node.attributes;
            };
            attributeArray.compliant = true;
            attributeArray.ignoreAttr = {};
            attributeArray.renames = {};
        }
        attributeArray.__export__ = false;
        this.attributeArray = attributeArray;

        // Backwards compatibility aliases
        /** @id MochiKit.DOM.computedStyle  */
        m._deprecated(this, 'computedStyle', 'MochiKit.Style.getStyle', '1.4', true);
        /** @id MochiKit.DOM.elementDimensions  */
        m._deprecated(this, 'elementDimensions', 'MochiKit.Style.getElementDimensions', '1.4');
        /** @id MochiKit.DOM.elementPosition  */
        m._deprecated(this, 'elementPosition', 'MochiKit.Style.getElementPosition', '1.4');
        /** @id MochiKit.DOM.getViewportDimensions */
        m._deprecated(this, 'getViewportDimensions', 'MochiKit.Style.getViewportDimensions', '1.4');
        /** @id MochiKit.DOM.hideElement */
        m._deprecated(this, 'hideElement', 'MochiKit.Style.hideElement', '1.4');
        /** @id MochiKit.DOM.makeClipping */
        m._deprecated(this, 'makeClipping', 'MochiKit.Style.makeClipping', '1.4.1');
        /** @id MochiKit.DOM.makePositioned */
        m._deprecated(this, 'makePositioned', 'MochiKit.Style.makePositioned', '1.4.1');
        /** @id MochiKit.DOM.setElementDimensions */
        m._deprecated(this, 'setElementDimensions', 'MochiKit.Style.setElementDimensions', '1.4');
        /** @id MochiKit.DOM.setElementPosition */
        m._deprecated(this, 'setElementPosition', 'MochiKit.Style.setElementPosition', '1.4');
        /** @id MochiKit.DOM.setDisplayForElement */
        m._deprecated(this, 'setDisplayForElement', 'MochiKit.Style.setDisplayForElement', '1.4');
        /** @id MochiKit.DOM.setOpacity */
        m._deprecated(this, 'setOpacity', 'MochiKit.Style.setOpacity', '1.4');
        /** @id MochiKit.DOM.showElement */
        m._deprecated(this, 'showElement', 'MochiKit.Style.showElement', '1.4');
        /** @id MochiKit.DOM.undoClipping */
        m._deprecated(this, 'undoClipping', 'MochiKit.Style.undoClipping', '1.4.1');
        /** @id MochiKit.DOM.undoPositioned */
        m._deprecated(this, 'undoPositioned', 'MochiKit.Style.undoPositioned', '1.4.1');
        /** @id MochiKit.DOM.Coordinates */
        m._deprecated(this, 'Coordinates', 'MochiKit.Style.Coordinates', '1.4');
        /** @id MochiKit.DOM.Dimensions */
        m._deprecated(this, 'Dimensions', 'MochiKit.Style.Dimensions', '1.4');

        // shorthand for createDOM syntax
        var createDOMFunc = this.createDOMFunc;
        /** @id MochiKit.DOM.UL */
        this.UL = createDOMFunc("ul");
        /** @id MochiKit.DOM.OL */
        this.OL = createDOMFunc("ol");
        /** @id MochiKit.DOM.LI */
        this.LI = createDOMFunc("li");
        /** @id MochiKit.DOM.DL */
        this.DL = createDOMFunc("dl");
        /** @id MochiKit.DOM.DT */
        this.DT = createDOMFunc("dt");
        /** @id MochiKit.DOM.DD */
        this.DD = createDOMFunc("dd");
        /** @id MochiKit.DOM.TD */
        this.TD = createDOMFunc("td");
        /** @id MochiKit.DOM.TR */
        this.TR = createDOMFunc("tr");
        /** @id MochiKit.DOM.TBODY */
        this.TBODY = createDOMFunc("tbody");
        /** @id MochiKit.DOM.THEAD */
        this.THEAD = createDOMFunc("thead");
        /** @id MochiKit.DOM.TFOOT */
        this.TFOOT = createDOMFunc("tfoot");
        /** @id MochiKit.DOM.TABLE */
        this.TABLE = createDOMFunc("table");
        /** @id MochiKit.DOM.TH */
        this.TH = createDOMFunc("th");
        /** @id MochiKit.DOM.INPUT */
        this.INPUT = createDOMFunc("input");
        /** @id MochiKit.DOM.SPAN */
        this.SPAN = createDOMFunc("span");
        /** @id MochiKit.DOM.A */
        this.A = createDOMFunc("a");
        /** @id MochiKit.DOM.DIV */
        this.DIV = createDOMFunc("div");
        /** @id MochiKit.DOM.IMG */
        this.IMG = createDOMFunc("img");
        /** @id MochiKit.DOM.BUTTON */
        this.BUTTON = createDOMFunc("button");
        /** @id MochiKit.DOM.TT */
        this.TT = createDOMFunc("tt");
        /** @id MochiKit.DOM.PRE */
        this.PRE = createDOMFunc("pre");
        /** @id MochiKit.DOM.H1 */
        this.H1 = createDOMFunc("h1");
        /** @id MochiKit.DOM.H2 */
        this.H2 = createDOMFunc("h2");
        /** @id MochiKit.DOM.H3 */
        this.H3 = createDOMFunc("h3");
        /** @id MochiKit.DOM.H4 */
        this.H4 = createDOMFunc("h4");
        /** @id MochiKit.DOM.H5 */
        this.H5 = createDOMFunc("h5");
        /** @id MochiKit.DOM.H6 */
        this.H6 = createDOMFunc("h6");
        /** @id MochiKit.DOM.BR */
        this.BR = createDOMFunc("br");
        /** @id MochiKit.DOM.HR */
        this.HR = createDOMFunc("hr");
        /** @id MochiKit.DOM.LABEL */
        this.LABEL = createDOMFunc("label");
        /** @id MochiKit.DOM.TEXTAREA */
        this.TEXTAREA = createDOMFunc("textarea");
        /** @id MochiKit.DOM.FORM */
        this.FORM = createDOMFunc("form");
        /** @id MochiKit.DOM.P */
        this.P = createDOMFunc("p");
        /** @id MochiKit.DOM.SELECT */
        this.SELECT = createDOMFunc("select");
        /** @id MochiKit.DOM.OPTION */
        this.OPTION = createDOMFunc("option");
        /** @id MochiKit.DOM.OPTGROUP */
        this.OPTGROUP = createDOMFunc("optgroup");
        /** @id MochiKit.DOM.LEGEND */
        this.LEGEND = createDOMFunc("legend");
        /** @id MochiKit.DOM.FIELDSET */
        this.FIELDSET = createDOMFunc("fieldset");
        /** @id MochiKit.DOM.STRONG */
        this.STRONG = createDOMFunc("strong");
        /** @id MochiKit.DOM.CANVAS */
        this.CANVAS = createDOMFunc("canvas");

        /** @id MochiKit.DOM.$ */
        this.$ = this.getElement;

        m.nameFunctions(this);

    }
});


MochiKit.DOM.__new__(((typeof(window) == "undefined") ? this : window));

//
// XXX: Internet Explorer blows
//
if (MochiKit.__export__) {
    withWindow = MochiKit.DOM.withWindow;
    withDocument = MochiKit.DOM.withDocument;
}

MochiKit.Base._exportSymbols(this, MochiKit.DOM);
/***

MochiKit.Selector 1.5

See <http://mochikit.com/> for documentation, downloads, license, etc.

(c) 2005 Bob Ippolito and others.  All rights Reserved.

***/

MochiKit.Base._module('Selector', '1.5', ['Base', 'DOM', 'Iter']);

MochiKit.Selector.Selector = function (expression) {
    this.params = {classNames: [], pseudoClassNames: []};
    this.expression = expression.toString().replace(/(^\s+|\s+$)/g, '');
    this.parseExpression();
    this.compileMatcher();
};

MochiKit.Selector.Selector.prototype = {
    /***

    Selector class: convenient object to make CSS selections.

    ***/
    __class__: MochiKit.Selector.Selector,

    /** @id MochiKit.Selector.Selector.prototype.parseExpression */
    parseExpression: function () {
        function abort(message) {
            throw 'Parse error in selector: ' + message;
        }

        if (this.expression == '')  {
            abort('empty expression');
        }

        var repr = MochiKit.Base.repr;
        var params = this.params;
        var expr = this.expression;
        var match, modifier, clause, rest;
        while (match = expr.match(/^(.*)\[([a-z0-9_:-]+?)(?:([~\|!^$*]?=)(?:"([^"]*)"|([^\]\s]*)))?\]$/i)) {
            params.attributes = params.attributes || [];
            params.attributes.push({name: match[2], operator: match[3], value: match[4] || match[5] || ''});
            expr = match[1];
        }

        if (expr == '*') {
            return this.params.wildcard = true;
        }

        while (match = expr.match(/^([^a-z0-9_-])?([a-z0-9_-]+(?:\([^)]*\))?)(.*)/i)) {
            modifier = match[1];
            clause = match[2];
            rest = match[3];
            switch (modifier) {
                case '#':
                    params.id = clause;
                    break;
                case '.':
                    params.classNames.push(clause);
                    break;
                case ':':
                    params.pseudoClassNames.push(clause);
                    break;
                case '':
                case undefined:
                    params.tagName = clause.toUpperCase();
                    break;
                default:
                    abort(repr(expr));
            }
            expr = rest;
        }

        if (expr.length > 0) {
            abort(repr(expr));
        }
    },

    /** @id MochiKit.Selector.Selector.prototype.buildMatchExpression */
    buildMatchExpression: function () {
        var repr = MochiKit.Base.repr;
        var params = this.params;
        var conditions = [];
        var clause, i;

        function childElements(element) {
            return "MochiKit.Base.filter(function (node) { return node.nodeType == 1; }, " + element + ".childNodes)";
        }

        if (params.wildcard) {
            conditions.push('true');
        }
        if (clause = params.id) {
            conditions.push('element.id == ' + repr(clause));
        }
        if (clause = params.tagName) {
            conditions.push('element.tagName.toUpperCase() == ' + repr(clause));
        }
        if ((clause = params.classNames).length > 0) {
            for (i = 0; i < clause.length; i++) {
                conditions.push('MochiKit.DOM.hasElementClass(element, ' + repr(clause[i]) + ')');
            }
        }
        if ((clause = params.pseudoClassNames).length > 0) {
            for (i = 0; i < clause.length; i++) {
                var match = clause[i].match(/^([^(]+)(?:\((.*)\))?$/);
                var pseudoClass = match[1];
                var pseudoClassArgument = match[2];
                switch (pseudoClass) {
                    case 'root':
                        conditions.push('element.nodeType == 9 || element === element.ownerDocument.documentElement'); break;
                    case 'nth-child':
                    case 'nth-last-child':
                    case 'nth-of-type':
                    case 'nth-last-of-type':
                        match = pseudoClassArgument.match(/^((?:(\d+)n\+)?(\d+)|odd|even)$/);
                        if (!match) {
                            throw "Invalid argument to pseudo element nth-child: " + pseudoClassArgument;
                        }
                        var a, b;
                        if (match[0] == 'odd') {
                            a = 2;
                            b = 1;
                        } else if (match[0] == 'even') {
                            a = 2;
                            b = 0;
                        } else {
                            a = match[2] && parseInt(match) || null;
                            b = parseInt(match[3]);
                        }
                        conditions.push('this.nthChild(element,' + a + ',' + b
                                        + ',' + !!pseudoClass.match('^nth-last')    // Reverse
                                        + ',' + !!pseudoClass.match('of-type$')     // Restrict to same tagName
                                        + ')');
                        break;
                    case 'first-child':
                        conditions.push('this.nthChild(element, null, 1)');
                        break;
                    case 'last-child':
                        conditions.push('this.nthChild(element, null, 1, true)');
                        break;
                    case 'first-of-type':
                        conditions.push('this.nthChild(element, null, 1, false, true)');
                        break;
                    case 'last-of-type':
                        conditions.push('this.nthChild(element, null, 1, true, true)');
                        break;
                    case 'only-child':
                        conditions.push(childElements('element.parentNode') + '.length == 1');
                        break;
                    case 'only-of-type':
                        conditions.push('MochiKit.Base.filter(function (node) { return node.tagName == element.tagName; }, ' + childElements('element.parentNode') + ').length == 1');
                        break;
                    case 'empty':
                        conditions.push('element.childNodes.length == 0');
                        break;
                    case 'enabled':
                        conditions.push('(this.isUIElement(element) && element.disabled === false)');
                        break;
                    case 'disabled':
                        conditions.push('(this.isUIElement(element) && element.disabled === true)');
                        break;
                    case 'checked':
                        conditions.push('(this.isUIElement(element) && element.checked === true)');
                        break;
                    case 'not':
                        var subselector = new MochiKit.Selector.Selector(pseudoClassArgument);
                        conditions.push('!( ' + subselector.buildMatchExpression() + ')')
                        break;
                }
            }
        }
        if (clause = params.attributes) {
            MochiKit.Base.map(function (attribute) {
                var value = 'MochiKit.DOM.getNodeAttribute(element, ' + repr(attribute.name) + ')';
                var splitValueBy = function (delimiter) {
                    return value + '.split(' + repr(delimiter) + ')';
                }
                conditions.push(value + ' != null');
                switch (attribute.operator) {
                    case '=':
                        conditions.push(value + ' == ' + repr(attribute.value));
                        break;
                    case '~=':
                        conditions.push('MochiKit.Base.findValue(' + splitValueBy(' ') + ', ' + repr(attribute.value) + ') > -1');
                        break;
                    case '^=':
                        conditions.push(value + '.substring(0, ' + attribute.value.length + ') == ' + repr(attribute.value));
                        break;
                    case '$=':
                        conditions.push(value + '.substring(' + value + '.length - ' + attribute.value.length + ') == ' + repr(attribute.value));
                        break;
                    case '*=':
                        conditions.push(value + '.match(' + repr(attribute.value) + ')');
                        break;
                    case '|=':
                        conditions.push(splitValueBy('-') + '[0].toUpperCase() == ' + repr(attribute.value.toUpperCase()));
                        break;
                    case '!=':
                        conditions.push(value + ' != ' + repr(attribute.value));
                        break;
                    case '':
                    case undefined:
                        // Condition already added above
                        break;
                    default:
                        throw 'Unknown operator ' + attribute.operator + ' in selector';
                }
            }, clause);
        }

        return conditions.join(' && ');
    },

    /** @id MochiKit.Selector.Selector.prototype.compileMatcher */
    compileMatcher: function () {
        var code = 'return (!element.tagName) ? false : ' +
                   this.buildMatchExpression() + ';';
        this.match = new Function('element', code);
    },

    /** @id MochiKit.Selector.Selector.prototype.nthChild */
    nthChild: function (element, a, b, reverse, sametag){
        var siblings = MochiKit.Base.filter(function (node) {
            return node.nodeType == 1;
        }, element.parentNode.childNodes);
        if (sametag) {
            siblings = MochiKit.Base.filter(function (node) {
                return node.tagName == element.tagName;
            }, siblings);
        }
        if (reverse) {
            siblings = MochiKit.Iter.reversed(siblings);
        }
        if (a) {
            var actualIndex = MochiKit.Base.findIdentical(siblings, element);
            return ((actualIndex + 1 - b) / a) % 1 == 0;
        } else {
            return b == MochiKit.Base.findIdentical(siblings, element) + 1;
        }
    },

    /** @id MochiKit.Selector.Selector.prototype.isUIElement */
    isUIElement: function (element) {
        return MochiKit.Base.findValue(['input', 'button', 'select', 'option', 'textarea', 'object'],
                element.tagName.toLowerCase()) > -1;
    },

    /** @id MochiKit.Selector.Selector.prototype.findElements */
    findElements: function (scope, axis) {
        var element;

        if (axis == undefined) {
            axis = "";
        }

        function inScope(element, scope) {
            if (axis == "") {
                return MochiKit.DOM.isChildNode(element, scope);
            } else if (axis == ">") {
                return element.parentNode === scope;
            } else if (axis == "+") {
                return element === nextSiblingElement(scope);
            } else if (axis == "~") {
                var sibling = scope;
                while (sibling = nextSiblingElement(sibling)) {
                    if (element === sibling) {
                        return true;
                    }
                }
                return false;
            } else {
                throw "Invalid axis: " + axis;
            }
        }

        if (element = MochiKit.DOM.getElement(this.params.id)) {
            if (this.match(element)) {
                if (!scope || inScope(element, scope)) {
                    return [element];
                }
            }
        }

        function nextSiblingElement(node) {
            node = node.nextSibling;
            while (node && node.nodeType != 1) {
                node = node.nextSibling;
            }
            return node;
        }

        if (axis == "") {
            scope = (scope || MochiKit.DOM.currentDocument()).getElementsByTagName(this.params.tagName || '*');
        } else if (axis == ">") {
            if (!scope) {
                throw "> combinator not allowed without preceeding expression";
            }
            scope = MochiKit.Base.filter(function (node) {
                return node.nodeType == 1;
            }, scope.childNodes);
        } else if (axis == "+") {
            if (!scope) {
                throw "+ combinator not allowed without preceeding expression";
            }
            scope = nextSiblingElement(scope) && [nextSiblingElement(scope)];
        } else if (axis == "~") {
            if (!scope) {
                throw "~ combinator not allowed without preceeding expression";
            }
            var newscope = [];
            while (nextSiblingElement(scope)) {
                scope = nextSiblingElement(scope);
                newscope.push(scope);
            }
            scope = newscope;
        }

        if (!scope) {
            return [];
        }

        var results = MochiKit.Base.filter(MochiKit.Base.bind(function (scopeElt) {
            return this.match(scopeElt);
        }, this), scope);

        return results;
    },

    /** @id MochiKit.Selector.Selector.prototype.repr */
    repr: function () {
        return 'Selector(' + this.expression + ')';
    },

    toString: MochiKit.Base.forwardCall("repr")
};

MochiKit.Base.update(MochiKit.Selector, {

    /** @id MochiKit.Selector.findChildElements */
    findChildElements: function (element, expressions) {
        element = MochiKit.DOM.getElement(element);
        var uniq = function(arr) {
            var res = [];
            for (var i = 0; i < arr.length; i++) {
                if (MochiKit.Base.findIdentical(res, arr[i]) < 0) {
                    res.push(arr[i]);
                }
            }
            return res;
        };
        return MochiKit.Base.flattenArray(MochiKit.Base.map(function (expression) {
            var nextScope = "";
            var reducer = function (results, expr) {
                var match = expr.match(/^[>+~]$/);
                if (match) {
                    nextScope = match[0];
                    return results;
                } else {
                    var selector = new MochiKit.Selector.Selector(expr);
                    var elements = MochiKit.Iter.reduce(function (elements, result) {
                        return MochiKit.Base.extend(elements, selector.findElements(result || element, nextScope));
                    }, results, []);
                    nextScope = "";
                    return elements;
                }
            };
            var exprs = expression.replace(/(^\s+|\s+$)/g, '').split(/\s+/);
            return uniq(MochiKit.Iter.reduce(reducer, exprs, [null]));
        }, expressions));
    },

    findDocElements: function () {
        return MochiKit.Selector.findChildElements(MochiKit.DOM.currentDocument(), arguments);
    },

    __new__: function () {
        this.$$ = this.findDocElements;
        MochiKit.Base.nameFunctions(this);
    }
});

MochiKit.Selector.__new__();

MochiKit.Base._exportSymbols(this, MochiKit.Selector);
/***

MochiKit.Style 1.5

See <http://mochikit.com/> for documentation, downloads, license, etc.

(c) 2005-2006 Bob Ippolito, Beau Hartshorne.  All rights Reserved.

***/

MochiKit.Base._module('Style', '1.5', ['Base', 'DOM']);


/** @id MochiKit.Style.Dimensions */
MochiKit.Style.Dimensions = function (w, h) {
    if (!(this instanceof MochiKit.Style.Dimensions)) {
        return new MochiKit.Style.Dimensions(w, h);
    }
    this.w = w;
    this.h = h;
};

MochiKit.Style.Dimensions.prototype.__repr__ = function () {
    var repr = MochiKit.Base.repr;
    return '{w: '  + repr(this.w) + ', h: ' + repr(this.h) + '}';
};

MochiKit.Style.Dimensions.prototype.toString = function () {
    return this.__repr__();
};


/** @id MochiKit.Style.Coordinates */
MochiKit.Style.Coordinates = function (x, y) {
    if (!(this instanceof MochiKit.Style.Coordinates)) {
        return new MochiKit.Style.Coordinates(x, y);
    }
    this.x = x;
    this.y = y;
};

MochiKit.Style.Coordinates.prototype.__repr__ = function () {
    var repr = MochiKit.Base.repr;
    return '{x: '  + repr(this.x) + ', y: ' + repr(this.y) + '}';
};

MochiKit.Style.Coordinates.prototype.toString = function () {
    return this.__repr__();
};


MochiKit.Base.update(MochiKit.Style, {

    /** @id MochiKit.Style.getStyle */
    getStyle: function (elem, cssProperty) {
        var dom = MochiKit.DOM;
        var d = dom._document;

        elem = dom.getElement(elem);
        cssProperty = MochiKit.Base.camelize(cssProperty);

        if (!elem || elem == d) {
            return undefined;
        }
        if (cssProperty == 'opacity' && typeof(elem.filters) != 'undefined') {
            var opacity = (MochiKit.Style.getStyle(elem, 'filter') || '').match(/alpha\(opacity=(.*)\)/);
            if (opacity && opacity[1]) {
                return parseFloat(opacity[1]) / 100;
            }
            return 1.0;
        }
        if (cssProperty == 'float' || cssProperty == 'cssFloat' || cssProperty == 'styleFloat') {
            if (elem.style["float"]) {
                return elem.style["float"];
            } else if (elem.style.cssFloat) {
                return elem.style.cssFloat;
            } else if (elem.style.styleFloat) {
                return elem.style.styleFloat;
            } else {
                return "none";
            }
        }
        var value = elem.style ? elem.style[cssProperty] : null;
        if (!value) {
            if (d.defaultView && d.defaultView.getComputedStyle) {
                var css = d.defaultView.getComputedStyle(elem, null);
                cssProperty = cssProperty.replace(/([A-Z])/g, '-$1'
                    ).toLowerCase(); // from dojo.style.toSelectorCase
                value = css ? css.getPropertyValue(cssProperty) : null;
            } else if (elem.currentStyle) {
                value = elem.currentStyle[cssProperty];
                if (/^\d/.test(value) && !/px$/.test(value) && cssProperty != 'fontWeight') {
                    /* Convert to px using an hack from Dean Edwards */
                    var left = elem.style.left;
                    var rsLeft = elem.runtimeStyle.left;
                    elem.runtimeStyle.left = elem.currentStyle.left;
                    elem.style.left = value || 0;
                    value = elem.style.pixelLeft + "px";
                    elem.style.left = left;
                    elem.runtimeStyle.left = rsLeft;
                }
            }
        }
        if (cssProperty == 'opacity') {
            value = parseFloat(value);
        }

        if (/Opera/.test(navigator.userAgent) && (MochiKit.Base.findValue(['left', 'top', 'right', 'bottom'], cssProperty) != -1)) {
            if (MochiKit.Style.getStyle(elem, 'position') == 'static') {
                value = 'auto';
            }
        }

        return value == 'auto' ? null : value;
    },

    /** @id MochiKit.Style.setStyle */
    setStyle: function (elem, style) {
        elem = MochiKit.DOM.getElement(elem);
        for (var name in style) {
            switch (name) {
            case 'opacity':
                MochiKit.Style.setOpacity(elem, style[name]);
                break;
            case 'float':
            case 'cssFloat':
            case 'styleFloat':
                if (typeof(elem.style["float"]) != "undefined") {
                    elem.style["float"] = style[name];
                } else if (typeof(elem.style.cssFloat) != "undefined") {
                    elem.style.cssFloat = style[name];
                } else {
                    elem.style.styleFloat = style[name];
                }
                break;
            default:
                elem.style[MochiKit.Base.camelize(name)] = style[name];
            }
        }
    },

    /** @id MochiKit.Style.setOpacity */
    setOpacity: function (elem, o) {
        elem = MochiKit.DOM.getElement(elem);
        var self = MochiKit.Style;
        if (o == 1) {
            var toSet = /Gecko/.test(navigator.userAgent) && !(/Konqueror|AppleWebKit|KHTML/.test(navigator.userAgent));
            elem.style["opacity"] = toSet ? 0.999999 : 1.0;
            if (/MSIE/.test(navigator.userAgent)) {
                elem.style['filter'] =
                    self.getStyle(elem, 'filter').replace(/alpha\([^\)]*\)/gi, '');
            }
        } else {
            if (o < 0.00001) {
                o = 0;
            }
            elem.style["opacity"] = o;
            if (/MSIE/.test(navigator.userAgent)) {
                elem.style['filter'] =
                    self.getStyle(elem, 'filter').replace(/alpha\([^\)]*\)/gi, '') + 'alpha(opacity=' + o * 100 + ')';
            }
        }
    },

    /*

        getElementPosition is adapted from YAHOO.util.Dom.getXY v0.9.0.
        Copyright: Copyright (c) 2006, Yahoo! Inc. All rights reserved.
        License: BSD, http://developer.yahoo.net/yui/license.txt

    */

    /** @id MochiKit.Style.getElementPosition */
    getElementPosition: function (elem, /* optional */relativeTo) {
        var self = MochiKit.Style;
        var dom = MochiKit.DOM;
        var isCoordinates = function (o) {
            return o != null &&
                   o.nodeType == null &&
                   typeof(o.x) == "number" &&
                   typeof(o.y) == "number";
        }

        if (typeof(elem) == "string") {
            elem = dom.getElement(elem);
        }
        if (elem == null ||
            (!isCoordinates(elem) && self.getStyle(elem, 'display') == 'none')) {
            return undefined;
        }

        var c = new self.Coordinates(0, 0);
        var box = null;
        var parent = null;

        var d = MochiKit.DOM._document;
        var de = d.documentElement;
        var b = d.body;

        if (!elem.parentNode && elem.x && elem.y) {
            /* it's just a MochiKit.Style.Coordinates object */
            c.x += elem.x || 0;
            c.y += elem.y || 0;
        } else if (elem.getBoundingClientRect) { // IE shortcut
            /*

                The IE shortcut can be off by two. We fix it. See:
                http://msdn.microsoft.com/workshop/author/dhtml/reference/methods/getboundingclientrect.asp

                This is similar to the method used in
                MochiKit.Signal.Event.mouse().

            */
            box = elem.getBoundingClientRect();

            c.x += box.left +
                (de.scrollLeft || b.scrollLeft) -
                (de.clientLeft || 0);

            c.y += box.top +
                (de.scrollTop || b.scrollTop) -
                (de.clientTop || 0);

        } else if (elem.offsetParent) {
            c.x += elem.offsetLeft;
            c.y += elem.offsetTop;
            parent = elem.offsetParent;

            if (parent != elem) {
                while (parent) {
                    c.x += parseInt(parent.style.borderLeftWidth) || 0;
                    c.y += parseInt(parent.style.borderTopWidth) || 0;
                    c.x += parent.offsetLeft;
                    c.y += parent.offsetTop;
                    parent = parent.offsetParent;
                }
            }

            /*

                Opera < 9 and old Safari (absolute) incorrectly account for
                body offsetTop and offsetLeft.

            */
            var ua = navigator.userAgent.toLowerCase();
            if ((typeof(opera) != 'undefined' &&
                parseFloat(opera.version()) < 9) ||
                (ua.indexOf('AppleWebKit') != -1 &&
                self.getStyle(elem, 'position') == 'absolute')) {

                c.x -= b.offsetLeft;
                c.y -= b.offsetTop;

            }

            // Adjust position for strange Opera scroll bug
            if (elem.parentNode) {
                parent = elem.parentNode;
            } else {
                parent = null;
            }
            while (parent) {
                var tagName = parent.tagName.toUpperCase();
                if (tagName === 'BODY' || tagName === 'HTML') {
                    break;
                }
                var disp = self.getStyle(parent, 'display');
                // Handle strange Opera bug for some display
                if (disp.search(/^inline|table-row.*$/i)) {
                    c.x -= parent.scrollLeft;
                    c.y -= parent.scrollTop;
                }
                if (parent.parentNode) {
                    parent = parent.parentNode;
                } else {
                    parent = null;
                }
            }
        }

        if (relativeTo) {
            relativeTo = arguments.callee(relativeTo);
            if (relativeTo) {
                c.x -= (relativeTo.x || 0);
                c.y -= (relativeTo.y || 0);
            }
        }

        return c;
    },

    /** @id MochiKit.Style.setElementPosition */
    setElementPosition: function (elem, newPos/* optional */, units) {
        elem = MochiKit.DOM.getElement(elem);
        if (typeof(units) == 'undefined') {
            units = 'px';
        }
        var newStyle = {};
        var isUndefNull = MochiKit.Base.isUndefinedOrNull;
        if (!isUndefNull(newPos.x)) {
            newStyle['left'] = newPos.x + units;
        }
        if (!isUndefNull(newPos.y)) {
            newStyle['top'] = newPos.y + units;
        }
        MochiKit.DOM.updateNodeAttributes(elem, {'style': newStyle});
    },

    /** @id MochiKit.Style.makePositioned */
    makePositioned: function (element) {
        element = MochiKit.DOM.getElement(element);
        var pos = MochiKit.Style.getStyle(element, 'position');
        if (pos == 'static' || !pos) {
            element.style.position = 'relative';
            // Opera returns the offset relative to the positioning context,
            // when an element is position relative but top and left have
            // not been defined
            if (/Opera/.test(navigator.userAgent)) {
                element.style.top = 0;
                element.style.left = 0;
            }
        }
    },

    /** @id MochiKit.Style.undoPositioned */
    undoPositioned: function (element) {
        element = MochiKit.DOM.getElement(element);
        if (element.style.position == 'relative') {
            element.style.position = element.style.top = element.style.left = element.style.bottom = element.style.right = '';
        }
    },

    /** @id MochiKit.Style.makeClipping */
    makeClipping: function (element) {
        element = MochiKit.DOM.getElement(element);
        var s = element.style;
        var oldOverflow = { 'overflow': s.overflow,
                            'overflow-x': s.overflowX,
                            'overflow-y': s.overflowY };
        if ((MochiKit.Style.getStyle(element, 'overflow') || 'visible') != 'hidden') {
            element.style.overflow = 'hidden';
            element.style.overflowX = 'hidden';
            element.style.overflowY = 'hidden';
        }
        return oldOverflow;
    },

    /** @id MochiKit.Style.undoClipping */
    undoClipping: function (element, overflow) {
        element = MochiKit.DOM.getElement(element);
        if (typeof(overflow) == 'string') {
            element.style.overflow = overflow;
        } else if (overflow != null) {
            element.style.overflow = overflow['overflow'];
            element.style.overflowX = overflow['overflow-x'];
            element.style.overflowY = overflow['overflow-y'];
        }
    },

    /** @id MochiKit.Style.getElementDimensions */
    getElementDimensions: function (elem, contentSize/*optional*/) {
        var self = MochiKit.Style;
        var dom = MochiKit.DOM;
        if (typeof(elem.w) == 'number' || typeof(elem.h) == 'number') {
            return new self.Dimensions(elem.w || 0, elem.h || 0);
        }
        elem = dom.getElement(elem);
        if (!elem) {
            return undefined;
        }
        var disp = self.getStyle(elem, 'display');
        // display can be empty/undefined on WebKit/KHTML
        if (disp == 'none' || disp == '' || typeof(disp) == 'undefined') {
            var s = elem.style;
            var originalVisibility = s.visibility;
            var originalPosition = s.position;
            var originalDisplay = s.display;
            s.visibility = 'hidden';
            s.position = 'absolute';
            s.display = self._getDefaultDisplay(elem);
            var originalWidth = elem.offsetWidth;
            var originalHeight = elem.offsetHeight;
            s.display = originalDisplay;
            s.position = originalPosition;
            s.visibility = originalVisibility;
        } else {
            originalWidth = elem.offsetWidth || 0;
            originalHeight = elem.offsetHeight || 0;
        }
        if (contentSize) {
            var tableCell = 'colSpan' in elem && 'rowSpan' in elem;
            var collapse = (tableCell && elem.parentNode && self.getStyle(
                    elem.parentNode, 'borderCollapse') == 'collapse')
            if (collapse) {
                if (/MSIE/.test(navigator.userAgent)) {
                    var borderLeftQuota = elem.previousSibling? 0.5 : 1;
                    var borderRightQuota = elem.nextSibling? 0.5 : 1;
                }
                else {
                    var borderLeftQuota = 0.5;
                    var borderRightQuota = 0.5;
                }
            } else {
                var borderLeftQuota = 1;
                var borderRightQuota = 1;
            }
            originalWidth -= Math.round(
                (parseFloat(self.getStyle(elem, 'paddingLeft')) || 0)
              + (parseFloat(self.getStyle(elem, 'paddingRight')) || 0)
              + borderLeftQuota *
                (parseFloat(self.getStyle(elem, 'borderLeftWidth')) || 0)
              + borderRightQuota *
                (parseFloat(self.getStyle(elem, 'borderRightWidth')) || 0)
            );
            if (tableCell) {
                if (/Gecko|Opera/.test(navigator.userAgent)
                    && !/Konqueror|AppleWebKit|KHTML/.test(navigator.userAgent)) {
                    var borderHeightQuota = 0;
                } else if (/MSIE/.test(navigator.userAgent)) {
                    var borderHeightQuota = 1;
                } else {
                    var borderHeightQuota = collapse? 0.5 : 1;
                }
            } else {
                var borderHeightQuota = 1;
            }
            originalHeight -= Math.round(
                (parseFloat(self.getStyle(elem, 'paddingTop')) || 0)
              + (parseFloat(self.getStyle(elem, 'paddingBottom')) || 0)
              + borderHeightQuota * (
                (parseFloat(self.getStyle(elem, 'borderTopWidth')) || 0)
              + (parseFloat(self.getStyle(elem, 'borderBottomWidth')) || 0))
            );
        }
        return new self.Dimensions(originalWidth, originalHeight);
    },

    /** @id MochiKit.Style.setElementDimensions */
    setElementDimensions: function (elem, newSize/* optional */, units) {
        elem = MochiKit.DOM.getElement(elem);
        if (typeof(units) == 'undefined') {
            units = 'px';
        }
        var newStyle = {};
        var isUndefNull = MochiKit.Base.isUndefinedOrNull;
        if (!isUndefNull(newSize.w)) {
            newStyle['width'] = newSize.w + units;
        }
        if (!isUndefNull(newSize.h)) {
            newStyle['height'] = newSize.h + units;
        }
        MochiKit.DOM.updateNodeAttributes(elem, {'style': newStyle});
    },

    _getDefaultDisplay: function (elem) {
        var self = MochiKit.Style;
        var dom = MochiKit.DOM;
        elem = dom.getElement(elem);
        if (!elem) {
            return undefined;
        }
        var tagName = elem.tagName.toUpperCase();
        return self._defaultDisplay[tagName] || 'block';
    },

    /** @id MochiKit.Style.setDisplayForElement */
    setDisplayForElement: function (display, element/*, ...*/) {
        var elements = MochiKit.Base.extend(null, arguments, 1);
        var getElement = MochiKit.DOM.getElement;
        for (var i = 0; i < elements.length; i++) {
            element = getElement(elements[i]);
            if (element) {
                element.style.display = display;
            }
        }
    },

    /** @id MochiKit.Style.getViewportDimensions */
    getViewportDimensions: function () {
        var d = new MochiKit.Style.Dimensions();
        var w = MochiKit.DOM._window;
        var b = MochiKit.DOM._document.body;
        if (w.innerWidth) {
            d.w = w.innerWidth;
            d.h = w.innerHeight;
        } else if (b && b.parentElement && b.parentElement.clientWidth) {
            d.w = b.parentElement.clientWidth;
            d.h = b.parentElement.clientHeight;
        } else if (b && b.clientWidth) {
            d.w = b.clientWidth;
            d.h = b.clientHeight;
        }
        return d;
    },

    /** @id MochiKit.Style.getViewportPosition */
    getViewportPosition: function () {
        var c = new MochiKit.Style.Coordinates(0, 0);
        var d = MochiKit.DOM._document;
        var de = d.documentElement;
        var db = d.body;
        if (de && (de.scrollTop || de.scrollLeft)) {
            c.x = de.scrollLeft;
            c.y = de.scrollTop;
        } else if (db) {
            c.x = db.scrollLeft;
            c.y = db.scrollTop;
        }
        return c;
    },

    __new__: function () {
        var m = MochiKit.Base;

        var inlines = ['A','ABBR','ACRONYM','B','BASEFONT','BDO','BIG','BR',
                       'CITE','CODE','DFN','EM','FONT','I','IMG','KBD','LABEL',
                       'Q','S','SAMP','SMALL','SPAN','STRIKE','STRONG','SUB',
                       'SUP','TEXTAREA','TT','U','VAR'];
        this._defaultDisplay = { 'TABLE': 'table',
                                 'THEAD': 'table-header-group',
                                 'TBODY': 'table-row-group',
                                 'TFOOT': 'table-footer-group',
                                 'COLGROUP': 'table-column-group',
                                 'COL': 'table-column',
                                 'TR': 'table-row',
                                 'TD': 'table-cell',
                                 'TH': 'table-cell',
                                 'CAPTION': 'table-caption',
                                 'LI': 'list-item',
                                 'INPUT': 'inline-block',
                                 'SELECT': 'inline-block' };
        // CSS 'display' support in IE6/7 is just broken...
        if (/MSIE/.test(navigator.userAgent)) {
            for (var k in this._defaultDisplay) {
                var v = this._defaultDisplay[k];
                if (v.indexOf('table') == 0) {
                    this._defaultDisplay[k] = 'block';
                }
            }
        }
        for (var i = 0; i < inlines.length; i++) {
            this._defaultDisplay[inlines[i]] = 'inline';
        }

        // Backwards compatibility aliases
        m._deprecated(this, 'elementPosition', 'MochiKit.Style.getElementPosition', '1.3', true);
        m._deprecated(this, 'elementDimensions', 'MochiKit.Style.getElementDimensions', '1.3', true);

        this.hideElement = m.partial(this.setDisplayForElement, 'none');
        // TODO: showElement could be improved by using getDefaultDisplay.
        this.showElement = m.partial(this.setDisplayForElement, 'block');

        m.nameFunctions(this);
    }
});

MochiKit.Style.__new__();
MochiKit.Base._exportSymbols(this, MochiKit.Style);
/***

MochiKit.LoggingPane 1.5

See <http://mochikit.com/> for documentation, downloads, license, etc.

(c) 2005 Bob Ippolito.  All rights Reserved.

***/

MochiKit.Base._module('LoggingPane', '1.5', ['Base', 'Logging']);

/** @id MochiKit.LoggingPane.createLoggingPane */
MochiKit.LoggingPane.createLoggingPane = function (inline/* = false */) {
    var m = MochiKit.LoggingPane;
    inline = !(!inline);
    if (m._loggingPane && m._loggingPane.inline != inline) {
        m._loggingPane.closePane();
        m._loggingPane = null;
    }
    if (!m._loggingPane || m._loggingPane.closed) {
        m._loggingPane = new m.LoggingPane(inline, MochiKit.Logging.logger);
    }
    return m._loggingPane;
};

/** @id MochiKit.LoggingPane.LoggingPane */
MochiKit.LoggingPane.LoggingPane = function (inline/* = false */, logger/* = MochiKit.Logging.logger */) {

    /* Use a div if inline, pop up a window if not */
    /* Create the elements */
    if (typeof(logger) == "undefined" || logger === null) {
        logger = MochiKit.Logging.logger;
    }
    this.logger = logger;
    var update = MochiKit.Base.update;
    var updatetree = MochiKit.Base.updatetree;
    var bind = MochiKit.Base.bind;
    var clone = MochiKit.Base.clone;
    var win = window;
    var uid = "_MochiKit_LoggingPane";
    if (typeof(MochiKit.DOM) != "undefined") {
        win = MochiKit.DOM.currentWindow();
    }
    if (!inline) {
        // name the popup with the base URL for uniqueness
        var url = win.location.href.split("?")[0].replace(/[#:\/.><&%-]/g, "_");
        var name = uid + "_" + url;
        var nwin = win.open("", name, "dependent,resizable,height=200");
        if (!nwin) {
            alert("Not able to open debugging window due to pop-up blocking.");
            return undefined;
        }
        nwin.document.write(
            '<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0 Transitional//EN" '
            + '"http://www.w3.org/TR/html4/loose.dtd">'
            + '<html><head><title>[MochiKit.LoggingPane]</title></head>'
            + '<body></body></html>'
        );
        nwin.document.close();
        nwin.document.title += ' ' + win.document.title;
        win = nwin;
    }
    var doc = win.document;
    this.doc = doc;

    // Connect to the debug pane if it already exists (i.e. in a window orphaned by the page being refreshed)
    var debugPane = doc.getElementById(uid);
    var existing_pane = !!debugPane;
    if (debugPane && typeof(debugPane.loggingPane) != "undefined") {
        debugPane.loggingPane.logger = this.logger;
        debugPane.loggingPane.buildAndApplyFilter();
        return debugPane.loggingPane;
    }

    if (existing_pane) {
        // clear any existing contents
        var child;
        while ((child = debugPane.firstChild)) {
            debugPane.removeChild(child);
        }
    } else {
        debugPane = doc.createElement("div");
        debugPane.id = uid;
    }
    debugPane.loggingPane = this;
    var levelFilterField = doc.createElement("input");
    var infoFilterField = doc.createElement("input");
    var filterButton = doc.createElement("button");
    var loadButton = doc.createElement("button");
    var clearButton = doc.createElement("button");
    var closeButton = doc.createElement("button");
    var logPaneArea = doc.createElement("div");
    var logPane = doc.createElement("div");

    /* Set up the functions */
    var listenerId = uid + "_Listener";
    this.colorTable = clone(this.colorTable);
    var messages = [];
    var messageFilter = null;

    /** @id MochiKit.LoggingPane.messageLevel */
    var messageLevel = function (msg) {
        var level = msg.level;
        if (typeof(level) == "number") {
            level = MochiKit.Logging.LogLevel[level];
        }
        return level;
    };

    /** @id MochiKit.LoggingPane.messageText */
    var messageText = function (msg) {
        return msg.info.join(" ");
    };

    /** @id MochiKit.LoggingPane.addMessageText */
    var addMessageText = bind(function (msg) {
        var level = messageLevel(msg);
        var text = messageText(msg);
        var c = this.colorTable[level];
        var p = doc.createElement("span");
        p.className = "MochiKit-LogMessage MochiKit-LogLevel-" + level;
        p.style.cssText = "margin: 0px; white-space: -moz-pre-wrap; white-space: -o-pre-wrap; white-space: pre-wrap; white-space: pre-line; word-wrap: break-word; wrap-option: emergency; color: " + c;
        p.appendChild(doc.createTextNode(level + ": " + text));
        logPane.appendChild(p);
        logPane.appendChild(doc.createElement("br"));
        if (logPaneArea.offsetHeight > logPaneArea.scrollHeight) {
            logPaneArea.scrollTop = 0;
        } else {
            logPaneArea.scrollTop = logPaneArea.scrollHeight;
        }
    }, this);

    /** @id MochiKit.LoggingPane.addMessage */
    var addMessage = function (msg) {
        messages[messages.length] = msg;
        addMessageText(msg);
    };

    /** @id MochiKit.LoggingPane.buildMessageFilter */
    var buildMessageFilter = function () {
        var levelre, infore;
        try {
            /* Catch any exceptions that might arise due to invalid regexes */
            levelre = new RegExp(levelFilterField.value);
            infore = new RegExp(infoFilterField.value);
        } catch(e) {
            /* If there was an error with the regexes, do no filtering */
            logDebug("Error in filter regex: " + e.message);
            return null;
        }

        return function (msg) {
            return (
                levelre.test(messageLevel(msg)) &&
                infore.test(messageText(msg))
            );
        };
    };

    /** @id MochiKit.LoggingPane.clearMessagePane */
    var clearMessagePane = function () {
        while (logPane.firstChild) {
            logPane.removeChild(logPane.firstChild);
        }
    };

    /** @id MochiKit.LoggingPane.clearMessages */
    var clearMessages = function () {
        messages = [];
        clearMessagePane();
    };

    /** @id MochiKit.LoggingPane.closePane */
    var closePane = bind(function () {
        if (this.closed) {
            return;
        }
        this.closed = true;
        if (MochiKit.LoggingPane._loggingPane == this) {
            MochiKit.LoggingPane._loggingPane = null;
        }
        this.logger.removeListener(listenerId);
        try {
            try {
              debugPane.loggingPane = null;
            } catch(e) { logFatal("Bookmarklet was closed incorrectly."); }
            if (inline) {
                debugPane.parentNode.removeChild(debugPane);
            } else {
                this.win.close();
            }
        } catch(e) {}
    }, this);

    /** @id MochiKit.LoggingPane.filterMessages */
    var filterMessages = function () {
        clearMessagePane();

        for (var i = 0; i < messages.length; i++) {
            var msg = messages[i];
            if (messageFilter === null || messageFilter(msg)) {
                addMessageText(msg);
            }
        }
    };

    this.buildAndApplyFilter = function () {
        messageFilter = buildMessageFilter();

        filterMessages();

        this.logger.removeListener(listenerId);
        this.logger.addListener(listenerId, messageFilter, addMessage);
    };


    /** @id MochiKit.LoggingPane.loadMessages */
    var loadMessages = bind(function () {
        messages = this.logger.getMessages();
        filterMessages();
    }, this);

    /** @id MochiKit.LoggingPane.filterOnEnter */
    var filterOnEnter = bind(function (event) {
        event = event || window.event;
        key = event.which || event.keyCode;
        if (key == 13) {
            this.buildAndApplyFilter();
        }
    }, this);

    /* Create the debug pane */
    var style = "display: block; z-index: 1000; left: 0px; bottom: 0px; position: fixed; width: 100%; background-color: white; font: " + this.logFont;
    if (inline) {
        style += "; height: 10em; border-top: 2px solid black";
    } else {
        style += "; height: 100%;";
    }
    debugPane.style.cssText = style;

    if (!existing_pane) {
        doc.body.appendChild(debugPane);
    }

    /* Create the filter fields */
    style = {"cssText": "width: 33%; display: inline; font: " + this.logFont};

    updatetree(levelFilterField, {
        "value": "FATAL|ERROR|WARNING|INFO|DEBUG",
        "onkeypress": filterOnEnter,
        "style": style
    });
    debugPane.appendChild(levelFilterField);

    updatetree(infoFilterField, {
        "value": ".*",
        "onkeypress": filterOnEnter,
        "style": style
    });
    debugPane.appendChild(infoFilterField);

    /* Create the buttons */
    style = "width: 8%; display:inline; font: " + this.logFont;

    filterButton.appendChild(doc.createTextNode("Filter"));
    filterButton.onclick = bind("buildAndApplyFilter", this);
    filterButton.style.cssText = style;
    debugPane.appendChild(filterButton);

    loadButton.appendChild(doc.createTextNode("Load"));
    loadButton.onclick = loadMessages;
    loadButton.style.cssText = style;
    debugPane.appendChild(loadButton);

    clearButton.appendChild(doc.createTextNode("Clear"));
    clearButton.onclick = clearMessages;
    clearButton.style.cssText = style;
    debugPane.appendChild(clearButton);

    closeButton.appendChild(doc.createTextNode("Close"));
    closeButton.onclick = closePane;
    closeButton.style.cssText = style;
    debugPane.appendChild(closeButton);

    /* Create the logging pane */
    logPaneArea.style.cssText = "overflow: auto; width: 100%";
    logPane.style.cssText = "width: 100%; height: " + (inline ? "8em" : "100%");

    logPaneArea.appendChild(logPane);
    debugPane.appendChild(logPaneArea);

    this.buildAndApplyFilter();
    loadMessages();

    if (inline) {
        this.win = undefined;
    } else {
        this.win = win;
    }
    this.inline = inline;
    this.closePane = closePane;
    this.closed = false;


    return this;
};

MochiKit.LoggingPane.LoggingPane.prototype = {
    "logFont": "8pt Verdana,sans-serif",
    "colorTable": {
        "ERROR": "red",
        "FATAL": "darkred",
        "WARNING": "blue",
        "INFO": "black",
        "DEBUG": "green"
    }
};

MochiKit.LoggingPane.__new__ = function () {
    MochiKit.Base.nameFunctions(this);
    MochiKit.LoggingPane._loggingPane = null;
};

MochiKit.LoggingPane.__new__();

MochiKit.Base._exportSymbols(this, MochiKit.LoggingPane);
/***

MochiKit.Color 1.5

See <http://mochikit.com/> for documentation, downloads, license, etc.

(c) 2005 Bob Ippolito and others.  All rights Reserved.

***/

MochiKit.Base._module('Color', '1.5', ['Base', 'DOM', 'Style']);

/** @id MochiKit.Color.Color */
MochiKit.Color.Color = function (red, green, blue, alpha) {
    if (typeof(alpha) == 'undefined' || alpha === null) {
        alpha = 1.0;
    }
    this.rgb = {
        r: red,
        g: green,
        b: blue,
        a: alpha
    };
};


// Prototype methods

MochiKit.Color.Color.prototype = {

    __class__: MochiKit.Color.Color,

    /** @id MochiKit.Color.Color.prototype.colorWithAlpha */
    colorWithAlpha: function (alpha) {
        var rgb = this.rgb;
        var m = MochiKit.Color;
        return m.Color.fromRGB(rgb.r, rgb.g, rgb.b, alpha);
    },

    /** @id MochiKit.Color.Color.prototype.colorWithHue */
    colorWithHue: function (hue) {
        // get an HSL model, and set the new hue...
        var hsl = this.asHSL();
        hsl.h = hue;
        var m = MochiKit.Color;
        // convert back to RGB...
        return m.Color.fromHSL(hsl);
    },

    /** @id MochiKit.Color.Color.prototype.colorWithSaturation */
    colorWithSaturation: function (saturation) {
        // get an HSL model, and set the new hue...
        var hsl = this.asHSL();
        hsl.s = saturation;
        var m = MochiKit.Color;
        // convert back to RGB...
        return m.Color.fromHSL(hsl);
    },

    /** @id MochiKit.Color.Color.prototype.colorWithLightness */
    colorWithLightness: function (lightness) {
        // get an HSL model, and set the new hue...
        var hsl = this.asHSL();
        hsl.l = lightness;
        var m = MochiKit.Color;
        // convert back to RGB...
        return m.Color.fromHSL(hsl);
    },

    /** @id MochiKit.Color.Color.prototype.darkerColorWithLevel */
    darkerColorWithLevel: function (level) {
        var hsl  = this.asHSL();
        hsl.l = Math.max(hsl.l - level, 0);
        var m = MochiKit.Color;
        return m.Color.fromHSL(hsl);
    },

    /** @id MochiKit.Color.Color.prototype.lighterColorWithLevel */
    lighterColorWithLevel: function (level) {
        var hsl  = this.asHSL();
        hsl.l = Math.min(hsl.l + level, 1);
        var m = MochiKit.Color;
        return m.Color.fromHSL(hsl);
    },

    /** @id MochiKit.Color.Color.prototype.blendedColor */
    blendedColor: function (other, /* optional */ fraction) {
        if (typeof(fraction) == 'undefined' || fraction === null) {
            fraction = 0.5;
        }
        var sf = 1.0 - fraction;
        var s = this.rgb;
        var d = other.rgb;
        var df = fraction;
        return MochiKit.Color.Color.fromRGB(
            (s.r * sf) + (d.r * df),
            (s.g * sf) + (d.g * df),
            (s.b * sf) + (d.b * df),
            (s.a * sf) + (d.a * df)
        );
    },

    /** @id MochiKit.Color.Color.prototype.compareRGB */
    compareRGB: function (other) {
        var a = this.asRGB();
        var b = other.asRGB();
        return MochiKit.Base.compare(
            [a.r, a.g, a.b, a.a],
            [b.r, b.g, b.b, b.a]
        );
    },

    /** @id MochiKit.Color.Color.prototype.isLight */
    isLight: function () {
        return this.asHSL().b > 0.5;
    },

    /** @id MochiKit.Color.Color.prototype.isDark */
    isDark: function () {
        return (!this.isLight());
    },

    /** @id MochiKit.Color.Color.prototype.toHSLString */
    toHSLString: function () {
        var c = this.asHSL();
        var ccc = MochiKit.Color.clampColorComponent;
        var rval = this._hslString;
        if (!rval) {
            var mid = (
                ccc(c.h, 360).toFixed(0)
                + "," + ccc(c.s, 100).toPrecision(4) + "%"
                + "," + ccc(c.l, 100).toPrecision(4) + "%"
            );
            var a = c.a;
            if (a >= 1) {
                a = 1;
                rval = "hsl(" + mid + ")";
            } else {
                if (a <= 0) {
                    a = 0;
                }
                rval = "hsla(" + mid + "," + a + ")";
            }
            this._hslString = rval;
        }
        return rval;
    },

    /** @id MochiKit.Color.Color.prototype.toRGBString */
    toRGBString: function () {
        var c = this.rgb;
        var ccc = MochiKit.Color.clampColorComponent;
        var rval = this._rgbString;
        if (!rval) {
            var mid = (
                ccc(c.r, 255).toFixed(0)
                + "," + ccc(c.g, 255).toFixed(0)
                + "," + ccc(c.b, 255).toFixed(0)
            );
            if (c.a != 1) {
                rval = "rgba(" + mid + "," + c.a + ")";
            } else {
                rval = "rgb(" + mid + ")";
            }
            this._rgbString = rval;
        }
        return rval;
    },

    /** @id MochiKit.Color.Color.prototype.asRGB */
    asRGB: function () {
        return MochiKit.Base.clone(this.rgb);
    },

    /** @id MochiKit.Color.Color.prototype.toHexString */
    toHexString: function () {
        var m = MochiKit.Color;
        var c = this.rgb;
        var ccc = MochiKit.Color.clampColorComponent;
        var rval = this._hexString;
        if (!rval) {
            rval = ("#" +
                m.toColorPart(ccc(c.r, 255)) +
                m.toColorPart(ccc(c.g, 255)) +
                m.toColorPart(ccc(c.b, 255))
            );
            this._hexString = rval;
        }
        return rval;
    },

    /** @id MochiKit.Color.Color.prototype.asHSV */
    asHSV: function () {
        var hsv = this.hsv;
        var c = this.rgb;
        if (typeof(hsv) == 'undefined' || hsv === null) {
            hsv = MochiKit.Color.rgbToHSV(this.rgb);
            this.hsv = hsv;
        }
        return MochiKit.Base.clone(hsv);
    },

    /** @id MochiKit.Color.Color.prototype.asHSL */
    asHSL: function () {
        var hsl = this.hsl;
        var c = this.rgb;
        if (typeof(hsl) == 'undefined' || hsl === null) {
            hsl = MochiKit.Color.rgbToHSL(this.rgb);
            this.hsl = hsl;
        }
        return MochiKit.Base.clone(hsl);
    },

    /** @id MochiKit.Color.Color.prototype.toString */
    toString: function () {
        return this.toRGBString();
    },

    /** @id MochiKit.Color.Color.prototype.repr */
    repr: function () {
        var c = this.rgb;
        var col = [c.r, c.g, c.b, c.a];
        return this.__class__.NAME + "(" + col.join(", ") + ")";
    }

};

// Constructor methods

MochiKit.Base.update(MochiKit.Color.Color, {
    /** @id MochiKit.Color.Color.fromRGB */
    fromRGB: function (red, green, blue, alpha) {
        // designated initializer
        var Color = MochiKit.Color.Color;
        if (arguments.length == 1) {
            var rgb = red;
            red = rgb.r;
            green = rgb.g;
            blue = rgb.b;
            if (typeof(rgb.a) == 'undefined') {
                alpha = undefined;
            } else {
                alpha = rgb.a;
            }
        }
        return new Color(red, green, blue, alpha);
    },

    /** @id MochiKit.Color.Color.fromHSL */
    fromHSL: function (hue, saturation, lightness, alpha) {
        var m = MochiKit.Color;
        return m.Color.fromRGB(m.hslToRGB.apply(m, arguments));
    },

    /** @id MochiKit.Color.Color.fromHSV */
    fromHSV: function (hue, saturation, value, alpha) {
        var m = MochiKit.Color;
        return m.Color.fromRGB(m.hsvToRGB.apply(m, arguments));
    },

    /** @id MochiKit.Color.Color.fromName */
    fromName: function (name) {
        var Color = MochiKit.Color.Color;
        // Opera 9 seems to "quote" named colors(?!)
        if (name.charAt(0) == '"') {
            name = name.substr(1, name.length - 2);
        }
        var htmlColor = Color._namedColors[name.toLowerCase()];
        if (typeof(htmlColor) == 'string') {
            return Color.fromHexString(htmlColor);
        } else if (name == "transparent") {
            return Color.transparentColor();
        }
        return null;
    },

    /** @id MochiKit.Color.Color.fromString */
    fromString: function (colorString) {
        var self = MochiKit.Color.Color;
        var three = colorString.substr(0, 3);
        if (three == "rgb") {
            return self.fromRGBString(colorString);
        } else if (three == "hsl") {
            return self.fromHSLString(colorString);
        } else if (colorString.charAt(0) == "#") {
            return self.fromHexString(colorString);
        }
        return self.fromName(colorString);
    },


    /** @id MochiKit.Color.Color.fromHexString */
    fromHexString: function (hexCode) {
        if (hexCode.charAt(0) == '#') {
            hexCode = hexCode.substring(1);
        }
        var components = [];
        var i, hex;
        if (hexCode.length == 3) {
            for (i = 0; i < 3; i++) {
                hex = hexCode.substr(i, 1);
                components.push(parseInt(hex + hex, 16) / 255.0);
            }
        } else {
            for (i = 0; i < 6; i += 2) {
                hex = hexCode.substr(i, 2);
                components.push(parseInt(hex, 16) / 255.0);
            }
        }
        var Color = MochiKit.Color.Color;
        return Color.fromRGB.apply(Color, components);
    },


    _fromColorString: function (pre, method, scales, colorCode) {
        // parses either HSL or RGB
        if (colorCode.indexOf(pre) === 0) {
            colorCode = colorCode.substring(colorCode.indexOf("(", 3) + 1, colorCode.length - 1);
        }
        var colorChunks = colorCode.split(/\s*,\s*/);
        var colorFloats = [];
        for (var i = 0; i < colorChunks.length; i++) {
            var c = colorChunks[i];
            var val;
            var three = c.substring(c.length - 3);
            if (c.charAt(c.length - 1) == '%') {
                val = 0.01 * parseFloat(c.substring(0, c.length - 1));
            } else if (three == "deg") {
                val = parseFloat(c) / 360.0;
            } else if (three == "rad") {
                val = parseFloat(c) / (Math.PI * 2);
            } else {
                val = scales[i] * parseFloat(c);
            }
            colorFloats.push(val);
        }
        return this[method].apply(this, colorFloats);
    },

    /** @id MochiKit.Color.Color.fromComputedStyle */
    fromComputedStyle: function (elem, style) {
        var d = MochiKit.DOM;
        var cls = MochiKit.Color.Color;
        for (elem = d.getElement(elem); elem; elem = elem.parentNode) {
            var actualColor = MochiKit.Style.getStyle.apply(d, arguments);
            if (!actualColor) {
                continue;
            }
            var color = cls.fromString(actualColor);
            if (!color) {
                break;
            }
            if (color.asRGB().a > 0) {
                return color;
            }
        }
        return null;
    },

    /** @id MochiKit.Color.Color.fromBackground */
    fromBackground: function (elem) {
        var cls = MochiKit.Color.Color;
        return cls.fromComputedStyle(
            elem, "backgroundColor", "background-color") || cls.whiteColor();
    },

    /** @id MochiKit.Color.Color.fromText */
    fromText: function (elem) {
        var cls = MochiKit.Color.Color;
        return cls.fromComputedStyle(
            elem, "color", "color") || cls.blackColor();
    },

    /** @id MochiKit.Color.Color.namedColors */
    namedColors: function () {
        return MochiKit.Base.clone(MochiKit.Color.Color._namedColors);
    }
});


// Module level functions

MochiKit.Base.update(MochiKit.Color, {
    /** @id MochiKit.Color.clampColorComponent */
    clampColorComponent: function (v, scale) {
        v *= scale;
        if (v < 0) {
            return 0;
        } else if (v > scale) {
            return scale;
        } else {
            return v;
        }
    },

    _hslValue: function (n1, n2, hue) {
        if (hue > 6.0) {
            hue -= 6.0;
        } else if (hue < 0.0) {
            hue += 6.0;
        }
        var val;
        if (hue < 1.0) {
            val = n1 + (n2 - n1) * hue;
        } else if (hue < 3.0) {
            val = n2;
        } else if (hue < 4.0) {
            val = n1 + (n2 - n1) * (4.0 - hue);
        } else {
            val = n1;
        }
        return val;
    },

    /** @id MochiKit.Color.hsvToRGB */
    hsvToRGB: function (hue, saturation, value, alpha) {
        if (arguments.length == 1) {
            var hsv = hue;
            hue = hsv.h;
            saturation = hsv.s;
            value = hsv.v;
            alpha = hsv.a;
        }
        var red;
        var green;
        var blue;
        if (saturation === 0) {
            red = value;
            green = value;
            blue = value;
        } else {
            var i = Math.floor(hue * 6);
            var f = (hue * 6) - i;
            var p = value * (1 - saturation);
            var q = value * (1 - (saturation * f));
            var t = value * (1 - (saturation * (1 - f)));
            switch (i) {
                case 1: red = q; green = value; blue = p; break;
                case 2: red = p; green = value; blue = t; break;
                case 3: red = p; green = q; blue = value; break;
                case 4: red = t; green = p; blue = value; break;
                case 5: red = value; green = p; blue = q; break;
                case 6: // fall through
                case 0: red = value; green = t; blue = p; break;
            }
        }
        return {
            r: red,
            g: green,
            b: blue,
            a: alpha
        };
    },

    /** @id MochiKit.Color.hslToRGB */
    hslToRGB: function (hue, saturation, lightness, alpha) {
        if (arguments.length == 1) {
            var hsl = hue;
            hue = hsl.h;
            saturation = hsl.s;
            lightness = hsl.l;
            alpha = hsl.a;
        }
        var red;
        var green;
        var blue;
        if (saturation === 0) {
            red = lightness;
            green = lightness;
            blue = lightness;
        } else {
            var m2;
            if (lightness <= 0.5) {
                m2 = lightness * (1.0 + saturation);
            } else {
                m2 = lightness + saturation - (lightness * saturation);
            }
            var m1 = (2.0 * lightness) - m2;
            var f = MochiKit.Color._hslValue;
            var h6 = hue * 6.0;
            red = f(m1, m2, h6 + 2);
            green = f(m1, m2, h6);
            blue = f(m1, m2, h6 - 2);
        }
        return {
            r: red,
            g: green,
            b: blue,
            a: alpha
        };
    },

    /** @id MochiKit.Color.rgbToHSV */
    rgbToHSV: function (red, green, blue, alpha) {
        if (arguments.length == 1) {
            var rgb = red;
            red = rgb.r;
            green = rgb.g;
            blue = rgb.b;
            alpha = rgb.a;
        }
        var max = Math.max(Math.max(red, green), blue);
        var min = Math.min(Math.min(red, green), blue);
        var hue;
        var saturation;
        var value = max;
        if (min == max) {
            hue = 0;
            saturation = 0;
        } else {
            var delta = (max - min);
            saturation = delta / max;

            if (red == max) {
                hue = (green - blue) / delta;
            } else if (green == max) {
                hue = 2 + ((blue - red) / delta);
            } else {
                hue = 4 + ((red - green) / delta);
            }
            hue /= 6;
            if (hue < 0) {
                hue += 1;
            }
            if (hue > 1) {
                hue -= 1;
            }
        }
        return {
            h: hue,
            s: saturation,
            v: value,
            a: alpha
        };
    },

    /** @id MochiKit.Color.rgbToHSL */
    rgbToHSL: function (red, green, blue, alpha) {
        if (arguments.length == 1) {
            var rgb = red;
            red = rgb.r;
            green = rgb.g;
            blue = rgb.b;
            alpha = rgb.a;
        }
        var max = Math.max(red, Math.max(green, blue));
        var min = Math.min(red, Math.min(green, blue));
        var hue;
        var saturation;
        var lightness = (max + min) / 2.0;
        var delta = max - min;
        if (delta === 0) {
            hue = 0;
            saturation = 0;
        } else {
            if (lightness <= 0.5) {
                saturation = delta / (max + min);
            } else {
                saturation = delta / (2 - max - min);
            }
            if (red == max) {
                hue = (green - blue) / delta;
            } else if (green == max) {
                hue = 2 + ((blue - red) / delta);
            } else {
                hue = 4 + ((red - green) / delta);
            }
            hue /= 6;
            if (hue < 0) {
                hue += 1;
            }
            if (hue > 1) {
                hue -= 1;
            }

        }
        return {
            h: hue,
            s: saturation,
            l: lightness,
            a: alpha
        };
    },

    /** @id MochiKit.Color.toColorPart */
    toColorPart: function (num) {
        num = Math.round(num);
        var digits = num.toString(16);
        if (num < 16) {
            return '0' + digits;
        }
        return digits;
    },

    __new__: function () {
        var m = MochiKit.Base;
        /** @id MochiKit.Color.Color.fromRGBString */
        this.Color.fromRGBString = m.bind(
            this.Color._fromColorString, this.Color, "rgb", "fromRGB",
            [1.0/255.0, 1.0/255.0, 1.0/255.0, 1]
        );
        /** @id MochiKit.Color.Color.fromHSLString */
        this.Color.fromHSLString = m.bind(
            this.Color._fromColorString, this.Color, "hsl", "fromHSL",
            [1.0/360.0, 0.01, 0.01, 1]
        );

        var third = 1.0 / 3.0;
        /** @id MochiKit.Color.colors */
        var colors = {
            // NSColor colors plus transparent
            /** @id MochiKit.Color.blackColor */
            black: [0, 0, 0],
            /** @id MochiKit.Color.blueColor */
            blue: [0, 0, 1],
            /** @id MochiKit.Color.brownColor */
            brown: [0.6, 0.4, 0.2],
            /** @id MochiKit.Color.cyanColor */
            cyan: [0, 1, 1],
            /** @id MochiKit.Color.darkGrayColor */
            darkGray: [third, third, third],
            /** @id MochiKit.Color.grayColor */
            gray: [0.5, 0.5, 0.5],
            /** @id MochiKit.Color.greenColor */
            green: [0, 1, 0],
            /** @id MochiKit.Color.lightGrayColor */
            lightGray: [2 * third, 2 * third, 2 * third],
            /** @id MochiKit.Color.magentaColor */
            magenta: [1, 0, 1],
            /** @id MochiKit.Color.orangeColor */
            orange: [1, 0.5, 0],
            /** @id MochiKit.Color.purpleColor */
            purple: [0.5, 0, 0.5],
            /** @id MochiKit.Color.redColor */
            red: [1, 0, 0],
            /** @id MochiKit.Color.transparentColor */
            transparent: [0, 0, 0, 0],
            /** @id MochiKit.Color.whiteColor */
            white: [1, 1, 1],
            /** @id MochiKit.Color.yellowColor */
            yellow: [1, 1, 0]
        };

        for (var k in colors) {
            var name = k + "Color";
            var value = this.Color.fromRGB.apply(this.Color, colors[k]);
            this.Color[name] = m.partial(m.operator.identity, value);
        }

        var isColor = function () {
            for (var i = 0; i < arguments.length; i++) {
                if (!(arguments[i] instanceof MochiKit.Color.Color)) {
                    return false;
                }
            }
            return true;
        };

        var compareColor = function (a, b) {
            return a.compareRGB(b);
        };

        m.nameFunctions(this);

        m.registerComparator(this.Color.NAME, isColor, compareColor);
    }
});

MochiKit.Color.__new__();

// Full table of css3 X11 colors <http://www.w3.org/TR/css3-color/#X11COLORS>

MochiKit.Color.Color._namedColors = {
    aliceblue: "#f0f8ff",
    antiquewhite: "#faebd7",
    aqua: "#00ffff",
    aquamarine: "#7fffd4",
    azure: "#f0ffff",
    beige: "#f5f5dc",
    bisque: "#ffe4c4",
    black: "#000000",
    blanchedalmond: "#ffebcd",
    blue: "#0000ff",
    blueviolet: "#8a2be2",
    brown: "#a52a2a",
    burlywood: "#deb887",
    cadetblue: "#5f9ea0",
    chartreuse: "#7fff00",
    chocolate: "#d2691e",
    coral: "#ff7f50",
    cornflowerblue: "#6495ed",
    cornsilk: "#fff8dc",
    crimson: "#dc143c",
    cyan: "#00ffff",
    darkblue: "#00008b",
    darkcyan: "#008b8b",
    darkgoldenrod: "#b8860b",
    darkgray: "#a9a9a9",
    darkgreen: "#006400",
    darkgrey: "#a9a9a9",
    darkkhaki: "#bdb76b",
    darkmagenta: "#8b008b",
    darkolivegreen: "#556b2f",
    darkorange: "#ff8c00",
    darkorchid: "#9932cc",
    darkred: "#8b0000",
    darksalmon: "#e9967a",
    darkseagreen: "#8fbc8f",
    darkslateblue: "#483d8b",
    darkslategray: "#2f4f4f",
    darkslategrey: "#2f4f4f",
    darkturquoise: "#00ced1",
    darkviolet: "#9400d3",
    deeppink: "#ff1493",
    deepskyblue: "#00bfff",
    dimgray: "#696969",
    dimgrey: "#696969",
    dodgerblue: "#1e90ff",
    firebrick: "#b22222",
    floralwhite: "#fffaf0",
    forestgreen: "#228b22",
    fuchsia: "#ff00ff",
    gainsboro: "#dcdcdc",
    ghostwhite: "#f8f8ff",
    gold: "#ffd700",
    goldenrod: "#daa520",
    gray: "#808080",
    green: "#008000",
    greenyellow: "#adff2f",
    grey: "#808080",
    honeydew: "#f0fff0",
    hotpink: "#ff69b4",
    indianred: "#cd5c5c",
    indigo: "#4b0082",
    ivory: "#fffff0",
    khaki: "#f0e68c",
    lavender: "#e6e6fa",
    lavenderblush: "#fff0f5",
    lawngreen: "#7cfc00",
    lemonchiffon: "#fffacd",
    lightblue: "#add8e6",
    lightcoral: "#f08080",
    lightcyan: "#e0ffff",
    lightgoldenrodyellow: "#fafad2",
    lightgray: "#d3d3d3",
    lightgreen: "#90ee90",
    lightgrey: "#d3d3d3",
    lightpink: "#ffb6c1",
    lightsalmon: "#ffa07a",
    lightseagreen: "#20b2aa",
    lightskyblue: "#87cefa",
    lightslategray: "#778899",
    lightslategrey: "#778899",
    lightsteelblue: "#b0c4de",
    lightyellow: "#ffffe0",
    lime: "#00ff00",
    limegreen: "#32cd32",
    linen: "#faf0e6",
    magenta: "#ff00ff",
    maroon: "#800000",
    mediumaquamarine: "#66cdaa",
    mediumblue: "#0000cd",
    mediumorchid: "#ba55d3",
    mediumpurple: "#9370db",
    mediumseagreen: "#3cb371",
    mediumslateblue: "#7b68ee",
    mediumspringgreen: "#00fa9a",
    mediumturquoise: "#48d1cc",
    mediumvioletred: "#c71585",
    midnightblue: "#191970",
    mintcream: "#f5fffa",
    mistyrose: "#ffe4e1",
    moccasin: "#ffe4b5",
    navajowhite: "#ffdead",
    navy: "#000080",
    oldlace: "#fdf5e6",
    olive: "#808000",
    olivedrab: "#6b8e23",
    orange: "#ffa500",
    orangered: "#ff4500",
    orchid: "#da70d6",
    palegoldenrod: "#eee8aa",
    palegreen: "#98fb98",
    paleturquoise: "#afeeee",
    palevioletred: "#db7093",
    papayawhip: "#ffefd5",
    peachpuff: "#ffdab9",
    peru: "#cd853f",
    pink: "#ffc0cb",
    plum: "#dda0dd",
    powderblue: "#b0e0e6",
    purple: "#800080",
    red: "#ff0000",
    rosybrown: "#bc8f8f",
    royalblue: "#4169e1",
    saddlebrown: "#8b4513",
    salmon: "#fa8072",
    sandybrown: "#f4a460",
    seagreen: "#2e8b57",
    seashell: "#fff5ee",
    sienna: "#a0522d",
    silver: "#c0c0c0",
    skyblue: "#87ceeb",
    slateblue: "#6a5acd",
    slategray: "#708090",
    slategrey: "#708090",
    snow: "#fffafa",
    springgreen: "#00ff7f",
    steelblue: "#4682b4",
    tan: "#d2b48c",
    teal: "#008080",
    thistle: "#d8bfd8",
    tomato: "#ff6347",
    turquoise: "#40e0d0",
    violet: "#ee82ee",
    wheat: "#f5deb3",
    white: "#ffffff",
    whitesmoke: "#f5f5f5",
    yellow: "#ffff00",
    yellowgreen: "#9acd32"
};

MochiKit.Base._exportSymbols(this, MochiKit.Color);
/***

MochiKit.Signal 1.5

See <http://mochikit.com/> for documentation, downloads, license, etc.

(c) 2006 Jonathan Gardner, Beau Hartshorne, Bob Ippolito.  All rights Reserved.

***/

MochiKit.Base._module('Signal', '1.5', ['Base', 'DOM', 'Style']);

MochiKit.Signal._observers = [];

/** @id MochiKit.Signal.Event */
MochiKit.Signal.Event = function (src, e) {
    this._event = e || window.event;
    this._src = src;
};
MochiKit.Signal.Event.__export__ = false;

MochiKit.Base.update(MochiKit.Signal.Event.prototype, {

    __repr__: function () {
        var repr = MochiKit.Base.repr;
        var str = '{event(): ' + repr(this.event()) +
            ', src(): ' + repr(this.src()) +
            ', type(): ' + repr(this.type()) +
            ', target(): ' + repr(this.target());

        if (this.type() &&
            this.type().indexOf('key') === 0 ||
            this.type().indexOf('mouse') === 0 ||
            this.type().indexOf('click') != -1 ||
            this.type() == 'contextmenu') {
            str += ', modifier(): ' + '{alt: ' + repr(this.modifier().alt) +
            ', ctrl: ' + repr(this.modifier().ctrl) +
            ', meta: ' + repr(this.modifier().meta) +
            ', shift: ' + repr(this.modifier().shift) +
            ', any: ' + repr(this.modifier().any) + '}';
        }

        if (this.type() && this.type().indexOf('key') === 0) {
            str += ', key(): {code: ' + repr(this.key().code) +
                ', string: ' + repr(this.key().string) + '}';
        }

        if (this.type() && (
            this.type().indexOf('mouse') === 0 ||
            this.type().indexOf('click') != -1 ||
            this.type() == 'contextmenu')) {

            str += ', mouse(): {page: ' + repr(this.mouse().page) +
                ', client: ' + repr(this.mouse().client);

            if (this.type() != 'mousemove' && this.type() != 'mousewheel') {
                str += ', button: {left: ' + repr(this.mouse().button.left) +
                    ', middle: ' + repr(this.mouse().button.middle) +
                    ', right: ' + repr(this.mouse().button.right) + '}';
            }
            if (this.type() == 'mousewheel') {
                str += ', wheel: ' + repr(this.mouse().wheel);
            }
            str += '}';
        }
        if (this.type() == 'mouseover' || this.type() == 'mouseout' || 
            this.type() == 'mouseenter' || this.type() == 'mouseleave') {
            str += ', relatedTarget(): ' + repr(this.relatedTarget());
        }
        str += '}';
        return str;
    },

     /** @id MochiKit.Signal.Event.prototype.toString */
    toString: function () {
        return this.__repr__();
    },

    /** @id MochiKit.Signal.Event.prototype.src */
    src: function () {
        return this._src;
    },

    /** @id MochiKit.Signal.Event.prototype.event  */
    event: function () {
        return this._event;
    },

    /** @id MochiKit.Signal.Event.prototype.type */
    type: function () {
        if (this._event.type === "DOMMouseScroll") {
            return "mousewheel";
        } else {
            return this._event.type || undefined;
        }
    },

    /** @id MochiKit.Signal.Event.prototype.target */
    target: function () {
        return this._event.target || this._event.srcElement;
    },

    _relatedTarget: null,
    /** @id MochiKit.Signal.Event.prototype.relatedTarget */
    relatedTarget: function () {
        if (this._relatedTarget !== null) {
            return this._relatedTarget;
        }

        var elem = null;
        if (this.type() == 'mouseover' || this.type() == 'mouseenter') {
            elem = (this._event.relatedTarget ||
                this._event.fromElement);
        } else if (this.type() == 'mouseout' || this.type() == 'mouseleave') {
            elem = (this._event.relatedTarget ||
                this._event.toElement);
        }
        try {
            if (elem !== null && elem.nodeType !== null) {
                this._relatedTarget = elem;
                return elem;
            }
        } catch (ignore) {
            // Firefox 3 throws a permission denied error when accessing
            // any property on XUL elements (e.g. scrollbars)...
        }

        return undefined;
    },

    _modifier: null,
    /** @id MochiKit.Signal.Event.prototype.modifier */
    modifier: function () {
        if (this._modifier !== null) {
            return this._modifier;
        }
        var m = {};
        m.alt = this._event.altKey;
        m.ctrl = this._event.ctrlKey;
        m.meta = this._event.metaKey || false; // IE and Opera punt here
        m.shift = this._event.shiftKey;
        m.any = m.alt || m.ctrl || m.shift || m.meta;
        this._modifier = m;
        return m;
    },

    _key: null,
    /** @id MochiKit.Signal.Event.prototype.key */
    key: function () {
        if (this._key !== null) {
            return this._key;
        }
        var k = {};
        if (this.type() && this.type().indexOf('key') === 0) {

            /*

                If you're looking for a special key, look for it in keydown or
                keyup, but never keypress. If you're looking for a Unicode
                chracter, look for it with keypress, but never keyup or
                keydown.

                Notes:

                FF key event behavior:
                key     event   charCode    keyCode
                DOWN    ku,kd   0           40
                DOWN    kp      0           40
                ESC     ku,kd   0           27
                ESC     kp      0           27
                a       ku,kd   0           65
                a       kp      97          0
                shift+a ku,kd   0           65
                shift+a kp      65          0
                1       ku,kd   0           49
                1       kp      49          0
                shift+1 ku,kd   0           0
                shift+1 kp      33          0

                IE key event behavior:
                (IE doesn't fire keypress events for special keys.)
                key     event   keyCode
                DOWN    ku,kd   40
                DOWN    kp      undefined
                ESC     ku,kd   27
                ESC     kp      27
                a       ku,kd   65
                a       kp      97
                shift+a ku,kd   65
                shift+a kp      65
                1       ku,kd   49
                1       kp      49
                shift+1 ku,kd   49
                shift+1 kp      33

                Safari key event behavior:
                (Safari sets charCode and keyCode to something crazy for
                special keys.)
                key     event   charCode    keyCode
                DOWN    ku,kd   63233       40
                DOWN    kp      63233       63233
                ESC     ku,kd   27          27
                ESC     kp      27          27
                a       ku,kd   97          65
                a       kp      97          97
                shift+a ku,kd   65          65
                shift+a kp      65          65
                1       ku,kd   49          49
                1       kp      49          49
                shift+1 ku,kd   33          49
                shift+1 kp      33          33

            */

            /* look for special keys here */
            if (this.type() == 'keydown' || this.type() == 'keyup') {
                k.code = this._event.keyCode;
                k.string = (MochiKit.Signal._specialKeys[k.code] ||
                    'KEY_UNKNOWN');
                this._key = k;
                return k;

            /* look for characters here */
            } else if (this.type() == 'keypress') {

                /*

                    Special key behavior:

                    IE: does not fire keypress events for special keys
                    FF: sets charCode to 0, and sets the correct keyCode
                    Safari: sets keyCode and charCode to something stupid

                */

                k.code = 0;
                k.string = '';

                if (typeof(this._event.charCode) != 'undefined' &&
                    this._event.charCode !== 0 &&
                    !MochiKit.Signal._specialMacKeys[this._event.charCode]) {
                    k.code = this._event.charCode;
                    k.string = String.fromCharCode(k.code);
                } else if (this._event.keyCode &&
                    typeof(this._event.charCode) == 'undefined') { // IE
                    k.code = this._event.keyCode;
                    k.string = String.fromCharCode(k.code);
                }

                this._key = k;
                return k;
            }
        }
        return undefined;
    },

    _mouse: null,
    /** @id MochiKit.Signal.Event.prototype.mouse */
    mouse: function () {
        if (this._mouse !== null) {
            return this._mouse;
        }

        var m = {};
        var e = this._event;

        if (this.type() && (
            this.type().indexOf('mouse') === 0 ||
            this.type().indexOf('click') != -1 ||
            this.type() == 'contextmenu')) {

            m.client = new MochiKit.Style.Coordinates(0, 0);
            if (e.clientX || e.clientY) {
                m.client.x = (!e.clientX || e.clientX < 0) ? 0 : e.clientX;
                m.client.y = (!e.clientY || e.clientY < 0) ? 0 : e.clientY;
            }

            m.page = new MochiKit.Style.Coordinates(0, 0);
            if (e.pageX || e.pageY) {
                m.page.x = (!e.pageX || e.pageX < 0) ? 0 : e.pageX;
                m.page.y = (!e.pageY || e.pageY < 0) ? 0 : e.pageY;
            } else {
                /*

                    The IE shortcut can be off by two. We fix it. See:
                    http://msdn.microsoft.com/workshop/author/dhtml/reference/methods/getboundingclientrect.asp

                    This is similar to the method used in
                    MochiKit.Style.getElementPosition().

                */
                var de = MochiKit.DOM._document.documentElement;
                var b = MochiKit.DOM._document.body;

                m.page.x = e.clientX +
                    (de.scrollLeft || b.scrollLeft) -
                    (de.clientLeft || 0);

                m.page.y = e.clientY +
                    (de.scrollTop || b.scrollTop) -
                    (de.clientTop || 0);

            }
            if (this.type() != 'mousemove' && this.type() != 'mousewheel') {
                m.button = {};
                m.button.left = false;
                m.button.right = false;
                m.button.middle = false;

                /* we could check e.button, but which is more consistent */
                if (e.which) {
                    m.button.left = (e.which == 1);
                    m.button.middle = (e.which == 2);
                    m.button.right = (e.which == 3);

                    /*

                        Mac browsers and right click:

                            - Safari doesn't fire any click events on a right
                              click:
                              http://bugs.webkit.org/show_bug.cgi?id=6595

                            - Firefox fires the event, and sets ctrlKey = true

                            - Opera fires the event, and sets metaKey = true

                        oncontextmenu is fired on right clicks between
                        browsers and across platforms.

                    */

                } else {
                    m.button.left = !!(e.button & 1);
                    m.button.right = !!(e.button & 2);
                    m.button.middle = !!(e.button & 4);
                }
            }
            if (this.type() == 'mousewheel') {
                m.wheel = new MochiKit.Style.Coordinates(0, 0);
                if (e.wheelDeltaX || e.wheelDeltaY) {
                    m.wheel.x = e.wheelDeltaX / -40 || 0;
                    m.wheel.y = e.wheelDeltaY / -40 || 0;
                } else if (e.wheelDelta) {
                    m.wheel.y = e.wheelDelta / -40;
                } else {
                    m.wheel.y = e.detail || 0;
                }
            }
            this._mouse = m;
            return m;
        }
        return undefined;
    },

    /** @id MochiKit.Signal.Event.prototype.stop */
    stop: function () {
        this.stopPropagation();
        this.preventDefault();
    },

    /** @id MochiKit.Signal.Event.prototype.stopPropagation */
    stopPropagation: function () {
        if (this._event.stopPropagation) {
            this._event.stopPropagation();
        } else {
            this._event.cancelBubble = true;
        }
    },

    /** @id MochiKit.Signal.Event.prototype.preventDefault */
    preventDefault: function () {
        if (this._event.preventDefault) {
            this._event.preventDefault();
        } else if (this._confirmUnload === null) {
            this._event.returnValue = false;
        }
    },

    _confirmUnload: null,

    /** @id MochiKit.Signal.Event.prototype.confirmUnload */
    confirmUnload: function (msg) {
        if (this.type() == 'beforeunload') {
            this._confirmUnload = msg;
            this._event.returnValue = msg;
        }
    }
});

/* Safari sets keyCode to these special values onkeypress. */
MochiKit.Signal._specialMacKeys = {
    3: 'KEY_ENTER',
    63289: 'KEY_NUM_PAD_CLEAR',
    63276: 'KEY_PAGE_UP',
    63277: 'KEY_PAGE_DOWN',
    63275: 'KEY_END',
    63273: 'KEY_HOME',
    63234: 'KEY_ARROW_LEFT',
    63232: 'KEY_ARROW_UP',
    63235: 'KEY_ARROW_RIGHT',
    63233: 'KEY_ARROW_DOWN',
    63302: 'KEY_INSERT',
    63272: 'KEY_DELETE'
};

/* for KEY_F1 - KEY_F12 */
(function () {
    var _specialMacKeys = MochiKit.Signal._specialMacKeys;
    for (var i = 63236; i <= 63242; i++) {
        // no F0
        _specialMacKeys[i] = 'KEY_F' + (i - 63236 + 1);
    }
})();

/* Standard keyboard key codes. */
MochiKit.Signal._specialKeys = {
    8: 'KEY_BACKSPACE',
    9: 'KEY_TAB',
    12: 'KEY_NUM_PAD_CLEAR', // weird, for Safari and Mac FF only
    13: 'KEY_ENTER',
    16: 'KEY_SHIFT',
    17: 'KEY_CTRL',
    18: 'KEY_ALT',
    19: 'KEY_PAUSE',
    20: 'KEY_CAPS_LOCK',
    27: 'KEY_ESCAPE',
    32: 'KEY_SPACEBAR',
    33: 'KEY_PAGE_UP',
    34: 'KEY_PAGE_DOWN',
    35: 'KEY_END',
    36: 'KEY_HOME',
    37: 'KEY_ARROW_LEFT',
    38: 'KEY_ARROW_UP',
    39: 'KEY_ARROW_RIGHT',
    40: 'KEY_ARROW_DOWN',
    44: 'KEY_PRINT_SCREEN',
    45: 'KEY_INSERT',
    46: 'KEY_DELETE',
    59: 'KEY_SEMICOLON', // weird, for Safari and IE only
    91: 'KEY_WINDOWS_LEFT',
    92: 'KEY_WINDOWS_RIGHT',
    93: 'KEY_SELECT',
    106: 'KEY_NUM_PAD_ASTERISK',
    107: 'KEY_NUM_PAD_PLUS_SIGN',
    109: 'KEY_NUM_PAD_HYPHEN-MINUS',
    110: 'KEY_NUM_PAD_FULL_STOP',
    111: 'KEY_NUM_PAD_SOLIDUS',
    144: 'KEY_NUM_LOCK',
    145: 'KEY_SCROLL_LOCK',
    186: 'KEY_SEMICOLON',
    187: 'KEY_EQUALS_SIGN',
    188: 'KEY_COMMA',
    189: 'KEY_HYPHEN-MINUS',
    190: 'KEY_FULL_STOP',
    191: 'KEY_SOLIDUS',
    192: 'KEY_GRAVE_ACCENT',
    219: 'KEY_LEFT_SQUARE_BRACKET',
    220: 'KEY_REVERSE_SOLIDUS',
    221: 'KEY_RIGHT_SQUARE_BRACKET',
    222: 'KEY_APOSTROPHE'
    // undefined: 'KEY_UNKNOWN'
};

(function () {
    /* for KEY_0 - KEY_9 */
    var _specialKeys = MochiKit.Signal._specialKeys;
    for (var i = 48; i <= 57; i++) {
        _specialKeys[i] = 'KEY_' + (i - 48);
    }

    /* for KEY_A - KEY_Z */
    for (i = 65; i <= 90; i++) {
        _specialKeys[i] = 'KEY_' + String.fromCharCode(i);
    }

    /* for KEY_NUM_PAD_0 - KEY_NUM_PAD_9 */
    for (i = 96; i <= 105; i++) {
        _specialKeys[i] = 'KEY_NUM_PAD_' + (i - 96);
    }

    /* for KEY_F1 - KEY_F12 */
    for (i = 112; i <= 123; i++) {
        // no F0
        _specialKeys[i] = 'KEY_F' + (i - 112 + 1);
    }
})();

/* Internal object to keep track of created signals. */
MochiKit.Signal.Ident = function (ident) {
    this.source = ident.source;
    this.signal = ident.signal;
    this.listener = ident.listener;
    this.isDOM = ident.isDOM;
    this.objOrFunc = ident.objOrFunc;
    this.funcOrStr = ident.funcOrStr;
    this.connected = ident.connected;
};
MochiKit.Signal.Ident.__export__ = false;
MochiKit.Signal.Ident.prototype = {};

MochiKit.Base.update(MochiKit.Signal, {

    _unloadCache: function () {
        var self = MochiKit.Signal;
        var observers = self._observers;

        for (var i = 0; i < observers.length; i++) {
            if (observers[i].signal !== 'onload' && observers[i].signal !== 'onunload') {
                self._disconnect(observers[i]);
            }
        }
    },

    _listener: function (src, sig, func, obj, isDOM) {
        var self = MochiKit.Signal;
        var E = self.Event;
        if (!isDOM) {
            /* We don't want to re-bind already bound methods */
            if (typeof(func.im_self) == 'undefined') {
                return MochiKit.Base.bindLate(func, obj);
            } else {
                return func;
            }
        }
        obj = obj || src;
        if (typeof(func) == "string") {
            if (sig === 'onload' || sig === 'onunload') {
                return function (nativeEvent) {
                    obj[func].apply(obj, [new E(src, nativeEvent)]);
                    
                    var ident = new MochiKit.Signal.Ident({
                        source: src, signal: sig, objOrFunc: obj, funcOrStr: func});
                    
                    MochiKit.Signal._disconnect(ident);
                };
            } else {
                return function (nativeEvent) {
                    obj[func].apply(obj, [new E(src, nativeEvent)]);
                };
            }
        } else {
            if (sig === 'onload' || sig === 'onunload') {
                return function (nativeEvent) {
                    func.apply(obj, [new E(src, nativeEvent)]);
                    
                    var ident = new MochiKit.Signal.Ident({
                        source: src, signal: sig, objOrFunc: func});
                    
                    MochiKit.Signal._disconnect(ident);
                };
            } else {
                return function (nativeEvent) {
                    func.apply(obj, [new E(src, nativeEvent)]);
                };
            }
        }
    },

    _browserAlreadyHasMouseEnterAndLeave: function () {
        return /MSIE/.test(navigator.userAgent);
    },

    _browserLacksMouseWheelEvent: function () {
        return /Gecko\//.test(navigator.userAgent);
    },

    _mouseEnterListener: function (src, sig, func, obj) {
        var E = MochiKit.Signal.Event;
        return function (nativeEvent) {
            var e = new E(src, nativeEvent);
            try {
                e.relatedTarget().nodeName;
            } catch (err) {
                /* probably hit a permission denied error; possibly one of
                 * firefox's screwy anonymous DIVs inside an input element.
                 * Allow this event to propogate up.
                 */
                return;
            }
            e.stop();
            if (MochiKit.DOM.isChildNode(e.relatedTarget(), src)) {
                /* We've moved between our node and a child. Ignore. */
                return;
            }
            e.type = function () { return sig; };
            if (typeof(func) == "string") {
                return obj[func].apply(obj, [e]);
            } else {
                return func.apply(obj, [e]);
            }
        };
    },

    _getDestPair: function (objOrFunc, funcOrStr) {
        var obj = null;
        var func = null;
        if (typeof(funcOrStr) != 'undefined') {
            obj = objOrFunc;
            func = funcOrStr;
            if (typeof(funcOrStr) == 'string') {
                if (typeof(objOrFunc[funcOrStr]) != "function") {
                    throw new Error("'funcOrStr' must be a function on 'objOrFunc'");
                }
            } else if (typeof(funcOrStr) != 'function') {
                throw new Error("'funcOrStr' must be a function or string");
            }
        } else if (typeof(objOrFunc) != "function") {
            throw new Error("'objOrFunc' must be a function if 'funcOrStr' is not given");
        } else {
            func = objOrFunc;
        }
        return [obj, func];
    },

    /** @id MochiKit.Signal.connect */
    connect: function (src, sig, objOrFunc/* optional */, funcOrStr) {
        if (typeof(src) == "string") {
            src = MochiKit.DOM.getElement(src);
        }
        var self = MochiKit.Signal;

        if (typeof(sig) != 'string') {
            throw new Error("'sig' must be a string");
        }

        var destPair = self._getDestPair(objOrFunc, funcOrStr);
        var obj = destPair[0];
        var func = destPair[1];
        if (typeof(obj) == 'undefined' || obj === null) {
            obj = src;
        }

        var isDOM = !!(src.addEventListener || src.attachEvent);
        if (isDOM && (sig === "onmouseenter" || sig === "onmouseleave")
                  && !self._browserAlreadyHasMouseEnterAndLeave()) {
            var listener = self._mouseEnterListener(src, sig.substr(2), func, obj);
            if (sig === "onmouseenter") {
                sig = "onmouseover";
            } else {
                sig = "onmouseout";
            }
        } else if (isDOM && sig == "onmousewheel" && self._browserLacksMouseWheelEvent()) {
            var listener = self._listener(src, sig, func, obj, isDOM);
            sig = "onDOMMouseScroll";
        } else {
            var listener = self._listener(src, sig, func, obj, isDOM);
        }

        if (src.addEventListener) {
            src.addEventListener(sig.substr(2), listener, false);
        } else if (src.attachEvent) {
            src.attachEvent(sig, listener); // useCapture unsupported
        }

        var ident = new MochiKit.Signal.Ident({
            source: src, 
            signal: sig, 
            listener: listener, 
            isDOM: isDOM, 
            objOrFunc: objOrFunc, 
            funcOrStr: funcOrStr, 
            connected: true
        });
        self._observers.push(ident);

        if (!isDOM && typeof(src.__connect__) == 'function') {
            var args = MochiKit.Base.extend([ident], arguments, 1);
            src.__connect__.apply(src, args);
        }

        return ident;
    },

    _disconnect: function (ident) {
        // already disconnected
        if (!ident.connected) {
            return;
        }
        ident.connected = false;
        var src = ident.source;
        var sig = ident.signal;
        var listener = ident.listener;
        // check isDOM
        if (!ident.isDOM) {
            if (typeof(src.__disconnect__) == 'function') {
                src.__disconnect__(ident, sig, ident.objOrFunc, ident.funcOrStr);
            }
            return;
        }
        if (src.removeEventListener) {
            src.removeEventListener(sig.substr(2), listener, false);
        } else if (src.detachEvent) {
            src.detachEvent(sig, listener); // useCapture unsupported
        } else {
            throw new Error("'src' must be a DOM element");
        }
    },

     /** @id MochiKit.Signal.disconnect */
    disconnect: function (ident) {
        var self = MochiKit.Signal;
        var observers = self._observers;
        var m = MochiKit.Base;
        if (arguments.length > 1) {
            // compatibility API
            var src = arguments[0];
            if (typeof(src) == "string") {
                src = MochiKit.DOM.getElement(src);
            }
            var sig = arguments[1];
            var obj = arguments[2];
            var func = arguments[3];
            for (var i = observers.length - 1; i >= 0; i--) {
                var o = observers[i];
                if (o.source === src && o.signal === sig && o.objOrFunc === obj && o.funcOrStr === func) {
                    self._disconnect(o);
                    if (!self._lock) {
                        observers.splice(i, 1);
                    } else {
                        self._dirty = true;
                    }
                    return true;
                }
            }
        } else {
            var idx = m.findIdentical(observers, ident);
            if (idx >= 0) {
                self._disconnect(ident);
                if (!self._lock) {
                    observers.splice(idx, 1);
                } else {
                    self._dirty = true;
                }
                return true;
            }
        }
        return false;
    },

    /** @id MochiKit.Signal.disconnectAllTo */
    disconnectAllTo: function (objOrFunc, /* optional */funcOrStr) {
        var self = MochiKit.Signal;
        var observers = self._observers;
        var disconnect = self._disconnect;
        var locked = self._lock;
        var dirty = self._dirty;
        if (typeof(funcOrStr) === 'undefined') {
            funcOrStr = null;
        }
        for (var i = observers.length - 1; i >= 0; i--) {
            var ident = observers[i];
            if (ident.objOrFunc === objOrFunc &&
                    (funcOrStr === null || ident.funcOrStr === funcOrStr)) {
                disconnect(ident);
                if (locked) {
                    dirty = true;
                } else {
                    observers.splice(i, 1);
                }
            }
        }
        self._dirty = dirty;
    },

    /** @id MochiKit.Signal.disconnectAll */
    disconnectAll: function (src/* optional */, sig) {
        if (typeof(src) == "string") {
            src = MochiKit.DOM.getElement(src);
        }
        var m = MochiKit.Base;
        var signals = m.flattenArguments(m.extend(null, arguments, 1));
        var self = MochiKit.Signal;
        var disconnect = self._disconnect;
        var observers = self._observers;
        var i, ident;
        var locked = self._lock;
        var dirty = self._dirty;
        if (signals.length === 0) {
            // disconnect all
            for (i = observers.length - 1; i >= 0; i--) {
                ident = observers[i];
                if (ident.source === src) {
                    disconnect(ident);
                    if (!locked) {
                        observers.splice(i, 1);
                    } else {
                        dirty = true;
                    }
                }
            }
        } else {
            var sigs = {};
            for (i = 0; i < signals.length; i++) {
                sigs[signals[i]] = true;
            }
            for (i = observers.length - 1; i >= 0; i--) {
                ident = observers[i];
                if (ident.source === src && ident.signal in sigs) {
                    disconnect(ident);
                    if (!locked) {
                        observers.splice(i, 1);
                    } else {
                        dirty = true;
                    }
                }
            }
        }
        self._dirty = dirty;
    },

    /** @id MochiKit.Signal.signal */
    signal: function (src, sig) {
        var self = MochiKit.Signal;
        var observers = self._observers;
        if (typeof(src) == "string") {
            src = MochiKit.DOM.getElement(src);
        }
        var args = MochiKit.Base.extend(null, arguments, 2);
        var errors = [];
        self._lock = true;
        for (var i = 0; i < observers.length; i++) {
            var ident = observers[i];
            if (ident.source === src && ident.signal === sig &&
                    ident.connected) {
                try {
                    if (ident.isDOM && ident.funcOrStr != null) {
                        var obj = ident.objOrFunc;
                        obj[ident.funcOrStr].apply(obj, args);
                    } else if (ident.isDOM) {
                        ident.objOrFunc.apply(src, args);
                    } else {
                        ident.listener.apply(src, args);
                    }
                } catch (e) {
                    errors.push(e);
                }
            }
        }
        self._lock = false;
        if (self._dirty) {
            self._dirty = false;
            for (var i = observers.length - 1; i >= 0; i--) {
                if (!observers[i].connected) {
                    observers.splice(i, 1);
                }
            }
        }
        if (errors.length == 1) {
            throw errors[0];
        } else if (errors.length > 1) {
            var e = new Error("Multiple errors thrown in handling 'sig', see errors property");
            e.errors = errors;
            throw e;
        }
    }

});

MochiKit.Signal.__new__ = function (win) {
    var m = MochiKit.Base;
    this._document = document;
    this._window = win;
    this._lock = false;
    this._dirty = false;

    try {
        this.connect(window, 'onunload', this._unloadCache);
    } catch (e) {
        // pass: might not be a browser
    }

    m.nameFunctions(this);
};

MochiKit.Signal.__new__(this);

//
// XXX: Internet Explorer blows
//
if (MochiKit.__export__) {
    connect = MochiKit.Signal.connect;
    disconnect = MochiKit.Signal.disconnect;
    disconnectAll = MochiKit.Signal.disconnectAll;
    signal = MochiKit.Signal.signal;
}

MochiKit.Base._exportSymbols(this, MochiKit.Signal);
/***

MochiKit.Position 1.5

See <http://mochikit.com/> for documentation, downloads, license, etc.

(c) 2005-2006 Bob Ippolito and others.  All rights Reserved.

***/

MochiKit.Base._module('Position', '1.5', ['Base', 'DOM', 'Style']);

MochiKit.Base.update(MochiKit.Position, {
    // Don't export from this module
    __export__: false,

    // set to true if needed, warning: firefox performance problems
    // NOT neeeded for page scrolling, only if draggable contained in
    // scrollable elements
    includeScrollOffsets: false,

    /** @id MochiKit.Position.prepare */
    prepare: function () {
        var deltaX =  window.pageXOffset
                   || document.documentElement.scrollLeft
                   || document.body.scrollLeft
                   || 0;
        var deltaY =  window.pageYOffset
                   || document.documentElement.scrollTop
                   || document.body.scrollTop
                   || 0;
        this.windowOffset = new MochiKit.Style.Coordinates(deltaX, deltaY);
    },

    /** @id MochiKit.Position.cumulativeOffset */
    cumulativeOffset: function (element) {
        var valueT = 0;
        var valueL = 0;
        do {
            valueT += element.offsetTop  || 0;
            valueL += element.offsetLeft || 0;
            element = element.offsetParent;
        } while (element);
        return new MochiKit.Style.Coordinates(valueL, valueT);
    },

    /** @id MochiKit.Position.realOffset */
    realOffset: function (element) {
        var valueT = 0;
        var valueL = 0;
        do {
            valueT += element.scrollTop  || 0;
            valueL += element.scrollLeft || 0;
            element = element.parentNode;
        } while (element);
        return new MochiKit.Style.Coordinates(valueL, valueT);
    },

    /** @id MochiKit.Position.within */
    within: function (element, x, y) {
        if (this.includeScrollOffsets) {
            return this.withinIncludingScrolloffsets(element, x, y);
        }
        this.xcomp = x;
        this.ycomp = y;
        this.offset = this.cumulativeOffset(element);
        if (element.style.position == "fixed") {
            this.offset.x += this.windowOffset.x;
            this.offset.y += this.windowOffset.y;
        }

        return (y >= this.offset.y &&
                y <  this.offset.y + element.offsetHeight &&
                x >= this.offset.x &&
                x <  this.offset.x + element.offsetWidth);
    },

    /** @id MochiKit.Position.withinIncludingScrolloffsets */
    withinIncludingScrolloffsets: function (element, x, y) {
        var offsetcache = this.realOffset(element);

        this.xcomp = x + offsetcache.x - this.windowOffset.x;
        this.ycomp = y + offsetcache.y - this.windowOffset.y;
        this.offset = this.cumulativeOffset(element);

        return (this.ycomp >= this.offset.y &&
                this.ycomp <  this.offset.y + element.offsetHeight &&
                this.xcomp >= this.offset.x &&
                this.xcomp <  this.offset.x + element.offsetWidth);
    },

    // within must be called directly before
    /** @id MochiKit.Position.overlap */
    overlap: function (mode, element) {
        if (!mode) {
            return 0;
        }
        if (mode == 'vertical') {
          return ((this.offset.y + element.offsetHeight) - this.ycomp) /
                 element.offsetHeight;
        }
        if (mode == 'horizontal') {
          return ((this.offset.x + element.offsetWidth) - this.xcomp) /
                 element.offsetWidth;
        }
    },

    /** @id MochiKit.Position.absolutize */
    absolutize: function (element) {
        element = MochiKit.DOM.getElement(element);
        if (element.style.position == 'absolute') {
            return;
        }
        MochiKit.Position.prepare();

        var offsets = MochiKit.Position.positionedOffset(element);
        var width = element.clientWidth;
        var height = element.clientHeight;

        var oldStyle = {
            'position': element.style.position,
            'left': offsets.x - parseFloat(element.style.left  || 0),
            'top': offsets.y - parseFloat(element.style.top || 0),
            'width': element.style.width,
            'height': element.style.height
        };

        element.style.position = 'absolute';
        element.style.top = offsets.y + 'px';
        element.style.left = offsets.x + 'px';
        element.style.width = width + 'px';
        element.style.height = height + 'px';

        return oldStyle;
    },

    /** @id MochiKit.Position.positionedOffset */
    positionedOffset: function (element) {
        var valueT = 0, valueL = 0;
        do {
            valueT += element.offsetTop  || 0;
            valueL += element.offsetLeft || 0;
            element = element.offsetParent;
            if (element) {
                var p = MochiKit.Style.getStyle(element, 'position');
                if (p == 'relative' || p == 'absolute') {
                    break;
                }
            }
        } while (element);
        return new MochiKit.Style.Coordinates(valueL, valueT);
    },

    /** @id MochiKit.Position.relativize */
    relativize: function (element, oldPos) {
        element = MochiKit.DOM.getElement(element);
        if (element.style.position == 'relative') {
            return;
        }
        MochiKit.Position.prepare();

        var top = parseFloat(element.style.top || 0) -
                  (oldPos['top'] || 0);
        var left = parseFloat(element.style.left || 0) -
                   (oldPos['left'] || 0);

        element.style.position = oldPos['position'];
        element.style.top = top + 'px';
        element.style.left = left + 'px';
        element.style.width = oldPos['width'];
        element.style.height = oldPos['height'];
    },

    /** @id MochiKit.Position.clone */
    clone: function (source, target) {
        source = MochiKit.DOM.getElement(source);
        target = MochiKit.DOM.getElement(target);
        target.style.position = 'absolute';
        var offsets = this.cumulativeOffset(source);
        target.style.top = offsets.y + 'px';
        target.style.left = offsets.x + 'px';
        target.style.width = source.offsetWidth + 'px';
        target.style.height = source.offsetHeight + 'px';
    },

    /** @id MochiKit.Position.page */
    page: function (forElement) {
        var valueT = 0;
        var valueL = 0;

        var element = forElement;
        do {
            valueT += element.offsetTop  || 0;
            valueL += element.offsetLeft || 0;

            // Safari fix
            if (element.offsetParent == document.body && MochiKit.Style.getStyle(element, 'position') == 'absolute') {
                break;
            }
        } while (element = element.offsetParent);

        element = forElement;
        do {
            valueT -= element.scrollTop  || 0;
            valueL -= element.scrollLeft || 0;
        } while (element = element.parentNode);

        return new MochiKit.Style.Coordinates(valueL, valueT);
    }
});

MochiKit.Position.__new__ = function (win) {
    MochiKit.Base.nameFunctions(this);
};

MochiKit.Position.__new__(this);

MochiKit.Base._exportSymbols(this, MochiKit.Position);
/***

MochiKit.Visual 1.5

See <http://mochikit.com/> for documentation, downloads, license, etc.

(c) 2005 Bob Ippolito and others.  All rights Reserved.

***/

MochiKit.Base._module('Visual', '1.5', ['Base', 'DOM', 'Style', 'Color', 'Position']);

MochiKit.Visual._RoundCorners = function (e, options) {
    e = MochiKit.DOM.getElement(e);
    this._setOptions(options);
    if (this.options.__unstable__wrapElement) {
        e = this._doWrap(e);
    }

    var color = this.options.color;
    var C = MochiKit.Color.Color;
    if (this.options.color === "fromElement") {
        color = C.fromBackground(e);
    } else if (!(color instanceof C)) {
        color = C.fromString(color);
    }
    this.isTransparent = (color.asRGB().a <= 0);

    var bgColor = this.options.bgColor;
    if (this.options.bgColor === "fromParent") {
        bgColor = C.fromBackground(e.offsetParent);
    } else if (!(bgColor instanceof C)) {
        bgColor = C.fromString(bgColor);
    }

    this._roundCornersImpl(e, color, bgColor);
};

MochiKit.Visual._RoundCorners.prototype = {
    _doWrap: function (e) {
        var parent = e.parentNode;
        var doc = MochiKit.DOM.currentDocument();
        if (typeof(doc.defaultView) === "undefined"
            || doc.defaultView === null) {
            return e;
        }
        var style = doc.defaultView.getComputedStyle(e, null);
        if (typeof(style) === "undefined" || style === null) {
            return e;
        }
        var wrapper = MochiKit.DOM.DIV({"style": {
            display: "block",
            // convert padding to margin
            marginTop: style.getPropertyValue("padding-top"),
            marginRight: style.getPropertyValue("padding-right"),
            marginBottom: style.getPropertyValue("padding-bottom"),
            marginLeft: style.getPropertyValue("padding-left"),
            // remove padding so the rounding looks right
            padding: "0px"
            /*
            paddingRight: "0px",
            paddingLeft: "0px"
            */
        }});
        wrapper.innerHTML = e.innerHTML;
        e.innerHTML = "";
        e.appendChild(wrapper);
        return e;
    },

    _roundCornersImpl: function (e, color, bgColor) {
        if (this.options.border) {
            this._renderBorder(e, bgColor);
        }
        if (this._isTopRounded()) {
            this._roundTopCorners(e, color, bgColor);
        }
        if (this._isBottomRounded()) {
            this._roundBottomCorners(e, color, bgColor);
        }
    },

    _renderBorder: function (el, bgColor) {
        var borderValue = "1px solid " + this._borderColor(bgColor);
        var borderL = "border-left: "  + borderValue;
        var borderR = "border-right: " + borderValue;
        var style = "style='" + borderL + ";" + borderR +  "'";
        el.innerHTML = "<div " + style + ">" + el.innerHTML + "</div>";
    },

    _roundTopCorners: function (el, color, bgColor) {
        var corner = this._createCorner(bgColor);
        for (var i = 0; i < this.options.numSlices; i++) {
            corner.appendChild(
                this._createCornerSlice(color, bgColor, i, "top")
            );
        }
        el.style.paddingTop = 0;
        el.insertBefore(corner, el.firstChild);
    },

    _roundBottomCorners: function (el, color, bgColor) {
        var corner = this._createCorner(bgColor);
        for (var i = (this.options.numSlices - 1); i >= 0; i--) {
            corner.appendChild(
                this._createCornerSlice(color, bgColor, i, "bottom")
            );
        }
        el.style.paddingBottom = 0;
        el.appendChild(corner);
    },

    _createCorner: function (bgColor) {
        var dom = MochiKit.DOM;
        return dom.DIV({style: {backgroundColor: bgColor.toString()}});
    },

    _createCornerSlice: function (color, bgColor, n, position) {
        var slice = MochiKit.DOM.SPAN();

        var inStyle = slice.style;
        inStyle.backgroundColor = color.toString();
        inStyle.display = "block";
        inStyle.height = "1px";
        inStyle.overflow = "hidden";
        inStyle.fontSize = "1px";

        var borderColor = this._borderColor(color, bgColor);
        if (this.options.border && n === 0) {
            inStyle.borderTopStyle = "solid";
            inStyle.borderTopWidth = "1px";
            inStyle.borderLeftWidth = "0px";
            inStyle.borderRightWidth = "0px";
            inStyle.borderBottomWidth = "0px";
            // assumes css compliant box model
            inStyle.height = "0px";
            inStyle.borderColor = borderColor.toString();
        } else if (borderColor) {
            inStyle.borderColor = borderColor.toString();
            inStyle.borderStyle = "solid";
            inStyle.borderWidth = "0px 1px";
        }

        if (!this.options.compact && (n == (this.options.numSlices - 1))) {
            inStyle.height = "2px";
        }

        this._setMargin(slice, n, position);
        this._setBorder(slice, n, position);

        return slice;
    },

    _setOptions: function (options) {
        this.options = {
            corners: "all",
            color: "fromElement",
            bgColor: "fromParent",
            blend: true,
            border: false,
            compact: false,
            __unstable__wrapElement: false
        };
        MochiKit.Base.update(this.options, options);

        this.options.numSlices = (this.options.compact ? 2 : 4);
    },

    _whichSideTop: function () {
        var corners = this.options.corners;
        if (this._hasString(corners, "all", "top")) {
            return "";
        }

        var has_tl = (corners.indexOf("tl") != -1);
        var has_tr = (corners.indexOf("tr") != -1);
        if (has_tl && has_tr) {
            return "";
        }
        if (has_tl) {
            return "left";
        }
        if (has_tr) {
            return "right";
        }
        return "";
    },

    _whichSideBottom: function () {
        var corners = this.options.corners;
        if (this._hasString(corners, "all", "bottom")) {
            return "";
        }

        var has_bl = (corners.indexOf('bl') != -1);
        var has_br = (corners.indexOf('br') != -1);
        if (has_bl && has_br) {
            return "";
        }
        if (has_bl) {
            return "left";
        }
        if (has_br) {
            return "right";
        }
        return "";
    },

    _borderColor: function (color, bgColor) {
        if (color == "transparent") {
            return bgColor;
        } else if (this.options.border) {
            return this.options.border;
        } else if (this.options.blend) {
            return bgColor.blendedColor(color);
        }
        return "";
    },


    _setMargin: function (el, n, corners) {
        var marginSize = this._marginSize(n) + "px";
        var whichSide = (
            corners == "top" ? this._whichSideTop() : this._whichSideBottom()
        );
        var style = el.style;

        if (whichSide == "left") {
            style.marginLeft = marginSize;
            style.marginRight = "0px";
        } else if (whichSide == "right") {
            style.marginRight = marginSize;
            style.marginLeft = "0px";
        } else {
            style.marginLeft = marginSize;
            style.marginRight = marginSize;
        }
    },

    _setBorder: function (el, n, corners) {
        var borderSize = this._borderSize(n) + "px";
        var whichSide = (
            corners == "top" ? this._whichSideTop() : this._whichSideBottom()
        );

        var style = el.style;
        if (whichSide == "left") {
            style.borderLeftWidth = borderSize;
            style.borderRightWidth = "0px";
        } else if (whichSide == "right") {
            style.borderRightWidth = borderSize;
            style.borderLeftWidth = "0px";
        } else {
            style.borderLeftWidth = borderSize;
            style.borderRightWidth = borderSize;
        }
    },

    _marginSize: function (n) {
        if (this.isTransparent) {
            return 0;
        }

        var o = this.options;
        if (o.compact && o.blend) {
            var smBlendedMarginSizes = [1, 0];
            return smBlendedMarginSizes[n];
        } else if (o.compact) {
            var compactMarginSizes = [2, 1];
            return compactMarginSizes[n];
        } else if (o.blend) {
            var blendedMarginSizes = [3, 2, 1, 0];
            return blendedMarginSizes[n];
        } else {
            var marginSizes = [5, 3, 2, 1];
            return marginSizes[n];
        }
    },

    _borderSize: function (n) {
        var o = this.options;
        var borderSizes;
        if (o.compact && (o.blend || this.isTransparent)) {
            return 1;
        } else if (o.compact) {
            borderSizes = [1, 0];
        } else if (o.blend) {
            borderSizes = [2, 1, 1, 1];
        } else if (o.border) {
            borderSizes = [0, 2, 0, 0];
        } else if (this.isTransparent) {
            borderSizes = [5, 3, 2, 1];
        } else {
            return 0;
        }
        return borderSizes[n];
    },

    _hasString: function (str) {
        for (var i = 1; i< arguments.length; i++) {
            if (str.indexOf(arguments[i]) != -1) {
                return true;
            }
        }
        return false;
    },

    _isTopRounded: function () {
        return this._hasString(this.options.corners,
            "all", "top", "tl", "tr"
        );
    },

    _isBottomRounded: function () {
        return this._hasString(this.options.corners,
            "all", "bottom", "bl", "br"
        );
    },

    _hasSingleTextChild: function (el) {
        return (el.childNodes.length == 1 && el.childNodes[0].nodeType == 3);
    }
};

/** @id MochiKit.Visual.roundElement */
MochiKit.Visual.roundElement = function (e, options) {
    new MochiKit.Visual._RoundCorners(e, options);
};

/** @id MochiKit.Visual.roundClass */
MochiKit.Visual.roundClass = function (tagName, className, options) {
    var elements = MochiKit.DOM.getElementsByTagAndClassName(
        tagName, className
    );
    for (var i = 0; i < elements.length; i++) {
        MochiKit.Visual.roundElement(elements[i], options);
    }
};

/** @id MochiKit.Visual.tagifyText */
MochiKit.Visual.tagifyText = function (element, /* optional */tagifyStyle) {
    /***

    Change a node text to character in tags.

    @param tagifyStyle: the style to apply to character nodes, default to
    'position: relative'.

    ***/
    tagifyStyle = tagifyStyle || 'position:relative';
    if (/MSIE/.test(navigator.userAgent)) {
        tagifyStyle += ';zoom:1';
    }
    element = MochiKit.DOM.getElement(element);
    var ma = MochiKit.Base.map;
    ma(function (child) {
        if (child.nodeType == 3) {
            ma(function (character) {
                element.insertBefore(
                    MochiKit.DOM.SPAN({style: tagifyStyle},
                        character == ' ' ? String.fromCharCode(160) : character), child);
            }, child.nodeValue.split(''));
            MochiKit.DOM.removeElement(child);
        }
    }, element.childNodes);
};

MochiKit.Visual._forceRerendering = function (element) {
    try {
        element = MochiKit.DOM.getElement(element);
        var n = document.createTextNode(' ');
        element.appendChild(n);
        element.removeChild(n);
    } catch(e) {
    }
};

/** @id MochiKit.Visual.multiple */
MochiKit.Visual.multiple = function (elements, effect, /* optional */options) {
    /***

    Launch the same effect subsequently on given elements.

    ***/
    options = MochiKit.Base.update({
        speed: 0.1, delay: 0.0
    }, options);
    var masterDelay = options.delay;
    var index = 0;
    MochiKit.Base.map(function (innerelement) {
        options.delay = index * options.speed + masterDelay;
        new effect(innerelement, options);
        index += 1;
    }, elements);
};

MochiKit.Visual.PAIRS = {
    'slide': ['slideDown', 'slideUp'],
    'blind': ['blindDown', 'blindUp'],
    'appear': ['appear', 'fade'],
    'size': ['grow', 'shrink']
};

/** @id MochiKit.Visual.toggle */
MochiKit.Visual.toggle = function (element, /* optional */effect, /* optional */options) {
    /***

    Toggle an item between two state depending of its visibility, making
    a effect between these states. Default  effect is 'appear', can be
    'slide' or 'blind'.

    ***/
    element = MochiKit.DOM.getElement(element);
    effect = (effect || 'appear').toLowerCase();
    options = MochiKit.Base.update({
        queue: {position: 'end', scope: (element.id || 'global'), limit: 1}
    }, options);
    var v = MochiKit.Visual;
    v[MochiKit.Style.getStyle(element, 'display') != 'none' ?
      v.PAIRS[effect][1] : v.PAIRS[effect][0]](element, options);
};

/***

Transitions: define functions calculating variations depending of a position.

***/

MochiKit.Visual.Transitions = { __export__: false };

/** @id MochiKit.Visual.Transitions.linear */
MochiKit.Visual.Transitions.linear = function (pos) {
    return pos;
};

/** @id MochiKit.Visual.Transitions.sinoidal */
MochiKit.Visual.Transitions.sinoidal = function (pos) {
    return 0.5 - Math.cos(pos*Math.PI)/2;
};

/** @id MochiKit.Visual.Transitions.reverse */
MochiKit.Visual.Transitions.reverse = function (pos) {
    return 1 - pos;
};

/** @id MochiKit.Visual.Transitions.flicker */
MochiKit.Visual.Transitions.flicker = function (pos) {
    return 0.25 - Math.cos(pos*Math.PI)/4 + Math.random()/2;
};

/** @id MochiKit.Visual.Transitions.wobble */
MochiKit.Visual.Transitions.wobble = function (pos) {
    return 0.5 - Math.cos(9*pos*Math.PI)/2;
};

/** @id MochiKit.Visual.Transitions.pulse */
MochiKit.Visual.Transitions.pulse = function (pos, pulses) {
    if (pulses) {
        pos *= 2 * pulses;
    } else {
        pos *= 10;
    }
    var decimals = pos - Math.floor(pos);
    return (Math.floor(pos) % 2 == 0) ? decimals : 1 - decimals;
};

/** @id MochiKit.Visual.Transitions.parabolic */
MochiKit.Visual.Transitions.parabolic = function (pos) {
   return pos * pos;
};

/** @id MochiKit.Visual.Transitions.spring */
MochiKit.Visual.Transitions.spring = function (pos) {
   return 1 - (Math.cos(pos * 2.5 * Math.PI) * Math.exp(-pos * 6));
};

/** @id MochiKit.Visual.Transitions.none */
MochiKit.Visual.Transitions.none = function (pos) {
    return 0;
};

/** @id MochiKit.Visual.Transitions.full */
MochiKit.Visual.Transitions.full = function (pos) {
    return 1;
};

/***

Core effects

***/

MochiKit.Visual.ScopedQueue = function () {
    var cls = arguments.callee;
    if (!(this instanceof cls)) {
        return new cls();
    }
    this.__init__();
};
MochiKit.Visual.ScopedQueue.__export__ = false;

MochiKit.Base.update(MochiKit.Visual.ScopedQueue.prototype, {
    __init__: function () {
        this.effects = [];
        this.interval = null;
    },

    /** @id MochiKit.Visual.ScopedQueue.prototype.add */
    add: function (effect) {
        var timestamp = new Date().getTime();

        var position = (typeof(effect.options.queue) == 'string') ?
            effect.options.queue : effect.options.queue.position;

        var ma = MochiKit.Base.map;
        switch (position) {
            case 'front':
                // move unstarted effects after this effect
                ma(function (e) {
                    if (e.state == 'idle') {
                        e.startOn += effect.finishOn;
                        e.finishOn += effect.finishOn;
                    }
                }, this.effects);
                break;
            case 'end':
                var finish;
                // start effect after last queued effect has finished
                ma(function (e) {
                    var i = e.finishOn;
                    if (i >= (finish || i)) {
                        finish = i;
                    }
                }, this.effects);
                timestamp = finish || timestamp;
                break;
            case 'break':
                ma(function (e) {
                    e.finalize();
                }, this.effects);
                break;
            case 'replace':
                ma(function (e) {
                    e.cancel();
                }, this.effects);
                break;
        }

        effect.startOn += timestamp;
        effect.finishOn += timestamp;
        if (!effect.options.queue.limit ||
            this.effects.length < effect.options.queue.limit) {
            this.effects.push(effect);
        }

        if (!this.interval) {
            this.interval = this.startLoop(MochiKit.Base.bind(this.loop, this),
                                        40);
        }
    },

    /** @id MochiKit.Visual.ScopedQueue.prototype.startLoop */
    startLoop: function (func, interval) {
        return setInterval(func, interval);
    },

    /** @id MochiKit.Visual.ScopedQueue.prototype.remove */
    remove: function (effect) {
        this.effects = MochiKit.Base.filter(function (e) {
            return e != effect;
        }, this.effects);
        if (!this.effects.length) {
            this.stopLoop(this.interval);
            this.interval = null;
        }
    },

    /** @id MochiKit.Visual.ScopedQueue.prototype.stopLoop */
    stopLoop: function (interval) {
        clearInterval(interval);
    },

    /** @id MochiKit.Visual.ScopedQueue.prototype.loop */
    loop: function () {
        var timePos = new Date().getTime();
        MochiKit.Base.map(function (effect) {
            effect.loop(timePos);
        }, this.effects);
    }
});

MochiKit.Visual.Queues = {
    __export__: false,
    instances: {},
    get: function (queueName) {
        if (typeof(queueName) != 'string') {
            return queueName;
        }

        if (!this.instances[queueName]) {
            this.instances[queueName] = new MochiKit.Visual.ScopedQueue();
        }
        return this.instances[queueName];
    }
};

MochiKit.Visual.Queue = MochiKit.Visual.Queues.get('global');
MochiKit.Visual.Queue.__export__ = false;

MochiKit.Visual.DefaultOptions = {
    __export__: false,
    transition: MochiKit.Visual.Transitions.sinoidal,
    duration: 1.0,  // seconds
    fps: 25.0,  // max. 25fps due to MochiKit.Visual.Queue implementation
    sync: false,  // true for combining
    from: 0.0,
    to: 1.0,
    delay: 0.0,
    queue: 'parallel'
};

MochiKit.Visual.Base = function () {};

MochiKit.Visual.Base.prototype = {
    /***

    Basic class for all Effects. Define a looping mechanism called for each step
    of an effect. Don't instantiate it, only subclass it.

    ***/

    __class__ : MochiKit.Visual.Base,

    /** @id MochiKit.Visual.Base.prototype.start */
    start: function (options) {
        var v = MochiKit.Visual;
        this.options = MochiKit.Base.setdefault(options,
                                                v.DefaultOptions);
        this.currentFrame = 0;
        this.state = 'idle';
        this.startOn = this.options.delay*1000;
        this.finishOn = this.startOn + (this.options.duration*1000);
        this.event('beforeStart');
        if (!this.options.sync) {
            v.Queues.get(typeof(this.options.queue) == 'string' ?
                'global' : this.options.queue.scope).add(this);
        }
    },

    /** @id MochiKit.Visual.Base.prototype.loop */
    loop: function (timePos) {
        if (timePos >= this.startOn) {
            if (timePos >= this.finishOn) {
                return this.finalize();
            }
            var pos = (timePos - this.startOn) / (this.finishOn - this.startOn);
            var frame =
                Math.round(pos * this.options.fps * this.options.duration);
            if (frame > this.currentFrame) {
                this.render(pos);
                this.currentFrame = frame;
            }
        }
    },

    /** @id MochiKit.Visual.Base.prototype.render */
    render: function (pos) {
        if (this.state == 'idle') {
            this.state = 'running';
            this.event('beforeSetup');
            this.setup();
            this.event('afterSetup');
        }
        if (this.state == 'running') {
            var trans = this.options.transition;
            if (typeof(trans) == "string") {
                trans = MochiKit.Visual.Transitions[trans];
            }
            if (typeof(trans) == "function") {
                pos = trans(pos);
            }
            pos *= (this.options.to - this.options.from);
            pos += this.options.from;
            this.event('beforeUpdate');
            this.update(pos);
            this.event('afterUpdate');
        }
    },

    /** @id MochiKit.Visual.Base.prototype.cancel */
    cancel: function () {
        if (!this.options.sync) {
            MochiKit.Visual.Queues.get(typeof(this.options.queue) == 'string' ?
                'global' : this.options.queue.scope).remove(this);
        }
        this.state = 'finished';
    },

    /** @id MochiKit.Visual.Base.prototype.finalize */
    finalize: function () {
        this.render(1.0);
        this.cancel();
        this.event('beforeFinish');
        this.finish();
        this.event('afterFinish');
    },

    setup: function () {
    },

    finish: function () {
    },

    update: function (position) {
    },

    /** @id MochiKit.Visual.Base.prototype.event */
    event: function (eventName) {
        if (this.options[eventName + 'Internal']) {
            this.options[eventName + 'Internal'](this);
        }
        if (this.options[eventName]) {
            this.options[eventName](this);
        }
    },

    /** @id MochiKit.Visual.Base.prototype.repr */
    repr: function () {
        return '[' + this.__class__.NAME + ', options:' +
               MochiKit.Base.repr(this.options) + ']';
    }
};

/** @id MochiKit.Visual.Parallel */
MochiKit.Visual.Parallel = function (effects, options) {
    var cls = arguments.callee;
    if (!(this instanceof cls)) {
        return new cls(effects, options);
    }

    this.__init__(effects, options);
};

MochiKit.Visual.Parallel.prototype = new MochiKit.Visual.Base();

MochiKit.Base.update(MochiKit.Visual.Parallel.prototype, {
    /***

    Run multiple effects at the same time.

    ***/

    __class__ : MochiKit.Visual.Parallel,

    __init__: function (effects, options) {
        this.effects = effects || [];
        this.start(options);
    },

    /** @id MochiKit.Visual.Parallel.prototype.update */
    update: function (position) {
        MochiKit.Base.map(function (effect) {
            effect.render(position);
        }, this.effects);
    },

    /** @id MochiKit.Visual.Parallel.prototype.finish */
    finish: function () {
        MochiKit.Base.map(function (effect) {
            effect.finalize();
        }, this.effects);
    }
});

/** @id MochiKit.Visual.Sequence */
MochiKit.Visual.Sequence = function (effects, options) {
    var cls = arguments.callee;
    if (!(this instanceof cls)) {
        return new cls(effects, options);
    }
    this.__init__(effects, options);
};

MochiKit.Visual.Sequence.prototype = new MochiKit.Visual.Base();

MochiKit.Base.update(MochiKit.Visual.Sequence.prototype, {

    __class__ : MochiKit.Visual.Sequence,

    __init__: function (effects, options) {
        var defs = { transition: MochiKit.Visual.Transitions.linear,
                     duration: 0 };
        this.effects = effects || [];
        MochiKit.Base.map(function (effect) {
            defs.duration += effect.options.duration;
        }, this.effects);
        MochiKit.Base.setdefault(options, defs);
        this.start(options);
    },

    /** @id MochiKit.Visual.Sequence.prototype.update */
    update: function (position) {
        var time = position * this.options.duration;
        for (var i = 0; i < this.effects.length; i++) {
            var effect = this.effects[i];
            if (time <= effect.options.duration) {
                effect.render(time / effect.options.duration);
                break;
            } else {
                time -= effect.options.duration;
            }
        }
    },

    /** @id MochiKit.Visual.Sequence.prototype.finish */
    finish: function () {
        MochiKit.Base.map(function (effect) {
            effect.finalize();
        }, this.effects);
    }
});

/** @id MochiKit.Visual.Opacity */
MochiKit.Visual.Opacity = function (element, options) {
    var cls = arguments.callee;
    if (!(this instanceof cls)) {
        return new cls(element, options);
    }
    this.__init__(element, options);
};

MochiKit.Visual.Opacity.prototype = new MochiKit.Visual.Base();

MochiKit.Base.update(MochiKit.Visual.Opacity.prototype, {
    /***

    Change the opacity of an element.

    @param options: 'from' and 'to' change the starting and ending opacities.
    Must be between 0.0 and 1.0. Default to current opacity and 1.0.

    ***/

    __class__ : MochiKit.Visual.Opacity,

    __init__: function (element, /* optional */options) {
        var b = MochiKit.Base;
        var s = MochiKit.Style;
        this.element = MochiKit.DOM.getElement(element);
        // make this work on IE on elements without 'layout'
        if (this.element.currentStyle &&
            (!this.element.currentStyle.hasLayout)) {
            s.setStyle(this.element, {zoom: 1});
        }
        options = b.update({
            from: s.getStyle(this.element, 'opacity') || 0.0,
            to: 1.0
        }, options);
        this.start(options);
    },

    /** @id MochiKit.Visual.Opacity.prototype.update */
    update: function (position) {
        MochiKit.Style.setStyle(this.element, {'opacity': position});
    }
});

/**  @id MochiKit.Visual.Move.prototype */
MochiKit.Visual.Move = function (element, options) {
    var cls = arguments.callee;
    if (!(this instanceof cls)) {
        return new cls(element, options);
    }
    this.__init__(element, options);
};

MochiKit.Visual.Move.prototype = new MochiKit.Visual.Base();

MochiKit.Base.update(MochiKit.Visual.Move.prototype, {
    /***

    Move an element between its current position to a defined position

    @param options: 'x' and 'y' for final positions, default to 0, 0.

    ***/

    __class__ : MochiKit.Visual.Move,

    __init__: function (element, /* optional */options) {
        this.element = MochiKit.DOM.getElement(element);
        options = MochiKit.Base.update({
            x: 0,
            y: 0,
            mode: 'relative'
        }, options);
        this.start(options);
    },

    /** @id MochiKit.Visual.Move.prototype.setup */
    setup: function () {
        // Bug in Opera: Opera returns the 'real' position of a static element
        // or relative element that does not have top/left explicitly set.
        // ==> Always set top and left for position relative elements in your
        // stylesheets (to 0 if you do not need them)
        MochiKit.Style.makePositioned(this.element);

        var s = this.element.style;
        var originalVisibility = s.visibility;
        var originalDisplay = s.display;
        if (originalDisplay == 'none') {
            s.visibility = 'hidden';
            s.display = '';
        }

        this.originalLeft = parseFloat(MochiKit.Style.getStyle(this.element, 'left') || '0');
        this.originalTop = parseFloat(MochiKit.Style.getStyle(this.element, 'top') || '0');

        if (this.options.mode == 'absolute') {
            // absolute movement, so we need to calc deltaX and deltaY
            this.options.x -= this.originalLeft;
            this.options.y -= this.originalTop;
        }
        if (originalDisplay == 'none') {
            s.visibility = originalVisibility;
            s.display = originalDisplay;
        }
    },

    /** @id MochiKit.Visual.Move.prototype.update */
    update: function (position) {
        MochiKit.Style.setStyle(this.element, {
            left: Math.round(this.options.x * position + this.originalLeft) + 'px',
            top: Math.round(this.options.y * position + this.originalTop) + 'px'
        });
    }
});

/** @id MochiKit.Visual.Scale */
MochiKit.Visual.Scale = function (element, percent, options) {
    var cls = arguments.callee;
    if (!(this instanceof cls)) {
        return new cls(element, percent, options);
    }
    this.__init__(element, percent, options);
};

MochiKit.Visual.Scale.prototype = new MochiKit.Visual.Base();

MochiKit.Base.update(MochiKit.Visual.Scale.prototype, {
    /***

    Change the size of an element.

    @param percent: final_size = percent*original_size

    @param options: several options changing scale behaviour

    ***/

    __class__ : MochiKit.Visual.Scale,

    __init__: function (element, percent, /* optional */options) {
        this.element = MochiKit.DOM.getElement(element);
        options = MochiKit.Base.update({
            scaleX: true,
            scaleY: true,
            scaleContent: true,
            scaleFromCenter: false,
            scaleMode: 'box',  // 'box' or 'contents' or {} with provided values
            scaleFrom: 100.0,
            scaleTo: percent
        }, options);
        this.start(options);
    },

    /** @id MochiKit.Visual.Scale.prototype.setup */
    setup: function () {
        this.restoreAfterFinish = this.options.restoreAfterFinish || false;
        this.elementPositioning = MochiKit.Style.getStyle(this.element,
                                                        'position');

        var ma = MochiKit.Base.map;
        var b = MochiKit.Base.bind;
        this.originalStyle = {};
        ma(b(function (k) {
                this.originalStyle[k] = this.element.style[k];
            }, this), ['top', 'left', 'width', 'height', 'fontSize']);

        this.originalTop = this.element.offsetTop;
        this.originalLeft = this.element.offsetLeft;

        var fontSize = MochiKit.Style.getStyle(this.element,
                                             'font-size') || '100%';
        ma(b(function (fontSizeType) {
            if (fontSize.indexOf(fontSizeType) > 0) {
                this.fontSize = parseFloat(fontSize);
                this.fontSizeType = fontSizeType;
            }
        }, this), ['em', 'px', '%']);

        this.factor = (this.options.scaleTo - this.options.scaleFrom)/100;

        if (/^content/.test(this.options.scaleMode)) {
            this.dims = [this.element.scrollHeight, this.element.scrollWidth];
        } else if (this.options.scaleMode == 'box') {
            this.dims = [this.element.offsetHeight, this.element.offsetWidth];
        } else {
            this.dims = [this.options.scaleMode.originalHeight,
                         this.options.scaleMode.originalWidth];
        }
    },

    /** @id MochiKit.Visual.Scale.prototype.update */
    update: function (position) {
        var currentScale = (this.options.scaleFrom/100.0) +
                           (this.factor * position);
        if (this.options.scaleContent && this.fontSize) {
            MochiKit.Style.setStyle(this.element, {
                fontSize: this.fontSize * currentScale + this.fontSizeType
            });
        }
        this.setDimensions(this.dims[0] * currentScale,
                           this.dims[1] * currentScale);
    },

    /** @id MochiKit.Visual.Scale.prototype.finish */
    finish: function () {
        if (this.restoreAfterFinish) {
            MochiKit.Style.setStyle(this.element, this.originalStyle);
        }
    },

    /** @id MochiKit.Visual.Scale.prototype.setDimensions */
    setDimensions: function (height, width) {
        var d = {};
        var r = Math.round;
        if (/MSIE/.test(navigator.userAgent)) {
            r = Math.ceil;
        }
        if (this.options.scaleX) {
            d.width = r(width) + 'px';
        }
        if (this.options.scaleY) {
            d.height = r(height) + 'px';
        }
        if (this.options.scaleFromCenter) {
            var topd = (height - this.dims[0])/2;
            var leftd = (width - this.dims[1])/2;
            if (this.elementPositioning == 'absolute') {
                if (this.options.scaleY) {
                    d.top = this.originalTop - topd + 'px';
                }
                if (this.options.scaleX) {
                    d.left = this.originalLeft - leftd + 'px';
                }
            } else {
                if (this.options.scaleY) {
                    d.top = -topd + 'px';
                }
                if (this.options.scaleX) {
                    d.left = -leftd + 'px';
                }
            }
        }
        MochiKit.Style.setStyle(this.element, d);
    }
});

/** @id MochiKit.Visual.Highlight */
MochiKit.Visual.Highlight = function (element, options) {
    var cls = arguments.callee;
    if (!(this instanceof cls)) {
        return new cls(element, options);
    }
    this.__init__(element, options);
};

MochiKit.Visual.Highlight.prototype = new MochiKit.Visual.Base();

MochiKit.Base.update(MochiKit.Visual.Highlight.prototype, {
    /***

    Highlight an item of the page.

    @param options: 'startcolor' for choosing highlighting color, default
    to '#ffff99'.

    ***/

    __class__ : MochiKit.Visual.Highlight,

    __init__: function (element, /* optional */options) {
        this.element = MochiKit.DOM.getElement(element);
        options = MochiKit.Base.update({
            startcolor: '#ffff99'
        }, options);
        this.start(options);
    },

    /** @id MochiKit.Visual.Highlight.prototype.setup */
    setup: function () {
        var b = MochiKit.Base;
        var s = MochiKit.Style;
        // Prevent executing on elements not in the layout flow
        if (s.getStyle(this.element, 'display') == 'none') {
            this.cancel();
            return;
        }
        // Disable background image during the effect
        this.oldStyle = {
            backgroundImage: s.getStyle(this.element, 'background-image')
        };
        s.setStyle(this.element, {
            backgroundImage: 'none'
        });

        if (!this.options.endcolor) {
            this.options.endcolor =
                MochiKit.Color.Color.fromBackground(this.element).toHexString();
        }
        if (b.isUndefinedOrNull(this.options.restorecolor)) {
            this.options.restorecolor = s.getStyle(this.element,
                                                   'background-color');
        }
        // init color calculations
        this._base = b.map(b.bind(function (i) {
            return parseInt(
                this.options.startcolor.slice(i*2 + 1, i*2 + 3), 16);
        }, this), [0, 1, 2]);
        this._delta = b.map(b.bind(function (i) {
            return parseInt(this.options.endcolor.slice(i*2 + 1, i*2 + 3), 16)
                - this._base[i];
        }, this), [0, 1, 2]);
    },

    /** @id MochiKit.Visual.Highlight.prototype.update */
    update: function (position) {
        var m = '#';
        MochiKit.Base.map(MochiKit.Base.bind(function (i) {
            m += MochiKit.Color.toColorPart(Math.round(this._base[i] +
                                            this._delta[i]*position));
        }, this), [0, 1, 2]);
        MochiKit.Style.setStyle(this.element, {
            backgroundColor: m
        });
    },

    /** @id MochiKit.Visual.Highlight.prototype.finish */
    finish: function () {
        MochiKit.Style.setStyle(this.element,
            MochiKit.Base.update(this.oldStyle, {
                backgroundColor: this.options.restorecolor
        }));
    }
});

/** @id MochiKit.Visual.ScrollTo */
MochiKit.Visual.ScrollTo = function (element, options) {
    var cls = arguments.callee;
    if (!(this instanceof cls)) {
        return new cls(element, options);
    }
    this.__init__(element, options);
};

MochiKit.Visual.ScrollTo.prototype = new MochiKit.Visual.Base();

MochiKit.Base.update(MochiKit.Visual.ScrollTo.prototype, {
    /***

    Scroll to an element in the page.

    ***/

    __class__ : MochiKit.Visual.ScrollTo,

    __init__: function (element, /* optional */options) {
        this.element = MochiKit.DOM.getElement(element);
        this.start(options);
    },

    /** @id MochiKit.Visual.ScrollTo.prototype.setup */
    setup: function () {
        var p = MochiKit.Position;
        p.prepare();
        var offsets = p.cumulativeOffset(this.element);
        if (this.options.offset) {
            offsets.y += this.options.offset;
        }
        var max;
        if (window.innerHeight) {
            max = window.innerHeight - window.height;
        } else if (document.documentElement &&
                   document.documentElement.clientHeight) {
            max = document.documentElement.clientHeight -
                  document.body.scrollHeight;
        } else if (document.body) {
            max = document.body.clientHeight - document.body.scrollHeight;
        }
        this.scrollStart = p.windowOffset.y;
        this.delta = (offsets.y > max ? max : offsets.y) - this.scrollStart;
    },

    /** @id MochiKit.Visual.ScrollTo.prototype.update */
    update: function (position) {
        var p = MochiKit.Position;
        p.prepare();
        window.scrollTo(p.windowOffset.x, this.scrollStart + (position * this.delta));
    }
});

MochiKit.Visual._CSS_LENGTH = /^(([\+\-]?[0-9\.]+)(em|ex|px|in|cm|mm|pt|pc|\%))|0$/;

MochiKit.Visual.Morph = function (element, options) {
    var cls = arguments.callee;
    if (!(this instanceof cls)) {
        return new cls(element, options);
    }
    this.__init__(element, options);
};

MochiKit.Visual.Morph.prototype = new MochiKit.Visual.Base();

MochiKit.Base.update(MochiKit.Visual.Morph.prototype, {
    /***

    Morph effect: make a transformation from current style to the given style,
    automatically making a transition between the two.

    ***/

    __class__ : MochiKit.Visual.Morph,

    __init__: function (element, /* optional */options) {
        this.element = MochiKit.DOM.getElement(element);
        this.start(options);
    },

    /** @id MochiKit.Visual.Morph.prototype.setup */
    setup: function () {
        var b = MochiKit.Base;
        var style = this.options.style;
        this.styleStart = {};
        this.styleEnd = {};
        this.units = {};
        var value, unit;
        for (var s in style) {
            value = style[s];
            s = b.camelize(s);
            if (MochiKit.Visual._CSS_LENGTH.test(value)) {
                var components = value.match(/^([\+\-]?[0-9\.]+)(.*)$/);
                value = parseFloat(components[1]);
                unit = (components.length == 3) ? components[2] : null;
                this.styleEnd[s] = value;
                this.units[s] = unit;
                value = MochiKit.Style.getStyle(this.element, s);
                components = value.match(/^([\+\-]?[0-9\.]+)(.*)$/);
                value = parseFloat(components[1]);
                this.styleStart[s] = value;
            } else if (/[Cc]olor$/.test(s)) {
                var c = MochiKit.Color.Color;
                value = c.fromString(value);
                if (value) {
                    this.units[s] = "color";
                    this.styleEnd[s] = value.toHexString();
                    value = MochiKit.Style.getStyle(this.element, s);
                    this.styleStart[s] = c.fromString(value).toHexString();

                    this.styleStart[s] = b.map(b.bind(function (i) {
                        return parseInt(
                            this.styleStart[s].slice(i*2 + 1, i*2 + 3), 16);
                    }, this), [0, 1, 2]);
                    this.styleEnd[s] = b.map(b.bind(function (i) {
                        return parseInt(
                            this.styleEnd[s].slice(i*2 + 1, i*2 + 3), 16);
                    }, this), [0, 1, 2]);
                }
            } else {
                // For non-length & non-color properties, we just set the value
                this.element.style[s] = value;
            }
        }
    },

    /** @id MochiKit.Visual.Morph.prototype.update */
    update: function (position) {
        var value;
        for (var s in this.styleStart) {
            if (this.units[s] == "color") {
                var m = '#';
                var start = this.styleStart[s];
                var end = this.styleEnd[s];
                MochiKit.Base.map(MochiKit.Base.bind(function (i) {
                    m += MochiKit.Color.toColorPart(Math.round(start[i] +
                                                    (end[i] - start[i])*position));
                }, this), [0, 1, 2]);
                this.element.style[s] = m;
            } else {
                value = this.styleStart[s] + Math.round((this.styleEnd[s] - this.styleStart[s]) * position * 1000) / 1000 + this.units[s];
                this.element.style[s] = value;
            }
        }
    }
});

/***

Combination effects.

***/

/** @id MochiKit.Visual.fade */
MochiKit.Visual.fade = function (element, /* optional */ options) {
    /***

    Fade a given element: change its opacity and hide it in the end.

    @param options: 'to' and 'from' to change opacity.

    ***/
    var s = MochiKit.Style;
    var oldOpacity = s.getStyle(element, 'opacity');
    options = MochiKit.Base.update({
        from: s.getStyle(element, 'opacity') || 1.0,
        to: 0.0,
        afterFinishInternal: function (effect) {
            if (effect.options.to !== 0) {
                return;
            }
            s.hideElement(effect.element);
            s.setStyle(effect.element, {'opacity': oldOpacity});
        }
    }, options);
    return new MochiKit.Visual.Opacity(element, options);
};

/** @id MochiKit.Visual.appear */
MochiKit.Visual.appear = function (element, /* optional */ options) {
    /***

    Make an element appear.

    @param options: 'to' and 'from' to change opacity.

    ***/
    var s = MochiKit.Style;
    var v = MochiKit.Visual;
    options = MochiKit.Base.update({
        from: (s.getStyle(element, 'display') == 'none' ? 0.0 :
               s.getStyle(element, 'opacity') || 0.0),
        to: 1.0,
        // force Safari to render floated elements properly
        afterFinishInternal: function (effect) {
            v._forceRerendering(effect.element);
        },
        beforeSetupInternal: function (effect) {
            s.setStyle(effect.element, {'opacity': effect.options.from});
            s.showElement(effect.element);
        }
    }, options);
    return new v.Opacity(element, options);
};

/** @id MochiKit.Visual.puff */
MochiKit.Visual.puff = function (element, /* optional */ options) {
    /***

    'Puff' an element: grow it to double size, fading it and make it hidden.

    ***/
    var s = MochiKit.Style;
    var v = MochiKit.Visual;
    element = MochiKit.DOM.getElement(element);
    var elementDimensions = MochiKit.Style.getElementDimensions(element, true);
    var oldStyle = {
        position: s.getStyle(element, 'position'),
        top: element.style.top,
        left: element.style.left,
        width: element.style.width,
        height: element.style.height,
        opacity: s.getStyle(element, 'opacity')
    };
    options = MochiKit.Base.update({
        beforeSetupInternal: function (effect) {
            MochiKit.Position.absolutize(effect.effects[0].element);
        },
        afterFinishInternal: function (effect) {
            s.hideElement(effect.effects[0].element);
            s.setStyle(effect.effects[0].element, oldStyle);
        },
        scaleContent: true,
        scaleFromCenter: true
    }, options);
    return new v.Parallel(
        [new v.Scale(element, 200,
            {sync: true, scaleFromCenter: options.scaleFromCenter,
             scaleMode: {originalHeight: elementDimensions.h,
                         originalWidth: elementDimensions.w},
             scaleContent: options.scaleContent, restoreAfterFinish: true}),
         new v.Opacity(element, {sync: true, to: 0.0 })],
        options);
};

/** @id MochiKit.Visual.blindUp */
MochiKit.Visual.blindUp = function (element, /* optional */ options) {
    /***

    Blind an element up: change its vertical size to 0.

    ***/
    var d = MochiKit.DOM;
    var s = MochiKit.Style;
    element = d.getElement(element);
    var elementDimensions = s.getElementDimensions(element, true);
    var elemClip = s.makeClipping(element);
    options = MochiKit.Base.update({
        scaleContent: false,
        scaleX: false,
        scaleMode: {originalHeight: elementDimensions.h,
                    originalWidth: elementDimensions.w},
        restoreAfterFinish: true,
        afterFinishInternal: function (effect) {
            s.hideElement(effect.element);
            s.undoClipping(effect.element, elemClip);
        }
    }, options);
    return new MochiKit.Visual.Scale(element, 0, options);
};

/** @id MochiKit.Visual.blindDown */
MochiKit.Visual.blindDown = function (element, /* optional */ options) {
    /***

    Blind an element down: restore its vertical size.

    ***/
    var d = MochiKit.DOM;
    var s = MochiKit.Style;
    element = d.getElement(element);
    var elementDimensions = s.getElementDimensions(element, true);
    var elemClip;
    options = MochiKit.Base.update({
        scaleContent: false,
        scaleX: false,
        scaleFrom: 0,
        scaleMode: {originalHeight: elementDimensions.h,
                    originalWidth: elementDimensions.w},
        restoreAfterFinish: true,
        afterSetupInternal: function (effect) {
            elemClip = s.makeClipping(effect.element);
            s.setStyle(effect.element, {height: '0px'});
            s.showElement(effect.element);
        },
        afterFinishInternal: function (effect) {
            s.undoClipping(effect.element, elemClip);
        }
    }, options);
    return new MochiKit.Visual.Scale(element, 100, options);
};

/** @id MochiKit.Visual.switchOff */
MochiKit.Visual.switchOff = function (element, /* optional */ options) {
    /***

    Apply a switch-off-like effect.

    ***/
    var d = MochiKit.DOM;
    var s = MochiKit.Style;
    element = d.getElement(element);
    var elementDimensions = s.getElementDimensions(element, true);
    var oldOpacity = s.getStyle(element, 'opacity');
    var elemClip;
    options = MochiKit.Base.update({
        duration: 0.7,
        restoreAfterFinish: true,
        beforeSetupInternal: function (effect) {
            s.makePositioned(element);
            elemClip = s.makeClipping(element);
        },
        afterFinishInternal: function (effect) {
            s.hideElement(element);
            s.undoClipping(element, elemClip);
            s.undoPositioned(element);
            s.setStyle(element, {'opacity': oldOpacity});
        }
    }, options);
    var v = MochiKit.Visual;
    return new v.Sequence(
        [new v.appear(element,
                      { sync: true, duration: 0.57 * options.duration,
                        from: 0, transition: v.Transitions.flicker }),
         new v.Scale(element, 1,
                     { sync: true, duration: 0.43 * options.duration,
                       scaleFromCenter: true, scaleX: false,
                       scaleMode: {originalHeight: elementDimensions.h,
                                   originalWidth: elementDimensions.w},
                       scaleContent: false, restoreAfterFinish: true })],
        options);
};

/** @id MochiKit.Visual.dropOut */
MochiKit.Visual.dropOut = function (element, /* optional */ options) {
    /***

    Make an element fall and disappear.

    ***/
    var d = MochiKit.DOM;
    var s = MochiKit.Style;
    element = d.getElement(element);
    var oldStyle = {
        top: s.getStyle(element, 'top'),
        left: s.getStyle(element, 'left'),
        opacity: s.getStyle(element, 'opacity')
    };

    options = MochiKit.Base.update({
        duration: 0.5,
        distance: 100,
        beforeSetupInternal: function (effect) {
            s.makePositioned(effect.effects[0].element);
        },
        afterFinishInternal: function (effect) {
            s.hideElement(effect.effects[0].element);
            s.undoPositioned(effect.effects[0].element);
            s.setStyle(effect.effects[0].element, oldStyle);
        }
    }, options);
    var v = MochiKit.Visual;
    return new v.Parallel(
        [new v.Move(element, {x: 0, y: options.distance, sync: true}),
         new v.Opacity(element, {sync: true, to: 0.0})],
        options);
};

/** @id MochiKit.Visual.shake */
MochiKit.Visual.shake = function (element, /* optional */ options) {
    /***

    Move an element from left to right several times.

    ***/
    var d = MochiKit.DOM;
    var v = MochiKit.Visual;
    var s = MochiKit.Style;
    element = d.getElement(element);
    var oldStyle = {
        top: s.getStyle(element, 'top'),
        left: s.getStyle(element, 'left')
    };
    options = MochiKit.Base.update({
        duration: 0.5,
        afterFinishInternal: function (effect) {
            s.undoPositioned(element);
            s.setStyle(element, oldStyle);
        }
    }, options);
    return new v.Sequence(
        [new v.Move(element, { sync: true, duration: 0.1 * options.duration,
                               x: 20, y: 0 }),
         new v.Move(element, { sync: true, duration: 0.2 * options.duration,
                               x: -40, y: 0 }),
         new v.Move(element, { sync: true, duration: 0.2 * options.duration,
                               x: 40, y: 0 }),
         new v.Move(element, { sync: true, duration: 0.2 * options.duration,
                               x: -40, y: 0 }),
         new v.Move(element, { sync: true, duration: 0.2 * options.duration,
                               x: 40, y: 0 }),
         new v.Move(element, { sync: true, duration: 0.1 * options.duration,
                               x: -20, y: 0 })],
        options);
};

/** @id MochiKit.Visual.slideDown */
MochiKit.Visual.slideDown = function (element, /* optional */ options) {
    /***

    Slide an element down.
    It needs to have the content of the element wrapped in a container
    element with fixed height.

    ***/
    var d = MochiKit.DOM;
    var b = MochiKit.Base;
    var s = MochiKit.Style;
    element = d.getElement(element);
    if (!element.firstChild) {
        throw new Error("MochiKit.Visual.slideDown must be used on a element with a child");
    }
    d.removeEmptyTextNodes(element);
    var oldInnerBottom = s.getStyle(element.firstChild, 'bottom') || 0;
    var elementDimensions = s.getElementDimensions(element, true);
    var elemClip;
    options = b.update({
        scaleContent: false,
        scaleX: false,
        scaleFrom: 0,
        scaleMode: {originalHeight: elementDimensions.h,
                    originalWidth: elementDimensions.w},
        restoreAfterFinish: true,
        afterSetupInternal: function (effect) {
            s.makePositioned(effect.element);
            s.makePositioned(effect.element.firstChild);
            if (/Opera/.test(navigator.userAgent)) {
                s.setStyle(effect.element, {top: ''});
            }
            elemClip = s.makeClipping(effect.element);
            s.setStyle(effect.element, {height: '0px'});
            s.showElement(effect.element);
        },
        afterUpdateInternal: function (effect) {
            var elementDimensions = s.getElementDimensions(effect.element, true);
            s.setStyle(effect.element.firstChild,
               {bottom: (effect.dims[0] - elementDimensions.h) + 'px'});
        },
        afterFinishInternal: function (effect) {
            s.undoClipping(effect.element, elemClip);
            // IE will crash if child is undoPositioned first
            if (/MSIE/.test(navigator.userAgent)) {
                s.undoPositioned(effect.element);
                s.undoPositioned(effect.element.firstChild);
            } else {
                s.undoPositioned(effect.element.firstChild);
                s.undoPositioned(effect.element);
            }
            s.setStyle(effect.element.firstChild, {bottom: oldInnerBottom});
        }
    }, options);

    return new MochiKit.Visual.Scale(element, 100, options);
};

/** @id MochiKit.Visual.slideUp */
MochiKit.Visual.slideUp = function (element, /* optional */ options) {
    /***

    Slide an element up.
    It needs to have the content of the element wrapped in a container
    element with fixed height.

    ***/
    var d = MochiKit.DOM;
    var b = MochiKit.Base;
    var s = MochiKit.Style;
    element = d.getElement(element);
    if (!element.firstChild) {
        throw new Error("MochiKit.Visual.slideUp must be used on a element with a child");
    }
    d.removeEmptyTextNodes(element);
    var oldInnerBottom = s.getStyle(element.firstChild, 'bottom');
    var elementDimensions = s.getElementDimensions(element, true);
    var elemClip;
    options = b.update({
        scaleContent: false,
        scaleX: false,
        scaleMode: {originalHeight: elementDimensions.h,
                    originalWidth: elementDimensions.w},
        scaleFrom: 100,
        restoreAfterFinish: true,
        beforeStartInternal: function (effect) {
            s.makePositioned(effect.element);
            s.makePositioned(effect.element.firstChild);
            if (/Opera/.test(navigator.userAgent)) {
                s.setStyle(effect.element, {top: ''});
            }
            elemClip = s.makeClipping(effect.element);
            s.showElement(effect.element);
        },
        afterUpdateInternal: function (effect) {
            var elementDimensions = s.getElementDimensions(effect.element, true);
            s.setStyle(effect.element.firstChild,
                {bottom: (effect.dims[0] - elementDimensions.h) + 'px'});
        },
        afterFinishInternal: function (effect) {
            s.hideElement(effect.element);
            s.undoClipping(effect.element, elemClip);
            s.undoPositioned(effect.element.firstChild);
            s.undoPositioned(effect.element);
            s.setStyle(effect.element.firstChild, {bottom: oldInnerBottom});
        }
    }, options);
    return new MochiKit.Visual.Scale(element, 0, options);
};

// Bug in opera makes the TD containing this element expand for a instance
// after finish
/** @id MochiKit.Visual.squish */
MochiKit.Visual.squish = function (element, /* optional */ options) {
    /***

    Reduce an element and make it disappear.

    ***/
    var d = MochiKit.DOM;
    var b = MochiKit.Base;
    var s = MochiKit.Style;
    var elementDimensions = s.getElementDimensions(element, true);
    var elemClip;
    options = b.update({
        restoreAfterFinish: true,
        scaleMode: {originalHeight: elementDimensions.w,
                    originalWidth: elementDimensions.h},
        beforeSetupInternal: function (effect) {
            elemClip = s.makeClipping(effect.element);
        },
        afterFinishInternal: function (effect) {
            s.hideElement(effect.element);
            s.undoClipping(effect.element, elemClip);
        }
    }, options);

    return new MochiKit.Visual.Scale(element, /Opera/.test(navigator.userAgent) ? 1 : 0, options);
};

/** @id MochiKit.Visual.grow */
MochiKit.Visual.grow = function (element, /* optional */ options) {
    /***

    Grow an element to its original size. Make it zero-sized before
    if necessary.

    ***/
    var d = MochiKit.DOM;
    var v = MochiKit.Visual;
    var s = MochiKit.Style;
    element = d.getElement(element);
    options = MochiKit.Base.update({
        direction: 'center',
        moveTransition: v.Transitions.sinoidal,
        scaleTransition: v.Transitions.sinoidal,
        opacityTransition: v.Transitions.full,
        scaleContent: true,
        scaleFromCenter: false
    }, options);
    var oldStyle = {
        top: element.style.top,
        left: element.style.left,
        height: element.style.height,
        width: element.style.width,
        opacity: s.getStyle(element, 'opacity')
    };
    var dims = s.getElementDimensions(element, true);
    var initialMoveX, initialMoveY;
    var moveX, moveY;

    switch (options.direction) {
        case 'top-left':
            initialMoveX = initialMoveY = moveX = moveY = 0;
            break;
        case 'top-right':
            initialMoveX = dims.w;
            initialMoveY = moveY = 0;
            moveX = -dims.w;
            break;
        case 'bottom-left':
            initialMoveX = moveX = 0;
            initialMoveY = dims.h;
            moveY = -dims.h;
            break;
        case 'bottom-right':
            initialMoveX = dims.w;
            initialMoveY = dims.h;
            moveX = -dims.w;
            moveY = -dims.h;
            break;
        case 'center':
            initialMoveX = dims.w / 2;
            initialMoveY = dims.h / 2;
            moveX = -dims.w / 2;
            moveY = -dims.h / 2;
            break;
    }

    var optionsParallel = MochiKit.Base.update({
        beforeSetupInternal: function (effect) {
            s.setStyle(effect.effects[0].element, {height: '0px'});
            s.showElement(effect.effects[0].element);
        },
        afterFinishInternal: function (effect) {
            s.undoClipping(effect.effects[0].element);
            s.undoPositioned(effect.effects[0].element);
            s.setStyle(effect.effects[0].element, oldStyle);
        }
    }, options);

    return new v.Move(element, {
        x: initialMoveX,
        y: initialMoveY,
        duration: 0.01,
        beforeSetupInternal: function (effect) {
            s.hideElement(effect.element);
            s.makeClipping(effect.element);
            s.makePositioned(effect.element);
        },
        afterFinishInternal: function (effect) {
            new v.Parallel(
                [new v.Opacity(effect.element, {
                    sync: true, to: 1.0, from: 0.0,
                    transition: options.opacityTransition
                 }),
                 new v.Move(effect.element, {
                     x: moveX, y: moveY, sync: true,
                     transition: options.moveTransition
                 }),
                 new v.Scale(effect.element, 100, {
                        scaleMode: {originalHeight: dims.h,
                                    originalWidth: dims.w},
                        sync: true,
                        scaleFrom: /Opera/.test(navigator.userAgent) ? 1 : 0,
                        transition: options.scaleTransition,
                        scaleContent: options.scaleContent,
                        scaleFromCenter: options.scaleFromCenter,
                        restoreAfterFinish: true
                })
                ], optionsParallel
            );
        }
    });
};

/** @id MochiKit.Visual.shrink */
MochiKit.Visual.shrink = function (element, /* optional */ options) {
    /***

    Shrink an element and make it disappear.

    ***/
    var d = MochiKit.DOM;
    var v = MochiKit.Visual;
    var s = MochiKit.Style;
    element = d.getElement(element);
    options = MochiKit.Base.update({
        direction: 'center',
        moveTransition: v.Transitions.sinoidal,
        scaleTransition: v.Transitions.sinoidal,
        opacityTransition: v.Transitions.none,
        scaleContent: true,
        scaleFromCenter: false
    }, options);
    var oldStyle = {
        top: element.style.top,
        left: element.style.left,
        height: element.style.height,
        width: element.style.width,
        opacity: s.getStyle(element, 'opacity')
    };

    var dims = s.getElementDimensions(element, true);
    var moveX, moveY;

    switch (options.direction) {
        case 'top-left':
            moveX = moveY = 0;
            break;
        case 'top-right':
            moveX = dims.w;
            moveY = 0;
            break;
        case 'bottom-left':
            moveX = 0;
            moveY = dims.h;
            break;
        case 'bottom-right':
            moveX = dims.w;
            moveY = dims.h;
            break;
        case 'center':
            moveX = dims.w / 2;
            moveY = dims.h / 2;
            break;
    }
    var elemClip;

    var optionsParallel = MochiKit.Base.update({
        beforeStartInternal: function (effect) {
            s.makePositioned(effect.effects[0].element);
            elemClip = s.makeClipping(effect.effects[0].element);
        },
        afterFinishInternal: function (effect) {
            s.hideElement(effect.effects[0].element);
            s.undoClipping(effect.effects[0].element, elemClip);
            s.undoPositioned(effect.effects[0].element);
            s.setStyle(effect.effects[0].element, oldStyle);
        }
    }, options);

    return new v.Parallel(
        [new v.Opacity(element, {
            sync: true, to: 0.0, from: 1.0,
            transition: options.opacityTransition
         }),
         new v.Scale(element, /Opera/.test(navigator.userAgent) ? 1 : 0, {
             scaleMode: {originalHeight: dims.h, originalWidth: dims.w},
             sync: true, transition: options.scaleTransition,
             scaleContent: options.scaleContent,
             scaleFromCenter: options.scaleFromCenter,
             restoreAfterFinish: true
         }),
         new v.Move(element, {
             x: moveX, y: moveY, sync: true, transition: options.moveTransition
         })
        ], optionsParallel
    );
};

/** @id MochiKit.Visual.pulsate */
MochiKit.Visual.pulsate = function (element, /* optional */ options) {
    /***

    Pulse an element between appear/fade.

    ***/
    var d = MochiKit.DOM;
    var v = MochiKit.Visual;
    var b = MochiKit.Base;
    var oldOpacity = MochiKit.Style.getStyle(element, 'opacity');
    options = b.update({
        duration: 3.0,
        from: 0,
        afterFinishInternal: function (effect) {
            MochiKit.Style.setStyle(effect.element, {'opacity': oldOpacity});
        }
    }, options);
    var transition = options.transition || v.Transitions.sinoidal;
    options.transition = function (pos) {
        return transition(1 - v.Transitions.pulse(pos, options.pulses));
    };
    return new v.Opacity(element, options);
};

/** @id MochiKit.Visual.fold */
MochiKit.Visual.fold = function (element, /* optional */ options) {
    /***

    Fold an element, first vertically, then horizontally.

    ***/
    var d = MochiKit.DOM;
    var v = MochiKit.Visual;
    var s = MochiKit.Style;
    element = d.getElement(element);
    var elementDimensions = s.getElementDimensions(element, true);
    var oldStyle = {
        top: element.style.top,
        left: element.style.left,
        width: element.style.width,
        height: element.style.height
    };
    var elemClip = s.makeClipping(element);
    options = MochiKit.Base.update({
        scaleContent: false,
        scaleX: false,
        scaleMode: {originalHeight: elementDimensions.h,
                    originalWidth: elementDimensions.w},
        afterFinishInternal: function (effect) {
            new v.Scale(element, 1, {
                scaleContent: false,
                scaleY: false,
                scaleMode: {originalHeight: elementDimensions.h,
                            originalWidth: elementDimensions.w},
                afterFinishInternal: function (effect) {
                    s.hideElement(effect.element);
                    s.undoClipping(effect.element, elemClip);
                    s.setStyle(effect.element, oldStyle);
                }
            });
        }
    }, options);
    return new v.Scale(element, 5, options);
};


MochiKit.Base.nameFunctions(MochiKit.Visual);
MochiKit.Base._exportSymbols(this, MochiKit.Visual);
/***
MochiKit.DragAndDrop 1.5

See <http://mochikit.com/> for documentation, downloads, license, etc.

Copyright (c) 2005 Thomas Fuchs (http://script.aculo.us, http://mir.aculo.us)
    Mochi-ized By Thomas Herve (_firstname_@nimail.org)

***/

MochiKit.Base._module('DragAndDrop', '1.5', ['Base', 'Iter', 'DOM', 'Signal', 'Visual', 'Position']);

MochiKit.DragAndDrop.Droppables = {
    /***

    Manage all droppables. Shouldn't be used, use the Droppable object instead.

    ***/
    drops: [],

    remove: function (element) {
        this.drops = MochiKit.Base.filter(function (d) {
            return d.element != MochiKit.DOM.getElement(element);
        }, this.drops);
    },

    register: function (drop) {
        this.drops.push(drop);
    },

    unregister: function (drop) {
        this.drops = MochiKit.Base.filter(function (d) {
            return d != drop;
        }, this.drops);
    },

    prepare: function (element) {
        MochiKit.Base.map(function (drop) {
            if (drop.isAccepted(element)) {
                if (drop.options.activeclass) {
                    MochiKit.DOM.addElementClass(drop.element,
                                                 drop.options.activeclass);
                }
                drop.options.onactive(drop.element, element);
            }
        }, this.drops);
    },

    findDeepestChild: function (drops) {
        var deepest = drops[0];

        for (var i = 1; i < drops.length; ++i) {
            if (MochiKit.DOM.isChildNode(drops[i].element, deepest.element)) {
                deepest = drops[i];
            }
        }
        return deepest;
    },

    show: function (point, element) {
        if (!this.drops.length) {
            return;
        }
        var affected = [];

        if (this.last_active) {
            this.last_active.deactivate();
        }
        MochiKit.Iter.forEach(this.drops, function (drop) {
            if (drop.isAffected(point, element)) {
                affected.push(drop);
            }
        });
        if (affected.length > 0) {
            var drop = this.findDeepestChild(affected);
            MochiKit.Position.within(drop.element, point.page.x, point.page.y);
            drop.options.onhover(element, drop.element,
                MochiKit.Position.overlap(drop.options.overlap, drop.element));
            drop.activate();
        }
    },

    fire: function (event, element) {
        if (!this.last_active) {
            return;
        }
        MochiKit.Position.prepare();

        if (this.last_active.isAffected(event.mouse(), element)) {
            this.last_active.options.ondrop(element,
               this.last_active.element, event);
        }
    },

    reset: function (element) {
        MochiKit.Base.map(function (drop) {
            if (drop.options.activeclass) {
                MochiKit.DOM.removeElementClass(drop.element,
                                                drop.options.activeclass);
            }
            drop.options.ondesactive(drop.element, element);
        }, this.drops);
        if (this.last_active) {
            this.last_active.deactivate();
        }
    }
};

/** @id MochiKit.DragAndDrop.Droppable */
MochiKit.DragAndDrop.Droppable = function (element, options) {
    var cls = arguments.callee;
    if (!(this instanceof cls)) {
        return new cls(element, options);
    }
    this.__init__(element, options);
};

MochiKit.DragAndDrop.Droppable.prototype = {
    /***

    A droppable object. Simple use is to create giving an element:

        new MochiKit.DragAndDrop.Droppable('myelement');

    Generally you'll want to define the 'ondrop' function and maybe the
    'accept' option to filter draggables.

    ***/
    __class__: MochiKit.DragAndDrop.Droppable,

    __init__: function (element, /* optional */options) {
        var d = MochiKit.DOM;
        var b = MochiKit.Base;
        this.element = d.getElement(element);
        this.options = b.update({

            /** @id MochiKit.DragAndDrop.greedy */
            greedy: true,

            /** @id MochiKit.DragAndDrop.hoverclass */
            hoverclass: null,

            /** @id MochiKit.DragAndDrop.activeclass */
            activeclass: null,

            /** @id MochiKit.DragAndDrop.hoverfunc */
            hoverfunc: b.noop,

            /** @id MochiKit.DragAndDrop.accept */
            accept: null,

            /** @id MochiKit.DragAndDrop.onactive */
            onactive: b.noop,

            /** @id MochiKit.DragAndDrop.ondesactive */
            ondesactive: b.noop,

            /** @id MochiKit.DragAndDrop.onhover */
            onhover: b.noop,

            /** @id MochiKit.DragAndDrop.ondrop */
            ondrop: b.noop,

            /** @id MochiKit.DragAndDrop.containment */
            containment: [],
            tree: false
        }, options);

        // cache containers
        this.options._containers = [];
        b.map(MochiKit.Base.bind(function (c) {
            this.options._containers.push(d.getElement(c));
        }, this), this.options.containment);

        MochiKit.Style.makePositioned(this.element); // fix IE

        MochiKit.DragAndDrop.Droppables.register(this);
    },

    /** @id MochiKit.DragAndDrop.isContained */
    isContained: function (element) {
        if (this.options._containers.length) {
            var containmentNode;
            if (this.options.tree) {
                containmentNode = element.treeNode;
            } else {
                containmentNode = element.parentNode;
            }
            return MochiKit.Iter.some(this.options._containers, function (c) {
                return containmentNode == c;
            });
        } else {
            return true;
        }
    },

    /** @id MochiKit.DragAndDrop.isAccepted */
    isAccepted: function (element) {
        return ((!this.options.accept) || MochiKit.Iter.some(
          this.options.accept, function (c) {
            return MochiKit.DOM.hasElementClass(element, c);
        }));
    },

    /** @id MochiKit.DragAndDrop.isAffected */
    isAffected: function (point, element) {
        return ((this.element != element) &&
                this.isContained(element) &&
                this.isAccepted(element) &&
                MochiKit.Position.within(this.element, point.page.x,
                                                       point.page.y));
    },

    /** @id MochiKit.DragAndDrop.deactivate */
    deactivate: function () {
        /***

        A droppable is deactivate when a draggable has been over it and left.

        ***/
        if (this.options.hoverclass) {
            MochiKit.DOM.removeElementClass(this.element,
                                            this.options.hoverclass);
        }
        this.options.hoverfunc(this.element, false);
        MochiKit.DragAndDrop.Droppables.last_active = null;
    },

    /** @id MochiKit.DragAndDrop.activate */
    activate: function () {
        /***

        A droppable is active when a draggable is over it.

        ***/
        if (this.options.hoverclass) {
            MochiKit.DOM.addElementClass(this.element, this.options.hoverclass);
        }
        this.options.hoverfunc(this.element, true);
        MochiKit.DragAndDrop.Droppables.last_active = this;
    },

    /** @id MochiKit.DragAndDrop.destroy */
    destroy: function () {
        /***

        Delete this droppable.

        ***/
        MochiKit.DragAndDrop.Droppables.unregister(this);
    },

    /** @id MochiKit.DragAndDrop.repr */
    repr: function () {
        return '[' + this.__class__.NAME + ", options:" + MochiKit.Base.repr(this.options) + "]";
    }
};

MochiKit.DragAndDrop.Draggables = {
    /***

    Manage draggables elements. Not intended to direct use.

    ***/
    drags: [],

    register: function (draggable) {
        if (this.drags.length === 0) {
            var conn = MochiKit.Signal.connect;
            this.eventMouseUp = conn(document, 'onmouseup', this, this.endDrag);
            this.eventMouseMove = conn(document, 'onmousemove', this,
                                       this.updateDrag);
            this.eventKeypress = conn(document, 'onkeypress', this,
                                      this.keyPress);
        }
        this.drags.push(draggable);
    },

    unregister: function (draggable) {
        this.drags = MochiKit.Base.filter(function (d) {
            return d != draggable;
        }, this.drags);
        if (this.drags.length === 0) {
            var disc = MochiKit.Signal.disconnect;
            disc(this.eventMouseUp);
            disc(this.eventMouseMove);
            disc(this.eventKeypress);
        }
    },

    activate: function (draggable) {
        // allows keypress events if window is not currently focused
        // fails for Safari
        window.focus();
        this.activeDraggable = draggable;
    },

    deactivate: function () {
        this.activeDraggable = null;
    },

    updateDrag: function (event) {
        if (!this.activeDraggable) {
            return;
        }
        var pointer = event.mouse();
        // Mozilla-based browsers fire successive mousemove events with
        // the same coordinates, prevent needless redrawing (moz bug?)
        if (this._lastPointer && (MochiKit.Base.repr(this._lastPointer.page) ==
                                  MochiKit.Base.repr(pointer.page))) {
            return;
        }
        this._lastPointer = pointer;
        this.activeDraggable.updateDrag(event, pointer);
    },

    endDrag: function (event) {
        if (!this.activeDraggable) {
            return;
        }
        this._lastPointer = null;
        this.activeDraggable.endDrag(event);
        this.activeDraggable = null;
    },

    keyPress: function (event) {
        if (this.activeDraggable) {
            this.activeDraggable.keyPress(event);
        }
    },

    notify: function (eventName, draggable, event) {
        MochiKit.Signal.signal(this, eventName, draggable, event);
    }
};

/** @id MochiKit.DragAndDrop.Draggable */
MochiKit.DragAndDrop.Draggable = function (element, options) {
    var cls = arguments.callee;
    if (!(this instanceof cls)) {
        return new cls(element, options);
    }
    this.__init__(element, options);
};

MochiKit.DragAndDrop.Draggable.prototype = {
    /***

    A draggable object. Simple instantiate :

        new MochiKit.DragAndDrop.Draggable('myelement');

    ***/
    __class__ : MochiKit.DragAndDrop.Draggable,

    __init__: function (element, /* optional */options) {
        var v = MochiKit.Visual;
        var b = MochiKit.Base;
        options = b.update({

            /** @id MochiKit.DragAndDrop.handle */
            handle: false,

            /** @id MochiKit.DragAndDrop.starteffect */
            starteffect: function (innerelement) {
                this._savedOpacity = MochiKit.Style.getStyle(innerelement, 'opacity') || 1.0;
                new v.Opacity(innerelement, {duration:0.2, from:this._savedOpacity, to:0.7});
            },
            /** @id MochiKit.DragAndDrop.reverteffect */
            reverteffect: function (innerelement, top_offset, left_offset) {
                var dur = Math.sqrt(Math.abs(top_offset^2) +
                          Math.abs(left_offset^2))*0.02;
                return new v.Move(innerelement,
                            {x: -left_offset, y: -top_offset, duration: dur});
            },

            /** @id MochiKit.DragAndDrop.endeffect */
            endeffect: function (innerelement) {
                new v.Opacity(innerelement, {duration:0.2, from:0.7, to:this._savedOpacity});
            },

            /** @id MochiKit.DragAndDrop.onchange */
            onchange: b.noop,

            /** @id MochiKit.DragAndDrop.zindex */
            zindex: 1000,

            /** @id MochiKit.DragAndDrop.revert */
            revert: false,

            /** @id MochiKit.DragAndDrop.scroll */
            scroll: false,

            /** @id MochiKit.DragAndDrop.scrollSensitivity */
            scrollSensitivity: 20,

            /** @id MochiKit.DragAndDrop.scrollSpeed */
            scrollSpeed: 15,
            // false, or xy or [x, y] or function (x, y){return [x, y];}

            /** @id MochiKit.DragAndDrop.snap */
            snap: false
        }, options);

        var d = MochiKit.DOM;
        this.element = d.getElement(element);

        if (options.handle && (typeof(options.handle) == 'string')) {
            this.handle = d.getFirstElementByTagAndClassName(null,
                                       options.handle, this.element);
        }
        if (!this.handle) {
            this.handle = d.getElement(options.handle);
        }
        if (!this.handle) {
            this.handle = this.element;
        }

        if (options.scroll && !options.scroll.scrollTo && !options.scroll.outerHTML) {
            options.scroll = d.getElement(options.scroll);
            this._isScrollChild = MochiKit.DOM.isChildNode(this.element, options.scroll);
        }

        MochiKit.Style.makePositioned(this.element);  // fix IE

        this.delta = this.currentDelta();
        this.options = options;
        this.dragging = false;

        this.eventMouseDown = MochiKit.Signal.connect(this.handle,
                              'onmousedown', this, this.initDrag);
        MochiKit.DragAndDrop.Draggables.register(this);
    },

    /** @id MochiKit.DragAndDrop.destroy */
    destroy: function () {
        MochiKit.Signal.disconnect(this.eventMouseDown);
        MochiKit.DragAndDrop.Draggables.unregister(this);
    },

    /** @id MochiKit.DragAndDrop.currentDelta */
    currentDelta: function () {
        var s = MochiKit.Style.getStyle;
        return [
          parseInt(s(this.element, 'left') || '0'),
          parseInt(s(this.element, 'top') || '0')];
    },

    /** @id MochiKit.DragAndDrop.initDrag */
    initDrag: function (event) {
        if (!event.mouse().button.left) {
            return;
        }
        // abort on form elements, fixes a Firefox issue
        var src = event.target();
        var tagName = (src.tagName || '').toUpperCase();
        if (tagName === 'INPUT' || tagName === 'SELECT' ||
            tagName === 'OPTION' || tagName === 'BUTTON' ||
            tagName === 'TEXTAREA') {
            return;
        }

        if (this._revert) {
            this._revert.cancel();
            this._revert = null;
        }

        var pointer = event.mouse();
        var pos = MochiKit.Position.cumulativeOffset(this.element);
        this.offset = [pointer.page.x - pos.x, pointer.page.y - pos.y];

        MochiKit.DragAndDrop.Draggables.activate(this);
        event.stop();
    },

    /** @id MochiKit.DragAndDrop.startDrag */
    startDrag: function (event) {
        this.dragging = true;
        if (this.options.selectclass) {
            MochiKit.DOM.addElementClass(this.element,
                                         this.options.selectclass);
        }
        if (this.options.zindex) {
            this.originalZ = parseInt(MochiKit.Style.getStyle(this.element,
                                      'z-index') || '0');
            this.element.style.zIndex = this.options.zindex;
        }

        if (this.options.ghosting) {
            this._clone = this.element.cloneNode(true);
            this.ghostPosition = MochiKit.Position.absolutize(this.element);
            this.element.parentNode.insertBefore(this._clone, this.element);
        }

        if (this.options.scroll) {
            if (this.options.scroll == window) {
                var where = this._getWindowScroll(this.options.scroll);
                this.originalScrollLeft = where.left;
                this.originalScrollTop = where.top;
            } else {
                this.originalScrollLeft = this.options.scroll.scrollLeft;
                this.originalScrollTop = this.options.scroll.scrollTop;
            }
        }

        MochiKit.DragAndDrop.Droppables.prepare(this.element);
        MochiKit.DragAndDrop.Draggables.notify('start', this, event);
        if (this.options.starteffect) {
            this.options.starteffect(this.element);
        }
    },

    /** @id MochiKit.DragAndDrop.updateDrag */
    updateDrag: function (event, pointer) {
        if (!this.dragging) {
            this.startDrag(event);
        }
        MochiKit.Position.prepare();
        MochiKit.DragAndDrop.Droppables.show(pointer, this.element);
        MochiKit.DragAndDrop.Draggables.notify('drag', this, event);
        this.draw(pointer);
        this.options.onchange(this);

        if (this.options.scroll) {
            this.stopScrolling();
            var p, q;
            if (this.options.scroll == window) {
                var s = this._getWindowScroll(this.options.scroll);
                p = new MochiKit.Style.Coordinates(s.left, s.top);
                q = new MochiKit.Style.Coordinates(s.left + s.width,
                                                   s.top + s.height);
            } else {
                p = MochiKit.Position.page(this.options.scroll);
                p.x += this.options.scroll.scrollLeft;
                p.y += this.options.scroll.scrollTop;
                p.x += (window.pageXOffset || document.documentElement.scrollLeft || document.body.scrollLeft || 0);
                p.y += (window.pageYOffset || document.documentElement.scrollTop || document.body.scrollTop || 0);
                q = new MochiKit.Style.Coordinates(p.x + this.options.scroll.offsetWidth,
                                                   p.y + this.options.scroll.offsetHeight);
            }
            var speed = [0, 0];
            if (pointer.page.x > (q.x - this.options.scrollSensitivity)) {
                speed[0] = pointer.page.x - (q.x - this.options.scrollSensitivity);
            } else if (pointer.page.x < (p.x + this.options.scrollSensitivity)) {
                speed[0] = pointer.page.x - (p.x + this.options.scrollSensitivity);
            }
            if (pointer.page.y > (q.y - this.options.scrollSensitivity)) {
                speed[1] = pointer.page.y - (q.y - this.options.scrollSensitivity);
            } else if (pointer.page.y < (p.y + this.options.scrollSensitivity)) {
                speed[1] = pointer.page.y - (p.y + this.options.scrollSensitivity);
            }
            this.startScrolling(speed);
        }

        // fix AppleWebKit rendering
        if (/AppleWebKit/.test(navigator.appVersion)) {
            window.scrollBy(0, 0);
        }
        event.stop();
    },

    /** @id MochiKit.DragAndDrop.finishDrag */
    finishDrag: function (event, success) {
        var dr = MochiKit.DragAndDrop;
        this.dragging = false;
        if (this.options.selectclass) {
            MochiKit.DOM.removeElementClass(this.element,
                                            this.options.selectclass);
        }

        if (this.options.ghosting) {
            // XXX: from a user point of view, it would be better to remove
            // the node only *after* the MochiKit.Visual.Move end when used
            // with revert.
            MochiKit.Position.relativize(this.element, this.ghostPosition);
            MochiKit.DOM.removeElement(this._clone);
            this._clone = null;
        }

        if (success) {
            dr.Droppables.fire(event, this.element);
        }
        dr.Draggables.notify('end', this, event);

        var revert = this.options.revert;
        if (revert && typeof(revert) == 'function') {
            revert = revert(this.element);
        }

        var d = this.currentDelta();
        if (revert && this.options.reverteffect) {
            this._revert = this.options.reverteffect(this.element,
                d[1] - this.delta[1], d[0] - this.delta[0]);
        } else {
            this.delta = d;
        }

        if (this.options.zindex) {
            this.element.style.zIndex = this.originalZ;
        }

        if (this.options.endeffect) {
            this.options.endeffect(this.element);
        }

        dr.Draggables.deactivate();
        dr.Droppables.reset(this.element);
    },

    /** @id MochiKit.DragAndDrop.keyPress */
    keyPress: function (event) {
        if (event.key().string != "KEY_ESCAPE") {
            return;
        }
        this.finishDrag(event, false);
        event.stop();
    },

    /** @id MochiKit.DragAndDrop.endDrag */
    endDrag: function (event) {
        if (!this.dragging) {
            return;
        }
        this.stopScrolling();
        this.finishDrag(event, true);
        event.stop();
    },

    /** @id MochiKit.DragAndDrop.draw */
    draw: function (point) {
        var pos = MochiKit.Position.cumulativeOffset(this.element);
        var d = this.currentDelta();
        pos.x -= d[0];
        pos.y -= d[1];

        if (this.options.scroll && (this.options.scroll != window && this._isScrollChild)) {
            pos.x -= this.options.scroll.scrollLeft - this.originalScrollLeft;
            pos.y -= this.options.scroll.scrollTop - this.originalScrollTop;
        }

        var p = [point.page.x - pos.x - this.offset[0],
                 point.page.y - pos.y - this.offset[1]];

        if (this.options.snap) {
            if (typeof(this.options.snap) == 'function') {
                p = this.options.snap(p[0], p[1]);
            } else {
                if (this.options.snap instanceof Array) {
                    var i = -1;
                    p = MochiKit.Base.map(MochiKit.Base.bind(function (v) {
                            i += 1;
                            return Math.round(v/this.options.snap[i]) *
                                   this.options.snap[i];
                        }, this), p);
                } else {
                    p = MochiKit.Base.map(MochiKit.Base.bind(function (v) {
                        return Math.round(v/this.options.snap) *
                               this.options.snap;
                        }, this), p);
                }
            }
        }
        var style = this.element.style;
        if ((!this.options.constraint) ||
            (this.options.constraint == 'horizontal')) {
            style.left = p[0] + 'px';
        }
        if ((!this.options.constraint) ||
            (this.options.constraint == 'vertical')) {
            style.top = p[1] + 'px';
        }
        if (style.visibility == 'hidden') {
            style.visibility = '';  // fix gecko rendering
        }
    },

    /** @id MochiKit.DragAndDrop.stopScrolling */
    stopScrolling: function () {
        if (this.scrollInterval) {
            clearInterval(this.scrollInterval);
            this.scrollInterval = null;
            MochiKit.DragAndDrop.Draggables._lastScrollPointer = null;
        }
    },

    /** @id MochiKit.DragAndDrop.startScrolling */
    startScrolling: function (speed) {
        if (!speed[0] && !speed[1]) {
            return;
        }
        this.scrollSpeed = [speed[0] * this.options.scrollSpeed,
                            speed[1] * this.options.scrollSpeed];
        this.lastScrolled = new Date();
        this.scrollInterval = setInterval(MochiKit.Base.bind(this.scroll, this), 10);
    },

    /** @id MochiKit.DragAndDrop.scroll */
    scroll: function () {
        var current = new Date();
        var delta = current - this.lastScrolled;
        this.lastScrolled = current;

        if (this.options.scroll == window) {
            var s = this._getWindowScroll(this.options.scroll);
            if (this.scrollSpeed[0] || this.scrollSpeed[1]) {
                var dm = delta / 1000;
                this.options.scroll.scrollTo(s.left + dm * this.scrollSpeed[0],
                                             s.top + dm * this.scrollSpeed[1]);
            }
        } else {
            this.options.scroll.scrollLeft += this.scrollSpeed[0] * delta / 1000;
            this.options.scroll.scrollTop += this.scrollSpeed[1] * delta / 1000;
        }

        var d = MochiKit.DragAndDrop;

        MochiKit.Position.prepare();
        d.Droppables.show(d.Draggables._lastPointer, this.element);
        d.Draggables.notify('drag', this);
        if (this._isScrollChild) {
            d.Draggables._lastScrollPointer = d.Draggables._lastScrollPointer || d.Draggables._lastPointer;
            d.Draggables._lastScrollPointer.x += this.scrollSpeed[0] * delta / 1000;
            d.Draggables._lastScrollPointer.y += this.scrollSpeed[1] * delta / 1000;
            if (d.Draggables._lastScrollPointer.x < 0) {
                d.Draggables._lastScrollPointer.x = 0;
            }
            if (d.Draggables._lastScrollPointer.y < 0) {
                d.Draggables._lastScrollPointer.y = 0;
            }
            this.draw(d.Draggables._lastScrollPointer);
        }

        this.options.onchange(this);
    },

    _getWindowScroll: function (win) {
        var vp, w, h;
        MochiKit.DOM.withWindow(win, function () {
            vp = MochiKit.Style.getViewportPosition(win.document);
        });
        if (win.innerWidth) {
            w = win.innerWidth;
            h = win.innerHeight;
        } else if (win.document.documentElement && win.document.documentElement.clientWidth) {
            w = win.document.documentElement.clientWidth;
            h = win.document.documentElement.clientHeight;
        } else {
            w = win.document.body.offsetWidth;
            h = win.document.body.offsetHeight;
        }
        return {top: vp.y, left: vp.x, width: w, height: h};
    },

    /** @id MochiKit.DragAndDrop.repr */
    repr: function () {
        return '[' + this.__class__.NAME + ", options:" + MochiKit.Base.repr(this.options) + "]";
    }
};

MochiKit.DragAndDrop.__new__ = function () {
    MochiKit.Base.nameFunctions(this);
};

MochiKit.DragAndDrop.__new__();

MochiKit.Base._exportSymbols(this, MochiKit.DragAndDrop);
/***
Copyright (c) 2005 Thomas Fuchs (http://script.aculo.us, http://mir.aculo.us)
    Mochi-ized By Thomas Herve (_firstname_@nimail.org)

See scriptaculous.js for full license.

***/

MochiKit.Base._module('Sortable', '1.5', ['Base', 'Iter', 'DOM', 'Position', 'DragAndDrop']);

MochiKit.Base.update(MochiKit.Sortable, {
    __export__: false,

    /***

    Manage sortables. Mainly use the create function to add a sortable.

    ***/
    sortables: {},

    _findRootElement: function (element) {
        while (element.tagName.toUpperCase() != "BODY") {
            if (element.id && MochiKit.Sortable.sortables[element.id]) {
                return element;
            }
            element = element.parentNode;
        }
    },

    _createElementId: function(element) {
        if (element.id == null || element.id == "") {
            var d = MochiKit.DOM;
            var id;
            var count = 1;
            while (d.getElement(id = "sortable" + count) != null) {
                count += 1;
            }
            d.setNodeAttribute(element, "id", id);
        }
    },

    /** @id MochiKit.Sortable.options */
    options: function (element) {
        element = MochiKit.Sortable._findRootElement(MochiKit.DOM.getElement(element));
        if (!element) {
            return;
        }
        return MochiKit.Sortable.sortables[element.id];
    },

    /** @id MochiKit.Sortable.destroy */
    destroy: function (element){
        var s = MochiKit.Sortable.options(element);
        var b = MochiKit.Base;
        var d = MochiKit.DragAndDrop;

        if (s) {
            MochiKit.Signal.disconnect(s.startHandle);
            MochiKit.Signal.disconnect(s.endHandle);
            b.map(function (dr) {
                d.Droppables.remove(dr);
            }, s.droppables);
            b.map(function (dr) {
                dr.destroy();
            }, s.draggables);

            delete MochiKit.Sortable.sortables[s.element.id];
        }
    },

    /** @id MochiKit.Sortable.create */
    create: function (element, options) {
        element = MochiKit.DOM.getElement(element);
        var self = MochiKit.Sortable;
        self._createElementId(element);

        /** @id MochiKit.Sortable.options */
        options = MochiKit.Base.update({

            /** @id MochiKit.Sortable.element */
            element: element,

            /** @id MochiKit.Sortable.tag */
            tag: 'li',  // assumes li children, override with tag: 'tagname'

            /** @id MochiKit.Sortable.dropOnEmpty */
            dropOnEmpty: false,

            /** @id MochiKit.Sortable.tree */
            tree: false,

            /** @id MochiKit.Sortable.treeTag */
            treeTag: 'ul',

            /** @id MochiKit.Sortable.overlap */
            overlap: 'vertical',  // one of 'vertical', 'horizontal'

            /** @id MochiKit.Sortable.constraint */
            constraint: 'vertical',  // one of 'vertical', 'horizontal', false
            // also takes array of elements (or ids); or false

            /** @id MochiKit.Sortable.containment */
            containment: [element],

            /** @id MochiKit.Sortable.handle */
            handle: false,  // or a CSS class

            /** @id MochiKit.Sortable.only */
            only: false,

            /** @id MochiKit.Sortable.hoverclass */
            hoverclass: null,

            /** @id MochiKit.Sortable.ghosting */
            ghosting: false,

            /** @id MochiKit.Sortable.scroll */
            scroll: false,

            /** @id MochiKit.Sortable.scrollSensitivity */
            scrollSensitivity: 20,

            /** @id MochiKit.Sortable.scrollSpeed */
            scrollSpeed: 15,

            /** @id MochiKit.Sortable.format */
            format: /^[^_]*_(.*)$/,

            /** @id MochiKit.Sortable.onChange */
            onChange: MochiKit.Base.noop,

            /** @id MochiKit.Sortable.onUpdate */
            onUpdate: MochiKit.Base.noop,

            /** @id MochiKit.Sortable.accept */
            accept: null
        }, options);

        // clear any old sortable with same element
        self.destroy(element);

        // build options for the draggables
        var options_for_draggable = {
            revert: true,
            ghosting: options.ghosting,
            scroll: options.scroll,
            scrollSensitivity: options.scrollSensitivity,
            scrollSpeed: options.scrollSpeed,
            constraint: options.constraint,
            handle: options.handle
        };

        if (options.starteffect) {
            options_for_draggable.starteffect = options.starteffect;
        }

        if (options.reverteffect) {
            options_for_draggable.reverteffect = options.reverteffect;
        } else if (options.ghosting) {
            options_for_draggable.reverteffect = function (innerelement) {
                innerelement.style.top = 0;
                innerelement.style.left = 0;
            };
        }

        if (options.endeffect) {
            options_for_draggable.endeffect = options.endeffect;
        }

        if (options.zindex) {
            options_for_draggable.zindex = options.zindex;
        }

        // build options for the droppables
        var options_for_droppable = {
            overlap: options.overlap,
            containment: options.containment,
            hoverclass: options.hoverclass,
            onhover: self.onHover,
            tree: options.tree,
            accept: options.accept
        }

        var options_for_tree = {
            onhover: self.onEmptyHover,
            overlap: options.overlap,
            containment: options.containment,
            hoverclass: options.hoverclass,
            accept: options.accept
        }

        // fix for gecko engine
        MochiKit.DOM.removeEmptyTextNodes(element);

        options.draggables = [];
        options.droppables = [];

        // drop on empty handling
        if (options.dropOnEmpty || options.tree) {
            new MochiKit.DragAndDrop.Droppable(element, options_for_tree);
            options.droppables.push(element);
        }
        MochiKit.Base.map(function (e) {
            // handles are per-draggable
            var handle = options.handle ?
                MochiKit.DOM.getFirstElementByTagAndClassName(null,
                    options.handle, e) : e;
            options.draggables.push(
                new MochiKit.DragAndDrop.Draggable(e,
                    MochiKit.Base.update(options_for_draggable,
                                         {handle: handle})));
            new MochiKit.DragAndDrop.Droppable(e, options_for_droppable);
            if (options.tree) {
                e.treeNode = element;
            }
            options.droppables.push(e);
        }, (self.findElements(element, options) || []));

        if (options.tree) {
            MochiKit.Base.map(function (e) {
                new MochiKit.DragAndDrop.Droppable(e, options_for_tree);
                e.treeNode = element;
                options.droppables.push(e);
            }, (self.findTreeElements(element, options) || []));
        }

        // keep reference
        self.sortables[element.id] = options;

        options.lastValue = self.serialize(element);
        options.startHandle = MochiKit.Signal.connect(MochiKit.DragAndDrop.Draggables, 'start',
                                MochiKit.Base.partial(self.onStart, element));
        options.endHandle = MochiKit.Signal.connect(MochiKit.DragAndDrop.Draggables, 'end',
                                MochiKit.Base.partial(self.onEnd, element));
    },

    /** @id MochiKit.Sortable.onStart */
    onStart: function (element, draggable) {
        var self = MochiKit.Sortable;
        var options = self.options(element);
        options.lastValue = self.serialize(options.element);
    },

    /** @id MochiKit.Sortable.onEnd */
    onEnd: function (element, draggable) {
        var self = MochiKit.Sortable;
        self.unmark();
        var options = self.options(element);
        if (options.lastValue != self.serialize(options.element)) {
            options.onUpdate(options.element);
        }
    },

    // return all suitable-for-sortable elements in a guaranteed order

    /** @id MochiKit.Sortable.findElements */
    findElements: function (element, options) {
        return MochiKit.Sortable.findChildren(element, options.only, options.tree, options.tag);
    },

    /** @id MochiKit.Sortable.findTreeElements */
    findTreeElements: function (element, options) {
        return MochiKit.Sortable.findChildren(
            element, options.only, options.tree ? true : false, options.treeTag);
    },

    /** @id MochiKit.Sortable.findChildren */
    findChildren: function (element, only, recursive, tagName) {
        if (!element.hasChildNodes()) {
            return null;
        }
        tagName = tagName.toUpperCase();
        if (only) {
            only = MochiKit.Base.flattenArray([only]);
        }
        var elements = [];
        MochiKit.Base.map(function (e) {
            if (e.tagName &&
                e.tagName.toUpperCase() == tagName &&
               (!only ||
                MochiKit.Iter.some(only, function (c) {
                    return MochiKit.DOM.hasElementClass(e, c);
                }))) {
                elements.push(e);
            }
            if (recursive) {
                var grandchildren = MochiKit.Sortable.findChildren(e, only, recursive, tagName);
                if (grandchildren && grandchildren.length > 0) {
                    elements = elements.concat(grandchildren);
                }
            }
        }, element.childNodes);
        return elements;
    },

    /** @id MochiKit.Sortable.onHover */
    onHover: function (element, dropon, overlap) {
        if (MochiKit.DOM.isChildNode(dropon, element)) {
            return;
        }
        var self = MochiKit.Sortable;

        if (overlap > .33 && overlap < .66 && self.options(dropon).tree) {
            return;
        } else if (overlap > 0.5) {
            self.mark(dropon, 'before');
            if (dropon.previousSibling != element) {
                var oldParentNode = element.parentNode;
                element.style.visibility = 'hidden';  // fix gecko rendering
                dropon.parentNode.insertBefore(element, dropon);
                if (dropon.parentNode != oldParentNode) {
                    self.options(oldParentNode).onChange(element);
                }
                self.options(dropon.parentNode).onChange(element);
            }
        } else {
            self.mark(dropon, 'after');
            var nextElement = dropon.nextSibling || null;
            if (nextElement != element) {
                var oldParentNode = element.parentNode;
                element.style.visibility = 'hidden';  // fix gecko rendering
                dropon.parentNode.insertBefore(element, nextElement);
                if (dropon.parentNode != oldParentNode) {
                    self.options(oldParentNode).onChange(element);
                }
                self.options(dropon.parentNode).onChange(element);
            }
        }
    },

    _offsetSize: function (element, type) {
        if (type == 'vertical' || type == 'height') {
            return element.offsetHeight;
        } else {
            return element.offsetWidth;
        }
    },

    /** @id MochiKit.Sortable.onEmptyHover */
    onEmptyHover: function (element, dropon, overlap) {
        var oldParentNode = element.parentNode;
        var self = MochiKit.Sortable;
        var droponOptions = self.options(dropon);

        if (!MochiKit.DOM.isChildNode(dropon, element)) {
            var index;

            var children = self.findElements(dropon, {tag: droponOptions.tag,
                                                      only: droponOptions.only});
            var child = null;

            if (children) {
                var offset = self._offsetSize(dropon, droponOptions.overlap) * (1.0 - overlap);

                for (index = 0; index < children.length; index += 1) {
                    if (offset - self._offsetSize(children[index], droponOptions.overlap) >= 0) {
                        offset -= self._offsetSize(children[index], droponOptions.overlap);
                    } else if (offset - (self._offsetSize (children[index], droponOptions.overlap) / 2) >= 0) {
                        child = index + 1 < children.length ? children[index + 1] : null;
                        break;
                    } else {
                        child = children[index];
                        break;
                    }
                }
            }

            dropon.insertBefore(element, child);

            self.options(oldParentNode).onChange(element);
            droponOptions.onChange(element);
        }
    },

    /** @id MochiKit.Sortable.unmark */
    unmark: function () {
        var m = MochiKit.Sortable._marker;
        if (m) {
            MochiKit.Style.hideElement(m);
        }
    },

    /** @id MochiKit.Sortable.mark */
    mark: function (dropon, position) {
        // mark on ghosting only
        var d = MochiKit.DOM;
        var self = MochiKit.Sortable;
        var sortable = self.options(dropon.parentNode);
        if (sortable && !sortable.ghosting) {
            return;
        }

        if (!self._marker) {
            self._marker = d.getElement('dropmarker') ||
                        document.createElement('DIV');
            MochiKit.Style.hideElement(self._marker);
            d.addElementClass(self._marker, 'dropmarker');
            self._marker.style.position = 'absolute';
            document.getElementsByTagName('body').item(0).appendChild(self._marker);
        }
        var offsets = MochiKit.Position.cumulativeOffset(dropon);
        self._marker.style.left = offsets.x + 'px';
        self._marker.style.top = offsets.y + 'px';

        if (position == 'after') {
            if (sortable.overlap == 'horizontal') {
                self._marker.style.left = (offsets.x + dropon.clientWidth) + 'px';
            } else {
                self._marker.style.top = (offsets.y + dropon.clientHeight) + 'px';
            }
        }
        MochiKit.Style.showElement(self._marker);
    },

    _tree: function (element, options, parent) {
        var self = MochiKit.Sortable;
        var children = self.findElements(element, options) || [];

        for (var i = 0; i < children.length; ++i) {
            var match = children[i].id.match(options.format);

            if (!match) {
                continue;
            }

            var child = {
                id: encodeURIComponent(match ? match[1] : null),
                element: element,
                parent: parent,
                children: [],
                position: parent.children.length,
                container: self._findChildrenElement(children[i], options.treeTag.toUpperCase())
            }

            /* Get the element containing the children and recurse over it */
            if (child.container) {
                self._tree(child.container, options, child)
            }

            parent.children.push (child);
        }

        return parent;
    },

    /* Finds the first element of the given tag type within a parent element.
       Used for finding the first LI[ST] within a L[IST]I[TEM].*/
    _findChildrenElement: function (element, containerTag) {
        if (element && element.hasChildNodes) {
            containerTag = containerTag.toUpperCase();
            for (var i = 0; i < element.childNodes.length; ++i) {
                if (element.childNodes[i].tagName.toUpperCase() == containerTag) {
                    return element.childNodes[i];
                }
            }
        }
        return null;
    },

    /** @id MochiKit.Sortable.tree */
    tree: function (element, options) {
        element = MochiKit.DOM.getElement(element);
        var sortableOptions = MochiKit.Sortable.options(element);
        options = MochiKit.Base.update({
            tag: sortableOptions.tag,
            treeTag: sortableOptions.treeTag,
            only: sortableOptions.only,
            name: element.id,
            format: sortableOptions.format
        }, options || {});

        var root = {
            id: null,
            parent: null,
            children: new Array,
            container: element,
            position: 0
        }

        return MochiKit.Sortable._tree(element, options, root);
    },

    /**
     * Specifies the sequence for the Sortable.
     * @param {Node} element    Element to use as the Sortable.
     * @param {Object} newSequence    New sequence to use.
     * @param {Object} options    Options to use fro the Sortable.
     */
    setSequence: function (element, newSequence, options) {
        var self = MochiKit.Sortable;
        var b = MochiKit.Base;
        element = MochiKit.DOM.getElement(element);
        options = b.update(self.options(element), options || {});

        var nodeMap = {};
        b.map(function (n) {
            var m = n.id.match(options.format);
            if (m) {
                nodeMap[m[1]] = [n, n.parentNode];
            }
            n.parentNode.removeChild(n);
        }, self.findElements(element, options));

        b.map(function (ident) {
            var n = nodeMap[ident];
            if (n) {
                n[1].appendChild(n[0]);
                delete nodeMap[ident];
            }
        }, newSequence);
    },

    /* Construct a [i] index for a particular node */
    _constructIndex: function (node) {
        var index = '';
        do {
            if (node.id) {
                index = '[' + node.position + ']' + index;
            }
        } while ((node = node.parent) != null);
        return index;
    },

    /** @id MochiKit.Sortable.sequence */
    sequence: function (element, options) {
        element = MochiKit.DOM.getElement(element);
        var self = MochiKit.Sortable;
        var options = MochiKit.Base.update(self.options(element), options || {});

        return MochiKit.Base.map(function (item) {
            return item.id.match(options.format) ? item.id.match(options.format)[1] : '';
        }, MochiKit.DOM.getElement(self.findElements(element, options) || []));
    },

    /**
     * Serializes the content of a Sortable. Useful to send this content through a XMLHTTPRequest.
     * These options override the Sortable options for the serialization only.
     * @param {Node} element    Element to serialize.
     * @param {Object} options    Serialization options.
     */
    serialize: function (element, options) {
        element = MochiKit.DOM.getElement(element);
        var self = MochiKit.Sortable;
        options = MochiKit.Base.update(self.options(element), options || {});
        var name = encodeURIComponent(options.name || element.id);

        if (options.tree) {
            return MochiKit.Base.flattenArray(MochiKit.Base.map(function (item) {
                return [name + self._constructIndex(item) + "[id]=" +
                encodeURIComponent(item.id)].concat(item.children.map(arguments.callee));
            }, self.tree(element, options).children)).join('&');
        } else {
            return MochiKit.Base.map(function (item) {
                return name + "[]=" + encodeURIComponent(item);
            }, self.sequence(element, options)).join('&');
        }
    }
});

// trunk compatibility
MochiKit.Sortable.Sortable = MochiKit.Sortable;

MochiKit.Sortable.__new__ = function () {
    MochiKit.Base.nameFunctions(this);
};

MochiKit.Sortable.__new__();

MochiKit.Base._exportSymbols(this, MochiKit.Sortable);
