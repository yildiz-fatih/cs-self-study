package deque;

import java.util.Iterator;
import java.util.NoSuchElementException;
import java.util.Objects;

public class LinkedListDeque<T> implements Deque<T>, Iterable<T> {

    class Node {
        T value;
        Node prev, next;

        public Node(T value, Node prev, Node next) {
            this.value = value;
            this.prev = prev;
            this.next = next;
        }
    }

    private Node sentinel;
    private int size;

    public LinkedListDeque() {
        sentinel = new Node(null, null, null);
        sentinel.next = sentinel;
        sentinel.prev = sentinel;
        this.size = 0;
    }

    @Override
    public void addFirst(T item) {
        Node n =  new Node(item, sentinel, sentinel.next);
        sentinel.next.prev = n;
        sentinel.next = n;

        size += 1;
    }

    @Override
    public void addLast(T item) {
        Node n = new Node(item, sentinel.prev, sentinel);
        sentinel.prev.next = n;
        sentinel.prev = n;

        size += 1;
    }

    @Override
    public int size() {
        return size;
    }

    @Override
    public void printDeque() {
        Node p = sentinel.next;
        for (int i = 0; i < size; i += 1) {
            System.out.print(p.value + " ");
            p = p.next;
        }
        System.out.println();
    }

    @Override
    public T removeFirst() {
        if (isEmpty()) {
            return null;
        }

        T item = sentinel.next.value;
        sentinel.next = sentinel.next.next;
        sentinel.next.prev = sentinel;

        size -= 1;

        return item;
    }

    @Override
    public T removeLast() {
        if (isEmpty()) {
            return null;
        }

        T item = sentinel.prev.value;
        sentinel.prev = sentinel.prev.prev;
        sentinel.prev.next = sentinel;

        size -= 1;

        return item;
    }

    @Override
    public T get(int index) {
        if (index + 1 > size) {
            return null;
        }

        Node p = sentinel.next;
        for (int i = 0; i < index; i += 1) {
            p = p.next;
        }

        return p.value;
    }

    public T getRecursive(int index) {
        return getRecursiveHelper(index, sentinel.next);
    }

    private T getRecursiveHelper(int index, Node current) {
        if (index == 0) {
            return (T) current.value;
        } else {
            return getRecursiveHelper(index - 1, current.next);
        }
    }


    @Override
    public Iterator<T> iterator() {
        return new LinkedListDequeIterator();
    }

    private class LinkedListDequeIterator implements Iterator<T> {
        private Node current = sentinel.next;
        private int count = 0;

        @Override
        public boolean hasNext() {
            return count < size;
        }

        @Override
        public T next() {
            if (!hasNext()) {
                throw new NoSuchElementException();
            }
            T val = current.value;
            current = current.next;
            count++;
            return val;
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