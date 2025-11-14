use wasmtime::*;
use std::env;
use std::fs;
use std::sync::{Arc, Mutex};

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
        let s = value.to_string();
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
        s.parse::<i64>().unwrap_or(0)
    });

    // Placeholder list operations
    let list_new = Func::wrap(&mut store, |_: Caller<'_, ()>| -> i32 { 0 });
    let list_append = Func::wrap(&mut store, |_: Caller<'_, ()>, _list: i32, _value: i64| {});
    let list_get = Func::wrap(&mut store, |_: Caller<'_, ()>, _list: i32, _index: i64| -> i64 { 0 });
    let list_set = Func::wrap(&mut store, |_: Caller<'_, ()>, _list: i32, _index: i64, _value: i64| {});
    let list_len = Func::wrap(&mut store, |_: Caller<'_, ()>, _list: i32| -> i64 { 0 });

    let mut linker = Linker::new(&engine);
    linker.define(&store, "env", "print", print)?;
    linker.define(&store, "env", "println", println)?;
    linker.define(&store, "env", "i64_to_str", i64_to_str)?;
    linker.define(&store, "env", "f64_to_str", f64_to_str)?;
    linker.define(&store, "env", "sqrt", sqrt_fn)?;
    linker.define(&store, "env", "str_concat", str_concat)?;
    linker.define(&store, "env", "str_to_i64", str_to_i64)?;
    linker.define(&store, "env", "list_new", list_new)?;
    linker.define(&store, "env", "list_append", list_append)?;
    linker.define(&store, "env", "list_get", list_get)?;
    linker.define(&store, "env", "list_set", list_set)?;
    linker.define(&store, "env", "list_len", list_len)?;

    let instance = linker.instantiate(&mut store, &module)?;
    let main = instance.get_typed_func::<(), ()>(&mut store, "main")?;

    main.call(&mut store, ())?;

    Ok(())
}
