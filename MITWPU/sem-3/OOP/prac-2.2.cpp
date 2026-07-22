#include <iostream>
using namespace std;
/*2. Create a class Student with data members rollNo, name, and marks. Define the 
member functions accept() and display() outside the class using the scope resolution 
operator*/
class Student {
    public:
    int roll;
    string name;
    float marks;
   void accept();
   void display();
};
   
    void Student::accept()
    {
        cout << "Enter your name: ";
        cin >> name;
        cout << "Enter your Roll number : ";
        cin >> roll;
        cout << "Enter your marks: ";
        cin >> marks;
    }

    void Student::display()
    {
       cout << "Your name is: "<< name<<endl;
       cout << "Your roll no is: "<<roll<<endl;
       cout << "Your marks are: "<< marks<<endl;
    }

int main(){
    Student s1,s2;
    s1.accept();
    s2.accept();

    s1.display();
    s2.display();
return 0;
}
