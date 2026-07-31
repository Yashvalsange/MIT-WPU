#include <iostream>
using namespace std;

// Inline function to find the maximum of two numbers
inline double findMax(double a, double b) {
    return (a > b) ? a : b;
}

int main() {
    double num1, num2;
    cout << "Enter two numbers to find the maximum: ";
    if (cin >> num1 >> num2) {
        cout << "The maximum of " << num1 << " and " << num2 << " is: " << findMax(num1, num2) << endl;
    } else {
        cout << "Invalid input." << endl;
    }
    return 0;
}
