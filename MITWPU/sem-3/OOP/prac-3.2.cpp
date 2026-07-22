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
