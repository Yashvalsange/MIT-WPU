#include <iostream>
using namespace std;

// Inline function to calculate simple interest
inline double calculateSimpleInterest(double principal, double rate, double time) {
    return (principal * rate * time) / 100.0;
}

int main() {
    double principal, rate, time;
    cout << "Enter Principal amount: ";
    if (!(cin >> principal)) {
        cout << "Invalid input." << endl;
        return 1;
    }
    cout << "Enter Rate of interest (%): ";
    if (!(cin >> rate)) {
        cout << "Invalid input." << endl;
        return 1;
    }
    cout << "Enter Time period (years): ";
    if (!(cin >> time)) {
        cout << "Invalid input." << endl;
        return 1;
    }

    double interest = calculateSimpleInterest(principal, rate, time);
    cout << "The Simple Interest is: " << interest << endl;
    cout << "Total Amount (Principal + Interest): " << (principal + interest) << endl;

    return 0;
}
