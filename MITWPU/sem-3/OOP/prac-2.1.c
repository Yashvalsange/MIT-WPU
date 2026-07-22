#include
using namespace std;
/1.Write a C++ program to declare a global variable num = 100 and a local variable num =
50. Display both values using the scope resolution operator/
int a=100;
int main(){
int b=50;
cout << "Global variable: "<< :: a<< endl;
cout << "Local Variable: "<< b;
return 0;
}
