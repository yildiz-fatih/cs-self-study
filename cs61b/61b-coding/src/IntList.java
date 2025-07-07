/* a linked-list like dynamic array structure */
public class IntList {
    private int value;
    private IntList next;

    public IntList(int value, IntList next) {
        this.value = value;
        this.next = next;
    }

    public int get(int index) {
        // recursive
        if (index == 0) { return value; }
        return next.get(index - 1);
    }

    public int size() {
        // iterative
        /*
        int size = 0;
        IntList p = this;
        while (p != null) {
            size += 1;
            p = p.next;
        }
        return size;
         */
        // recursive
        if (next == null) { return 1; }
        return 1 + this.next.size();
    }
}
