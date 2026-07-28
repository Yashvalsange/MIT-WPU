/*Write a program to calculate the area of 
a rectangle using functions defined outside the class. */
#include <iostream>
using namespace std;

class Rec{
    public:
    float l,b,a;
    void area();
    void accept();
    void display();

};

void Rec::accept(){
    cout << "Enter the length of rectangle (cm): ";
    cin >> l;
    cout << "Enter the breadth of rectangle (cm): ";
    cin >> b;
}

void Rec::area(){
    a= l*b;
}

void Rec::display(){
    cout << "The area of rectangle is = "<< a<<endl;
}

int main(){
    
    Rec r1;
    r1.accept();
    r1.area();
    r1.display();
    return 0;
}