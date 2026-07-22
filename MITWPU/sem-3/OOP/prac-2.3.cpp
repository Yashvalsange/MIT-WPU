#include <iostream>
using namespace std;
/*3.Create two namespaces, Physics and Chemistry, each containing a same variable name 
for accessing subject. Use the scope resolution operator to call the appropriate data 
member from each namespace*/
 
namespace phy {
    int marks = 37;
}

namespace chem {
    int marks = 45;
}

int main() {
    cout << "Physics marks: " << phy::marks << endl;
    cout << "Chemistry marks: " << chem::marks << endl;
    return 0;
}
