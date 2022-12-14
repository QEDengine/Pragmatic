// Source header
#include "StandardPragmaHandler.hpp"

// Standard library
#include <iomanip>

// Clang
#include <clang/Basic/Diagnostic.h>

// Mirror
#include "Globals.hpp"
#include "Utility.hpp"

namespace QED { namespace Pragmatic
{
	void StandardPragmaHandler::HandlePragma(clang::Preprocessor &preProcessor, clang::PragmaIntroducer introducer, clang::Token &buildTypeToken) 
	{
		auto& sourceManager = preProcessor.getSourceManager();
		std::vector<std::string> tokens;
		clang::Token token = buildTypeToken;

		while(token.isNot(clang::tok::eod))
		{
			// Get string from token
			const char* charData = sourceManager.getCharacterData(token.getLocation());
			std::string strData(charData, token.getLength());

			// Append
			tokens.push_back(strData);

			// Lex next token
			preProcessor.Lex(token);
		}

		// Get file
		metaFilePath = GetMacroValue(preProcessor, "PRAGMATIC_FILE_PATH");
		std::string sourceFilePath = sourceManager.getFilename(token.getLocation()).str();
		if (metaFilePath == "") metaFilePath = sourceFilePath + ".json";
		llvm::outs() << "[Pragmatic] Handling file : " << sourceFilePath << "\n"; 

		AddBuildTypeToJSON(tokens, preProcessor.getDiagnostics(), token.getLocation());
	}

	void StandardPragmaHandler::AddBuildTypeToJSON(std::vector<std::string>& tokens, clang::DiagnosticsEngine& diagnostics, clang::SourceLocation location)
	{
		// Check if size of tokens is at least 2 (source, "SomeFile.cpp")
		if (tokens.size() < 2)
		{
			unsigned ID = diagnostics.getCustomDiagID(clang::DiagnosticsEngine::Error, "#pragma standard needs a standard specified. Valid options are #pragma standard C++14, C++17 or C++20");
			diagnostics.Report(location, ID);
		}

		if (tokens[0] != "standard")
		{
			unsigned ID = diagnostics.getCustomDiagID(clang::DiagnosticsEngine::Error, "#pragma standard needs a standard specified. Valid options are #pragma standard C++14, C++17 or C++20");
			diagnostics.Report(location, ID);
		}

		std::string standard = tokens[1];
		if (standard[0] != '\"' || standard[standard.size() - 1] != '\"')
		{
			unsigned ID = diagnostics.getCustomDiagID(clang::DiagnosticsEngine::Error, "#pragma standard needs a standard specified. Valid options are #pragma standard \"C++14\", \"C++17\" or \"C++20\"");
			diagnostics.Report(location, ID);
		}
		standard = standard.substr(1, standard.size() - 2);

		auto meta = QED::Pragmatic::GetJSON();
		meta["BuildOptions"]["Standard"] = standard;
		std::ofstream sourceJson(QED::Pragmatic::metaFilePath);
		sourceJson << std::setw(4) << meta;
	}
}} // namesapce QED::Pragmatic