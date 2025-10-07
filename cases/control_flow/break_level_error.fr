// !"break 5" exceeds loop depth 2

void main() {
    for (i, 3) {
        for (j, 3) {
            break 5
        }
    }
}
