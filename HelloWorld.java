
public class HelloWorld {

	// Method to add two numbers
    public int add(int a, int b) {
        return a + b;
    }

    // Method to subtract two numbers
    public int subtract(int a, int b) {
        return a - b;
    }

    // Method to multiply two numbers
    public int multiply(int a, int b) {
        return a * b;
    }

    // Method to divide two numbers
    public double divide(int a, int b) {
        if (b == 0) {
            System.out.println("Error: Division by zero is not allowed.");
            return 0;
        }
        return (double) a / b;
    }

    // Main method to execute some calculations
    public static void main(String[] args) {
        Calculator myCalculator = new Calculator();

        System.out.println("Addition: 10 + 5 = " + myCalculator.add(10, 5));
        System.out.println("Subtraction: 10 - 5 = " + myCalculator.subtract(10, 5));
        System.out.println("Multiplication: 10 * 5 = " + myCalculator.multiply(10, 5));
        System.out.println("Division: 10 / 5 = " + myCalculator.divide(10, 5));
    }

}
