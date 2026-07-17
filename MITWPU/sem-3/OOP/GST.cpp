#include <iostream>
using namespace std;

int main()
{
    float price, gst, gstAmount, finalAmount;

    cout << "Enter Product Price: ";
    cin >> price;

    cout << "Enter GST Percentage: ";
    cin >> gst;

    gstAmount = (price * gst) / 100;
    finalAmount = price + gstAmount;

    cout << "\nGST Amount = " << gstAmount;
    cout << "\nFinal Payable Amount = " << finalAmount;

    return 0;
}
