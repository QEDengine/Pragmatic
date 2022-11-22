#pragma once

// Standard library
#include <string>
#include <vector>

// Clang
#include "clang/Basic/Diagnostic.h"
#include "clang/Basic/SourceLocation.h"
#include "clang/Lex/Preprocessor.h"
#include "clang/Basic/LangStandard.h"

// Pragmatic
#include "PragmaHandler.hpp"

#define STANDARD_PRAGMA_TOKEN "standard"

namespace QED { namespace Pragmatic
{

	class StandardPragma : public PragmaHandler
	{
		public:
		StandardPragma() : PragmaHandler(STANDARD_PRAGMA_TOKEN, {{}, {true}}, 2) { }

		private:
		std::string standard = "";

		public:
		virtual bool CheckTokens(clang::Preprocessor &preprocessor, std::vector<std::string> tokens, clang::DiagnosticsEngine& diagnostics, clang::SourceLocation sourceLocation) override
		{
			standard = tokens[1];
			
			// Always convert to lower case
			std::transform(standard.begin(), standard.end(), standard.begin(), [](unsigned char c){ return std::tolower(c); });

			// Get meta & save standard
			auto& meta = Meta::GetInstance(preprocessor);
			meta.json["graph"]["nodes"][sourceFilePath]["metadata"]["defined"] = sourceFilePath;
			meta.json["graph"]["nodes"][sourceFilePath]["metadata"]["standard"] = standard;

			// If not preprocessing with the same standard, raise error
			if (preprocessor.getLangOpts().LangStd != clang::LangStandard::getLangKind(standard))
			{
				unsigned ID = diagnostics.getCustomDiagID(clang::DiagnosticsEngine::Error, "Not preprocessing with the same language standard as required by pragma");
				diagnostics.Report(sourceLocation, ID);
				return false;
			}

			return true;
		}

		virtual std::string Response(clang::Preprocessor &preprocessor, std::vector<std::string> tokens, clang::DiagnosticsEngine& diagnostics) override { return ""; }
	};

}} // namespace QED::Pragmatic