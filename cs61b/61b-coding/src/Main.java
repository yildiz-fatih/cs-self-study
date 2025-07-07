public class Main {

    public static void main(String[] args) {
        IntList list = new IntList(15, null);
        list = new IntList(10, list);
        list = new IntList(5, list);

        System.out.println(list.size());
        System.out.println(list.get(1));
    }
}
