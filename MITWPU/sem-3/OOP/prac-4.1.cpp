/* Write a program to calculate the volume of a box using functions 
defined outside the class*/
#include <iostream>
using namespace std;
class Box {
};

void Box::accept(){
    cout << "Enter the length of box (cm): ";
    cin >> l;
    cout << "Enter the breadth of box (cm): ";
    cin >> b;
    cout << "Enter the height of box (cm): ";
    cin >> h;
}

void Box::volume(){
    v= l*b*h;
    cout << "The Volume of box is = " << v << " cm³" << endl;
}
 int main(){
    Box b1;
    b1.accept();
    b1.volume();
    return 0;
 }
