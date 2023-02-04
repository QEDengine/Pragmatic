
#include <iostream>
#include <string>



#pragma build "debug_source.cpp" "debug_source.o"
#pragma link "debug_source.o" "HelloWorld.exe"

#include "other.hpp"
#include "debug_source.hpp"

void print()
{
	std::cout << "Hello world!" << '\n' << __cplusplus << " == 201703L" << std::endl;
}

int main()
{
	print();
	print_msg("1 + 2 = " + std::to_string(Add(1, 2)));
	return 0;
}
