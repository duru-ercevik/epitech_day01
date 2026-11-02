import java.util.ArrayList;

class Ex05 {
    public static ArrayList<String> myGetArgs(String... var) {
        ArrayList<String> list = new ArrayList<>();
        for (String s : var) {
            list.add(s);
        }
        return list;
    }
}