#include <iostream>
using namespace std;
/*4. Write a C++ program to dynamically allocate memory for an integer using new, accept 
its value from the user, display it, and deallocate the memory using delete.*/

int main () {
    int *ptr;
    cout << "Enter a value: ";
    cin >> *ptr;

    cout << "The value is: " << ptr;

    delete ptr;
    ptr = nullptr;


    return 0;

}
