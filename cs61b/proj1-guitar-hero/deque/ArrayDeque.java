package deque;

public class ArrayDeque<T> implements Deque<T> {
    private T[] items;
    private int nextFirst;
    private int nextLast;
    private int size;

    public ArrayDeque() {
        this.items = (T[]) new Object[8];
        this.nextFirst = 4;
        this.nextLast = 5;
        this.size = 0;
    }

    @Override
    public void addFirst(T item) {
        items[nextFirst] = item;
        nextFirst = (nextFirst - 1 + items.length) % items.length;
        size += 1;
    }

    @Override
    public void addLast(T item) {
        items[nextLast] = item;
        nextLast = (nextLast + 1) % items.length;
        size += 1;
    }

    @Override
    public boolean isEmpty() {
        return size == 0;
    }

    @Override
    public int size() {
        return size;
    }

    @Override
    public void printDeque() {
        int curr = (nextFirst + 1) % items.length;
        for (int i = 0; i < size; i += 1) {
            System.out.print(items[curr] + " ");
            curr = (curr + 1) % items.length;
        }
        System.out.println();
    }

    @Override
    public T removeFirst() {
        if (isEmpty()) return null;

        int firstIndex = (nextFirst + 1) % items.length;
        T firstItem = items[firstIndex];
        items[firstIndex] = null;

        nextFirst = firstIndex;
        size -= 1;

        return firstItem;
    }

    @Override
    public T removeLast() {
        if (isEmpty()) return null;

        int lastIndex = (nextLast - 1 + items.length) % items.length;
        T lastItem = items[lastIndex];
        items[lastIndex] = null;

        nextLast = lastIndex;
        size -= 1;

        return lastItem;
    }

    @Override
    public T get(int index) {
        if (index < 0 || index >= size) return null;

        return items[(nextFirst + 1 + index) % items.length];
    }
}
