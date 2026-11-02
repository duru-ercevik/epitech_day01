class Ex06 {
    public static void sequence(int nbr) {
        if (nbr < 0) {
            return;
        }
        String current = "1";
        System.out.println(current);
        for (int i = 0; i < nbr; i++) {
            current = next(current);
            System.out.println(current);
        }
    }

    private static String next(String s) {
        StringBuilder sb = new StringBuilder();
        int i = 0;
        while (i < s.length()) {
            char c = s.charAt(i);
            int count = 1;
            while (i + count < s.length() && s.charAt(i + count) == c) {
                count++;
            }
            sb.append(count).append(c);
            i += count;
        }
        return sb.toString();
    }
}