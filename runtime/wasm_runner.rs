use wasmtime::*;
use std::env;
use std::fs;
use std::sync::{Arc, Mutex};
use std::collections::HashSet;
use std::io::{Read, Write};

fn main() -> Result<()> {
    let args: Vec<String> = env::args().collect();
    if args.len() < 2 {
        eprintln!("Usage: {} <file.wasm>", args[0]);
        std::process::exit(1);
    }

    let wasm_path = &args[1];
    let wasm_bytes = fs::read(wasm_path)?;

    let engine = Engine::default();
    let mut store = Store::new(&engine, ());
    let module = Module::new(&engine, &wasm_bytes)?;

    // String memory management
    let string_offset = Arc::new(Mutex::new(1024usize));
    
    // Shared storage for lists and sets
    let lists: Arc<Mutex<Vec<Vec<i64>>>> = Arc::new(Mutex::new(Vec::new()));
    let sets: Arc<Mutex<Vec<HashSet<i64>>>> = Arc::new(Mutex::new(Vec::new()));

    let print = Func::wrap(&mut store, |mut caller: Caller<'_, ()>, ptr: i32, len: i32| {
        let mem = caller.get_export("memory").unwrap().into_memory().unwrap();
        let data = mem.data(&caller);
        let slice = &data[ptr as usize..(ptr + len) as usize];
        let s = String::from_utf8_lossy(slice);
        print!("{}", s);
    });

    let println = Func::wrap(&mut store, |mut caller: Caller<'_, ()>, ptr: i32, len: i32| {
        let mem = caller.get_export("memory").unwrap().into_memory().unwrap();
        let data = mem.data(&caller);
        let slice = &data[ptr as usize..(ptr + len) as usize];
        let s = String::from_utf8_lossy(slice);
        println!("{}", s);
    });

    let offset_clone = string_offset.clone();
    let i64_to_str = Func::wrap(&mut store, move |mut caller: Caller<'_, ()>, value: i64| -> (i32, i32) {
        let s = value.to_string();
        let bytes = s.as_bytes();
        let len = bytes.len() as i32;
        
        let mem = caller.get_export("memory").unwrap().into_memory().unwrap();
        let mut offset = offset_clone.lock().unwrap();
        let ptr = *offset as i32;
        *offset += bytes.len();
        
        // Write string data to memory
        mem.write(&mut caller, ptr as usize, bytes).unwrap();
        
        (ptr, len)
    });

    let offset_clone = string_offset.clone();
    let f64_to_str = Func::wrap(&mut store, move |mut caller: Caller<'_, ()>, value: f64| -> (i32, i32) {
        let s = if value.fract() == 0.0 && value.is_finite() {
            format!("{:.1}", value)
        } else {
            value.to_string()
        };
        let bytes = s.as_bytes();
        let len = bytes.len() as i32;

        let mem = caller.get_export("memory").unwrap().into_memory().unwrap();
        let mut offset = offset_clone.lock().unwrap();
        let ptr = *offset as i32;
        *offset += bytes.len();

        mem.write(&mut caller, ptr as usize, bytes).unwrap();

        (ptr, len)
    });

    let offset_clone = string_offset.clone();
    let bool_to_str = Func::wrap(&mut store, move |mut caller: Caller<'_, ()>, value: i32| -> (i32, i32) {
        let s = if value != 0 { "true" } else { "false" };
        let bytes = s.as_bytes();
        let len = bytes.len() as i32;

        let mem = caller.get_export("memory").unwrap().into_memory().unwrap();
        let mut offset = offset_clone.lock().unwrap();
        let ptr = *offset as i32;
        *offset += bytes.len();

        mem.write(&mut caller, ptr as usize, bytes).unwrap();

        (ptr, len)
    });

    // List to string conversion
    let offset_clone = string_offset.clone();
    let lists_clone = lists.clone();
    let list_to_str = Func::wrap(&mut store, move |mut caller: Caller<'_, ()>, list_id: i32| -> (i32, i32) {
        let lists_lock = lists_clone.lock().unwrap();
        let s = if let Some(list_vec) = lists_lock.get(list_id as usize) {
            let elements: Vec<String> = list_vec.iter().map(|v| v.to_string()).collect();
            format!("[{}]", elements.join(", "))
        } else {
            "[]".to_string()
        };
        
        let bytes = s.as_bytes();
        let len = bytes.len() as i32;

        let mem = caller.get_export("memory").unwrap().into_memory().unwrap();
        let mut offset = offset_clone.lock().unwrap();
        let ptr = *offset as i32;
        *offset += bytes.len();

        mem.write(&mut caller, ptr as usize, bytes).unwrap();

        (ptr, len)
    });

    let sqrt_fn = Func::wrap(&mut store, |_caller: Caller<'_, ()>, value: f64| -> f64 {
        value.sqrt()
    });

    let offset_clone = string_offset.clone();
    let str_concat = Func::wrap(&mut store, move |mut caller: Caller<'_, ()>, 
                                                    ptr1: i32, len1: i32, 
                                                    ptr2: i32, len2: i32| -> (i32, i32) {
        let mem = caller.get_export("memory").unwrap().into_memory().unwrap();
        let data = mem.data(&caller);
        
        let slice1 = &data[ptr1 as usize..(ptr1 + len1) as usize];
        let slice2 = &data[ptr2 as usize..(ptr2 + len2) as usize];
        
        let mut result = Vec::with_capacity((len1 + len2) as usize);
        result.extend_from_slice(slice1);
        result.extend_from_slice(slice2);
        
        let mut offset = offset_clone.lock().unwrap();
        let ptr = *offset as i32;
        *offset += result.len();
        
        mem.write(&mut caller, ptr as usize, &result).unwrap();
        
        (ptr, result.len() as i32)
    });    let str_to_i64 = Func::wrap(&mut store, |mut caller: Caller<'_, ()>, ptr: i32, len: i32| -> i64 {
        let mem = caller.get_export("memory").unwrap().into_memory().unwrap();
        let data = mem.data(&caller);
        let slice = &data[ptr as usize..(ptr + len) as usize];
        let s = String::from_utf8_lossy(slice);
        // Try parsing as float first, then truncate to int
        if let Ok(f) = s.parse::<f64>() {
            f.trunc() as i64
        } else {
            s.parse::<i64>().unwrap_or(0)
        }
    });

    let str_to_f64 = Func::wrap(&mut store, |mut caller: Caller<'_, ()>, ptr: i32, len: i32| -> f64 {
        let mem = caller.get_export("memory").unwrap().into_memory().unwrap();
        let data = mem.data(&caller);
        let slice = &data[ptr as usize..(ptr + len) as usize];
        let s = String::from_utf8_lossy(slice);
        s.parse::<f64>().unwrap_or(0.0)
    });

    let offset_clone = string_offset.clone();
    let str_upper = Func::wrap(&mut store, move |mut caller: Caller<'_, ()>, ptr: i32, len: i32| -> (i32, i32) {
        let mem = caller.get_export("memory").unwrap().into_memory().unwrap();
        
        // Read the string data
        let s = {
            let data = mem.data(&caller);
            let slice = &data[ptr as usize..(ptr + len) as usize];
            String::from_utf8_lossy(slice).to_string()
        };
        
        let upper = s.to_uppercase();
        let bytes = upper.as_bytes();
        
        let mut offset = offset_clone.lock().unwrap();
        let new_ptr = *offset as i32;
        *offset += bytes.len();
        
        mem.write(&mut caller, new_ptr as usize, bytes).unwrap();
        (new_ptr, bytes.len() as i32)
    });

    let offset_clone = string_offset.clone();
    let str_lower = Func::wrap(&mut store, move |mut caller: Caller<'_, ()>, ptr: i32, len: i32| -> (i32, i32) {
        let mem = caller.get_export("memory").unwrap().into_memory().unwrap();
        
        let s = {
            let data = mem.data(&caller);
            let slice = &data[ptr as usize..(ptr + len) as usize];
            String::from_utf8_lossy(slice).to_string()
        };
        
        let lower = s.to_lowercase();
        let bytes = lower.as_bytes();
        
        let mut offset = offset_clone.lock().unwrap();
        let new_ptr = *offset as i32;
        *offset += bytes.len();
        
        mem.write(&mut caller, new_ptr as usize, bytes).unwrap();
        (new_ptr, bytes.len() as i32)
    });

    let offset_clone = string_offset.clone();
    let str_strip = Func::wrap(&mut store, move |mut caller: Caller<'_, ()>, ptr: i32, len: i32| -> (i32, i32) {
        let mem = caller.get_export("memory").unwrap().into_memory().unwrap();
        
        let s = {
            let data = mem.data(&caller);
            let slice = &data[ptr as usize..(ptr + len) as usize];
            String::from_utf8_lossy(slice).to_string()
        };
        
        let stripped = s.trim();
        let bytes = stripped.as_bytes();
        
        let mut offset = offset_clone.lock().unwrap();
        let new_ptr = *offset as i32;
        *offset += bytes.len();
        
        mem.write(&mut caller, new_ptr as usize, bytes).unwrap();
        (new_ptr, bytes.len() as i32)
    });

    let offset_clone = string_offset.clone();
    let str_replace = Func::wrap(&mut store, move |mut caller: Caller<'_, ()>, 
                                                     str_ptr: i32, str_len: i32,
                                                     old_ptr: i32, old_len: i32,
                                                     new_ptr: i32, new_len: i32| -> (i32, i32) {
        let mem = caller.get_export("memory").unwrap().into_memory().unwrap();
        
        let (s, old, new) = {
            let data = mem.data(&caller);
            let str_slice = &data[str_ptr as usize..(str_ptr + str_len) as usize];
            let old_slice = &data[old_ptr as usize..(old_ptr + old_len) as usize];
            let new_slice = &data[new_ptr as usize..(new_ptr + new_len) as usize];
            (
                String::from_utf8_lossy(str_slice).to_string(),
                String::from_utf8_lossy(old_slice).to_string(),
                String::from_utf8_lossy(new_slice).to_string()
            )
        };
        
        let result = s.replace(&old, &new);
        let bytes = result.as_bytes();
        
        let mut offset = offset_clone.lock().unwrap();
        let result_ptr = *offset as i32;
        *offset += bytes.len();
        
        mem.write(&mut caller, result_ptr as usize, bytes).unwrap();
        (result_ptr, bytes.len() as i32)
    });

    let offset_clone = string_offset.clone();
    let str_get = Func::wrap(&mut store, move |mut caller: Caller<'_, ()>, ptr: i32, len: i32, index: i64| -> (i32, i32) {
        let mem = caller.get_export("memory").unwrap().into_memory().unwrap();
        
        let s = {
            let data = mem.data(&caller);
            let slice = &data[ptr as usize..(ptr + len) as usize];
            String::from_utf8_lossy(slice).to_string()
        };
        
        let chars: Vec<char> = s.chars().collect();
        let idx = index as usize;
        
        if idx < chars.len() {
            let ch = chars[idx].to_string();
            let bytes = ch.as_bytes();
            
            let mut offset = offset_clone.lock().unwrap();
            let char_ptr = *offset as i32;
            *offset += bytes.len();
            
            mem.write(&mut caller, char_ptr as usize, bytes).unwrap();
            (char_ptr, bytes.len() as i32)
        } else {
            (0, 0)
        }
    });

    let str_contains = Func::wrap(&mut store, |mut caller: Caller<'_, ()>, 
                                                haystack_ptr: i32, haystack_len: i32,
                                                needle_ptr: i32, needle_len: i32| -> i32 {
        let mem = caller.get_export("memory").unwrap().into_memory().unwrap();
        let data = mem.data(&caller);
        
        let haystack_slice = &data[haystack_ptr as usize..(haystack_ptr + haystack_len) as usize];
        let needle_slice = &data[needle_ptr as usize..(needle_ptr + needle_len) as usize];
        
        let haystack = String::from_utf8_lossy(haystack_slice);
        let needle = String::from_utf8_lossy(needle_slice);
        
        if haystack.contains(needle.as_ref()) { 1 } else { 0 }
    });

    let offset_clone = string_offset.clone();
    let str_join = Func::wrap(&mut store, move |mut caller: Caller<'_, ()>, 
                                                 _sep_ptr: i32, _sep_len: i32,
                                                 _list_ptr: i32| -> (i32, i32) {
        // Placeholder for list join - returns empty string for now
        let mem = caller.get_export("memory").unwrap().into_memory().unwrap();
        let mut offset = offset_clone.lock().unwrap();
        let ptr = *offset as i32;
        *offset += 1;
        mem.write(&mut caller, ptr as usize, b"").unwrap();
        (ptr, 0)
    });

    let str_split = Func::wrap(&mut store, |_caller: Caller<'_, ()>, 
                                             _str_ptr: i32, _str_len: i32,
                                             _sep_ptr: i32, _sep_len: i32| -> i32 {
        // Placeholder for string split - returns empty list for now
        0
    });

    // List operations - using Vec stored in a shared state
    // (lists Arc was created at the top of main)
    
    let lists_clone = lists.clone();
    let list_new = Func::wrap(&mut store, move |_: Caller<'_, ()>| -> i32 {
        let mut lists_lock = lists_clone.lock().unwrap();
        lists_lock.push(Vec::new());
        (lists_lock.len() - 1) as i32
    });
    
    let lists_clone = lists.clone();
    let list_append = Func::wrap(&mut store, move |_: Caller<'_, ()>, list: i32, value: i64| -> i32 {
        let mut lists_lock = lists_clone.lock().unwrap();
        if let Some(list_vec) = lists_lock.get_mut(list as usize) {
            list_vec.push(value);
        }
        list
    });
    
    let lists_clone = lists.clone();
    let list_get = Func::wrap(&mut store, move |_: Caller<'_, ()>, list: i32, index: i64| -> i64 {
        let lists_lock = lists_clone.lock().unwrap();
        if let Some(list_vec) = lists_lock.get(list as usize) {
            if (index as usize) < list_vec.len() {
                return list_vec[index as usize];
            }
        }
        0
    });
    
    let lists_clone = lists.clone();
    let list_set = Func::wrap(&mut store, move |_: Caller<'_, ()>, list: i32, index: i64, value: i64| -> i32 {
        let mut lists_lock = lists_clone.lock().unwrap();
        if let Some(list_vec) = lists_lock.get_mut(list as usize) {
            if (index as usize) < list_vec.len() {
                list_vec[index as usize] = value;
            }
        }
        list
    });
    
    let lists_clone = lists.clone();
    let list_len = Func::wrap(&mut store, move |_: Caller<'_, ()>, list: i32| -> i64 {
        let lists_lock = lists_clone.lock().unwrap();
        if let Some(list_vec) = lists_lock.get(list as usize) {
            list_vec.len() as i64
        } else {
            0
        }
    });
    
    let lists_clone = lists.clone();
    let list_pop = Func::wrap(&mut store, move |_: Caller<'_, ()>, list: i32| -> (i32, i64) {
        let mut lists_lock = lists_clone.lock().unwrap();
        if let Some(list_vec) = lists_lock.get_mut(list as usize) {
            let value = list_vec.pop().unwrap_or(0);
            (list, value)
        } else {
            (list, 0)
        }
    });

    // Set to string conversion
    let offset_clone = string_offset.clone();
    let sets_clone = sets.clone();
    let set_to_str = Func::wrap(&mut store, move |mut caller: Caller<'_, ()>, set_id: i32| -> (i32, i32) {
        let sets_lock = sets_clone.lock().unwrap();
        let s = if let Some(set_ref) = sets_lock.get(set_id as usize) {
            let mut elements: Vec<String> = set_ref.iter().map(|v| v.to_string()).collect();
            elements.sort();
            format!("{{{}}}", elements.join(", "))
        } else {
            "{}".to_string()
        };
        
        let bytes = s.as_bytes();
        let len = bytes.len() as i32;

        let mem = caller.get_export("memory").unwrap().into_memory().unwrap();
        let mut offset = offset_clone.lock().unwrap();
        let ptr = *offset as i32;
        *offset += bytes.len();

        mem.write(&mut caller, ptr as usize, bytes).unwrap();

        (ptr, len)
    });

    // Set operations - using HashSet stored in a shared state
    
    let sets_clone = sets.clone();
    let set_new = Func::wrap(&mut store, move |_: Caller<'_, ()>| -> i32 {
        let mut sets_lock = sets_clone.lock().unwrap();
        sets_lock.push(HashSet::new());
        (sets_lock.len() - 1) as i32
    });
    
    let sets_clone = sets.clone();
    let set_add = Func::wrap(&mut store, move |_: Caller<'_, ()>, set_id: i32, value: i64| -> i32 {
        let mut sets_lock = sets_clone.lock().unwrap();
        if let Some(set) = sets_lock.get_mut(set_id as usize) {
            set.insert(value);
        }
        set_id
    });
    
    let sets_clone = sets.clone();
    let set_remove = Func::wrap(&mut store, move |_: Caller<'_, ()>, set_id: i32, value: i64| -> i32 {
        let mut sets_lock = sets_clone.lock().unwrap();
        if let Some(set) = sets_lock.get_mut(set_id as usize) {
            set.remove(&value);
        }
        set_id
    });
    
    let sets_clone = sets.clone();
    let set_contains = Func::wrap(&mut store, move |_: Caller<'_, ()>, set_id: i32, value: i64| -> i32 {
        let sets_lock = sets_clone.lock().unwrap();
        if let Some(set) = sets_lock.get(set_id as usize) {
            if set.contains(&value) { 1 } else { 0 }
        } else {
            0
        }
    });
    
    let sets_clone = sets.clone();
    let set_len = Func::wrap(&mut store, move |_: Caller<'_, ()>, set_id: i32| -> i64 {
        let sets_lock = sets_clone.lock().unwrap();
        if let Some(set) = sets_lock.get(set_id as usize) {
            set.len() as i64
        } else {
            0
        }
    });

    // Math functions
    let round_f64 = Func::wrap(&mut store, |_: Caller<'_, ()>, value: f64| -> f64 {
        value.round()
    });
    
    let floor_f64 = Func::wrap(&mut store, |_: Caller<'_, ()>, value: f64| -> f64 {
        value.floor()
    });
    
    let ceil_f64 = Func::wrap(&mut store, |_: Caller<'_, ()>, value: f64| -> f64 {
        value.ceil()
    });

    // File I/O operations - basic implementation
    let file_handles: Arc<Mutex<Vec<Option<fs::File>>>> = Arc::new(Mutex::new(Vec::new()));
    
    let file_handles_clone = file_handles.clone();
    let file_open = Func::wrap(&mut store, move |mut caller: Caller<'_, ()>, 
                                                  path_ptr: i32, path_len: i32,
                                                  mode_ptr: i32, mode_len: i32| -> i32 {
        let mem = caller.get_export("memory").unwrap().into_memory().unwrap();
        let data = mem.data(&caller);
        
        let path_slice = &data[path_ptr as usize..(path_ptr + path_len) as usize];
        let mode_slice = &data[mode_ptr as usize..(mode_ptr + mode_len) as usize];
        
        let path = String::from_utf8_lossy(path_slice).to_string();
        let mode = String::from_utf8_lossy(mode_slice).to_string();
        
        let file_result = match mode.as_str() {
            "r" => fs::File::open(&path),
            "w" => fs::File::create(&path),
            "a" => fs::OpenOptions::new().append(true).create(true).open(&path),
            _ => return -1,
        };
        
        match file_result {
            Ok(file) => {
                let mut handles = file_handles_clone.lock().unwrap();
                handles.push(Some(file));
                (handles.len() - 1) as i32
            },
            Err(_) => -1,
        }
    });
    
    let file_handles_clone = file_handles.clone();
    let offset_clone = string_offset.clone();
    let file_read = Func::wrap(&mut store, move |mut caller: Caller<'_, ()>, fd: i32| -> (i32, i32) {
        let mut handles = file_handles_clone.lock().unwrap();
        
        if let Some(Some(file)) = handles.get_mut(fd as usize) {
            let mut buffer = Vec::new();
            if file.read_to_end(&mut buffer).is_ok() {
                let len = buffer.len() as i32;
                
                let mem = caller.get_export("memory").unwrap().into_memory().unwrap();
                let mut offset = offset_clone.lock().unwrap();
                let ptr = *offset as i32;
                *offset += buffer.len();
                
                mem.write(&mut caller, ptr as usize, &buffer).unwrap();
                return (ptr, len);
            }
        }
        (0, 0)
    });
    
    let file_handles_clone = file_handles.clone();
    let file_write = Func::wrap(&mut store, move |mut caller: Caller<'_, ()>, 
                                                   fd: i32, ptr: i32, len: i32| {
        let mem = caller.get_export("memory").unwrap().into_memory().unwrap();
        let data = mem.data(&caller);
        let slice = &data[ptr as usize..(ptr + len) as usize];
        
        let mut handles = file_handles_clone.lock().unwrap();
        if let Some(Some(file)) = handles.get_mut(fd as usize) {
            let _ = file.write_all(slice);
        }
    });
    
    let file_handles_clone = file_handles.clone();
    let file_close = Func::wrap(&mut store, move |_: Caller<'_, ()>, fd: i32| {
        let mut handles = file_handles_clone.lock().unwrap();
        if let Some(slot) = handles.get_mut(fd as usize) {
            *slot = None;
        }
    });
    
    // Process control
    let exit_process = Func::wrap::<_, _, ()>(&mut store, |_: Caller<'_, ()>, code: i32| {
        std::process::exit(code);
    });

    let mut linker = Linker::new(&engine);
    linker.define(&store, "env", "print", print)?;
    linker.define(&store, "env", "println", println)?;
    linker.define(&store, "env", "i64_to_str", i64_to_str)?;
    linker.define(&store, "env", "f64_to_str", f64_to_str)?;
    linker.define(&store, "env", "bool_to_str", bool_to_str)?;
    linker.define(&store, "env", "list_to_str", list_to_str)?;
    linker.define(&store, "env", "set_to_str", set_to_str)?;
    linker.define(&store, "env", "sqrt", sqrt_fn)?;
    linker.define(&store, "env", "str_concat", str_concat)?;
    linker.define(&store, "env", "str_to_i64", str_to_i64)?;
    linker.define(&store, "env", "str_to_f64", str_to_f64)?;
    linker.define(&store, "env", "str_upper", str_upper)?;
    linker.define(&store, "env", "str_lower", str_lower)?;
    linker.define(&store, "env", "str_strip", str_strip)?;
    linker.define(&store, "env", "str_replace", str_replace)?;
    linker.define(&store, "env", "str_get", str_get)?;
    linker.define(&store, "env", "str_contains", str_contains)?;
    linker.define(&store, "env", "str_join", str_join)?;
    linker.define(&store, "env", "str_split", str_split)?;
    linker.define(&store, "env", "list_new", list_new)?;
    linker.define(&store, "env", "list_append", list_append)?;
    linker.define(&store, "env", "list_get", list_get)?;
    linker.define(&store, "env", "list_set", list_set)?;
    linker.define(&store, "env", "list_len", list_len)?;
    linker.define(&store, "env", "list_pop", list_pop)?;
    linker.define(&store, "env", "set_new", set_new)?;
    linker.define(&store, "env", "set_add", set_add)?;
    linker.define(&store, "env", "set_remove", set_remove)?;
    linker.define(&store, "env", "set_contains", set_contains)?;
    linker.define(&store, "env", "set_len", set_len)?;
    linker.define(&store, "env", "round_f64", round_f64)?;
    linker.define(&store, "env", "floor_f64", floor_f64)?;
    linker.define(&store, "env", "ceil_f64", ceil_f64)?;
    linker.define(&store, "env", "file_open", file_open)?;
    linker.define(&store, "env", "file_read", file_read)?;
    linker.define(&store, "env", "file_write", file_write)?;
    linker.define(&store, "env", "file_close", file_close)?;
    linker.define(&store, "env", "exit_process", exit_process)?;

    let instance = linker.instantiate(&mut store, &module)?;
    let main = instance.get_typed_func::<(), ()>(&mut store, "main")?;

    main.call(&mut store, ())?;

    Ok(())
}
