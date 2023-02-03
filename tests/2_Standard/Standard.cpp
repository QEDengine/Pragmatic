#pragma build "Standard.cpp" "Standard.o"
#pragma link "Standard.o" "Standard.exe"
#pragma standard "C++17"

#include <iostream>

int main()
{
	std::cout << __cplusplus << " == 201703L" << std::endl;

	return 201703L == __cplusplus ? 0 : 1;
}