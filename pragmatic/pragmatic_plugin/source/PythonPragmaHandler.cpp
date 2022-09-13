// Source header
#include "PythonPragmaHandler.hpp"

// Standard library
#include <iomanip>

// Clang
#include <clang/Basic/Diagnostic.h>
#include <clang/Parse/Parser.h>

// Mirror
#include "Globals.hpp"
#include "Utility.hpp"

namespace QED { namespace Pragmatic
{
	void PythonPragmaHandler::HandlePragma(clang::Preprocessor &preProcessor, clang::PragmaIntroducer introducer, clang::Token &buildTypeToken) 
	{
		auto& sourceManager = preProcessor.getSourceManager();
		std::vector<std::string> strTokens;
		std::vector<clang::Token> tokens;
		clang::Token token = buildTypeToken;

		int counter = 0;
		while(token.isNot(clang::tok::eod))
		{
			// Get string from token
			const char* charData = sourceManager.getCharacterData(token.getLocation());
			std::string strData(charData, token.getLength());

			// Append
			strTokens.push_back(strData);
			if (counter != 0)
				tokens.insert(tokens.begin(), token);
			counter++;

			// Lex next token
			preProcessor.Lex(token);
		}

		// Write code to preprocessed buffer
		llvm::MemoryBufferRef buffer("std::cout << \"Hello from python\" << std::endl;", "<pargmatic>");
		auto tempFileID = sourceManager.createFileID(buffer);
		preProcessor.EnterSourceFile(tempFileID, nullptr, token.getLocation());
		
		// Offset lines
		const auto& location = token.getLocation();
		sourceManager.AddLineNote(location, 50, sourceManager.getLineTableFilenameID(sourceManager.getFilename(location)), true, false, clang::SrcMgr::C_User);

		llvm::outs() << "Test pragma reached !" << "\n";
		for (auto& tokenStr : strTokens) llvm::outs() << tokenStr << "\n";
	}
}} // namesapce QED::Pragmatic