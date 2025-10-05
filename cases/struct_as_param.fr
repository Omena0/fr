// !Point: 5, 10

struct Point {
    int x
    int y
}

void printPoint(Point p) {
    println(f"Point: {p.x}, {p.y}")
}

void main() {
    Point p = Point(5, 10)
    printPoint(p)
}
