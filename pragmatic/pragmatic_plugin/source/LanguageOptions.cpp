// Souce header
#include "LanguageOptions.hpp"

#define STANDARD_PRAGMA_TOKEN "standard"

namespace QED { namespace Pragmatic
{
	StandardPragma::StandardPragma() : PragmaHandler(STANDARD_PRAGMA_TOKEN, { {}, {true} }, 2) { }

	bool StandardPragma::CheckTokens(clang::Preprocessor &preprocessor, std::vector<std::string> tokens, clang::DiagnosticsEngine& diagnostics, clang::SourceLocation sourceLocation)
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
			SetShouldRecompile();

			unsigned ID = diagnostics.getCustomDiagID(clang::DiagnosticsEngine::Error, "Not preprocessing with the same language standard as required by pragma");
			diagnostics.Report(sourceLocation, ID);
			
			return false;
		}

		return true;
	}

	std::string StandardPragma::Response(clang::Preprocessor &preprocessor, std::vector<std::string> tokens, clang::DiagnosticsEngine& diagnostics)
	{
		return "";
	}
}
} // namespace QED::Pragmatic