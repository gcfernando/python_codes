namespace Calculator;
public static class Calc
{
    public static string About() => "You're accessing .NET library";
    public static double Addition(double valueOne, double valueTwo) => valueOne + valueTwo;
    public static double Subtraction(double valueOne, double valueTwo) => valueOne - valueTwo;
    public static double Multiplication(double valueOne, double valueTwo) => valueOne * valueTwo;
    public static double Division(double valueOne, double valueTwo) => valueOne / valueTwo;
}