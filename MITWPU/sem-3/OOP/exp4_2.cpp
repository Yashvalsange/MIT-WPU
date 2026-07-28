//Write a program to store and display student
// information using functions defined outside the class.

#include <iostream>
using namespace std;

class Student {
    public: 
    string name;
    int roll, age,id;
    void accept();
    void display();

};

void Student::accept(){
    cout << "Enter the name of student: ";
    cin >> name;
    cout << "Enter the roll number of student: ";
    cin >> roll;
    cout << "Enter the age of student: ";
    cin >> age;
    cout << "Enter the ID of student: ";
    cin >> id;
}

void Student::display(){
    cout << "The name of student is: " << name << endl;
    cout << "The roll number of student is: " << roll << endl;
    cout << "The age of student is: " << age << endl;
    cout << "The ID of student is: " << id << endl;
    cout << "----------------------------------------------------" << endl;
}

int main(){
    Student s1,s2;
    s1.accept();
    s1.display();
    s2.accept();
    s2.display();
    return 0;
}