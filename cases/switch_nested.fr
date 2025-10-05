// !positive even

void main() {
    int x = 4
    
    switch (x) {
        case 1, 3, 5, 7, 9:
            switch (x) {
                case 1:
                    println("positive odd small")
                default:
                    println("positive odd")
            }
        case 2, 4, 6, 8:
            switch (x) {
                case 2:
                    println("positive even small")
                default:
                    println("positive even")
            }
        default:
            println("other")
    }
}
