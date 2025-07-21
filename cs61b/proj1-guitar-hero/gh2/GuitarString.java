package gh2;

import deque.ArrayDeque;
import deque.Deque;

public class GuitarString {
    private static final int SR = 44100;
    private static final double DECAY = .996;

    private final Deque<Double> buffer;

    public GuitarString(double frequency) {
        this.buffer = new ArrayDeque<>();
        int capacity = (int) Math.round(SR / frequency);
        for (int i = 0; i < capacity; i++) {
            this.buffer.addLast(0.0);
        }
    }

    public void pluck() {
        int size = this.buffer.size();
        for (int i = 0; i < size; i++) {
            this.buffer.removeFirst();
            double r = Math.random() - 0.5;
            this.buffer.addLast(r);
        }
    }

    public void tic() {
        double first = this.buffer.removeFirst();
        double second = this.buffer.get(0);
        double newSample = DECAY * 0.5 * (first + second);
        this.buffer.addLast(newSample);
    }

    public double sample() {
        return this.buffer.get(0);
    }
}