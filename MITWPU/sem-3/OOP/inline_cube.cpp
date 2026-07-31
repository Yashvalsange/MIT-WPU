#include <iostream>
using namespace std;

// Inline function to calculate the cube of a number
inline double cube(double num) {
    return num * num * num;
}

int main() {
    double number;
    cout << "Enter a number to find its cube: ";
    if (cin >> number) {
        cout << "The cube of " << number << " is: " << cube(number) << endl;
    } else {
        cout << "Invalid input." << endl;
    }
    return 0;
}
