


// Source header
#include "Hello.hpp"

// Build config
#pragma standard "c++17"

namespace Hello
{
	std::string Hello(std::string name)
	{
		std::string result = "Hello, " + name;
		if (__cplusplus == 201703L)
			result += " from c++17";
		return result + "!";
	}
}