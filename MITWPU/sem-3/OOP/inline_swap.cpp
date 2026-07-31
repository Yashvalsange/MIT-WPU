#include <iostream>
using namespace std;

// Inline function to swap two numbers using references
inline void swapNumbers(double &a, double &b) {
    double temp = a;
    a = b;
    b = temp;
}

int main() {
    double num1, num2;
    cout << "Enter first number (a): ";
    if (!(cin >> num1)) {
        cout << "Invalid input." << endl;
        return 1;
    }
    cout << "Enter second number (b): ";
    if (!(cin >> num2)) {
        cout << "Invalid input." << endl;
        return 1;
    }

    cout << "Before swap: a = " << num1 << ", b = " << num2 << endl;
    swapNumbers(num1, num2);
    cout << "After swap: a = " << num1 << ", b = " << num2 << endl;

    return 0;
}
