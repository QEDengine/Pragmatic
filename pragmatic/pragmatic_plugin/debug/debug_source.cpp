
#include <iostream>

#pragma standard "C++17"

#pragma object "debug_source.cpp" "debug_source.o"
#pragma link "HelloWorld.exe"

// #include "other.hpp"

void print()
{
	std::cout << "Hello world!" << __cplusplus << " == 201703L" << std::endl;
}

int main()
{
	print();
	return 0;
}
