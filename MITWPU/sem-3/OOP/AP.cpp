#include <iostream>
using namespace std;

int main()
{
    int length, width;

    cout << "Enter length and width: ";
    cin >> length >> width;

    cout << "Area = " << length * width << endl;
    cout << "Perimeter = " << 2 * (length + width);

    return 0;
}
