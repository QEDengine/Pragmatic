#pragma build "Main.cpp" "Main.o"
#pragma link "Main.o" "MultiSource.exe"
#include "SharedSettings.hpp"

#include "SomeClass.hpp"

int main()
{
	auto someInstance = SomeClass();

	someInstance.SetData("Lorem");
	someInstance.PrintData();
	someInstance.SetData("impsum");
	someInstance.PrintData();

	return 0;
}