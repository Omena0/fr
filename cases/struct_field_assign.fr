// !10\n30

struct Point {
    int x
    int y
}

void main() {
    Point p = Point(10, 20)
    println(p.x)
    p.y = 30
    println(p.y)
}
