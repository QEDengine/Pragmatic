// Source header
#include "PragmaHandler.hpp"
#include "clang/Basic/SourceLocation.h"
#include "clang/Basic/TokenKinds.h"

// Clang
#include <clang/Lex/Preprocessor.h>

// Pragmatic
#include "Utility.hpp"

namespace QED { namespace Pragmatic
{
	static bool shouldRecompile = false;

	void PragmaHandler::HandlePragma(clang::Preprocessor &preprocessor, clang::PragmaIntroducer introducer, clang::Token &sourceToken)
	{
		// Get clang utilities
		auto& sourceManager = preprocessor.getSourceManager();
		auto& diagnostics = preprocessor.getDiagnostics();

		// Get constants
		auto sourceLocation = sourceToken.getLocation();
		sourceFilePath = NormalizePath(sourceManager.getFilename(sourceLocation).str(), sourceManager.getFileManager().getFileSystemOpts().WorkingDir);
		sourceFileDir = GetDirectoryFromPath(sourceFilePath);
		auto fullSourceLocation = clang::FullSourceLoc(sourceLocation, sourceManager);
		includePath = sourceManager.getFilename(sourceManager.getIncludeLoc(fullSourceLocation.getFileID())).str();
		
		// Get tokens
		int format_index = 0;
		std::vector<std::string> tokens;
		clang::Token token = sourceToken;
		while(token.isNot(clang::tok::eod))
		{
			// Check if there are too many tokes declared for pragma
			if (format_index >= format.size())
			{
				unsigned ID = diagnostics.getCustomDiagID(clang::DiagnosticsEngine::Error, "Too many tokens in directive");
				diagnostics.Report(sourceLocation, ID);
				return;
			}

			// Get string from token
			const char* charData = sourceManager.getCharacterData(token.getLocation());
			std::string strData(charData, token.getLength());

			// Check for string literals
			if ((token.getKind() == clang::tok::TokenKind::string_literal) != format[format_index].isStringLiteral)
			{
				unsigned ID = diagnostics.getCustomDiagID(clang::DiagnosticsEngine::Error, "Expected a string literal token");
				diagnostics.Report(sourceLocation, ID);
				return;
			}

			// Append
			if (token.getKind() == clang::tok::TokenKind::string_literal)
				strData = strData.substr(1, strData.size() - 2);
			tokens.push_back(strData);

			// Lex next token
			preprocessor.Lex(token);

			format_index++;
		}

		// Check if enough arguments were declared for pragma
		if (format_index < format.size() - optional)
		{
			unsigned ID = diagnostics.getCustomDiagID(clang::DiagnosticsEngine::Error, "Too many tokens in directive");
			diagnostics.Report(sourceLocation, ID);
			return;
		}

		// Check tokens
		bool success = this->CheckTokens(preprocessor, tokens, diagnostics, sourceLocation);
		if (!success) return;

		// Handle response & write back to preprocessed buffer if needed
		std::string response = Response(preprocessor, tokens, diagnostics);
		if (response.size() > 0)
		{
			// Write back
			llvm::MemoryBufferRef buffer(response, "<pragmatic>");
			auto tempFileID = sourceManager.createFileID(buffer);
			preprocessor.EnterSourceFile(tempFileID, nullptr, token.getLocation());

			// Offset lines
			const auto& location = token.getLocation();
			sourceManager.AddLineNote(location, 50, sourceManager.getLineTableFilenameID(sourceManager.getFilename(location)), true, false, clang::SrcMgr::C_User);
		}
	}
}} // namespace QED::Pragmatic
