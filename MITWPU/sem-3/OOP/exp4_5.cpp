//Write a program to define a class student having data
// members name and roll no. Accept and display data
// for one object. Define the member function inside the class.

#include <iostream>
using namespace std;
class Student {

    string name;
    int roll;
    

public:

void accept(){
    cout << "Enter the name of student: ";
    cin >> name;
    cout << "Enter the roll number of student: ";
    cin >> roll;
}

void display(){
    cout << "----------------------------------------------------" << endl;
    cout << "The name of student is: " << name << endl;
    cout << "The roll number of student is: " << roll << endl;
    cout << "----------------------------------------------------" << endl;
}};

int main(){
    Student s1;
    s1.accept();
    s1.display();
    
    return 0;
}