"""
JavaScript Glue Generator for Fr WASM modules

Generates a JavaScript module that provides runtime support for Fr WASM,
including only the functions that are actually used by the compiled module.
"""

from typing import Set, Dict, List, Optional
import json

# All available runtime functions that can be imported from JS
# Organized by category, excluding file I/O, sockets, and multiprocessing
JS_RUNTIME_FUNCTIONS = {
    # Console I/O
    'print': {
        'signature': '(ptr, len) => {}',
        'implementation': '''(ptr, len) => {
            const text = readString(ptr, len);
            console.log(text)
        }''',
        'wasm_signature': '(param i32 i32)',
    },
    'println': {
        'signature': '(ptr, len) => {}',
        'implementation': '''(ptr, len) => {
            const text = readString(ptr, len);
            console.log(text)
        }''',
        'wasm_signature': '(param i32 i32)',
    },

    # String operations
    'str_concat': {
        'signature': '(ptr1, len1, ptr2, len2) => [ptr, len]',
        'implementation': '''(ptr1, len1, ptr2, len2) => {
            if (len1 === 0 && len2 === 0) return [0, 0];
            if (len1 === 0) return [ptr2, len2];
            if (len2 === 0) return [ptr1, len1];
            const s1 = readString(ptr1, len1);
            const s2 = readString(ptr2, len2);
            return allocString(s1 + s2);
        }''',
        'wasm_signature': '(param i32 i32 i32 i32) (result i32 i32)',
    },
    'str_to_i64': {
        'signature': '(ptr, len) => BigInt',
        'implementation': '''(ptr, len) => {
            if (len <= 0) return 0n;
            const s = readString(ptr, len);
            const f = parseFloat(s);
            // Guard against NaN/Infinity before converting to BigInt
            if (!Number.isFinite(f)) return 0n;
            return BigInt(Math.trunc(f)) || 0n;
        }''',
        'wasm_signature': '(param i32 i32) (result i64)',
    },
    'str_to_f64': {
        'signature': '(ptr, len) => number',
        'implementation': '''(ptr, len) => {
            if (len <= 0) return 0.0;
            const s = readString(ptr, len);
            return parseFloat(s) || 0.0;
        }''',
        'wasm_signature': '(param i32 i32) (result f64)',
    },
    'i64_to_str': {
        'signature': '(value) => [ptr, len]',
        'implementation': '''(value) => {
            const s = value.toString();
            return allocString(s);
        }''',
        'wasm_signature': '(param i64) (result i32 i32)',
    },
    'f64_to_str': {
        'signature': '(value) => [ptr, len]',
        'implementation': '''(value) => {
            const s = Number.isInteger(value) ? value.toFixed(1) : value.toString();
            return allocString(s);
        }''',
        'wasm_signature': '(param f64) (result i32 i32)',
    },
    'bool_to_str': {
        'signature': '(value) => [ptr, len]',
        'implementation': '''(value) => {
            const truthy = (typeof value === 'bigint') ? (value !== 0n) : !!value;
            return allocString(truthy ? 'true' : 'false');
        }''',
        'wasm_signature': '(param i64) (result i32 i32)',
    },
    'str_upper': {
        'signature': '(ptr, len) => [ptr, len]',
        'implementation': '''(ptr, len) => {
            const s = readString(ptr, len);
            return allocString(s.toUpperCase());
        }''',
        'wasm_signature': '(param i32 i32) (result i32 i32)',
    },
    'str_lower': {
        'signature': '(ptr, len) => [ptr, len]',
        'implementation': '''(ptr, len) => {
            const s = readString(ptr, len);
            return allocString(s.toLowerCase());
        }''',
        'wasm_signature': '(param i32 i32) (result i32 i32)',
    },
    'str_strip': {
        'signature': '(ptr, len) => [ptr, len]',
        'implementation': '''(ptr, len) => {
            const s = readString(ptr, len);
            return allocString(s.trim());
        }''',
        'wasm_signature': '(param i32 i32) (result i32 i32)',
    },
    'str_replace': {
        'signature': '(ptr, len, oldPtr, oldLen, newPtr, newLen) => [ptr, len]',
        'implementation': '''(ptr, len, oldPtr, oldLen, newPtr, newLen) => {
            const s = readString(ptr, len);
            const oldStr = readString(oldPtr, oldLen);
            const newStr = readString(newPtr, newLen);
            return allocString(s.split(oldStr).join(newStr));
        }''',
        'wasm_signature': '(param i32 i32 i32 i32 i32 i32) (result i32 i32)',
    },
    'str_get': {
        'signature': '(ptr, len, index) => [ptr, len]',
        'implementation': '''(ptr, len, index) => {
            const s = readString(ptr, len);
            const idx = Number(index);
            if (idx < 0 || idx >= s.length) return [0, 0];
            return allocString(s[idx]);
        }''',
        'wasm_signature': '(param i32 i32 i64) (result i32 i32)',
    },
    'str_contains': {
        'signature': '(ptr1, len1, ptr2, len2) => i32',
        'implementation': '''(ptr1, len1, ptr2, len2) => {
            const s1 = readString(ptr1, len1);
            const s2 = readString(ptr2, len2);
            return s1.includes(s2) ? 1 : 0;
        }''',
        'wasm_signature': '(param i32 i32 i32 i32) (result i32)',
    },
    'str_eq': {
        'signature': '(ptr1, len1, ptr2, len2) => i32',
        'implementation': '''(ptr1, len1, ptr2, len2) => {
            if (len1 !== len2) return 0;
            const s1 = readString(ptr1, len1);
            const s2 = readString(ptr2, len2);
            return s1 === s2 ? 1 : 0;
        }''',
        'wasm_signature': '(param i32 i32 i32 i32) (result i32)',
    },
    'str_join': {
        'signature': '(sepPtr, sepLen, listId) => [ptr, len]',
        'implementation': '''(sepPtr, sepLen, listId) => {
            const sep = readString(sepPtr, sepLen);
            const list = lists.get(listId) || [];
            const parts = list.map(v => {
                const packed = BigInt(v);
                const len = Number(packed >> 32n);
                const ptr = Number(packed & 0xffffffffn);
                if (len > 0) return readString(ptr, len);
                return v.toString();
            });
            return allocString(parts.join(sep));
        }''',
        'wasm_signature': '(param i32 i32 i32) (result i32 i32)',
    },
    'str_split': {
        'signature': '(strPtr, strLen, sepPtr, sepLen) => listId',
        'implementation': '''(strPtr, strLen, sepPtr, sepLen) => {
            const s = readString(strPtr, strLen);
            const sep = readString(sepPtr, sepLen);
            const parts = sep === '' ? [...s] : s.split(sep);
            const listId = lists.size;
            const list = [];
            for (const part of parts) {
                const [ptr, len] = allocString(part);
                const packed = (BigInt(len) << 32n) | BigInt(ptr);
                list.push(packed);
            }
            lists.set(listId, list);
            return listId;
        }''',
        'wasm_signature': '(param i32 i32 i32 i32) (result i32)',
    },

    # Math functions
    'sqrt': {
        'signature': '(value) => number',
        'implementation': '''(value) => Math.sqrt(value)''',
        'wasm_signature': '(param f64) (result f64)',
    },
    'pow': {
        'signature': '(base, exp) => number',
        'implementation': '''(base, exp) => Math.pow(base, exp)''',
        'wasm_signature': '(param f64 f64) (result f64)',
    },
    'round_f64': {
        'signature': '(value) => number',
        'implementation': '''(value) => Math.round(value)''',
        'wasm_signature': '(param f64) (result f64)',
    },
    'floor_f64': {
        'signature': '(value) => number',
        'implementation': '''(value) => Math.floor(value)''',
        'wasm_signature': '(param f64) (result f64)',
    },
    'ceil_f64': {
        'signature': '(value) => number',
        'implementation': '''(value) => Math.ceil(value)''',
        'wasm_signature': '(param f64) (result f64)',
    },

    # List operations
    'list_new': {
        'signature': '() => listId',
        'implementation': '''() => {
            const id = lists.size;
            lists.set(id, []);
            return id;
        }''',
        'wasm_signature': '(result i32)',
    },
    'list_append': {
        'signature': '(listId, value) => listId',
        'implementation': '''(listId, value) => {
            const list = lists.get(listId);
            if (list) list.push(value);
            return listId;
        }''',
        'wasm_signature': '(param i32 i64) (result i32)',
    },
    'list_get': {
        'signature': '(listId, index) => value',
        'implementation': '''(listId, index) => {
            const list = lists.get(listId);
            if (!list) return 0n;
            const idx = Number(index);
            if (idx < 0 || idx >= list.length) return 0n;
            return list[idx];
        }''',
        'wasm_signature': '(param i32 i64) (result i64)',
    },
    'list_set': {
        'signature': '(listId, index, value) => listId',
        'implementation': '''(listId, index, value) => {
            const list = lists.get(listId);
            if (list) {
                const idx = Number(index);
                if (idx >= 0 && idx < list.length) {
                    list[idx] = value;
                }
            }
            return listId;
        }''',
        'wasm_signature': '(param i32 i64 i64) (result i32)',
    },
    'list_len': {
        'signature': '(listId) => BigInt',
        'implementation': '''(listId) => {
            const list = lists.get(listId);
            return BigInt(list ? list.length : 0);
        }''',
        'wasm_signature': '(param i32) (result i64)',
    },
    'list_pop': {
        'signature': '(listId) => [listId, value]',
        'implementation': '''(listId) => {
            const list = lists.get(listId);
            if (!list || list.length === 0) return [listId, 0n];
            const value = list.pop();
            return [listId, value];
        }''',
        'wasm_signature': '(param i32) (result i32 i64)',
    },
    'list_to_str': {
        'signature': '(listId) => [ptr, len]',
        'implementation': '''(listId) => {
            const list = lists.get(listId) || [];
            const elements = list.map(v => {
                const packed = BigInt(v);
                const len = Number(packed >> 32n);
                const ptr = Number(packed & 0xffffffffn);
                if (len > 0) return readString(ptr, len);
                return v.toString();
            });
            return allocString('[' + elements.join(', ') + ']');
        }''',
        'wasm_signature': '(param i32) (result i32 i32)',
    },

    # Set operations
    'set_new': {
        'signature': '() => setId',
        'implementation': '''() => {
            const id = sets.size;
            sets.set(id, new Set());
            return id;
        }''',
        'wasm_signature': '(result i32)',
    },
    'set_add': {
        'signature': '(setId, value) => setId',
        'implementation': '''(setId, value) => {
            const set = sets.get(setId);
            if (set) set.add(value);
            return setId;
        }''',
        'wasm_signature': '(param i32 i64) (result i32)',
    },
    'set_remove': {
        'signature': '(setId, value) => setId',
        'implementation': '''(setId, value) => {
            const set = sets.get(setId);
            if (set) set.delete(value);
            return setId;
        }''',
        'wasm_signature': '(param i32 i64) (result i32)',
    },
    'set_contains': {
        'signature': '(setId, value) => i32',
        'implementation': '''(setId, value) => {
            const set = sets.get(setId);
            return (set && set.has(value)) ? 1 : 0;
        }''',
        'wasm_signature': '(param i32 i64) (result i32)',
    },
    'set_len': {
        'signature': '(setId) => BigInt',
        'implementation': '''(setId) => {
            const set = sets.get(setId);
            return BigInt(set ? set.size : 0);
        }''',
        'wasm_signature': '(param i32) (result i64)',
    },
    'set_to_str': {
        'signature': '(setId) => [ptr, len]',
        'implementation': '''(setId) => {
            const set = sets.get(setId);
            if (!set) return allocString('{}');
            const elements = [...set].map(v => v.toString());
            return allocString('{' + elements.join(', ') + '}');
        }''',
        'wasm_signature': '(param i32) (result i32 i32)',
    },

    # Error handling
    'runtime_error': {
        'signature': '(typePtr, typeLen, msgPtr, msgLen, lineNum) => {}',
        'implementation': '''(typePtr, typeLen, msgPtr, msgLen, lineNum) => {
            const type = readString(typePtr, typeLen) || 'Error';
            const msg = readString(msgPtr, msgLen) || '';
            const line = Number(lineNum) || 0;
            throw new FrRuntimeError(`${type}: ${msg}` + (line ? ` (line ${line})` : ''));
        }''',
        'wasm_signature': '(param i32 i32 i32 i32 i32)',
    },
    'index_error': {
        'signature': '(typePtr, typeLen, index, length) => {}',
        'implementation': r'''(typePtr, typeLen, index, length) => {
            const type = readString(typePtr, typeLen);
            throw new FrRuntimeError(`Index ${index} out of bounds for ${type} of length ${length}`);
        }''',
        'wasm_signature': '(param i32 i32 i64 i64)',
    },
    'exit_process': {
        'signature': '(code) => {}',
        'implementation': '''(code) => {
            throw new FrExitError(code);
        }''',
        'wasm_signature': '(param i32)',
    },

    # Sleep (blocking emulation)
    'sleep': {
        'signature': '(seconds) => {}',
        'implementation': '''(seconds) => {
            const ms = Math.max(0, Number(seconds) * 1000);
            const end = performance.now() + ms;
            while (performance.now() < end) {}
        }''',
        'wasm_signature': '(param f64)',
    },

    # File I/O stubs (not supported in browser, but satisfy imports)
    'file_open': {
        'signature': '(pathPtr, pathLen, modePtr, modeLen) => i32',
        'implementation': '''(pathPtr, pathLen, modePtr, modeLen) => {
            console.error('file_open is not supported in WebAssembly JS glue');
            return -1;
        }''',
        'wasm_signature': '(param i32 i32 i32 i32) (result i32)',
    },
    'file_read': {
        'signature': '(fd) => [ptr, len]',
        'implementation': '''(fd) => {
            console.error('file_read is not supported in WebAssembly JS glue');
            return [0, 0];
        }''',
        'wasm_signature': '(param i32) (result i32 i32)',
    },
    'file_write': {
        'signature': '(fd, ptr, len) => {}',
        'implementation': '''(fd, ptr, len) => {
            console.error('file_write is not supported in WebAssembly JS glue');
        }''',
        'wasm_signature': '(param i32 i32 i32)',
    },
    'file_close': {
        'signature': '(fd) => {}',
        'implementation': '''(fd) => {
            console.error('file_close is not supported in WebAssembly JS glue');
        }''',
        'wasm_signature': '(param i32)',
    },

    # String reference counting (no-ops in JS due to GC)
    'str_incref': {
        'signature': '(ptr, len) => {}',
        'implementation': '''(ptr, len) => {}''',
        'wasm_signature': '(param i32 i32)',
    },
    'str_decref': {
        'signature': '(ptr, len) => {}',
        'implementation': '''(ptr, len) => {}''',
        'wasm_signature': '(param i32 i32)',
    },
}
# Web-specific DOM and JS interop functions
JS_WEB_FUNCTIONS = {
    # DOM Query
    'dom_query': {
        'signature': '(selectorPtr, selectorLen) => elementHandle',
        'implementation': '''(selectorPtr, selectorLen) => {
            const selector = readString(selectorPtr, selectorLen);
            const elem = document.querySelector(selector);
            if (!elem) return 0;
            const id = domElements.size + 1;
            domElements.set(id, elem);
            return id;
        }''',
        'wasm_signature': '(param i32 i32) (result i32)',
        'category': 'dom',
    },
    'dom_query_all': {
        'signature': '(selectorPtr, selectorLen) => listId',
        'implementation': '''(selectorPtr, selectorLen) => {
            const selector = readString(selectorPtr, selectorLen);
            const elems = document.querySelectorAll(selector);
            const listId = lists.size;
            const list = [];
            elems.forEach(elem => {
                const id = domElements.size + 1;
                domElements.set(id, elem);
                list.push(BigInt(id));
            });
            lists.set(listId, list);
            return listId;
        }''',
        'wasm_signature': '(param i32 i32) (result i32)',
        'category': 'dom',
    },
    'dom_create': {
        'signature': '(tagPtr, tagLen) => elementHandle',
        'implementation': '''(tagPtr, tagLen) => {
            const tag = readString(tagPtr, tagLen);
            const elem = document.createElement(tag);
            // Auto-attach to document body so elements become visible by default
            if (document.body) {
                document.body.appendChild(elem);
            }
            const id = domElements.size + 1;
            domElements.set(id, elem);
            return id;
        }''',
        'wasm_signature': '(param i32 i32) (result i32)',
        'category': 'dom',
    },
    'dom_get_body': {
        'signature': '() => elementHandle',
        'implementation': '''() => {
            const id = domElements.size + 1;
            domElements.set(id, document.body);
            return id;
        }''',
        'wasm_signature': '(result i32)',
        'category': 'dom',
    },
    'dom_get_document': {
        'signature': '() => elementHandle',
        'implementation': '''() => {
            const id = domElements.size + 1;
            domElements.set(id, document);
            return id;
        }''',
        'wasm_signature': '(result i32)',
        'category': 'dom',
    },

    # DOM Manipulation
    'dom_set_text': {
        'signature': '(elemId, textPtr, textLen) => {}',
        'implementation': '''(elemId, textPtr, textLen) => {
            const elem = domElements.get(elemId);
            if (elem) elem.textContent = readString(textPtr, textLen);
        }''',
        'wasm_signature': '(param i32 i32 i32)',
        'category': 'dom',
    },
    'dom_get_text': {
        'signature': '(elemId) => [ptr, len]',
        'implementation': '''(elemId) => {
            const elem = domElements.get(elemId);
            if (!elem) return [0, 0];
            return allocString(elem.textContent || '');
        }''',
        'wasm_signature': '(param i32) (result i32 i32)',
        'category': 'dom',
    },
    'dom_set_html': {
        'signature': '(elemId, htmlPtr, htmlLen) => {}',
        'implementation': '''(elemId, htmlPtr, htmlLen) => {
            const elem = domElements.get(elemId);
            if (elem) elem.innerHTML = readString(htmlPtr, htmlLen);
        }''',
        'wasm_signature': '(param i32 i32 i32)',
        'category': 'dom',
    },
    'dom_get_html': {
        'signature': '(elemId) => [ptr, len]',
        'implementation': '''(elemId) => {
            const elem = domElements.get(elemId);
            if (!elem) return [0, 0];
            return allocString(elem.innerHTML || '');
        }''',
        'wasm_signature': '(param i32) (result i32 i32)',
        'category': 'dom',
    },
    'dom_set_attr': {
        'signature': '(elemId, namePtr, nameLen, valuePtr, valueLen) => {}',
        'implementation': '''(elemId, namePtr, nameLen, valuePtr, valueLen) => {
            const elem = domElements.get(elemId);
            if (elem) {
                const name = readString(namePtr, nameLen);
                const value = readString(valuePtr, valueLen);
                elem.setAttribute(name, value);
            }
        }''',
        'wasm_signature': '(param i32 i32 i32 i32 i32)',
        'category': 'dom',
    },
    'dom_get_attr': {
        'signature': '(elemId, namePtr, nameLen) => [ptr, len]',
        'implementation': '''(elemId, namePtr, nameLen) => {
            const elem = domElements.get(elemId);
            if (!elem) return [0, 0];
            const name = readString(namePtr, nameLen);
            const value = elem.getAttribute(name);
            return allocString(value || '');
        }''',
        'wasm_signature': '(param i32 i32 i32) (result i32 i32)',
        'category': 'dom',
    },
    'dom_remove_attr': {
        'signature': '(elemId, namePtr, nameLen) => {}',
        'implementation': '''(elemId, namePtr, nameLen) => {
            const elem = domElements.get(elemId);
            if (elem) {
                const name = readString(namePtr, nameLen);
                elem.removeAttribute(name);
            }
        }''',
        'wasm_signature': '(param i32 i32 i32)',
        'category': 'dom',
    },

    # DOM Tree Manipulation
    'dom_append': {
        'signature': '(parentId, childId) => {}',
        'implementation': '''(parentId, childId) => {
            const parent = domElements.get(parentId);
            const child = domElements.get(childId);
            if (parent && child) parent.appendChild(child);
        }''',
        'wasm_signature': '(param i32 i32)',
        'category': 'dom',
    },
    'dom_prepend': {
        'signature': '(parentId, childId) => {}',
        'implementation': '''(parentId, childId) => {
            const parent = domElements.get(parentId);
            const child = domElements.get(childId);
            if (parent && child) parent.prepend(child);
        }''',
        'wasm_signature': '(param i32 i32)',
        'category': 'dom',
    },
    'dom_remove': {
        'signature': '(elemId) => {}',
        'implementation': '''(elemId) => {
            const elem = domElements.get(elemId);
            if (elem && elem.parentNode) elem.parentNode.removeChild(elem);
        }''',
        'wasm_signature': '(param i32)',
        'category': 'dom',
    },
    'dom_clone': {
        'signature': '(elemId, deep) => elementHandle',
        'implementation': '''(elemId, deep) => {
            const elem = domElements.get(elemId);
            if (!elem) return 0;
            const clone = elem.cloneNode(deep !== 0);
            const id = domElements.size + 1;
            domElements.set(id, clone);
            return id;
        }''',
        'wasm_signature': '(param i32 i32) (result i32)',
        'category': 'dom',
    },
    'dom_parent': {
        'signature': '(elemId) => elementHandle',
        'implementation': '''(elemId) => {
            const elem = domElements.get(elemId);
            if (!elem || !elem.parentElement) return 0;
            const id = domElements.size + 1;
            domElements.set(id, elem.parentElement);
            return id;
        }''',
        'wasm_signature': '(param i32) (result i32)',
        'category': 'dom',
    },
    'dom_children': {
        'signature': '(elemId) => listId',
        'implementation': '''(elemId) => {
            const elem = domElements.get(elemId);
            const listId = lists.size;
            const list = [];
            if (elem) {
                for (const child of elem.children) {
                    const id = domElements.size + 1;
                    domElements.set(id, child);
                    list.push(BigInt(id));
                }
            }
            lists.set(listId, list);
            return listId;
        }''',
        'wasm_signature': '(param i32) (result i32)',
        'category': 'dom',
    },

    # CSS/Style
    'dom_add_class': {
        'signature': '(elemId, classPtr, classLen) => {}',
        'implementation': '''(elemId, classPtr, classLen) => {
            const elem = domElements.get(elemId);
            if (elem) elem.classList.add(readString(classPtr, classLen));
        }''',
        'wasm_signature': '(param i32 i32 i32)',
        'category': 'dom',
    },
    'dom_remove_class': {
        'signature': '(elemId, classPtr, classLen) => {}',
        'implementation': '''(elemId, classPtr, classLen) => {
            const elem = domElements.get(elemId);
            if (elem) elem.classList.remove(readString(classPtr, classLen));
        }''',
        'wasm_signature': '(param i32 i32 i32)',
        'category': 'dom',
    },
    'dom_toggle_class': {
        'signature': '(elemId, classPtr, classLen) => i32',
        'implementation': '''(elemId, classPtr, classLen) => {
            const elem = domElements.get(elemId);
            if (elem) return elem.classList.toggle(readString(classPtr, classLen)) ? 1 : 0;
            return 0;
        }''',
        'wasm_signature': '(param i32 i32 i32) (result i32)',
        'category': 'dom',
    },
    'dom_has_class': {
        'signature': '(elemId, classPtr, classLen) => i32',
        'implementation': '''(elemId, classPtr, classLen) => {
            const elem = domElements.get(elemId);
            if (elem) return elem.classList.contains(readString(classPtr, classLen)) ? 1 : 0;
            return 0;
        }''',
        'wasm_signature': '(param i32 i32 i32) (result i32)',
        'category': 'dom',
    },
    'dom_set_style': {
        'signature': '(elemId, propPtr, propLen, valuePtr, valueLen) => {}',
        'implementation': '''(elemId, propPtr, propLen, valuePtr, valueLen) => {
            const elem = domElements.get(elemId);
            if (elem) {
                const prop = readString(propPtr, propLen);
                const value = readString(valuePtr, valueLen);
                elem.style[prop] = value;
            }
        }''',
        'wasm_signature': '(param i32 i32 i32 i32 i32)',
        'category': 'dom',
    },
    'dom_get_style': {
        'signature': '(elemId, propPtr, propLen) => [ptr, len]',
        'implementation': '''(elemId, propPtr, propLen) => {
            const elem = domElements.get(elemId);
            if (!elem) return [0, 0];
            const prop = readString(propPtr, propLen);
            return allocString(elem.style[prop] || '');
        }''',
        'wasm_signature': '(param i32 i32 i32) (result i32 i32)',
        'category': 'dom',
    },

    # Form elements
    'dom_get_value': {
        'signature': '(elemId) => [ptr, len]',
        'implementation': '''(elemId) => {
            const elem = domElements.get(elemId);
            if (!elem) return [0, 0];
            return allocString(elem.value || '');
        }''',
        'wasm_signature': '(param i32) (result i32 i32)',
        'category': 'dom',
    },
    'dom_set_value': {
        'signature': '(elemId, valuePtr, valueLen) => {}',
        'implementation': '''(elemId, valuePtr, valueLen) => {
            const elem = domElements.get(elemId);
            if (elem) elem.value = readString(valuePtr, valueLen);
        }''',
        'wasm_signature': '(param i32 i32 i32)',
        'category': 'dom',
    },
    'dom_focus': {
        'signature': '(elemId) => {}',
        'implementation': '''(elemId) => {
            const elem = domElements.get(elemId);
            if (elem && elem.focus) elem.focus();
        }''',
        'wasm_signature': '(param i32)',
        'category': 'dom',
    },
    'dom_blur': {
        'signature': '(elemId) => {}',
        'implementation': '''(elemId) => {
            const elem = domElements.get(elemId);
            if (elem && elem.blur) elem.blur();
        }''',
        'wasm_signature': '(param i32)',
        'category': 'dom',
    },

    # Events
    'dom_on': {
        'signature': '(elemId, eventPtr, eventLen, callbackId) => {}',
        'implementation': '''(elemId, eventPtr, eventLen, callbackId) => {
            const elem = domElements.get(elemId);
            if (!elem) return;
            const eventName = readString(eventPtr, eventLen);
            const handler = (e) => {
                // Store event data for callback to access
                currentEvent = e;
                // Call the WASM callback function
                if (wasmInstance.exports['__callback_' + callbackId]) {
                    wasmInstance.exports['__callback_' + callbackId]();
                }
                currentEvent = null;
            };
            elem.addEventListener(eventName, handler);
            eventHandlers.set(callbackId, { elem, eventName, handler });
        }''',
        'wasm_signature': '(param i32 i32 i32 i32)',
        'category': 'dom',
    },
    'dom_off': {
        'signature': '(callbackId) => {}',
        'implementation': '''(callbackId) => {
            const entry = eventHandlers.get(callbackId);
            if (entry) {
                entry.elem.removeEventListener(entry.eventName, entry.handler);
                eventHandlers.delete(callbackId);
            }
        }''',
        'wasm_signature': '(param i32)',
        'category': 'dom',
    },
    'event_prevent_default': {
        'signature': '() => {}',
        'implementation': '''() => {
            if (currentEvent) currentEvent.preventDefault();
        }''',
        'wasm_signature': '',
        'category': 'dom',
    },
    'event_stop_propagation': {
        'signature': '() => {}',
        'implementation': '''() => {
            if (currentEvent) currentEvent.stopPropagation();
        }''',
        'wasm_signature': '',
        'category': 'dom',
    },
    'event_target': {
        'signature': '() => elementHandle',
        'implementation': '''() => {
            if (!currentEvent || !currentEvent.target) return 0;
            const id = domElements.size + 1;
            domElements.set(id, currentEvent.target);
            return id;
        }''',
        'wasm_signature': '(result i32)',
        'category': 'dom',
    },

    # Timers
    'set_timeout': {
        'signature': '(callbackIdx, ms, ...args) => timerId',
        'implementation': '''(callbackIdx, ms, ...args) => {
            // Get the callback function name from metadata
            const callbacks = metadata.callbacks || [];
            if (callbacks.length === 0) return 0;
            
            const funcName = callbacks[0];
            const func = wasmInstance.exports[funcName];
            if (!func) return 0;
            
            // Convert i32 args to BigInt for i64 WASM parameters
            // (WASM functions with i64 parameters expect BigInt)
            const convertedArgs = args.map(arg => 
                typeof arg === 'number' ? BigInt(arg) : arg
            );
            
            // Call the callback with converted arguments
            return setTimeout(() => {
                try {
                    func(...convertedArgs);
                } catch (e) {
                    console.error("Callback error:", e);
                }
            }, ms);
        }''',
        'wasm_signature': 'variadic',  # Special marker for variadic functions
        'category': 'timer',
    },
    'set_interval': {
        'signature': '(callbackIdx, ms, ...args) => timerId',
        'implementation': '''(callbackIdx, ms, ...args) => {
            // Get the callback function name from metadata
            const callbacks = metadata.callbacks || [];
            if (callbacks.length === 0) return 0;
            
            const funcName = callbacks[0];
            const func = wasmInstance.exports[funcName];
            if (!func) return 0;
            
            // Convert i32 args to BigInt for i64 WASM parameters
            // (WASM functions with i64 parameters expect BigInt)
            const convertedArgs = args.map(arg => 
                typeof arg === 'number' ? BigInt(arg) : arg
            );

            const intervalMs = Math.max(0, Number(ms));
            // Use a sub-millisecond target so high frequencies (e.g. 100k/s) still schedule.
            const targetInterval = intervalMs > 0 ? intervalMs : 0.01;
            // Drive the catch-up loop frequently without starving the event loop.
            const driverInterval = Math.max(1, Math.min(16, targetInterval));
            let next = performance.now() + targetInterval;
            
            const handler = () => {
                const now = performance.now();
                let iterations = 0;
                const maxIterations = 1000; // Safety cap so a stalled tab can't freeze the UI
                while (now >= next && iterations < maxIterations) {
                    try {
                        func(...convertedArgs);
                    } catch (e) {
                        console.error("Callback error:", e);
                        break;
                    }
                    next += targetInterval;
                    iterations += 1;
                }
                if (iterations === maxIterations) {
                    // If we hit the cap, resync to avoid an infinite catch-up loop.
                    next = performance.now() + targetInterval;
                }
            };

            const timerId = setInterval(handler, driverInterval);
            return timerId;
        }''',
        'wasm_signature': 'variadic',  # Special marker for variadic functions
        'category': 'timer',
    },
    'clear_timeout': {
        'signature': '(timerId) => {}',
        'implementation': '''(timerId) => clearTimeout(timerId)''',
        'wasm_signature': '(param i32)',
        'category': 'timer',
    },
    'clear_interval': {
        'signature': '(timerId) => {}',
        'implementation': '''(timerId) => clearInterval(timerId)''',
        'wasm_signature': '(param i32)',
        'category': 'timer',
    },

    # Console (browser)
    'console_log': {
        'signature': '(ptr, len) => {}',
        'implementation': '''(ptr, len) => {
            console.log(readString(ptr, len));
        }''',
        'wasm_signature': '(param i32 i32)',
        'category': 'console',
    },
    'console_error': {
        'signature': '(ptr, len) => {}',
        'implementation': '''(ptr, len) => {
            console.error(readString(ptr, len));
        }''',
        'wasm_signature': '(param i32 i32)',
        'category': 'console',
    },
    'console_warn': {
        'signature': '(ptr, len) => {}',
        'implementation': '''(ptr, len) => {
            console.warn(readString(ptr, len));
        }''',
        'wasm_signature': '(param i32 i32)',
        'category': 'console',
    },

    # Browser APIs
    'alert': {
        'signature': '(ptr, len) => {}',
        'implementation': '''(ptr, len) => {
            alert(readString(ptr, len));
        }''',
        'wasm_signature': '(param i32 i32)',
        'category': 'browser',
    },
    'confirm': {
        'signature': '(ptr, len) => i32',
        'implementation': '''(ptr, len) => {
            return confirm(readString(ptr, len)) ? 1 : 0;
        }''',
        'wasm_signature': '(param i32 i32) (result i32)',
        'category': 'browser',
    },
    'prompt': {
        'signature': '(msgPtr, msgLen, defaultPtr, defaultLen) => [ptr, len]',
        'implementation': '''(msgPtr, msgLen, defaultPtr, defaultLen) => {
            const msg = readString(msgPtr, msgLen);
            const defaultVal = readString(defaultPtr, defaultLen);
            const result = prompt(msg, defaultVal);
            return allocString(result || '');
        }''',
        'wasm_signature': '(param i32 i32 i32 i32) (result i32 i32)',
        'category': 'browser',
    },
    'get_location_href': {
        'signature': '() => [ptr, len]',
        'implementation': '''() => {
            return allocString(window.location.href);
        }''',
        'wasm_signature': '(result i32 i32)',
        'category': 'browser',
    },
    'set_location_href': {
        'signature': '(ptr, len) => {}',
        'implementation': '''(ptr, len) => {
            window.location.href = readString(ptr, len);
        }''',
        'wasm_signature': '(param i32 i32)',
        'category': 'browser',
    },
    'get_local_storage': {
        'signature': '(keyPtr, keyLen) => [ptr, len]',
        'implementation': '''(keyPtr, keyLen) => {
            const key = readString(keyPtr, keyLen);
            const value = localStorage.getItem(key);
            return allocString(value || '');
        }''',
        'wasm_signature': '(param i32 i32) (result i32 i32)',
        'category': 'storage',
    },
    'set_local_storage': {
        'signature': '(keyPtr, keyLen, valuePtr, valueLen) => {}',
        'implementation': '''(keyPtr, keyLen, valuePtr, valueLen) => {
            const key = readString(keyPtr, keyLen);
            const value = readString(valuePtr, valueLen);
            localStorage.setItem(key, value);
        }''',
        'wasm_signature': '(param i32 i32 i32 i32)',
        'category': 'storage',
    },
    'remove_local_storage': {
        'signature': '(keyPtr, keyLen) => {}',
        'implementation': '''(keyPtr, keyLen) => {
            const key = readString(keyPtr, keyLen);
            localStorage.removeItem(key);
        }''',
        'wasm_signature': '(param i32 i32)',
        'category': 'storage',
    },

    # Fetch API
    'fetch_text': {
        'signature': '(urlPtr, urlLen, callbackId) => {}',
        'implementation': '''(urlPtr, urlLen, callbackId) => {
            const url = readString(urlPtr, urlLen);
            fetch(url)
                .then(r => r.text())
                .then(text => {
                    const [ptr, len] = allocString(text);
                    if (wasmInstance.exports['__callback_str_' + callbackId]) {
                        wasmInstance.exports['__callback_str_' + callbackId](ptr, len);
                    }
                })
                .catch(err => {
                    console.error('Fetch error:', err);
                    if (wasmInstance.exports['__callback_str_' + callbackId]) {
                        wasmInstance.exports['__callback_str_' + callbackId](0, 0);
                    }
                });
        }''',
        'wasm_signature': '(param i32 i32 i32)',
        'category': 'fetch',
    },
    'fetch_json': {
        'signature': '(urlPtr, urlLen, callbackId) => {}',
        'implementation': '''(urlPtr, urlLen, callbackId) => {
            const url = readString(urlPtr, urlLen);
            fetch(url)
                .then(r => r.json())
                .then(json => {
                    const [ptr, len] = allocString(JSON.stringify(json));
                    if (wasmInstance.exports['__callback_str_' + callbackId]) {
                        wasmInstance.exports['__callback_str_' + callbackId](ptr, len);
                    }
                })
                .catch(err => {
                    console.error('Fetch error:', err);
                    if (wasmInstance.exports['__callback_str_' + callbackId]) {
                        wasmInstance.exports['__callback_str_' + callbackId](0, 0);
                    }
                });
        }''',
        'wasm_signature': '(param i32 i32 i32)',
        'category': 'fetch',
    },

    # JS interop - Call arbitrary JS functions
    'js_call': {
        'signature': '(funcNamePtr, funcNameLen, argsJson Ptr, argsJsonLen) => [ptr, len]',
        'implementation': '''(funcNamePtr, funcNameLen, argsJsonPtr, argsJsonLen) => {
            const funcName = readString(funcNamePtr, funcNameLen);
            const argsJson = readString(argsJsonPtr, argsJsonLen);
            try {
                const args = argsJson ? JSON.parse(argsJson) : [];
                // Look up function in global scope or jsImports
                let func = jsImports[funcName] || window[funcName];
                if (typeof func === 'function') {
                    const result = func(...args);
                    return allocString(JSON.stringify(result));
                }
                console.error('JS function not found:', funcName);
                return [0, 0];
            } catch (e) {
                console.error('JS call error:', e);
                return [0, 0];
            }
        }''',
        'wasm_signature': '(param i32 i32 i32 i32) (result i32 i32)',
        'category': 'js',
    },
    'js_eval': {
        'signature': '(codePtr, codeLen) => [ptr, len]',
        'implementation': '''(codePtr, codeLen) => {
            const code = readString(codePtr, codeLen);
            try {
                const result = eval(code);
                return allocString(JSON.stringify(result));
            } catch (e) {
                console.error('JS eval error:', e);
                return [0, 0];
            }
        }''',
        'wasm_signature': '(param i32 i32) (result i32 i32)',
        'category': 'js',
    },
    'js_get_global': {
        'signature': '(namePtr, nameLen) => [ptr, len]',
        'implementation': '''(namePtr, nameLen) => {
            const name = readString(namePtr, nameLen);
            try {
                const value = window[name];
                return allocString(JSON.stringify(value));
            } catch (e) {
                return [0, 0];
            }
        }''',
        'wasm_signature': '(param i32 i32) (result i32 i32)',
        'category': 'js',
    },
    'js_set_global': {
        'signature': '(namePtr, nameLen, valuePtr, valueLen) => {}',
        'implementation': '''(namePtr, nameLen, valuePtr, valueLen) => {
            const name = readString(namePtr, nameLen);
            const valueJson = readString(valuePtr, valueLen);
            try {
                window[name] = JSON.parse(valueJson);
            } catch (e) {
                window[name] = valueJson;
            }
        }''',
        'wasm_signature': '(param i32 i32 i32 i32)',
        'category': 'js',
    },

    # Performance
    'performance_now': {
        'signature': '() => f64',
        'implementation': '''() => performance.now()''',
        'wasm_signature': '(result f64)',
        'category': 'performance',
    },
}

def generate_js_glue(
        used_imports: Set[str],
        js_imports: Optional[Dict[str, str]] = None,
        output_element_id: Optional[str] = None,
        for_inline: bool = False
    ) -> str:
    """
    Generate JavaScript glue code for a Fr WASM module.

    Args:
        used_imports: Set of import names used by the WASM module
        js_imports: Optional dict mapping Fr function names to JS module paths
        output_element_id: Optional DOM element ID to write output to

    Returns:
        JavaScript module code as a string
    """
    # Always include core runtime functions because the WASM module imports them unconditionally
    used_functions = {**JS_RUNTIME_FUNCTIONS}

    # Add only the web-specific functions that the module actually needs
    for name, func in JS_WEB_FUNCTIONS.items():
        if name in used_imports:
            used_functions[name] = func

    # Check which categories are used
    uses_dom = any(f.get('category') == 'dom' for f in used_functions.values())
    uses_timer = any(f.get('category') == 'timer' for f in used_functions.values())
    uses_fetch = any(f.get('category') == 'fetch' for f in used_functions.values())
    uses_lists = any(name.startswith('list_') or name == 'str_split' or name == 'str_join'
                     or name == 'dom_query_all' or name == 'dom_children'
                     for name in used_functions)
    uses_sets = any(name.startswith('set_') for name in used_functions)

    # Build the JS module
    js_lines = [
        '// Fr WASM Runtime - Auto-generated JavaScript glue',
        '// Only includes functions used by this specific module',
        '',
        '// Error classes',
        'class FrRuntimeError extends Error {',
        '    constructor(message) {',
        '        super(message);',
        '        this.name = "FrRuntimeError";',
        '    }',
        '}',
        '',
        'class FrExitError extends Error {',
        '    constructor(code) {',
        '        super(`Program exited with code ${code}`);',
        '        this.name = "FrExitError";',
        '        this.code = code;',
        '    }',
        '}',
        '',
        '// Runtime state',
        'let memory = null;',
        'let wasmInstance = null;',
        'let metadata = null;',
        'let stringOffset = 1024;',
        'let outputBuffer = "";',
        'const functionCallStack = [];',  # Track function calls and their arguments
    ]

    if uses_lists:
        js_lines.append('const lists = new Map();')
    if uses_sets:
        js_lines.append('const sets = new Map();')
    if uses_dom:
        js_lines.extend([
            'const domElements = new Map();',
            'const eventHandlers = new Map();',
            'let currentEvent = null;',
        ])

    js_lines.extend(
        [
            'const jsImports = {};',
            '',
            '// Configuration',
            'const config = {',
            f'    outputElementId: {json.dumps(output_element_id)},',
            '    autoFlush: true,',
            '};',
            '',
            '// Memory helpers',
            'function readString(ptr, len) {',
            '    if (len <= 0 || ptr < 0) return "";',
            '    const bytes = new Uint8Array(memory.buffer, ptr, len);',
            '    return new TextDecoder().decode(bytes);',
            '}',
            '',
            'function allocString(s) {',
            '    const bytes = new TextEncoder().encode(s);',
            '    const ptr = stringOffset;',
            '    stringOffset += bytes.length;',
            '    // Grow memory if needed',
            '    const needed = stringOffset;',
            '    const currentSize = memory.buffer.byteLength;',
            '    if (needed > currentSize) {',
            '        const pages = Math.ceil((needed - currentSize) / 65536);',
            '        memory.grow(pages);',
            '    }',
            '    new Uint8Array(memory.buffer, ptr, bytes.length).set(bytes);',
            '    return [ptr, bytes.length];',
            '}',
            '',
            'function flushOutput() {',
            '    if (config.outputElementId) {',
            '        const elem = document.getElementById(config.outputElementId);',
            '        if (elem) {',
            '            elem.textContent += outputBuffer;',
            '        }',
            '    }',
            '    outputBuffer = "";',
            '}',
            '',
            '// Build import object with only used functions',
            'function buildImports() {',
            '    return {',
            '        env: {',
        ]
    )
    # Add each used function
    for name, func in sorted(used_functions.items()):
        impl = func['implementation']
        js_lines.append(f'            {name}: {impl},')

    js_lines.extend([
        '        }',
        '    };',
        '}',
        '',
    ])

    # Add JS import registration function
    if js_imports:
        js_lines.extend([
            '// Register JS imports',
            'function registerJsImports(imports) {',
            '    Object.assign(jsImports, imports);',
            '}',
            '',
        ])

    # Main loader functions
    js_lines.extend([
        '// Load and run Fr WASM module from file',
        'async function loadFrModule(wasmPath, options = {}) {',
        '    const response = await fetch(wasmPath);',
        '    const wasmBytes = await response.arrayBuffer();',
        '    return loadFrModuleFromBytes(wasmBytes, options);',
        '}',
        '',
        '// Load and run Fr WASM module from bytes',
        'async function loadFrModuleFromBytes(wasmBytes, options = {}) {',
        '    Object.assign(config, options);',
        '    ',
        '    const imports = buildImports();',
        '    const { instance } = await WebAssembly.instantiate(wasmBytes, imports);',
        '    ',
        '    wasmInstance = instance;',
        '    memory = instance.exports.memory;',
        '    ',
        '    return {',
        '        instance,',
        '        run: () => {',
        '            try {',
        '                if (instance.exports.main) {',
        '                    instance.exports.main();',
        '                }',
        '                flushOutput();',
        '                return { success: true, output: outputBuffer };',
        '            } catch (e) {',
        '                if (e instanceof FrExitError) {',
        '                    flushOutput();',
        '                    return { success: e.code === 0, exitCode: e.code, output: outputBuffer };',
        '                }',
        '                throw e;',
        '            }',
        '        },',
        '        getOutput: () => outputBuffer,',
        '        flushOutput,',
        '        memory,',
    ])

    if uses_dom:
        js_lines.append('        domElements,')
    if uses_lists:
        js_lines.append('        lists,')
    if uses_sets:
        js_lines.append('        sets,')

    js_lines.extend([
        '    };',
        '}',
        '',
    ])

    # Only add exports if not inline
    if not for_inline:
        js_lines.extend([
            '// Export for ES modules',
            'export { loadFrModule, FrRuntimeError, FrExitError, config };',
            '',
            '// Also support CommonJS',
            'if (typeof module !== "undefined" && module.exports) {',
            '    module.exports = { loadFrModule, FrRuntimeError, FrExitError, config };',
            '}',
        ])

    return '\n'.join(js_lines)

def generate_html_template(wasm_filename: str, js_glue_code: str, wasm_base64: str = "", title: str = "", metadata: dict = None) -> str:
    """Generate an HTML file with inlined JavaScript glue code and optionally embedded WASM."""
    # Serialize metadata as JSON
    metadata_json = json.dumps(metadata) if metadata else '{}'
    
    # If WASM is provided as base64, use it; otherwise load from file
    if wasm_base64:
        wasm_loader = f'''            const wasmBase64 = '{wasm_base64}';
            const wasmBytes = Uint8Array.from(atob(wasmBase64), c => c.charCodeAt(0));
            const wasmBuffer = wasmBytes.buffer;
            const wasmPath = null; // Not needed since we have bytes
            
            // Set metadata before loading module
            metadata = {metadata_json};
            
            const fr = await loadFrModuleFromBytes(wasmBuffer, {{
                outputElementId: 'output',
                autoFlush: true
            }});'''
    else:
        wasm_loader = f'''            const wasmPath = './{wasm_filename}';
            
            // Set metadata before loading module
            metadata = {metadata_json};
            
            const fr = await loadFrModule(wasmPath, {{
                outputElementId: 'output',
                autoFlush: true
            }});'''

    return f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body id="body">
    <div id="output"></div>
    <script>
// Fr WASM Runtime - Auto-generated JavaScript glue
// Only includes functions used by this specific module
{js_glue_code}

// Load and run Fr WASM module
(async function() {{
    const output = document.getElementById('body');
    try {{
{wasm_loader}

        const result = fr.run();
        if (!result.success) {{
            output.innerHTML += '<span class="error">\\nProgram exited with code ' + result.exitCode + '</span>';
        }}
    }} catch (e) {{
        output.innerHTML += '<span class="error">Error: ' + e.message + '</span>';
        console.error(e);
    }}
}})();
    </script>
</body>
</html>
'''

def get_all_import_names() -> Set[str]:
    """Get all available import function names."""
    all_funcs = {**JS_RUNTIME_FUNCTIONS, **JS_WEB_FUNCTIONS}
    return set(all_funcs.keys())

def get_wasm_import_declaration(name: str) -> Optional[str]:
    """Get the WAT import declaration for a function."""
    all_funcs = {**JS_RUNTIME_FUNCTIONS, **JS_WEB_FUNCTIONS}
    if name not in all_funcs:
        return None
    func = all_funcs[name]
    sig = func.get('wasm_signature', '')
    if sig:
        return f'(import "env" "{name}" (func ${name} {sig}))'
    return f'(import "env" "{name}" (func ${name}))'
