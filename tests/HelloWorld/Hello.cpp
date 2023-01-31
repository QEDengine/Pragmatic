#pragma build "Hello.cpp" "Hello.o"
#pragma link "Hello.o" "Hello.exe"

#include <iostream>

int main()
{
	std::cout << "Hello world !" << std::endl;

	return 0;
}