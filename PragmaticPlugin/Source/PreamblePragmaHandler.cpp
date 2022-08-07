// Source header
#include "PreamblePragmaHandler.hpp"

// Standard library
#include <chrono>
#include <thread>

// Clang
#include <clang/Basic/Diagnostic.h>
#include <clang/Lex/PPCallbacks.h>
#include <clang/Basic/Module.h>

// Mirror
#include "Globals.hpp"
#include "Utility.hpp"

class Callbacks : public clang::PPCallbacks
{
	clang::Preprocessor& preprocessor;
	clang::SourceManager& sourceManager;

	public:
	Callbacks(clang::Preprocessor& preprocessor) : preprocessor(preprocessor), sourceManager(preprocessor.getSourceManager()) { }

	virtual void moduleImport(clang::SourceLocation ImportLoc, clang::ModuleIdPath Path, const clang::Module *Imported) override
	{
		if (!preprocessor.hadModuleLoaderFatalFailure())
		{
			llvm::outs() << "[Pragmatic] Import found : " << std::string(Imported->Name) << "\n";
		}
		else
		{
			std::string importStr = "";
			const char* c = sourceManager.getCharacterData(ImportLoc);
			const unsigned int maxLen = 30;
			for (unsigned int i = 0; i < maxLen; i++)
			{
				importStr.push_back(c[i]);

				if (i == maxLen - 1) llvm::outs() << "[Pragmatic] Max import length reached!" << "\n";
				if (c[i] == '\0' || c[i] == ';') break;
			}

			llvm::outs() << "[Pragmatic] Import found but not loaded : " << importStr  << "\n";
		}
	}

	virtual void EndOfMainFile() override
	{
		preprocessor.CommitBacktrackedTokens();
  	}
};

namespace QED { namespace Pragmatic
{
	void PreamblePragmaHandler::HandlePragma(clang::Preprocessor &preProcessor, clang::PragmaIntroducer introducer, clang::Token &buildTypeToken) 
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

		llvm::outs() << "[Pragmatic] Preamble found" << "\n";

		preProcessor.getDiagnostics().setSuppressAllDiagnostics(true);
		preProcessor.addPPCallbacks(std::make_unique<Callbacks>(preProcessor));
	}
}} // namesapce QED::Pragmatic