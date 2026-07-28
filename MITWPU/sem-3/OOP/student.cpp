#include <iostream>
using namespace std;
class student {
int rollNO.
string name;
float marks;

void accept()
{
cout << " enter rollNo. of the student:";
cin >> rollNO.
cout << " enter name of the student:";
cin >> name;
cout << " enter marks of the student:";
ci >> marks;
}

void display()
{
cout <<"the roll no. of the student:";
cout <<"the name  of the student:";
cout <<"the marks of the student:";
}
}S1,S2
int main()
{
S1.accept();
S2.accept();
S1.display();
S2.display();

return 0;
}
