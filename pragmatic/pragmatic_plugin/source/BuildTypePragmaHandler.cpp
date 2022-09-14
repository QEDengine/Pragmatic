// Source header
#include "BuildTypePragmaHandler.hpp"

// Standard library
#include <iomanip>

// Clang
#include <clang/Basic/Diagnostic.h>
#include <clang/Lex/PPCallbacks.h>
#include <clang/Basic/Module.h>

// Mirror
#include "Globals.hpp"
#include "Utility.hpp"

namespace QED { namespace Pragmatic
{
	void BuildTypePragmaHandler::HandlePragma(clang::Preprocessor &preProcessor, clang::PragmaIntroducer introducer, clang::Token &buildTypeToken) 
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

		// ................
		
		// preProcessor.EnableBacktrackAtThisPos();
		// clang::SmallVector<clang::Token> Toks(8);
		// preProcessor.CollectPpImportSuffix(Toks);
		// for (auto& tok : Toks)
		// {
		// 	if (tok.getKind() != clang::tok::unknown)
		// 	{
		// 		clang::SourceLocation location = tok.getLocation();
		// 		llvm::outs() << location.printToString(sourceManager) << "\n";
		// 		int len = tok.getLength();
		// 		llvm::outs() << std::string(sourceManager.getCharacterData(location), len) << "\n";
		// 	}
		// }
		// preProcessor.Backtrack();

		// ................

		// Get file
		metaFilePath = GetMacroValue(preProcessor, "PRAGMATIC_FILE_PATH");
		std::string sourceFilePath = sourceManager.getFilename(token.getLocation()).str();
		if (metaFilePath == "") metaFilePath = sourceFilePath + ".json";
		llvm::outs() << "[Pragmatic] Handling file : " << sourceFilePath << "\n";

		AddBuildTypeToJSON(tokens, preProcessor.getDiagnostics(), token.getLocation());
	}

	void BuildTypePragmaHandler::AddBuildTypeToJSON(std::vector<std::string>& tokens, clang::DiagnosticsEngine& diagnostics, clang::SourceLocation location)
	{
		// Check if size of tokens is at least 2 (source, "SomeFile.cpp")
		if (tokens.size() < 2)
		{
			unsigned ID = diagnostics.getCustomDiagID(clang::DiagnosticsEngine::Error, "#pragma type needs a build type specified. Valid options are #pragma type executable, static library & dynamic library");
			diagnostics.Report(location, ID);
		}

		auto& sm = diagnostics.getSourceManager();
		std::string path = TrunkateClangPath(location.printToString(sm));

		// TODO: Validate build type tokens

		// Get build type
		std::string buildType = "";
		for (auto& token : tokens)
		{
			if (token == "type") continue;

			buildType += token + ' ';
		}

		buildType = buildType.substr(0, buildType.size() - 1);

		auto meta = QED::Pragmatic::GetJSON();

		bool found = false;
		for (auto& buildOption : meta["BuildOptions"])
		{
			if (buildOption.contains("Location") && buildOption["Location"] == path)
			{
				// Error handling : In a given file, only one build type is allowed.
				// Due to includes, redefinitions of the same build type are allowed.
				if (buildOption.contains("BuildType") && buildOption["BuildType"] != buildType)
				{
					unsigned ID = diagnostics.getCustomDiagID(clang::DiagnosticsEngine::Error, "#pragma type can only be defined once per target. It is redifined in the same file.");
					diagnostics.Report(location, ID);
				}

				buildOption["BuildType"] = buildType;
				found = true;
			}
		}
		if (!found)
			meta["BuildOptions"].push_back({ { "BuildType", buildType }, {"Location", path } });

		std::ofstream sourceJson(QED::Pragmatic::metaFilePath);
		sourceJson << std::setw(4) << meta;
	}
}} // namesapce QED::Pragmatic