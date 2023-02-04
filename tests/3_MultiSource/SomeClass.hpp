#pragma once

#pragma build "SomeClass.cpp" "SomeClass.o"
#pragma link "SomeClass.o" "MultiSource.exe"

// Standard library
#include <string>

class SomeClass
{
	public: // Ctor / dtor
	SomeClass() = default;
	~SomeClass() = default;

	public:
	void PrintData();
	void SetData(std::string str);

	private:
	std::string data;
};