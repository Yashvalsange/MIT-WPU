#include <iostream>
using namespace std;

int main()
{
    float km;

    cout << "Enter Distance in Kilometer: ";
    cin >> km;

    cout << "Meters = " << km * 1000 << endl;
    cout << "Centimeters = " << km * 100000 << endl;
    cout << "Millimeters = " << km * 1000000 << endl;

    return 0;
}
