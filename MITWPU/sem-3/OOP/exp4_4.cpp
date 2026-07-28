#include <iostream>
using namespace std;

class Square{
    public:
    int num,square;

void accept(){
    cout << "Enter a number: ";
    cin >> num;
}





void display(){
    cout << "The square of the number is = "<< num*num<<endl;
}};

int main(){
    
    Square r1;
    r1.accept();
    
    r1.display();
    return 0;
}