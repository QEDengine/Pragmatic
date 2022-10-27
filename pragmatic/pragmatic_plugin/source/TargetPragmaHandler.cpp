// Source header
#include "TargetPragmaHandler.hpp"

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
	void TargetPragmaHandler::HandlePragma(clang::Preprocessor &preProcessor, clang::PragmaIntroducer introducer, clang::Token &buildTypeToken) 
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

	void TargetPragmaHandler::AddBuildTypeToJSON(std::vector<std::string>& tokens, clang::DiagnosticsEngine& diagnostics, clang::SourceLocation location)
	{
		// Check if size of tokens is at least 2 (source, "SomeFile.cpp")
		if (tokens.size() < 2)
		{
			unsigned ID = diagnostics.getCustomDiagID(clang::DiagnosticsEngine::Error, "#pragma needs a string target name defined");
			diagnostics.Report(location, ID);
		}

		// TODO: Validate build type tokens

		// Get build type
		std::string targetName = "";
		for (auto& token : tokens)
		{
			if (token == "target") continue;

			targetName += token + ' ';
		}

		targetName = targetName.substr(1, targetName.size() - 3);

		auto& sm = diagnostics.getSourceManager();
		auto path = TrunkateClangPath(location.printToString(sm));

		auto meta = QED::Pragmatic::GetJSON();

		if (!meta.contains("Targets"))
			meta["Targets"].push_back({ { "Name", targetName }, {"Location", path } });
		else
		{
			bool found = false;
			for (auto& target : meta["Targets"])
			{
				if (target["Name"] == targetName)
				{
					found = true;
					if (target["Location"] != path)
					{
						auto errorMsg = "Target with name " + targetName + " is redefined, only target names defined with #pragma target must be unique.";
						unsigned ID = diagnostics.getCustomDiagID(clang::DiagnosticsEngine::Error, "Target redefined, only target names defined with #pragma target must be unique.");
						diagnostics.Report(location, ID);
					}
				}
			}
			if (!found)
			{
				meta["Targets"].push_back({ { "Name", targetName }, {"Location", ReplaceSlashes(path) } });
			}
		}
		
		std::ofstream sourceJson(QED::Pragmatic::metaFilePath);
		sourceJson << std::setw(4) << meta;
	}
}} // namesapce QED::Pragmatic