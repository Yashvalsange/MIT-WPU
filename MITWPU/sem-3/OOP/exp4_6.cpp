//Develop a class Account to accept account details 
//and display the balance using functions defined 
//outside the class.


#include <iostream>
using namespace std;

class Account {
    public: 
    string accname;
    int accno, balance;
    void accept();
    void display();

};

void Account::accept(){
    cout << "Enter the name of account holder: ";
    cin >> accname;
    cout << "Enter the account number  : ";
    cin >> accno;
    cout << "Enter the initial balance: ";
    cin >> balance;
}

void Account::display(){
    cout << "----------------------------------------------------" << endl;
    cout << "The name of account holder is: " << accname << endl;
    cout << "The account number is: " << accno << endl;
    cout << "The balance is: " << balance << endl;
    cout << "----------------------------------------------------" << endl;
}

int main(){
    Account a1;
    a1.accept();
    a1.display();

    return 0;
}