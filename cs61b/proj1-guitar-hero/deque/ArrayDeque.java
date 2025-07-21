package deque;

import java.util.Iterator;
import java.util.NoSuchElementException;
import java.util.Objects;

public class ArrayDeque<T> implements Deque<T>, Iterable<T> {
    private static final int MIN_CAPACITY = 8;
    private T[] items;
    private int nextFirst, nextLast, size;

    public ArrayDeque() {
        this.items = (T[]) new Object[MIN_CAPACITY];
        this.nextFirst = 4;
        this.nextLast = 5;
        this.size = 0;
    }

    private boolean isFull() {
        return size == items.length;
    }

    private boolean shouldShrink() {
        return items.length >= MIN_CAPACITY * 2 && size < items.length / 4;
    }

    private void resize(int newCapacity) {
        T[] resized = (T[]) new Object[newCapacity]; // new array, new size

        int currIndex = (nextFirst + 1) % items.length;
        for (int i = 0; i < size; i += 1) { // copy all items
            resized[i] = items[currIndex];
            currIndex = (currIndex + 1) % items.length;
        }
        // reset
        this.items = resized;
        nextFirst = newCapacity - 1;
        nextLast = size;
    }

    @Override
    public void addFirst(T item) {
        if (isFull()) {
            resize(items.length * 2);
        }

        items[nextFirst] = item;
        nextFirst = (nextFirst - 1 + items.length) % items.length;
        size += 1;
    }

    @Override
    public void addLast(T item) {
        if (isFull()) {
            resize(items.length * 2);
        }

        items[nextLast] = item;
        nextLast = (nextLast + 1) % items.length;
        size += 1;
    }

    @Override
    public int size() {
        return size;
    }

    @Override
    public void printDeque() {
        int currIndex = (nextFirst + 1) % items.length;
        for (int i = 0; i < size; i += 1) {
            System.out.print(items[currIndex] + " ");
            currIndex = (currIndex + 1) % items.length;
        }
        System.out.println();
    }

    @Override
    public T removeFirst() {
        if (isEmpty()) {
            return null;
        }

        int firstIndex = (nextFirst + 1) % items.length;
        T firstItem = items[firstIndex];
        items[firstIndex] = null;

        nextFirst = firstIndex;
        size -= 1;

        if (shouldShrink()) {
            resize(items.length / 2);
        }

        return firstItem;
    }

    @Override
    public T removeLast() {
        if (isEmpty()) {
            return null;
        }

        int lastIndex = (nextLast - 1 + items.length) % items.length;
        T lastItem = items[lastIndex];
        items[lastIndex] = null;

        nextLast = lastIndex;
        size -= 1;

        if (shouldShrink()) {
            resize(items.length / 2);
        }

        return lastItem;
    }

    @Override
    public T get(int index) {
        if (index < 0 || index >= size) {
            return null;
        }

        return items[(nextFirst + 1 + index) % items.length];
    }

    @Override
    public Iterator<T> iterator() {
        return new ArrayDequeIterator();
    }

    private class ArrayDequeIterator implements Iterator<T> {
        private int index = 0;

        @Override
        public boolean hasNext() {
            return index < size;
        }

        @Override
        public T next() {
            if (!hasNext()) {
                throw new NoSuchElementException();
            }
            T item = get(index);
            index++;
            return item;
        }
    }

    @Override
    public boolean equals(Object o) {
        if (this == o) {
            return true;
        }
        if (!(o instanceof Deque<?>)) {
            return false;
        }

        Deque<?> other = (Deque<?>) o;
        if (other.size() != this.size) {
            return false;
        }

        for (int i = 0; i < size; i++) {
            T thisItem = this.get(i);
            Object otherItem = other.get(i);

            if (!Objects.equals(thisItem, otherItem)) {
                return false;
            }
        }

        return true;
    }
}