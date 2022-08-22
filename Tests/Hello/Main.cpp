
// Standard library
#include <iostream>

// Project headers
#include "Hello.hpp"

// Using directives
using namespace std;

// Build configuration
#pragma type executable



int main()
{
	cout << Hello::Hello("World") << endl;
}