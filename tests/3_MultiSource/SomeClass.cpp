// Build settings
#include "SharedSettings.hpp"

// Source header
#include "SomeClass.hpp"

// Standard library
#include <iostream>

void SomeClass::PrintData()
{
	std::cout << data << std::endl;
}

void SomeClass::SetData(std::string str)
{
	data = str;
}