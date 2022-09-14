// Source header
#include "SourcePragmaHandler.hpp"

// Standard library
#include <iomanip>

// LLVM
#include <llvm/Support/raw_ostream.h>

// Clang
#include <clang/Basic/Diagnostic.h>
#include <clang/Lex/PreprocessorOptions.h>

// Pragmatic
#include "Utility.hpp"

namespace QED { namespace Pragmatic
{
	void SourcePragmaHandler::HandlePragma(clang::Preprocessor &preProcessor, clang::PragmaIntroducer introducer, clang::Token &sourceToken) 
	{
		auto& sourceManager = preProcessor.getSourceManager();
		std::vector<std::string> tokens;
		clang::Token token = sourceToken;

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
		std::string sourceFilePath = sourceManager.getFilename(sourceToken.getLocation()).str();
		if (metaFilePath == "") metaFilePath = sourceFilePath + ".json";
		llvm::outs() << "[Pragmatic] Handling file : " << sourceFilePath << "\n"; 

		AddSourceToJSON(tokens, preProcessor.getDiagnostics(), sourceToken.getLocation());
	}

	void SourcePragmaHandler::AddSourceToJSON(std::vector<std::string>& tokens, clang::DiagnosticsEngine& diagnostics, clang::SourceLocation location) 
	{
		// Check if size of tokens is at least 2 (source, "SomeFile.cpp")
		if (tokens.size() < 2)
		{
			unsigned ID = diagnostics.getCustomDiagID(clang::DiagnosticsEngine::Error, "#pragma source needs source files to be defined after #pragma source");
			diagnostics.Report(location, ID);
		}

		auto& sm = diagnostics.getSourceManager();
		std::string path = TrunkateClangPath(location.printToString(sm));

		// TODO: Validate source string token

		// Get source file
		std::string sourceFile;
		for (auto& token : tokens)
		{
			if (token == "source") continue;

			sourceFile = token.substr(1, token.size() - 2);
		}

		auto meta = QED::Pragmatic::GetJSON();
		bool found = false;
		for (auto& source : meta["Sources"])
		{
			if (source.contains("Location") && source["Location"] == path)
			{
				if (source.contains("Path") && std::find(source["Path"].begin(), source["Path"].end(), sourceFile) == source["Path"].end())
					source["Path"].push_back(sourceFile);
				found = true;
			}
		}
		if (!found)
		{
			meta["Sources"].push_back({ { "Path", {} }, {"Location", path } });
			meta["Sources"].at(meta["Sources"].size() - 1)["Path"].push_back(sourceFile);
		}
		
		std::ofstream sourceJson(QED::Pragmatic::metaFilePath);
		sourceJson << std::setw(4) << meta;
	}
}} // namespace QED::Pragmatic