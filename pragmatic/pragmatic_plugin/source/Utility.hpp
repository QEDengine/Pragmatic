#pragma once

// Standard library
#include <string>
#include <algorithm>
#include <fstream>
#include <filesystem>
#include <iomanip>
#include <regex>
// Clang
#include <clang/Lex/Preprocessor.h>
#include <clang/Lex/PreprocessorOptions.h>
// External
#include <nlohmann/json.hpp>
using json = nlohmann::ordered_json;

namespace QED { namespace Pragmatic
{
		inline std::string Replace(std::string str, std::string substring, std::string newValue)
		{
			return std::regex_replace(str, std::regex(substring), newValue);
		}
		inline std::string GetDirectoryFromPath(std::string path)
		{
			std::string directory;
			const size_t last_slash_idx = path.rfind('\\');
			if (std::string::npos != last_slash_idx)
			{
				directory = path.substr(0, last_slash_idx);
			}
			return directory;
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

		inline std::string NormalizePath(std::string path, std::string workingDir)
		{
			// Remove ./ from the front if it exists
			if (path[0] == '.' && path[1] == '/')
			{
				path = path.substr(2, path.size());
			}

			return path;
		}
}} // namespace QED::Pragmatic
