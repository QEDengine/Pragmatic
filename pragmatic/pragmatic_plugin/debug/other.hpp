#include <string>
#pragma build "other.cpp" "other.o"
#pragma link "other.o" "HelloWorld.exe"

void print_msg(std::string msg);