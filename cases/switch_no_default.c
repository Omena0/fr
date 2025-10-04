// !no match

void main() {
    int x = 10
    
    // Switch without default - no output expected if no match
    switch (x) {
        case 1:
            println("one")
        case 2:
            println("two")
    }
    
    println("no match")
}
