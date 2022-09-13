// Source header
#include "DirectoryPragmaHandler.hpp"

// Standard library
#include <iomanip>

// Clang
#include <clang/Basic/Diagnostic.h>

// Mirror
#include "Globals.hpp"
#include "Utility.hpp"

namespace QED { namespace Pragmatic
{
	void DirectoryPragmaHandler::HandlePragma(clang::Preprocessor &preProcessor, clang::PragmaIntroducer introducer, clang::Token &buildTypeToken) 
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

	void DirectoryPragmaHandler::AddBuildTypeToJSON(std::vector<std::string>& tokens, clang::DiagnosticsEngine& diagnostics, clang::SourceLocation location)
	{
		// Check if size of tokens is at least 2 (dir, build/intermediate "dirName")
		if (tokens.size() != 3)
		{
			unsigned ID = diagnostics.getCustomDiagID(clang::DiagnosticsEngine::Error, "#pragma dir needs a directory type specified. Valid options are #pragma dir build, intermediate");
			diagnostics.Report(location, ID);
		}

		// TODO: Validate build type tokens

		// Get dir
		std::string directory = tokens[2];
		if (directory[0] != '\"' || directory[directory.size() - 1] != '\"')
		{
			unsigned ID = diagnostics.getCustomDiagID(clang::DiagnosticsEngine::Error, "#pragma dir needs a directory type specified. Valid options are #pragma dir build, intermediate");
			diagnostics.Report(location, ID);
		}
		directory = directory.substr(1, directory.size() - 2);

		auto meta = QED::Pragmatic::GetJSON();
		if (tokens[1] == "build")
			meta["BuildOptions"]["BuildDirectory"] = directory;
		else if (tokens[1] == "intermediate")
			meta["BuildOptions"]["IntermediateDirectory"] = directory;
		else
		{
			unsigned ID = diagnostics.getCustomDiagID(clang::DiagnosticsEngine::Error, "#pragma dir needs a directory type specified. Valid options are #pragma dir build, intermediate");
			diagnostics.Report(location, ID);
		}
		std::ofstream sourceJson(QED::Pragmatic::metaFilePath);
		sourceJson << std::setw(4) << meta;
	}
}} // namesapce QED::Pragmatic