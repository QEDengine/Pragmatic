
#include <iostream>

#pragma standard "C++17"

#pragma object "debug_source.cpp" "debug_source.o"
#pragma link "HelloWorld.exe"

#include "other.hpp"

int main()
{
	std::cout << "Hello world!" << std::endl;
	return 0;
}
