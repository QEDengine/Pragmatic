// Source header
#include "Meta.hpp"
// Standard library
#include <string>
#include <algorithm>
#include <fstream>
#include <filesystem>
#include <iomanip>
#include <functional> 
// Pragmatic
#include "Utility.hpp"
#include "llvm/Support/raw_ostream.h"

namespace QED { namespace Pragmatic {
	Meta& Meta::GetInstance(clang::Preprocessor& preprocessor)
	{
		static Meta instance;
		if (instance.metaFilePath == "")
		{
			instance.metaFilePath = (GetMacroValue(preprocessor, "PRAGMATIC_FILE_PATH"));
		
			std::ifstream sourceFileJson(instance.metaFilePath);
			// If file doesn't exitst, create one
			if (!sourceFileJson)
			{
				std::ofstream o(instance.metaFilePath);
				o << "{\n\"graph\": {}\n}" << std::endl;
				o.close();
				sourceFileJson = std::ifstream(instance.metaFilePath);
			}

			// Read source file JSON
			sourceFileJson >> instance.json;
		
		}
		return instance;
	}

	void ClearDefinitions(json& json, std::string file)
	{
		auto iter = json.cbegin();
		for (; iter != json.cend();)
		{
			if ((std::string)iter.value()["metadata"]["defined"] == file)
				iter = json.erase(iter);
			else ++iter;
		}
	}

	void Meta::ClearDefinitionsForFile(std::string file)
	{
		// Clear nodes
		ClearDefinitions(json["graph"]["nodes"], file);

		// Clear edges
		ClearDefinitions(json["graph"]["edges"], file);
	}

	void Meta::Write()
	{
		std::ofstream sourceJson(metaFilePath);
		sourceJson << std::setw(4) << json;
	}
}} // namesapce QED::Pragmatic