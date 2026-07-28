// Create a class Product to store product 
//information and display the details using 
//functions defined outside the class.
#include <iostream>
using namespace std;   
class Product {
    public: 
    string name;
    int id, price;
    void accept();
    void display();

};

void Product::accept(){
    cout << "Enter the name of product: ";
    cin >> name;
    cout << "Enter the product ID: ";
    cin >> id;
    cout << "Enter the price of product: ";
    cin >> price;
}

void Product::display(){
    cout << "----------------------------------------------------" << endl;
    cout << "The name of product is: " << name << endl;
    cout << "The product ID is: " << id << endl;
    cout << "The price of product is: " << price << endl;
    cout << "----------------------------------------------------" << endl;
}

int main(){
    Product p1,p2;
    p1.accept();
    p1.display();
    p2.accept();
    p2.display();
    return 0;
}