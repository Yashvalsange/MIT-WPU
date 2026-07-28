#include <iostream>
using namespace std;
class area{
    float r,AOC;
    const float pi=3.14;
    public:

void accept(){
  cout<<"enter radius of circle=";
    cin>>r;   
}
void display(){
    AOC=pi*r*r;
 cout<<"Area of the circle is="<<AOC;
    AOC=pi*r*r;
}
};
int main()
{
    area a1;
  
   a1.accept();
 
   a1.display();

    return 0;
    }

//Write a c++ code to create a class staff having 
//data members as id and post. 
//Accept and display data for 2 staff.
// Write member function definition inside the class.
#include <iostream>
using namespace std;
class Staff{
    int id;
    string post;
    public:
    void accept(){
        cout<<"Enter the id of staff: ";
        cin>>id;
        cout<<"Enter the post of staff: ";
        cin>>post;
    }
    void display(){
        cout<<"Id: "<<id<<endl;
        cout<<"Post: "<<post<<endl;
    }
};

int main(){
   Staff s1,s2;
   s1.accept();
   s2.accept();
    s1.display();
    s2.display();
    return 0;
}

