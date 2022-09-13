#pragma once

// Standard library
#include <string>
#include <algorithm>
#include <fstream>
#include <filesystem>
#include <iomanip>

// Clang
#include <clang/Lex/PreprocessorOptions.h>

// JSON
#include <nlohmann/json.hpp>
using json = nlohmann::ordered_json;

// Pragmatic
#include "Globals.hpp"

namespace QED { namespace Pragmatic
{
		inline std::string TrunkateClangPath(std::string path)
		{
			llvm::outs() << "[Pragmatic] Source file path to trunkate : " << path << "\n";
			// Remove "Source"
			if (path.find("Source") != std::string::npos) path = path.erase(0, path.find("Source") + sizeof("Source") - 1);
			// Remove first two characters : "some/dir/header.hpp:x:y"
			while (path[0] == '.' || path[0] == '\\' || path[0] == '/')
			{
				path.erase(0, 1);
			}
			// Replace any backslashes
			std::replace(path.begin(), path.end(), '\\', '/');

			// Remove character position from the end : "some/dir/header.hpp"
			path = path.substr(0, path.find(':'));
			llvm::outs() << "[Pragmatic] Trunkated source file path : " << path << "\n";
			return path;
		}

		inline json GetJSON()
		{
			std::ifstream sourceFileJson(QED::Pragmatic::metaFilePath);
			// If file doesn't exitst, create one
			if (!sourceFileJson)
			{
				std::ofstream o(QED::Pragmatic::metaFilePath);
				o << "{\n}" << std::endl;
				o.close();
				sourceFileJson = std::ifstream(QED::Pragmatic::metaFilePath);
			}

			// Read source file JSON
			json meta;
			sourceFileJson >> meta;			

			return meta;
		}

		inline std::string GetMacroValue(clang::Preprocessor& preprocessor, std::string macroName)
		{
			auto& opts = preprocessor.getPreprocessorOpts();
			for (auto& macro : opts.Macros)
			{
				if (macro.first.rfind(macroName, 0) == 0)
				{
					std::string value = macro.first.substr(macro.first.find('=') + 1, macro.first.size());
					if (value.front() == '\"' && value.back() == '\"')
						value = value.substr(1, value.size() - 2);
					return value;
				}
			}
			return "";
		}
}} // namespace QED::Pragmatic
