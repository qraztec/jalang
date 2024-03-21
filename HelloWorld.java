import java.util.Scanner;
import java.util.ArrayList;

public class HelloWorld {

	// Method to add two numbers
    public static int addFunc(int a, int b) {
    a = b;
        return a + b;
    }

    // Method to subtract two numbers
    public static int subtract(int a, int b) {
        return a - b;
    }

    // Method to multiply two numbers
    public static int multiply(int a, int b) {
        return a * b;
    }

    // Method to divide two numbers
    public static double divide(int a, int b) {
        if (b == 0) {
            System.out.println("Error: Division by zero is not allowed.");
            return 0;
        }
        return (double) a / b;
    }

    // Main method to execute some calculations
    public static void main(String[] args) {
    //    Calculator myCalculator = new Calculator();
        Scanner scan = new Scanner(System.in);
        int a = scan.nextInt();
        String text = scan.next();
        ArrayList<Integer> arr = new ArrayList<>();
        arr.add(addFunc(a,6));


        System.out.println("Addition: 10 + 5 = " + addFunc(a, 5));
        System.out.println("Subtraction: 10 - 5 = " + subtract(10, 5));
        System.out.println("Multiplication: 10 * 5 = " + multiply(10, 5));
        System.out.println("Division: 10 / 5 = " + divide(10, 5));
    }

}
