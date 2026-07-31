#include <iostream>
using namespace std;

// Inline function to calculate the area of a circle
inline double calculateArea(double radius) {
    const double PI = 3.14159265358979323846;
    return PI * radius * radius;
}

int main() {
    double radius;
    cout << "Enter the radius of the circle: ";
    if (cin >> radius) {
        if (radius < 0) {
            cout << "Radius cannot be negative." << endl;
        } else {
            cout << "The area of the circle with radius " << radius << " is: " << calculateArea(radius) << endl;
        }
    } else {
        cout << "Invalid input." << endl;
    }
    return 0;
}
